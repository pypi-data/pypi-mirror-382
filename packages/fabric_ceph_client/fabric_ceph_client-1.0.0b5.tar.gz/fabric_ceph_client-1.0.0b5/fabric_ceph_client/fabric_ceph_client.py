# fabric_ceph_client.py
"""
Ceph Manager Client (Python)
----------------------------

Minimal, friendly wrapper for the FABRIC Ceph Manager service.

Features
- Token can be provided via `token` (string) or `token_file` (path to JSON or text file).
- If the file is JSON, the field `id_token` is extracted by default (configurable via `token_key`).
- Helper `refresh_token_from_file()` to re-read the file on demand.
- Also supports environment variables: FABRIC_CEPH_TOKEN, FABRIC_CEPH_TOKEN_FILE.
- X-Cluster routing header support.
- Retries on transient errors; handles JSON and text responses.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path
import json
import os

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# --------------------- Exceptions ---------------------

class ApiError(RuntimeError):
    def __init__(self, status: int, url: str, message: str = "", payload: Any = None):
        super().__init__(f"[{status}] {url} :: {message or payload}")
        self.status = status
        self.url = url
        self.message = message
        self.payload = payload


# --------------------- Client ---------------------

@dataclass
class CephManagerClient:
    base_url: str

    # Auth options (choose one):
    token: Optional[str] = None
    token_file: Optional[Union[str, Path]] = None
    token_key: str = "id_token"  # JSON field to extract when reading token_file

    timeout: int = 60
    verify: bool = True
    default_x_cluster: Optional[str] = None
    accept: str = "application/json, text/plain"

    # internal
    _session: requests.Session = field(init=False, repr=False, compare=False)

    def __post_init__(self):
        # Normalize base url (no trailing slash)
        self.base_url = self.base_url.rstrip("/")

        # Allow env overrides if args not set
        if not self.token and not self.token_file:
            env_token = os.getenv("FABRIC_CEPH_TOKEN")
            env_token_file = os.getenv("FABRIC_CEPH_TOKEN_FILE")
            if env_token:
                self.token = env_token
            elif env_token_file:
                self.token_file = env_token_file

        # If a token file is provided, load from it now
        if self.token_file and not self.token:
            self.refresh_token_from_file()

        self._session = requests.Session()
        # Robust retries for idempotent verbs
        retry = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET", "PUT", "DELETE", "POST"}),
            raise_on_status=False,
        )
        self._session.mount("http://", HTTPAdapter(max_retries=retry))
        self._session.mount("https://", HTTPAdapter(max_retries=retry))

    # ----- auth helpers -----

    def refresh_token_from_file(self) -> None:
        """
        Re-read `token_file` and set `self.token`.
        - If the file is JSON, extract `self.token_key` (default: 'id_token').
        - If not JSON, treat the file as plain-text with the token on a single line.
        """
        if not self.token_file:
            raise ValueError("token_file is not set")

        path = Path(self.token_file).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"Token file not found: {path}")

        raw = path.read_text(encoding="utf-8").strip()
        try:
            obj = json.loads(raw)
            token = (
                obj.get(self.token_key)
                or obj.get("access_token")
                or obj.get("token")
            )
            if not token:
                raise KeyError(
                    f"Token file JSON does not contain '{self.token_key}', 'access_token', or 'token'."
                )
            self.token = str(token).strip()
        except json.JSONDecodeError:
            # Plain text file containing the token
            self.token = raw

        if not self.token:
            raise ValueError("Token could not be loaded from token_file")

    # ----- internal request helpers -----

    def _headers(self, extra: Optional[Dict[str, str]] = None, x_cluster: Optional[str] = None) -> Dict[str, str]:
        h = {"Accept": self.accept}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        if x_cluster:
            h["X-Cluster"] = x_cluster
        elif self.default_x_cluster:
            h["X-Cluster"] = self.default_x_cluster
        if extra:
            h.update(extra)
        return h

    @staticmethod
    def _is_json(resp: requests.Response) -> bool:
        ct = (resp.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        return ct.endswith("/json") or ct.endswith("+json")

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        data: Optional[Union[str, bytes]] = None,
        headers: Optional[Dict[str, str]] = None,
        x_cluster: Optional[str] = None,
    ) -> Any:
        url = f"{self.base_url}{path if path.startswith('/') else '/' + path}"

        def _do():
            return self._session.request(
                method=method.upper(),
                url=url,
                params=params,
                json=json,
                data=data,
                headers=self._headers(headers, x_cluster=x_cluster),
                timeout=self.timeout,
                verify=self.verify,
            )

        resp = _do()

        # Optional: if token_file is configured and we got 401 once, refresh & retry once
        if resp.status_code == 401 and self.token_file:
            try:
                self.refresh_token_from_file()
                resp = _do()
            except Exception:
                pass

        if resp.status_code >= 400:
            # Try to parse structured error
            payload: Any
            message = ""
            if self._is_json(resp):
                try:
                    payload = resp.json()
                    message = (
                        payload.get("message")
                        or (payload.get("errors", [{}])[0].get("message")
                            if isinstance(payload.get("errors"), list) and payload["errors"] else "")
                        or payload.get("detail")
                        or ""
                    )
                except Exception:
                    payload = resp.text
            else:
                payload = resp.text
            raise ApiError(resp.status_code, url, message=message, payload=payload)

        # Success path: return JSON if JSON; else plain text
        if self._is_json(resp):
            return resp.json()
        return resp.text

    # --------------------- Cluster info ---------------------

    def list_cluster_info(self) -> Dict[str, Any]:
        """
        GET /cluster/info
        Returns an envelope with `data` = list of per-cluster objects:
          {
            "cluster": "europe",
            "fsid": "...",
            "mons": [{"name":"mon.a","v2":"ip:3300/0","v1":"ip:6789/0"}, ...],
            "mon_host": "[v2:...,v1:...] ...",
            "ceph_conf_minimal": "[global]\\n\\tfsid = ...\\n\\tmon_host = ...\\n",
            "error": null
          }
        """
        return self._request("GET", "/cluster/info")

    def cluster_minimal_confs(self) -> Dict[str, str]:
        """
        Convenience: returns {cluster_name: ceph_conf_minimal}.
        If a cluster has an error or missing snippet, it is omitted from the map.
        """
        info = self.list_cluster_info()
        out: Dict[str, str] = {}
        items = (info or {}).get("data", []) if isinstance(info, dict) else []
        for item in items:
            if isinstance(item, dict) and not item.get("error"):
                cluster = item.get("cluster")
                conf = item.get("ceph_conf_minimal")
                if cluster and isinstance(conf, str) and conf.strip():
                    out[cluster] = conf
        return out

    # --------------------- Cluster User (templated, cross-cluster sync) ---------------------

    def apply_user_templated(
            self,
            *,
            user_entity: str,
            template_capabilities: List[Dict[str, str]],
            fs_name: Optional[str] = None,
            subvol_name: Optional[str] = None,
            group_name: Optional[str] = None,
            # NEW:
            renders: Optional[List[Dict[str, str]]] = None,
            extra_subs: Optional[Dict[str, str]] = None,
            merge_strategy: Optional[str] = None,  # e.g. "comma", "multi", "auto"
            dry_run: bool = False,
            sync_across_clusters: bool = True,
            preferred_source: Optional[str] = None,
            x_cluster: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        POST /cluster/user

        Body (compat: either 'render' OR 'renders'):
          {
            "user_entity": "...",
            "template_capabilities": [
              {"entity": "mon", "cap": "allow r"},
              {"entity": "mds", "cap": "allow rw fsname={fs} path={path}"},
              {"entity": "osd", "cap": "allow rw tag cephfs data={fs}"}
            ],
            "render":  { "fs_name": "...", "subvol_name": "...", "group_name": "..." },
            "renders": [ { "fs_name": "...", "subvol_name": "...", "group_name": "..." }, ... ],
            "extra_subs": { "project": "p123" },
            "merge_strategy": "comma",
            "dry_run": false,
            "sync_across_clusters": true,
            "preferred_source": "europe"
          }
        """
        payload: Dict[str, Any] = {
            "user_entity": user_entity,
            "template_capabilities": template_capabilities,
            "sync_across_clusters": bool(sync_across_clusters),
            "dry_run": bool(dry_run),
        }

        # Back-compat single-render (if renders not provided)
        if renders and len(renders) > 0:
            # normalize items to only allowed keys
            norm = []
            for rc in renders:
                item = {
                    "fs_name": rc["fs_name"],
                    "subvol_name": rc["subvol_name"],
                }
                if rc.get("group_name"):
                    item["group_name"] = rc["group_name"]
                norm.append(item)
            payload["renders"] = norm
        else:
            if not fs_name or not subvol_name:
                raise ValueError("Either (fs_name & subvol_name) or 'renders' must be provided")
            payload["render"] = {"fs_name": fs_name, "subvol_name": subvol_name}
            if group_name:
                payload["render"]["group_name"] = group_name

        if preferred_source:
            payload["preferred_source"] = preferred_source
        if extra_subs:
            payload["extra_subs"] = extra_subs
        if merge_strategy:
            payload["merge_strategy"] = merge_strategy  # server-defined strategies

        return self._request("POST", "/cluster/user", json=payload, x_cluster=x_cluster)

    def apply_user_for_multiple_subvols(
            self,
            *,
            user_entity: str,
            template_capabilities: List[Dict[str, str]],
            contexts: List[Tuple[str, str, Optional[str]]],  # (fs_name, subvol_name, group_name)
            sync_across_clusters: bool = True,
            preferred_source: Optional[str] = None,
            merge_strategy: Optional[str] = "comma",
            dry_run: bool = False,
            x_cluster: Optional[str] = None,
            extra_subs: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        renders = []
        for fs_name, subvol_name, group_name in contexts:
            item = {"fs_name": fs_name, "subvol_name": subvol_name}
            if group_name:
                item["group_name"] = group_name
            renders.append(item)

        return self.apply_user_templated(
            user_entity=user_entity,
            template_capabilities=template_capabilities,
            renders=renders,
            extra_subs=extra_subs,
            merge_strategy=merge_strategy,
            dry_run=dry_run,
            sync_across_clusters=sync_across_clusters,
            preferred_source=preferred_source,
            x_cluster=x_cluster,
        )

    def list_users(self, *, x_cluster: Optional[str] = None) -> Dict[str, Any]:
        """GET /cluster/user"""
        return self._request("GET", "/cluster/user", x_cluster=x_cluster)

    def delete_user(self, entity: str, *, x_cluster: Optional[str] = None) -> Dict[str, Any]:
        """DELETE /cluster/user/{entity}"""
        return self._request("DELETE", f"/cluster/user/{entity}", x_cluster=x_cluster)

    def export_users(self, entities: List[str], *, x_cluster: Optional[str] = None) -> str:
        """
        POST /cluster/user/export
        Returns keyring text. Handles both plain-text and JSON-envelope (`{"keyring": "..."}").
        """
        if not entities:
            raise ValueError("entities must be a non-empty list")
        res = self._request("POST", "/cluster/user/export", json={"entities": entities}, x_cluster=x_cluster)
        if isinstance(res, dict) and "keyring" in res:
            return str(res["keyring"])
        if isinstance(res, str):
            return res
        return str(res)

    # --------------------- CephFS (subvolumes) ---------------------

    def create_or_resize_subvolume(
        self,
        vol_name: str,
        subvol_name: str,
        *,
        group_name: Optional[str] = None,
        size: Optional[int] = None,
        mode: Optional[str] = None,
        x_cluster: Optional[str] = None,
    ) -> Dict[str, Any]:
        """PUT /cephfs/subvolume/{vol_name}"""
        payload: Dict[str, Any] = {"subvol_name": subvol_name}
        if group_name:
            payload["group_name"] = group_name
        if size is not None:
            payload["size"] = int(size)
        if mode:
            payload["mode"] = str(mode)
        return self._request("PUT", f"/cephfs/subvolume/{vol_name}", json=payload, x_cluster=x_cluster)

    def get_subvolume_info(
        self, vol_name: str, subvol_name: str, *, group_name: Optional[str] = None, x_cluster: Optional[str] = None
    ) -> Dict[str, Any]:
        """GET /cephfs/subvolume/{vol_name}/info"""
        params = {"subvol_name": subvol_name}
        if group_name:
            params["group_name"] = group_name
        return self._request("GET", f"/cephfs/subvolume/{vol_name}/info", params=params, x_cluster=x_cluster)

    def subvolume_exists(
        self, vol_name: str, subvol_name: str, *, group_name: Optional[str] = None, x_cluster: Optional[str] = None
    ) -> bool:
        """GET /cephfs/subvolume/{vol_name}/exists -> {'exists': bool}"""
        params = {"subvol_name": subvol_name}
        if group_name:
            params["group_name"] = group_name
        res = self._request("GET", f"/cephfs/subvolume/{vol_name}/exists", params=params, x_cluster=x_cluster)
        if isinstance(res, dict) and "exists" in res:
            return bool(res["exists"])
        return bool(res)

    def delete_subvolume(
        self,
        vol_name: str,
        subvol_name: str,
        *,
        group_name: Optional[str] = None,
        force: bool = False,
        x_cluster: Optional[str] = None,
    ) -> Dict[str, Any]:
        """DELETE /cephfs/subvolume/{vol_name}"""
        params: Dict[str, Any] = {"subvol_name": subvol_name, "force": str(bool(force)).lower()}
        if group_name:
            params["group_name"] = group_name
        return self._request("DELETE", f"/cephfs/subvolume/{vol_name}", params=params, x_cluster=x_cluster)
