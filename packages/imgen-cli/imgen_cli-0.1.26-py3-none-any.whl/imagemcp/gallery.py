from __future__ import annotations

import http.server
import json
import mimetypes
import socketserver
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional
from urllib.parse import parse_qs, quote, unquote, urlparse

from . import SessionManager, build_slot_index
from .config import (
    ProjectConfig,
    ensure_project_config,
    get_project_index_path,
    load_project_index,
    register_project,
)
from .models import format_ts
from .storage import (
    InvalidPathError,
    ProjectPaths,
    delete_slot,
    list_manifests_for_slot,
    load_manifest,
)
from .campaign.workspace import CampaignWorkspace
from .campaign.schemas import (
    CampaignConfig,
    CampaignRoute,
    ExportManifest,
    PlacementManifest,
    ReviewState,
    RouteSeed,
)


ISO_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def _parse_timestamp(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.strptime(value, ISO_FORMAT)
    except Exception:  # pragma: no cover - fallback for unexpected formats
        return None


def _format_optional_timestamp(value: Optional[datetime]) -> Optional[str]:
    if value is None:
        return None
    return format_ts(value)


def _as_review_state(value) -> str:
    if isinstance(value, ReviewState):
        return value.value
    return str(value)


def _iter_campaign_workspaces(paths: ProjectPaths) -> Iterable[CampaignWorkspace]:
    campaigns_root = paths.campaigns_root
    if not campaigns_root.exists():
        return []
    workspaces: List[CampaignWorkspace] = []
    for entry in sorted(campaigns_root.iterdir()):
        if not entry.is_dir():
            continue
        workspace = CampaignWorkspace(paths, entry.name)
        if workspace.config_path.exists():
            workspaces.append(workspace)
    return workspaces


def _collect_routes(config: CampaignConfig, workspace: CampaignWorkspace) -> Dict[str, Dict[str, object]]:
    routes: Dict[str, Dict[str, object]] = {}
    try:
        for route in workspace.iter_routes() or []:
            routes[route.route_id] = {
                "routeId": route.route_id,
                "name": route.name,
                "summary": route.summary,
                "status": _as_review_state(route.status),
                "source": route.source,
                "promptTemplate": route.prompt_template,
                "promptTokens": list(route.prompt_tokens),
                "copyTokens": list(route.copy_tokens),
                "assetRefs": list(route.asset_refs),
            }
    except Exception:
        # Keep partial data if any route file fails to parse
        pass

    for seed in config.routes:
        if seed.route_id in routes:
            continue
        routes[seed.route_id] = {
            "routeId": seed.route_id,
            "name": seed.name,
            "summary": seed.summary,
            "status": _as_review_state(seed.status),
            "source": "seed",
            "promptTemplate": None,
            "promptTokens": list(seed.prompt_tokens),
            "copyTokens": list(seed.copy_tokens),
            "assetRefs": [],
        }
    return routes


def _collect_manifests(workspace: CampaignWorkspace) -> Dict[str, PlacementManifest]:
    manifests: Dict[str, PlacementManifest] = {}
    try:
        for manifest in workspace.iter_manifests() or []:
            manifests[manifest.placement_id] = manifest
    except Exception:
        pass
    return manifests


def _placement_state_counts(manifest: PlacementManifest) -> Dict[str, int]:
    counts: Dict[str, int] = {state.value: 0 for state in ReviewState}
    for route_entry in manifest.routes:
        for variant in route_entry.variants:
            state_key = _as_review_state(variant.review_state)
            counts[state_key] = counts.get(state_key, 0) + 1
    return counts


def _build_campaign_summary(workspace: CampaignWorkspace, project_id: str) -> Dict[str, object]:
    try:
        config = workspace.load_config()
    except Exception:
        return {}

    manifests = _collect_manifests(workspace)
    total_variants = 0
    counts: Dict[str, int] = {state.value: 0 for state in ReviewState}
    latest = None
    for manifest in manifests.values():
        updated_at = _parse_timestamp(manifest.updated_at)
        if updated_at and (latest is None or updated_at > latest):
            latest = updated_at
        for route_entry in manifest.routes:
            for variant in route_entry.variants:
                total_variants += 1
                state_key = _as_review_state(variant.review_state)
                counts[state_key] = counts.get(state_key, 0) + 1

    routes_count = len(_collect_routes(config, workspace))
    placements_count = len(config.placements) or len(manifests)
    approved = counts.get(ReviewState.APPROVED.value, 0)

    summary = {
        "projectId": project_id,
        "campaignId": config.campaign_id,
        "name": config.name,
        "status": _as_review_state(config.status),
        "tags": list(config.tags),
        "routes": routes_count,
        "placements": placements_count,
        "variants": total_variants,
        "approved": approved,
        "pending": counts.get(ReviewState.PENDING.value, 0),
        "revise": counts.get(ReviewState.REVISE.value, 0),
        "defaultProvider": config.default_provider,
        "updatedAt": _format_optional_timestamp(latest),
    }
    return summary


def _campaign_export_entries(workspace: CampaignWorkspace) -> List[Dict[str, object]]:
    entries: List[Dict[str, object]] = []
    exports_dir = workspace.exports_dir
    if not exports_dir.exists():
        return entries
    for manifest_path in sorted(exports_dir.rglob("manifest.json")):
        try:
            export_manifest = workspace.load_export_manifest(manifest_path)
        except Exception:
            continue
        entries.append(
            {
                "platform": export_manifest.platform,
                "exportId": export_manifest.export_id,
                "generatedAt": export_manifest.generated_at,
                "includeStates": [
                    _as_review_state(state) for state in (export_manifest.include_states or [])
                ],
                "fileCount": len(export_manifest.files),
                "csvFiles": [
                    {
                        "name": csv_file.name,
                        "path": csv_file.path,
                        "rowCount": csv_file.row_count,
                    }
                    for csv_file in export_manifest.csv_files
                ],
                "manifestPath": str(manifest_path.relative_to(workspace.root)),
            }
        )
    entries.sort(key=lambda item: item.get("generatedAt") or "", reverse=True)
    return entries


def _campaign_log_entries(workspace: CampaignWorkspace) -> List[Dict[str, object]]:
    logs: List[Dict[str, object]] = []
    logs_dir = workspace.logs_dir
    if not logs_dir.exists():
        return logs
    for log_path in sorted(logs_dir.glob("batch-*.jsonl")):
        try:
            stat = log_path.stat()
        except OSError:
            continue
        updated_at = datetime.utcfromtimestamp(stat.st_mtime)
        logs.append(
            {
                "filename": log_path.name,
                "updatedAt": format_ts(updated_at),
                "sizeBytes": stat.st_size,
                "relativePath": str(log_path.relative_to(workspace.root)),
            }
        )
    logs.sort(key=lambda item: item.get("updatedAt") or "", reverse=True)
    return logs


def _build_campaign_detail(workspace: CampaignWorkspace, project_id: str) -> Dict[str, object]:
    try:
        config = workspace.load_config()
    except Exception:
        return {}

    routes_map = _collect_routes(config, workspace)
    manifests = _collect_manifests(workspace)

    placement_entries: List[Dict[str, object]] = []
    seen_placements: set[str] = set()
    for placement in config.placements:
        placement_id = placement.override_id or placement.template_id
        seen_placements.add(placement_id)
        manifest = manifests.get(placement_id)
        counts = {state.value: 0 for state in ReviewState}
        total = 0
        updated_at = None
        if manifest:
            updated_at = manifest.updated_at
            for route_entry in manifest.routes:
                for variant in route_entry.variants:
                    total += 1
                    state_key = _as_review_state(variant.review_state)
                    counts[state_key] = counts.get(state_key, 0) + 1
        placement_entries.append(
            {
                "placementId": placement_id,
                "templateId": placement.template_id,
                "variants": total,
                "counts": counts,
                "provider": placement.provider,
                "notes": placement.notes,
                "updatedAt": updated_at,
            }
        )

    # Include manifests that reference placements not in the current config
    for placement_id, manifest in manifests.items():
        if placement_id in seen_placements:
            continue
        counts = {state.value: 0 for state in ReviewState}
        total = 0
        for route_entry in manifest.routes:
            for variant in route_entry.variants:
                total += 1
                state_key = _as_review_state(variant.review_state)
                counts[state_key] = counts.get(state_key, 0) + 1
        placement_entries.append(
            {
                "placementId": placement_id,
                "templateId": manifest.template_id,
                "variants": total,
                "counts": counts,
                "provider": None,
                "notes": None,
                "updatedAt": manifest.updated_at,
            }
        )

    total_variants = 0
    state_totals: Dict[str, int] = {state.value: 0 for state in ReviewState}
    matrix: List[Dict[str, object]] = []

    for placement_id, manifest in manifests.items():
        for route_entry in manifest.routes:
            variants_payload: List[Dict[str, object]] = []
            for variant in route_entry.variants:
                state_key = _as_review_state(variant.review_state)
                state_totals[state_key] = state_totals.get(state_key, 0) + 1
                total_variants += 1
                variants_payload.append(
                    {
                        "variantId": variant.variant_id,
                        "index": variant.index,
                        "file": variant.file,
                        "thumbnail": variant.thumbnail,
                        "reviewState": state_key,
                        "seed": variant.seed,
                        "prompt": variant.prompt,
                        "createdAt": variant.created_at,
                        "notes": variant.review_notes,
                        "provider": variant.provider,
                        "placementId": placement_id,
                        "routeId": route_entry.route_id,
                    }
                )
            matrix.append(
                {
                    "placementId": placement_id,
                    "routeId": route_entry.route_id,
                    "routeSummary": route_entry.summary,
                    "routeStatus": _as_review_state(route_entry.status),
                    "variants": variants_payload,
                }
            )

    # Sort for stable output
    placement_entries.sort(key=lambda item: item["placementId"])
    matrix.sort(key=lambda item: (item["placementId"], item["routeId"]))

    summary_latest = max(
        filter(None, (_parse_timestamp(item.get("updatedAt")) for item in placement_entries)),
        default=None,
    )

    detail = {
        "campaign": {
            "projectId": project_id,
            "campaignId": config.campaign_id,
            "name": config.name,
            "status": _as_review_state(config.status),
            "tags": list(config.tags),
            "defaultProvider": config.default_provider,
            "notes": config.notes,
            "brief": config.brief.model_dump(mode="python"),
            "variantDefaults": config.variant_defaults.model_dump(mode="python"),
            "updatedAt": _format_optional_timestamp(summary_latest),
        },
        "routes": list(routes_map.values()),
        "placements": placement_entries,
        "matrix": matrix,
        "stats": {
            "total": total_variants,
            "approved": state_totals.get(ReviewState.APPROVED.value, 0),
            "pending": state_totals.get(ReviewState.PENDING.value, 0),
            "revise": state_totals.get(ReviewState.REVISE.value, 0),
        },
        "exports": _campaign_export_entries(workspace),
        "logs": _campaign_log_entries(workspace),
    }
    detail["campaign"]["routesCount"] = len(detail["routes"])
    detail["campaign"]["placementsCount"] = len(detail["placements"])
    return detail


@dataclass
class ProjectInfo:
    project_id: str
    project_name: str
    project_root: Path
    target_root: str


@dataclass
class ProjectContext:
    info: ProjectInfo
    paths: ProjectPaths
    manager: SessionManager


class ProjectRegistry:
    def __init__(self, default_config: ProjectConfig, default_paths: ProjectPaths) -> None:
        self._default_id = default_config.project_id
        self._contexts: Dict[str, ProjectContext] = {}
        self._index_path = get_project_index_path()
        self.register_config(default_config, default_paths)

    def register_config(
        self,
        config: ProjectConfig,
        paths: Optional[ProjectPaths] = None,
    ) -> None:
        info = ProjectInfo(
            project_id=config.project_id,
            project_name=config.project_name,
            project_root=config.project_root,
            target_root=config.target_root,
        )
        if paths is None:
            paths = ProjectPaths.create(config.project_root, Path(config.target_root))
            paths.ensure_directories()
        context = ProjectContext(info=info, paths=paths, manager=SessionManager(paths))
        self._contexts[info.project_id] = context

    def list_projects(self) -> List[ProjectInfo]:
        projects: Dict[str, ProjectInfo] = {
            context.info.project_id: context.info for context in self._contexts.values()
        }
        for entry in load_project_index():
            info = ProjectInfo(
                project_id=entry.project_id,
                project_name=entry.project_name,
                project_root=entry.project_root,
                target_root=entry.target_root,
            )
            projects[info.project_id] = info
        return list(projects.values())

    def get_context(self, project_id: Optional[str]) -> ProjectContext:
        if not project_id:
            project_id = self._default_id
        context = self._contexts.get(project_id)
        if context:
            return context
        for info in self.list_projects():
            if info.project_id == project_id:
                paths = ProjectPaths.create(info.project_root, Path(info.target_root))
                paths.ensure_directories()
                context = ProjectContext(info=info, paths=paths, manager=SessionManager(paths))
                self._contexts[project_id] = context
                return context
        raise KeyError(project_id)

    def default_project(self) -> ProjectInfo:
        return self.get_context(self._default_id).info



class GalleryServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

    def __init__(self, address: tuple[str, int], registry: ProjectRegistry) -> None:
        handler = _make_handler(registry)
        super().__init__(address, handler)
        self.registry = registry


def serve_gallery(
    config: ProjectConfig,
    paths: ProjectPaths,
    host: str = "127.0.0.1",
    port: int = 8765,
) -> None:
    registry = ProjectRegistry(config, paths)
    with GalleryServer((host, port), registry) as server:
        print(f"Gallery serving at http://{host}:{port}/")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("Stopping gallery...")


def _make_handler(registry: ProjectRegistry):

    class Handler(http.server.BaseHTTPRequestHandler):
        server_version = "ImageGallery/1.0"

        def do_GET(self) -> None:  # noqa: N802 (HTTP method name)
            parsed = urlparse(self.path)
            if parsed.path == "/":
                return self._serve_app(parsed)
            if parsed.path == "/media":
                return self._handle_media(parsed)
            if parsed.path == "/media/campaign":
                return self._handle_campaign_media(parsed)
            if parsed.path == "/selected":
                return self._handle_selected(parsed)
            if parsed.path.startswith("/api/"):
                return self._handle_api(parsed)
            self._not_found()

        def do_POST(self) -> None:  # noqa: N802
            if self.path == "/select":
                return self._handle_select(redirect=True)
            if self.path == "/api/select":
                return self._handle_select(redirect=False)
            if self.path == "/api/register":
                return self._handle_register()
            parsed = urlparse(self.path)
            parts = [segment for segment in parsed.path.strip("/").split("/") if segment]
            if (
                len(parts) == 4
                and parts[0] == "api"
                and parts[1] == "campaigns"
                and parts[3] == "review"
            ):
                campaign_id = unquote(parts[2])
                params = parse_qs(parsed.query)
                project_id = params.get("project", [None])[0]
                return self._handle_api_campaign_review(project_id, campaign_id)
            self._not_found()

        def do_DELETE(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            parts = [segment for segment in parsed.path.strip("/").split("/") if segment]
            if len(parts) == 3 and parts[0] == "api" and parts[1] == "slots":
                params = parse_qs(parsed.query)
                project_id = params.get("project", [None])[0]
                slot = unquote(parts[2])
                return self._handle_api_slot_delete(project_id, slot)
            self._not_found()

        def _handle_media(self, parsed) -> None:
            params = parse_qs(parsed.query)
            project_id = params.get("project", [None])[0]
            slot = params.get("slot", [None])[0]
            session_id = params.get("session", [None])[0]
            filename = params.get("file", [None])[0]
            if not slot or not session_id or not filename:
                return self._not_found()
            context = self._get_context(project_id)
            if context is None:
                return self._not_found()
            try:
                ctx = context.manager.create_context(slot, session_id)
            except (ValueError, InvalidPathError):
                return self._not_found()
            manifest_path = ctx.manifest_path
            if not manifest_path.exists():
                return self._not_found()
            manifest = context.manager.read_manifest(ctx)
            allowed = {image.filename for image in manifest.images}
            allowed.update({image.raw_filename for image in manifest.images if image.raw_filename})
            if filename not in allowed:
                return self._not_found()
            file_path = ctx.session_dir / filename
            if not file_path.exists():
                return self._not_found()
            content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
            with file_path.open("rb") as fh:
                data = fh.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _handle_campaign_media(self, parsed) -> None:
            params = parse_qs(parsed.query)
            project_id = params.get("project", [None])[0]
            campaign_id = params.get("campaign", [None])[0]
            rel_path = params.get("path", [None])[0]
            if not campaign_id or not rel_path:
                return self._not_found()
            context = self._get_context(project_id)
            if context is None:
                return self._not_found()
            workspace = CampaignWorkspace(context.paths, campaign_id)
            target = (workspace.root / rel_path).resolve()
            try:
                target.relative_to(workspace.root)
            except ValueError:
                return self._not_found()
            if not target.exists() or not target.is_file():
                return self._not_found()
            content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
            with target.open("rb") as fh:
                data = fh.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _handle_selected(self, parsed) -> None:
            params = parse_qs(parsed.query)
            project_id = params.get("project", [None])[0]
            slot = params.get("slot", [None])[0]
            if slot is None:
                return self._bad_request("Missing slot")
            context = self._get_context(project_id)
            if context is None:
                return self._not_found()
            try:
                target_path = context.paths.target_for_slot(slot)
            except (ValueError, InvalidPathError):
                return self._not_found()
            if not target_path.exists():
                return self._not_found()
            content_type = mimetypes.guess_type(str(target_path))[0] or "application/octet-stream"
            with target_path.open("rb") as fh:
                data = fh.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _handle_select(self, redirect: bool) -> None:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length).decode("utf-8")
            params = parse_qs(body)
            project_id = params.get("project", [None])[0]
            slot = params.get("slot", [None])[0]
            session_id = params.get("session", [None])[0]
            index_raw = params.get("index", [None])[0]
            if slot is None or session_id is None or index_raw is None:
                return self._bad_request("Missing parameters")
            try:
                index = int(index_raw)
            except ValueError:
                return self._bad_request("Invalid index")
            context = self._get_context(project_id)
            if context is None:
                return self._not_found()
            try:
                ctx = context.manager.create_context(slot, session_id)
            except (ValueError, InvalidPathError):
                return self._not_found()
            if not ctx.manifest_path.exists():
                return self._not_found()
            manifest = context.manager.read_manifest(ctx)
            if index < 0 or index >= len(manifest.images):
                return self._bad_request("Index out of range")
            context.manager.promote_variant(ctx, manifest, index)
            if redirect:
                redirect_to = "/"
                self.send_response(303)
                self.send_header("Location", redirect_to)
                self.end_headers()
                return
            response = {
                "ok": True,
                "projectId": context.info.project_id,
                "slot": slot,
                "sessionId": session_id,
                "selectedIndex": index,
            }
            self._write_json(response)

        def _handle_api(self, parsed) -> None:
            parts = [segment for segment in parsed.path.strip("/").split("/") if segment]
            if len(parts) == 1 and parts[0] == "api":
                return self._write_json({"ok": True})
            if len(parts) == 2 and parts[0] == "api" and parts[1] == "projects":
                return self._handle_api_projects()
            if len(parts) >= 2 and parts[0] == "api" and parts[1] == "campaigns":
                params = parse_qs(parsed.query)
                project_id = params.get("project", [None])[0]
                if len(parts) == 2:
                    return self._handle_api_campaigns(project_id)
                campaign_id = unquote(parts[2])
                if len(parts) == 3:
                    return self._handle_api_campaign_detail(project_id, campaign_id)
                if len(parts) == 5 and parts[3] == "placements":
                    placement_id = unquote(parts[4])
                    return self._handle_api_campaign_placement(
                        project_id,
                        campaign_id,
                        placement_id,
                        params,
                    )
            if len(parts) >= 2 and parts[0] == "api" and parts[1] == "slots":
                params = parse_qs(parsed.query)
                project_id = params.get("project", [None])[0]
                if len(parts) == 2:
                    return self._handle_api_slots(project_id)
                slot = unquote(parts[2])
                if len(parts) == 3:
                    return self._handle_api_slot(project_id, slot)
                if len(parts) == 4 and parts[3] == "sessions":
                    return self._handle_api_slot_sessions(project_id, slot)
                if len(parts) == 5 and parts[3] == "sessions":
                    session_id = unquote(parts[4])
                    return self._handle_api_session_detail(project_id, slot, session_id)
            self._not_found()

        def _handle_api_projects(self) -> None:
            projects = []
            for info in registry.list_projects():
                projects.append(
                    {
                        "projectId": info.project_id,
                        "projectName": info.project_name,
                        "projectRoot": str(info.project_root),
                        "targetRoot": info.target_root,
                    }
                )
            default_info = registry.default_project()
            self._write_json(
                {
                    "projects": projects,
                    "defaultProjectId": default_info.project_id,
                }
            )

        def _handle_api_campaigns(self, project_id: Optional[str]) -> None:
            context = self._get_context(project_id)
            if context is None:
                return self._not_found()
            items: List[Dict[str, object]] = []
            for workspace in _iter_campaign_workspaces(context.paths):
                summary = _build_campaign_summary(workspace, context.info.project_id)
                if summary:
                    items.append(summary)
            items.sort(key=lambda item: (item.get("name") or item.get("campaignId") or "").lower())
            self._write_json(
                {
                    "projectId": context.info.project_id,
                    "projectName": context.info.project_name,
                    "campaigns": items,
                }
            )

        def _handle_api_campaign_detail(self, project_id: Optional[str], campaign_id: str) -> None:
            context = self._get_context(project_id)
            if context is None:
                return self._not_found()
            workspace = CampaignWorkspace(context.paths, campaign_id)
            if not workspace.config_path.exists():
                return self._not_found()
            detail = _build_campaign_detail(workspace, context.info.project_id)
            if not detail:
                return self._not_found()
            self._augment_campaign_detail(detail, context, workspace)
            self._write_json(detail)

        def _handle_api_campaign_placement(
            self,
            project_id: Optional[str],
            campaign_id: str,
            placement_id: str,
            params: Dict[str, List[str]],
        ) -> None:
            context = self._get_context(project_id)
            if context is None:
                return self._not_found()
            workspace = CampaignWorkspace(context.paths, campaign_id)
            if not workspace.config_path.exists():
                return self._not_found()
            manifests = _collect_manifests(workspace)
            manifest = manifests.get(placement_id)
            if manifest is None:
                return self._not_found()
            state_filter = params.get("state", [None])[0]
            allowed_state = _as_review_state(state_filter) if state_filter else None
            variants: List[Dict[str, object]] = []
            for route_entry in manifest.routes:
                for variant in route_entry.variants:
                    state_key = _as_review_state(variant.review_state)
                    if allowed_state and state_key != allowed_state:
                        continue
                    variant_payload = {
                        "variantId": variant.variant_id,
                        "index": variant.index,
                        "file": variant.file,
                        "thumbnail": variant.thumbnail,
                        "reviewState": state_key,
                        "seed": variant.seed,
                        "prompt": variant.prompt,
                        "notes": variant.review_notes,
                        "createdAt": variant.created_at,
                        "placementId": placement_id,
                        "routeId": route_entry.route_id,
                    }
                    variants.append(variant_payload)
            placement_counts = _placement_state_counts(manifest)
            response = {
                "placementId": placement_id,
                "campaignId": campaign_id,
                "variants": variants,
                "counts": placement_counts,
                "updatedAt": manifest.updated_at,
            }
            self._augment_campaign_variants(response["variants"], context, workspace)
            self._write_json(response)

        def _handle_api_campaign_review(self, project_id: Optional[str], campaign_id: str) -> None:
            context = self._get_context(project_id)
            if context is None:
                return self._not_found()
            workspace = CampaignWorkspace(context.paths, campaign_id)
            if not workspace.config_path.exists():
                return self._not_found()

            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length else b"{}"
            try:
                payload = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError:
                return self._bad_request("Invalid JSON payload")

            placement_id = payload.get("placementId") or payload.get("placement_id")
            route_id = payload.get("routeId") or payload.get("route_id")
            variant_index = payload.get("variantIndex") or payload.get("variant_index")
            state_value = payload.get("state")
            notes = payload.get("notes")

            if placement_id is None or route_id is None or variant_index is None or state_value is None:
                return self._bad_request("Missing required fields")

            try:
                variant_index = int(variant_index)
            except (TypeError, ValueError):
                return self._bad_request("variantIndex must be an integer")

            try:
                new_state = ReviewState(state_value)
            except ValueError:
                return self._bad_request("Invalid review state")

            manifests = _collect_manifests(workspace)
            manifest = manifests.get(placement_id)
            if manifest is None:
                return self._not_found()

            target_variant = None
            for route_entry in manifest.routes:
                if route_entry.route_id != route_id:
                    continue
                for variant in route_entry.variants:
                    if variant.index == variant_index:
                        target_variant = variant
                        break
                if target_variant:
                    break

            if target_variant is None:
                return self._not_found()

            target_variant.review_state = new_state
            if notes is not None:
                target_variant.review_notes = notes or None
            manifest.updated_at = format_ts(datetime.utcnow())

            workspace.save_manifest(manifest)

            placement_counts = _placement_state_counts(manifest)
            all_manifests = _collect_manifests(workspace)
            totals: Dict[str, int] = {state.value: 0 for state in ReviewState}
            total_variants = 0
            for item in all_manifests.values():
                counts = _placement_state_counts(item)
                for key, value in counts.items():
                    totals[key] = totals.get(key, 0) + value
                    total_variants += value

            variant_payload = {
                "variantId": target_variant.variant_id,
                "index": target_variant.index,
                "file": target_variant.file,
                "thumbnail": target_variant.thumbnail,
                "reviewState": new_state.value,
                "seed": target_variant.seed,
                "prompt": target_variant.prompt,
                "notes": target_variant.review_notes,
                "createdAt": target_variant.created_at,
                "placementId": placement_id,
                "routeId": route_id,
            }

            self._augment_campaign_variants([variant_payload], context, workspace)

            response = {
                "ok": True,
                "campaignId": campaign_id,
                "placementId": placement_id,
                "routeId": route_id,
                "counts": placement_counts,
                "stats": {
                    "total": total_variants,
                    "approved": totals.get(ReviewState.APPROVED.value, 0),
                    "pending": totals.get(ReviewState.PENDING.value, 0),
                    "revise": totals.get(ReviewState.REVISE.value, 0),
                },
                "variant": variant_payload,
            }
            self._write_json(response)

        def _handle_api_slots(self, project_id: Optional[str]) -> None:
            context = self._get_context(project_id)
            if context is None:
                return self._not_found()
            summaries = build_slot_index(context.paths)
            items = []
            for slot, summary in sorted(summaries.items()):
                last_updated = summary.last_updated
                items.append(
                    {
                        "slot": slot,
                        "sessionCount": summary.session_count,
                        "selectedPath": summary.selected_path,
                        "selectedIndex": summary.selected_index,
                        "lastUpdated": format_ts(last_updated) if last_updated else None,
                        "warningCount": len(summary.warnings),
                        "selectedImageUrl": self._selected_image_url(context.info.project_id, slot),
                    }
                )
            self._write_json(
                {
                    "projectId": context.info.project_id,
                    "projectName": context.info.project_name,
                    "slots": items,
                }
            )

        def _handle_api_slot(self, project_id: Optional[str], slot: str) -> None:
            context = self._get_context(project_id)
            if context is None:
                return self._not_found()
            try:
                manifests = list_manifests_for_slot(context.paths, slot)
            except (ValueError, InvalidPathError):
                return self._not_found()
            manifests.sort(key=lambda m: m.completed_at, reverse=True)
            summaries = [self._summarize_session(context, manifest) for manifest in manifests]
            variants: List[Dict[str, object]] = []
            slot_selected_hash = None
            current_selection = None
            if manifests:
                latest_manifest = manifests[0]
                if latest_manifest.images:
                    selected_index = latest_manifest.selected_index
                    if 0 <= selected_index < len(latest_manifest.images):
                        selected_image = latest_manifest.images[selected_index]
                        slot_selected_hash = selected_image.sha256
                        current_selection = {
                            "projectId": context.info.project_id,
                            "projectName": context.info.project_name,
                            "slot": latest_manifest.slot,
                            "sessionId": latest_manifest.session_id,
                            "variantIndex": selected_index,
                            "completedAt": format_ts(latest_manifest.completed_at),
                            "processed": {
                                "url": self._variant_media_url(
                                    context.info.project_id,
                                    latest_manifest.slot,
                                    latest_manifest.session_id,
                                    selected_image.filename,
                                ),
                                "filename": selected_image.filename,
                                "width": selected_image.width,
                                "height": selected_image.height,
                                "mediaType": selected_image.media_type,
                            },
                            "raw": (
                                {
                                    "url": self._variant_media_url(
                                        context.info.project_id,
                                        latest_manifest.slot,
                                        latest_manifest.session_id,
                                        selected_image.raw_filename,
                                    ),
                                    "filename": selected_image.raw_filename,
                                }
                                if selected_image.raw_filename
                                else None
                            ),
                            "slotImageUrl": self._selected_image_url(context.info.project_id, latest_manifest.slot),
                        }
            for manifest in manifests:
                variants.extend(self._map_manifest_variants(context, manifest, slot_selected_hash))
            variants.sort(key=lambda item: item["capturedAt"], reverse=True)
            self._write_json(
                {
                    "projectId": context.info.project_id,
                    "projectName": context.info.project_name,
                    "slot": slot,
                    "sessions": summaries,
                    "variants": variants,
                    "currentSelection": current_selection,
                }
            )

        def _handle_api_slot_delete(self, project_id: Optional[str], slot: Optional[str]) -> None:
            if not slot:
                return self._bad_request("Missing slot")
            context = self._get_context(project_id)
            if context is None:
                return self._not_found()
            try:
                result = delete_slot(context.paths, slot)
            except (ValueError, InvalidPathError):
                return self._not_found()
            response = {
                "ok": True,
                "projectId": context.info.project_id,
                "slot": result.slot,
                "removedSessions": result.removed_sessions,
                "removedTargets": result.removed_targets,
            }
            self._write_json(response)

        def _handle_api_slot_sessions(self, project_id: Optional[str], slot: str) -> None:
            context = self._get_context(project_id)
            if context is None:
                return self._not_found()
            try:
                manifests = list_manifests_for_slot(context.paths, slot)
            except (ValueError, InvalidPathError):
                return self._not_found()
            manifests.sort(key=lambda m: m.completed_at, reverse=True)
            summaries = [self._summarize_session(context, manifest) for manifest in manifests]
            variants: List[Dict[str, object]] = []
            slot_selected_hash = None
            current_selection = None
            if manifests:
                latest_manifest = manifests[0]
                if latest_manifest.images:
                    selected_index = latest_manifest.selected_index
                    if 0 <= selected_index < len(latest_manifest.images):
                        selected_image = latest_manifest.images[selected_index]
                        slot_selected_hash = selected_image.sha256
                        current_selection = {
                            "projectId": context.info.project_id,
                            "projectName": context.info.project_name,
                            "slot": latest_manifest.slot,
                            "sessionId": latest_manifest.session_id,
                            "variantIndex": selected_index,
                            "completedAt": format_ts(latest_manifest.completed_at),
                            "processed": {
                                "url": self._variant_media_url(
                                    context.info.project_id,
                                    latest_manifest.slot,
                                    latest_manifest.session_id,
                                    selected_image.filename,
                                ),
                                "filename": selected_image.filename,
                                "width": selected_image.width,
                                "height": selected_image.height,
                                "mediaType": selected_image.media_type,
                            },
                            "raw": (
                                {
                                    "url": self._variant_media_url(
                                        context.info.project_id,
                                        latest_manifest.slot,
                                        latest_manifest.session_id,
                                        selected_image.raw_filename,
                                    ),
                                    "filename": selected_image.raw_filename,
                                }
                                if selected_image.raw_filename
                                else None
                            ),
                            "slotImageUrl": self._selected_image_url(context.info.project_id, latest_manifest.slot),
                        }
            for manifest in manifests:
                variants.extend(self._map_manifest_variants(context, manifest, slot_selected_hash))
            variants.sort(key=lambda item: item["capturedAt"], reverse=True)
            self._write_json(
                {
                    "projectId": context.info.project_id,
                    "projectName": context.info.project_name,
                    "slot": slot,
                    "sessions": summaries,
                    "variants": variants,
                    "currentSelection": current_selection,
                }
            )

        def _handle_api_session_detail(self, project_id: Optional[str], slot: str, session_id: str) -> None:
            context = self._get_context(project_id)
            if context is None:
                return self._not_found()
            ctx, manifest = self._resolve_session(context, slot, session_id)
            if manifest is None or ctx is None:
                return self._not_found()
            detail = manifest.to_dict()
            variants = []
            for index, image in enumerate(manifest.images):
                processed_url = self._variant_media_url(context.info.project_id, manifest.slot, session_id, image.filename)
                raw_url = None
                if image.raw_filename:
                    raw_url = self._variant_media_url(context.info.project_id, manifest.slot, session_id, image.raw_filename)
                variants.append(
                    {
                        "index": index,
                        "selected": index == manifest.selected_index,
                        "processed": {
                            "url": processed_url,
                            "filename": image.filename,
                            "width": image.width,
                            "height": image.height,
                            "mediaType": image.media_type,
                        },
                        "raw": {
                            "url": raw_url,
                            "filename": image.raw_filename,
                        }
                        if raw_url
                        else None,
                        "sha256": image.sha256,
                        "original": {
                            "width": image.original_width,
                            "height": image.original_height,
                        },
                        "cropFraction": image.crop_fraction,
                    }
                )
            detail["variants"] = variants
            detail["projectId"] = context.info.project_id
            detail["projectName"] = context.info.project_name
            self._write_json(detail)
        def _find_session_dir(self, session_id: str):
            root = paths.sessions_root
            if not root.exists():
                return None
            for candidate in root.glob(f"*_{session_id}"):
                if candidate.is_dir():
                    return candidate
            return None

        def _serve_app(self, parsed=None) -> None:
            body = _app_html()
            self._write_html(body)

        def _write_html(self, body: str) -> None:
            data = body.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _write_json(self, payload) -> None:
            data = json.dumps(payload).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _get_context(self, project_id: Optional[str]) -> Optional[ProjectContext]:
            try:
                return registry.get_context(project_id)
            except KeyError:
                return None

        def _selected_image_url(self, project_id: str, slot: str) -> str:
            params = {
                "project": project_id,
                "slot": slot,
            }
            encoded = "&".join(f"{quote(str(key))}={quote(str(value))}" for key, value in params.items())
            return f"/selected?{encoded}"

        def _variant_media_url(
            self,
            project_id: str,
            slot: str,
            session_id: str,
            filename: str,
        ) -> str:
            params = {
                "project": project_id,
                "slot": slot,
                "session": session_id,
                "file": filename,
            }
            encoded = "&".join(f"{quote(str(key))}={quote(str(value))}" for key, value in params.items())
            return f"/media?{encoded}"

        def _campaign_media_url(
            self,
            project_id: str,
            campaign_id: str,
            relative_path: str,
        ) -> str:
            params = {
                "project": project_id,
                "campaign": campaign_id,
                "path": relative_path,
            }
            encoded = "&".join(f"{quote(str(key))}={quote(str(value))}" for key, value in params.items())
            return f"/media/campaign?{encoded}"

        def _augment_campaign_variants(
            self,
            variants: Iterable[Dict[str, object]],
            context: ProjectContext,
            workspace: CampaignWorkspace,
        ) -> None:
            for variant in variants:
                thumb_rel = variant.get("thumbnail")
                file_rel = variant.get("file")
                campaign_id = workspace.campaign_id
                if thumb_rel:
                    thumb_path = (workspace.root / thumb_rel).resolve()
                    try:
                        thumb_path.relative_to(workspace.root)
                    except ValueError:
                        variant["thumbnailUrl"] = None
                    else:
                        if thumb_path.exists():
                            variant["thumbnailUrl"] = self._campaign_media_url(
                                context.info.project_id,
                                campaign_id,
                                thumb_rel,
                            )
                        else:
                            variant["thumbnailUrl"] = None
                else:
                    variant["thumbnailUrl"] = None

                if file_rel:
                    file_path = (workspace.root / file_rel).resolve()
                    try:
                        file_path.relative_to(workspace.root)
                    except ValueError:
                        variant["imageUrl"] = None
                    else:
                        if file_path.exists():
                            variant["imageUrl"] = self._campaign_media_url(
                                context.info.project_id,
                                campaign_id,
                                file_rel,
                            )
                        else:
                            variant["imageUrl"] = None
                else:
                    variant["imageUrl"] = None

        def _augment_campaign_detail(
            self,
            detail: Dict[str, object],
            context: ProjectContext,
            workspace: CampaignWorkspace,
        ) -> None:
            matrix = detail.get("matrix", [])
            for cell in matrix:
                variants = cell.get("variants", [])
                self._augment_campaign_variants(variants, context, workspace)
            placements = detail.get("placements", [])
            for placement in placements:
                updated_at = placement.get("updatedAt")
                placement["updatedAt"] = updated_at
            exports = detail.get("exports", [])
            for entry in exports:
                generated_at = entry.get("generatedAt")
                entry["generatedAt"] = generated_at

        def _resolve_session(
            self,
            context: ProjectContext,
            slot: str,
            session_id: str,
        ) -> tuple[Optional[object], Optional[object]]:
            try:
                ctx = context.manager.create_context(slot, session_id)
            except (ValueError, InvalidPathError):
                return None, None
            if not ctx.manifest_path.exists():
                return None, None
            try:
                manifest = context.manager.read_manifest(ctx)
            except FileNotFoundError:
                return None, None
            return ctx, manifest

        def _summarize_session(self, context: ProjectContext, manifest) -> Dict[str, object]:
            summary: Dict[str, object] = {
                "projectId": context.info.project_id,
                "projectName": context.info.project_name,
                "slot": manifest.slot,
                "sessionId": manifest.session_id,
                "completedAt": format_ts(manifest.completed_at),
                "createdAt": format_ts(manifest.created_at),
                "variantCount": len(manifest.images),
                "selectedIndex": manifest.selected_index,
                "selectedPath": manifest.selected_path,
                "warnings": list(manifest.warnings),
                "provider": manifest.effective.provider,
                "model": manifest.effective.model,
                "size": manifest.effective.size or manifest.effective.aspect_ratio,
                "prompt": manifest.effective.prompt,
                "requestText": manifest.request.request_text,
            }
            return summary

        def _map_manifest_variants(
            self,
            context: ProjectContext,
            manifest,
            slot_selected_hash: Optional[str],
        ) -> List[Dict[str, object]]:
            results: List[Dict[str, object]] = []
            session_selected_hash: Optional[str] = None
            if 0 <= manifest.selected_index < len(manifest.images):
                session_selected_hash = manifest.images[manifest.selected_index].sha256
            for index, image in enumerate(manifest.images):
                processed = {
                    "url": self._variant_media_url(
                        context.info.project_id,
                        manifest.slot,
                        manifest.session_id,
                        image.filename,
                    ),
                    "filename": image.filename,
                    "width": image.width,
                    "height": image.height,
                    "mediaType": image.media_type,
                }
                raw = None
                if image.raw_filename:
                    raw = {
                        "url": self._variant_media_url(
                            context.info.project_id,
                            manifest.slot,
                            manifest.session_id,
                            image.raw_filename,
                        ),
                        "filename": image.raw_filename,
                    }
                results.append(
                    {
                        "projectId": context.info.project_id,
                        "projectName": context.info.project_name,
                        "slot": manifest.slot,
                        "sessionId": manifest.session_id,
                        "variantIndex": index,
                        "processed": processed,
                        "raw": raw,
                        "sessionWarnings": list(manifest.warnings),
                        "sessionProvider": manifest.effective.provider,
                        "sessionModel": manifest.effective.model,
                        "sessionSize": manifest.effective.size or manifest.effective.aspect_ratio,
                        "sessionPrompt": manifest.effective.prompt,
                        "sessionRequest": manifest.request.request_text,
                        "sessionCompletedAt": format_ts(manifest.completed_at),
                        "sessionCreatedAt": format_ts(manifest.created_at),
                        "capturedAt": format_ts(manifest.completed_at),
                        "isSessionSelected": session_selected_hash is not None
                        and image.sha256 == session_selected_hash,
                        "isSlotSelected": slot_selected_hash is not None
                        and image.sha256 == slot_selected_hash,
                        "sha256": image.sha256,
                        "cropFraction": image.crop_fraction,
                        "original": {
                            "width": image.original_width,
                            "height": image.original_height,
                        },
                    }
                )
            return results

        def _not_found(self) -> None:
            self.send_response(404)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"Not Found")

        def _bad_request(self, message: str) -> None:
            data = message.encode("utf-8")
            self.send_response(400)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, format: str, *args) -> None:  # noqa: A003 - match BaseHTTPRequestHandler signature
            return  # Silence default logging to keep CLI output clean

    return Handler
def _app_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>ImageMCP Gallery</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {
      color-scheme: dark;
      --bg: #0b0b0f;
      --bg-surface: #15151a;
      --bg-panel: #1f1f28;
      --accent: #38bdf8;
      --accent-soft: rgba(56, 189, 248, 0.16);
      --accent-strong: rgba(56, 189, 248, 0.32);
      --text: #f5f5f5;
      --text-soft: #cbd5f5;
      --border: rgba(148, 163, 184, 0.18);
      --warning: #f97316;
      --warning-soft: rgba(249, 115, 22, 0.2);
      font-family: "Inter", "SF Pro Text", "Segoe UI", system-ui, sans-serif;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      background: linear-gradient(160deg, #0b0b0f 0%, #11111a 40%, #060608 100%);
      color: var(--text);
    }

    a { color: var(--accent); text-decoration: none; }

    #app { min-height: 100vh; display: flex; flex-direction: column; }

    .top-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 1rem 1.5rem;
      background: rgba(12, 12, 20, 0.75);
      backdrop-filter: blur(14px);
      border-bottom: 1px solid var(--border);
      position: sticky;
      top: 0;
      z-index: 20;
    }

    .brand-group {
      display: flex;
      align-items: center;
      gap: 1.25rem;
    }

    .brand {
      font-weight: 600;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      font-size: 0.9rem;
      color: var(--text-soft);
    }

    .view-tabs {
      display: inline-flex;
      align-items: center;
      gap: 0.45rem;
      padding: 0.2rem;
      border-radius: 999px;
      background: rgba(148, 163, 184, 0.12);
      border: 1px solid rgba(148, 163, 184, 0.18);
    }

    .view-tabs .ghost-button {
      padding: 0.3rem 0.75rem;
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .view-tabs .ghost-button[data-active="true"] {
      background: var(--accent-soft);
      border-color: var(--accent);
      color: var(--accent);
      box-shadow: 0 10px 24px rgba(56, 189, 248, 0.22);
    }

    .project-switcher {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.35rem 0.55rem;
      border-radius: 999px;
      background: rgba(148, 163, 184, 0.12);
      border: 1px solid rgba(148, 163, 184, 0.18);
      font-size: 0.8rem;
    }

    .project-switcher label {
      font-weight: 600;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: var(--text-soft);
    }

    .project-switcher select {
      background: transparent;
      border: none;
      color: var(--text);
      font-size: 0.85rem;
      font-weight: 600;
      outline: none;
      appearance: none;
      padding-right: 1.4rem;
      position: relative;
      cursor: pointer;
    }

    .project-switcher select option {
      color: #0f172a;
    }

    .view-actions,
    .top-actions {
      display: flex;
      gap: 0.75rem;
      align-items: center;
    }

    main {
      flex: 1;
      padding: 1.5rem;
      max-width: 1280px;
      width: 100%;
      margin: 0 auto;
    }

    .view {
      display: none;
      flex-direction: column;
      gap: 1rem;
    }

    .view.active { display: flex; }

    .view-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
    }

    .view-header h1 {
      font-size: 1.6rem;
      margin: 0;
    }

    .view-subtitle {
      display: inline-block;
      margin-top: 0.35rem;
      font-size: 0.85rem;
      color: var(--text-soft);
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }

    .slot-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
      gap: 1.25rem;
    }

    .campaign-table-wrap {
      background: var(--bg-panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      overflow: hidden;
    }

    .campaign-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.85rem;
    }

    .campaign-table thead {
      background: rgba(12, 12, 20, 0.65);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-size: 0.72rem;
    }

    .campaign-table th,
    .campaign-table td {
      padding: 0.65rem 1rem;
      border-bottom: 1px solid rgba(148, 163, 184, 0.12);
      text-align: left;
    }

    .campaign-table tbody tr {
      cursor: pointer;
      transition: background 0.15s ease;
    }

    .campaign-table tbody tr:hover {
      background: rgba(56, 189, 248, 0.08);
    }

    .campaign-table tbody tr[data-active="true"] {
      background: rgba(56, 189, 248, 0.14);
    }

    .campaign-layout {
      display: flex;
      gap: 1.5rem;
      align-items: flex-start;
    }

    .campaign-sidebar {
      width: 280px;
      flex-shrink: 0;
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .campaign-summary {
      background: rgba(12, 12, 20, 0.6);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1rem;
      font-size: 0.82rem;
      display: flex;
      flex-direction: column;
      gap: 0.55rem;
    }

    .campaign-summary strong {
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--text-soft);
    }

    .campaign-chip {
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      padding: 0.2rem 0.55rem;
      border-radius: 999px;
      background: rgba(148, 163, 184, 0.12);
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .campaign-route-list {
      display: flex;
      flex-direction: column;
      gap: 0.4rem;
    }

    .campaign-route-card {
      border: 1px solid rgba(148, 163, 184, 0.18);
      border-radius: 10px;
      padding: 0.6rem 0.75rem;
      background: rgba(12, 12, 20, 0.48);
      cursor: pointer;
      transition: border 0.18s ease, background 0.18s ease;
    }

    .campaign-route-card:hover {
      border-color: var(--accent);
    }

    .campaign-route-card[data-active="true"] {
      border-color: var(--accent);
      background: rgba(56, 189, 248, 0.16);
      box-shadow: 0 12px 28px rgba(14, 165, 233, 0.24);
    }

    .campaign-grid-panel {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .campaign-matrix {
      display: grid;
      gap: 1rem;
    }

    .campaign-matrix-cell {
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 0.85rem;
      background: rgba(17, 24, 39, 0.55);
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }

    .campaign-matrix-header {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      gap: 0.75rem;
    }

    .campaign-variant-strip {
      display: flex;
      gap: 0.75rem;
      flex-wrap: wrap;
    }

    .campaign-variant-thumb {
      width: 120px;
      aspect-ratio: 1 / 1;
      border-radius: 10px;
      overflow: hidden;
      border: 1px solid rgba(148, 163, 184, 0.16);
      cursor: pointer;
      position: relative;
      transition: transform 0.18s ease, border 0.18s ease;
    }

    .campaign-variant-thumb img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    .campaign-variant-thumb:hover {
      transform: translateY(-2px);
      border-color: var(--accent);
    }

    .campaign-variant-thumb[data-state="approved"]::after {
      content: 'APP';
      position: absolute;
      top: 0.5rem;
      left: 0.5rem;
      background: rgba(34, 197, 94, 0.24);
      color: #4ade80;
      padding: 0.12rem 0.5rem;
      border-radius: 999px;
      font-size: 0.65rem;
      letter-spacing: 0.08em;
    }

    .campaign-variant-thumb[data-state="revise"]::after {
      content: 'REV';
      background: rgba(239, 68, 68, 0.24);
      color: #f87171;
    }

    .campaign-variant-thumb[data-state="pending"]::after {
      content: 'PND';
      background: rgba(250, 204, 21, 0.24);
      color: #facc15;
    }

    .campaign-list-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      color: var(--text-soft);
    }

    .campaign-export-list,
    .campaign-log-list {
      display: flex;
      flex-direction: column;
      gap: 0.45rem;
      font-size: 0.78rem;
    }

    .campaign-export-item,
    .campaign-log-item {
      padding: 0.45rem 0.6rem;
      border-radius: 8px;
      background: rgba(148, 163, 184, 0.08);
      border: 1px solid rgba(148, 163, 184, 0.12);
    }

    .campaign-overlay-body {
      display: flex;
      gap: 1rem;
      align-items: flex-start;
    }

    .campaign-overlay-image {
      width: 240px;
      border-radius: 12px;
      border: 1px solid var(--border);
      object-fit: contain;
      background: rgba(15, 23, 42, 0.8);
    }

    .campaign-overlay-meta {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }

    .campaign-overlay-meta select,
    .campaign-overlay-meta textarea {
      width: 100%;
      border-radius: 8px;
      border: 1px solid rgba(148, 163, 184, 0.24);
      background: rgba(12, 12, 20, 0.6);
      color: var(--text);
      padding: 0.45rem 0.6rem;
      font-family: inherit;
      font-size: 0.85rem;
      resize: vertical;
    }

    .campaign-overlay-meta textarea {
      min-height: 90px;
    }

    .campaign-overlay-actions {
      display: flex;
      gap: 0.6rem;
      justify-content: flex-end;
    }

    .slot-card {
      background: var(--bg-panel);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 1rem;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
      cursor: pointer;
      transition: transform 0.2s ease, border 0.2s ease, box-shadow 0.2s ease;
      position: relative;
    }

    .slot-card:hover {
      transform: translateY(-3px);
      border-color: var(--accent);
      box-shadow: 0 16px 36px rgba(15, 118, 209, 0.18);
    }

    .slot-card[data-active="true"] {
      border-color: var(--accent);
      box-shadow: 0 12px 28px rgba(14, 165, 233, 0.22);
    }

    .slot-card.has-warning {
      border-color: var(--warning-soft);
      box-shadow: 0 0 0 1px var(--warning-soft);
    }

    .thumb {
      width: 100%;
      aspect-ratio: 4 / 3;
      border-radius: 10px;
      overflow: hidden;
      background: linear-gradient(135deg, rgba(148, 163, 184, 0.08), rgba(30, 41, 59, 0.16));
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
    }

    .thumb img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    .thumb-placeholder {
      font-size: 0.8rem;
      color: var(--text-soft);
      text-transform: uppercase;
      letter-spacing: 0.1em;
    }

    .slot-meta {
      display: flex;
      flex-direction: column;
      gap: 0.4rem;
    }

    .slot-meta h2 {
      margin: 0;
      font-size: 1rem;
      font-weight: 600;
      color: var(--text);
    }

    .slot-meta span {
      font-size: 0.85rem;
      color: var(--text-soft);
    }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: 0.3rem;
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      padding: 0.15rem 0.45rem;
      border-radius: 999px;
      background: var(--accent-soft);
      color: var(--accent);
      font-weight: 600;
    }

    .badge-warning {
      background: var(--warning-soft);
      color: var(--warning);
    }

    .badge-info {
      background: rgba(59, 130, 246, 0.25);
      color: #93c5fd;
    }

    .ghost-button,
    .primary-button,
    .danger-button {
      border-radius: 8px;
      border: 1px solid transparent;
      padding: 0.45rem 0.9rem;
      font-size: 0.85rem;
      font-weight: 600;
      cursor: pointer;
      background: none;
      color: var(--text);
      transition: all 0.18s ease;
    }

    .ghost-button {
      border-color: rgba(148, 163, 184, 0.2);
      background: rgba(148, 163, 184, 0.08);
    }

    .ghost-button:hover {
      border-color: var(--accent);
      color: var(--accent);
    }

    .ghost-button[data-active="true"] {
      border-color: var(--accent);
      background: var(--accent-soft);
      color: var(--accent);
    }

    .primary-button {
      background: var(--accent);
      color: #020617;
      border-color: rgba(14, 165, 233, 0.4);
      box-shadow: 0 10px 30px rgba(14, 165, 233, 0.3);
    }

    .primary-button:hover {
      box-shadow: 0 18px 36px rgba(14, 165, 233, 0.35);
      transform: translateY(-1px);
    }

    .primary-button[disabled],
    .ghost-button[disabled],
    .danger-button[disabled] {
      opacity: 0.5;
      cursor: not-allowed;
      box-shadow: none;
    }

    .danger-button {
      background: rgba(239, 68, 68, 0.18);
      border-color: rgba(239, 68, 68, 0.42);
      color: #fca5a5;
    }

    .danger-button:hover {
      background: rgba(239, 68, 68, 0.28);
      border-color: rgba(248, 113, 113, 0.6);
      color: #fecaca;
    }

    .empty-state {
      padding: 2.5rem;
      border: 1px dashed rgba(148, 163, 184, 0.24);
      border-radius: 12px;
      text-align: center;
      color: var(--text-soft);
      margin-top: 1rem;
    }

    .slot-layout {
      display: grid;
      grid-template-columns: minmax(240px, 280px) 1fr;
      gap: 1.5rem;
    }

    .session-panel {
      background: rgba(15, 15, 25, 0.55);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 1rem;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
      max-height: calc(100vh - 200px);
      overflow-y: auto;
    }

    .session-panel h2 {
      margin: 0;
      font-size: 1rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--text-soft);
    }

    .session-list {
      display: flex;
      flex-direction: column;
      gap: 0.6rem;
    }

    .session-item {
      border-radius: 10px;
      padding: 0.6rem 0.75rem;
      border: 1px solid transparent;
      background: rgba(148, 163, 184, 0.05);
      text-align: left;
      color: inherit;
      cursor: pointer;
      transition: all 0.18s ease;
    }

    .session-item strong {
      display: block;
      font-size: 0.85rem;
      color: var(--text);
    }

    .session-item span {
      display: block;
      font-size: 0.75rem;
      color: var(--text-soft);
    }

    .session-item:hover {
      border-color: var(--accent);
      background: var(--accent-soft);
    }

    .session-item.active {
      border-color: var(--accent);
      background: rgba(2, 132, 199, 0.28);
      box-shadow: 0 10px 24px rgba(14, 165, 233, 0.22);
    }

    .session-detail {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .session-summary {
      background: rgba(12, 12, 20, 0.6);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 1rem 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }

    .summary-row {
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
      align-items: baseline;
      justify-content: space-between;
    }

    .summary-row h2 {
      margin: 0;
      font-size: 1.2rem;
    }

    .prompt-block {
      background: rgba(148, 163, 184, 0.08);
      border-radius: 10px;
      padding: 0.75rem;
      font-size: 0.9rem;
      line-height: 1.5;
      color: var(--text-soft);
      white-space: pre-wrap;
    }

    .warnings {
      border-radius: 12px;
      border: 1px solid var(--warning-soft);
      background: rgba(249, 115, 22, 0.08);
      padding: 0.85rem 1rem;
      color: var(--warning);
    }

    .warnings ul {
      margin: 0.5rem 0 0;
      padding-left: 1.1rem;
      color: var(--text);
    }

    .variant-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 1.25rem;
    }

    .variant-card {
      position: relative;
      border-radius: 14px;
      border: 1px solid var(--border);
      background: rgba(17, 24, 39, 0.55);
      overflow: hidden;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
      padding: 0.75rem;
    }

    .variant-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.5rem;
    }

    .variant-badges {
      display: flex;
      flex-wrap: wrap;
      gap: 0.35rem;
    }

    .variant-session {
      font-size: 0.78rem;
      color: var(--text-soft);
      white-space: nowrap;
    }

    .variant-card.is-selected {
      border-color: var(--accent);
      box-shadow: 0 16px 36px rgba(14, 165, 233, 0.28);
    }

    .variant-thumb {
      position: relative;
      border-radius: 10px;
      overflow: hidden;
      background: rgba(148, 163, 184, 0.08);
      aspect-ratio: 4 / 3;
    }

    .variant-thumb img {
      width: 100%;
      height: 100%;
      object-fit: contain;
      background: #0d1117;
    }

    .badge-selected {
      position: absolute;
      top: 0.75rem;
      left: 0.75rem;
      background: rgba(34, 197, 94, 0.24);
      color: #4ade80;
      padding: 0.25rem 0.6rem;
      border-radius: 999px;
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-weight: 600;
      backdrop-filter: blur(8px);
    }

    .variant-info {
      display: flex;
      flex-direction: column;
      gap: 0.4rem;
      font-size: 0.78rem;
      color: var(--text-soft);
    }

    .variant-info strong {
      font-size: 0.85rem;
      color: var(--text);
    }

    .variant-stats {
      display: flex;
      flex-wrap: wrap;
      gap: 0.55rem;
      font-size: 0.75rem;
      color: var(--text-soft);
    }

    .variant-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
    }

    .overlay {
      position: fixed;
      inset: 0;
      background: rgba(8, 8, 12, 0.85);
      backdrop-filter: blur(14px);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 50;
    }

    .overlay.hidden { display: none; }

    .overlay-card {
      width: min(90vw, 640px);
      max-height: 80vh;
      overflow-y: auto;
      background: rgba(12, 12, 20, 0.95);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      gap: 1rem;
      box-shadow: 0 24px 64px rgba(2, 132, 199, 0.35);
    }

    .overlay-card h2 {
      margin: 0;
    }

    .overlay-grid {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
      gap: 0.75rem 1rem;
      font-size: 0.85rem;
    }

    .overlay-grid dt {
      font-weight: 600;
      color: var(--text-soft);
    }

    .overlay-grid dd {
      margin: 0;
      color: var(--text);
      word-break: break-word;
    }

    pre.metadata-json {
      background: rgba(15, 23, 42, 0.7);
      padding: 0.9rem;
      border-radius: 10px;
      overflow-x: auto;
      border: 1px solid rgba(148, 163, 184, 0.16);
      font-size: 0.75rem;
      color: var(--text-soft);
    }

    .toast {
      position: fixed;
      bottom: 1.5rem;
      left: 50%;
      transform: translateX(-50%);
      padding: 0.75rem 1.2rem;
      border-radius: 999px;
      background: rgba(15, 23, 42, 0.82);
      border: 1px solid rgba(56, 189, 248, 0.35);
      color: var(--text);
      font-size: 0.85rem;
      box-shadow: 0 10px 30px rgba(14, 165, 233, 0.25);
      z-index: 60;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.3s ease;
    }

    .toast.visible { opacity: 1; }

    .hidden { display: none !important; }

    @media (max-width: 720px) {
      .top-bar {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.75rem;
      }
      .top-actions {
        width: 100%;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 0.6rem;
      }
      .project-switcher {
        width: 100%;
        justify-content: space-between;
      }
    }

    @media (max-width: 960px) {
      main { padding: 1rem; }
      .slot-layout {
        grid-template-columns: 1fr;
      }
      .session-panel { max-height: none; }
      .campaign-layout {
        flex-direction: column;
      }
      .campaign-sidebar {
        width: 100%;
      }
    }
  </style>
</head>
<body>
  <div id="app">
    <header class="top-bar">
      <div class="brand-group">
        <div class="brand">ImageMCP Gallery</div>
        <div class="view-tabs">
          <button id="tab-slots" class="ghost-button" type="button" data-active="true">Slots</button>
          <button id="tab-campaigns" class="ghost-button" type="button" data-active="false">Campaigns</button>
        </div>
      </div>
      <div class="top-actions">
        <div class="project-switcher">
          <label for="project-select">Project</label>
          <select id="project-select"></select>
        </div>
        <button id="refresh-slots" class="ghost-button" type="button">Refresh</button>
        <a href="https://github.com/severindeutschmann/ImageMCP" target="_blank" rel="noreferrer" class="ghost-button" style="display:inline-flex;align-items:center;">
          Docs ↗
        </a>
      </div>
    </header>
    <main>
      <section id="slots-view" class="view active">
        <div class="view-header">
          <div>
            <h1>Image Slots</h1>
            <span id="project-label" class="view-subtitle"></span>
          </div>
          <div class="view-actions">
            <button id="filter-warnings" class="ghost-button" data-active="false" type="button">Warnings only</button>
          </div>
        </div>
        <div id="slot-grid" class="slot-grid"></div>
        <div id="slots-empty" class="empty-state hidden">
          No image slots yet. Run <code>imgen gen --slot &lt;name&gt; ...</code> to create the first session.
        </div>
      </section>

      <section id="slot-detail" class="view hidden">
        <div class="view-header">
          <div style="display:flex;gap:0.75rem;align-items:center;">
            <button id="back-to-slots" class="ghost-button" type="button">↩ All slots</button>
            <div>
              <h1 id="slot-title">Slot</h1>
              <span id="slot-subtitle" style="font-size:0.85rem;color:var(--text-soft);"></span>
            </div>
          </div>
          <div class="view-actions">
            <button id="open-selected" class="ghost-button" type="button">Open selected</button>
            <button id="refresh-slot" class="ghost-button" type="button">Refresh</button>
            <button id="delete-slot" class="danger-button" type="button">Delete slot</button>
          </div>
        </div>
        <div class="slot-layout">
          <aside class="session-panel">
            <h2>Sessions</h2>
            <div id="session-list" class="session-list"></div>
            <div id="sessions-empty" class="empty-state hidden">No sessions yet for this slot.</div>
          </aside>
          <section class="session-detail">
            <div id="session-summary" class="session-summary hidden"></div>
            <div id="session-warnings" class="warnings hidden"></div>
            <div id="variant-grid" class="variant-grid"></div>
            <div id="variant-empty" class="empty-state hidden">No variants yet. Generate images to populate this gallery.</div>
          </section>
        </div>
      </section>

      <section id="campaigns-view" class="view hidden">
        <div class="view-header">
          <div>
            <h1>Campaigns</h1>
            <span id="campaigns-subtitle" class="view-subtitle"></span>
          </div>
          <div class="view-actions">
            <input id="campaign-search" type="search" placeholder="Search campaigns" style="padding:0.4rem 0.6rem;border-radius:8px;border:1px solid rgba(148,163,184,0.2);background:rgba(12,12,20,0.5);color:var(--text);" />
            <select id="campaign-status-filter" style="padding:0.35rem 0.75rem;border-radius:8px;border:1px solid rgba(148,163,184,0.2);background:rgba(12,12,20,0.5);color:var(--text);">
              <option value="all">All statuses</option>
              <option value="active">Active</option>
              <option value="draft">Draft</option>
              <option value="on_hold">On hold</option>
              <option value="completed">Completed</option>
            </select>
            <button id="refresh-campaigns" class="ghost-button" type="button">Refresh</button>
          </div>
        </div>
        <div class="campaign-table-wrap">
          <table class="campaign-table">
            <thead>
              <tr>
                <th>Campaign</th>
                <th>Status</th>
                <th>Routes</th>
                <th>Placements</th>
                <th>Approved</th>
                <th>Variants</th>
                <th>Updated</th>
              </tr>
            </thead>
            <tbody id="campaign-table-body"></tbody>
          </table>
          <div id="campaigns-empty" class="empty-state hidden">No campaigns yet. Run <code>imgen campaign init ...</code> to scaffold your first brief.</div>
        </div>
      </section>

      <section id="campaign-detail" class="view hidden">
        <div class="view-header">
          <div style="display:flex;gap:0.75rem;align-items:center;">
            <button id="back-to-campaigns" class="ghost-button" type="button">↩ All campaigns</button>
            <div>
              <h1 id="campaign-title">Campaign</h1>
              <span id="campaign-subtitle" class="view-subtitle"></span>
            </div>
          </div>
          <div class="view-actions">
            <button id="refresh-campaign-detail" class="ghost-button" type="button">Refresh</button>
          </div>
        </div>
        <div class="campaign-layout">
          <aside class="campaign-sidebar">
            <div id="campaign-summary" class="campaign-summary"></div>
            <div class="campaign-filters" style="display:flex;flex-direction:column;gap:0.5rem;">
              <label style="display:flex;flex-direction:column;gap:0.2rem;">
                <span class="view-subtitle" style="margin:0;">Filter by route</span>
                <select id="campaign-filter-route"></select>
              </label>
              <label style="display:flex;flex-direction:column;gap:0.2rem;">
                <span class="view-subtitle" style="margin:0;">Filter by placement</span>
                <select id="campaign-filter-placement"></select>
              </label>
              <label style="display:flex;flex-direction:column;gap:0.2rem;">
                <span class="view-subtitle" style="margin:0;">Review state</span>
                <select id="campaign-filter-state">
                  <option value="all">All states</option>
                  <option value="approved">Approved</option>
                  <option value="pending">Pending</option>
                  <option value="revise">Revise</option>
                </select>
              </label>
            </div>
            <div>
              <h2 class="view-subtitle" style="margin-bottom:0.4rem;">Routes</h2>
              <div id="campaign-route-list" class="campaign-route-list"></div>
            </div>
            <div>
              <h2 class="view-subtitle" style="margin-bottom:0.4rem;">Exports</h2>
              <div id="campaign-exports" class="campaign-export-list"></div>
            </div>
            <div>
              <h2 class="view-subtitle" style="margin-bottom:0.4rem;">Batch logs</h2>
              <div id="campaign-logs" class="campaign-log-list"></div>
            </div>
          </aside>
          <section class="campaign-grid-panel">
            <div id="campaign-grid" class="campaign-matrix"></div>
            <div id="campaign-empty" class="empty-state hidden">No variants generated yet.</div>
          </section>
        </div>
      </section>
    </main>
  </div>

  <div id="metadata-overlay" class="overlay hidden">
    <div class="overlay-card">
      <div style="display:flex;justify-content:space-between;align-items:center;gap:1rem;">
        <h2 id="metadata-title">Variant details</h2>
        <button id="metadata-close" class="ghost-button" type="button">Close</button>
      </div>
      <dl id="metadata-grid" class="overlay-grid"></dl>
      <pre id="metadata-json" class="metadata-json"></pre>
    </div>
  </div>

  <div id="campaign-overlay" class="overlay hidden">
    <div class="overlay-card">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:1rem;">
        <div>
          <h2 id="campaign-overlay-title">Variant details</h2>
          <div id="campaign-overlay-subtitle" style="font-size:0.8rem;color:var(--text-soft);"></div>
        </div>
        <button id="campaign-overlay-close" class="ghost-button" type="button">Close</button>
      </div>
      <div class="campaign-overlay-body">
        <img id="campaign-overlay-image" class="campaign-overlay-image" alt="Variant preview" />
        <div class="campaign-overlay-meta">
          <div id="campaign-overlay-info" class="campaign-overlay-info" style="display:flex;flex-direction:column;gap:0.35rem;font-size:0.82rem;color:var(--text-soft);"></div>
          <label>
            Review state
            <select id="campaign-overlay-state">
              <option value="approved">Approved</option>
              <option value="pending">Pending</option>
              <option value="revise">Revise</option>
            </select>
          </label>
          <label>
            Notes
            <textarea id="campaign-overlay-notes" placeholder="Add review notes"></textarea>
          </label>
          <div class="campaign-overlay-actions">
            <button id="campaign-overlay-reset" class="ghost-button" type="button">Reset</button>
            <button id="campaign-overlay-apply" class="primary-button" type="button">Apply</button>
          </div>
        </div>
      </div>
      <pre id="campaign-overlay-json" class="metadata-json"></pre>
    </div>
  </div>

  <div id="toast" class="toast hidden"></div>

  <script>
    (function() {
      const state = {
        projects: [],
        projectId: null,
        projectName: null,
        slots: [],
        slot: null,
        sessions: [],
        variants: [],
        sessionFilter: null,
        currentSelection: null,
        filterWarnings: false,
        pendingSlot: null,
        viewMode: 'slots',
        campaigns: [],
        campaignStatusFilter: 'all',
        campaignSearch: '',
        campaignFilters: { route: 'all', placement: 'all', state: 'all' },
        selectedCampaignId: null,
        campaignDetail: null,
        pendingCampaign: null,
        activeCampaignVariant: null,
      };

      const urlParams = new URLSearchParams(window.location.search);
      const initialProjectParam = urlParams.get('project');
      const initialSlotParam = urlParams.get('slot');
      state.pendingSlot = initialSlotParam;
      const initialCampaignParam = urlParams.get('campaign');
      state.pendingCampaign = initialCampaignParam;
      if (state.pendingCampaign) {
        state.viewMode = 'campaigns';
      }

      const slotGrid = document.getElementById('slot-grid');
      const slotsEmpty = document.getElementById('slots-empty');
      const slotsEmptyDefault = slotsEmpty ? slotsEmpty.innerHTML : '';
      const slotsView = document.getElementById('slots-view');
      const slotDetailView = document.getElementById('slot-detail');
      const slotTitle = document.getElementById('slot-title');
      const slotSubtitle = document.getElementById('slot-subtitle');
      const sessionList = document.getElementById('session-list');
      const sessionsEmpty = document.getElementById('sessions-empty');
      const sessionSummary = document.getElementById('session-summary');
      const sessionWarnings = document.getElementById('session-warnings');
      const variantGrid = document.getElementById('variant-grid');
      const variantEmpty = document.getElementById('variant-empty');
      const toast = document.getElementById('toast');
      const metadataOverlay = document.getElementById('metadata-overlay');
      const metadataGrid = document.getElementById('metadata-grid');
      const metadataJson = document.getElementById('metadata-json');
      const metadataTitle = document.getElementById('metadata-title');

      const tabSlots = document.getElementById('tab-slots');
      const tabCampaigns = document.getElementById('tab-campaigns');
      const campaignsView = document.getElementById('campaigns-view');
      const campaignDetailView = document.getElementById('campaign-detail');
      const campaignsSubtitle = document.getElementById('campaigns-subtitle');
      const campaignTableBody = document.getElementById('campaign-table-body');
      const campaignsEmpty = document.getElementById('campaigns-empty');
      const campaignSearchInput = document.getElementById('campaign-search');
      const campaignStatusFilter = document.getElementById('campaign-status-filter');
      const refreshCampaignsBtn = document.getElementById('refresh-campaigns');

      const campaignTitle = document.getElementById('campaign-title');
      const campaignSubtitle = document.getElementById('campaign-subtitle');
      const campaignSummary = document.getElementById('campaign-summary');
      const campaignRouteList = document.getElementById('campaign-route-list');
      const campaignExports = document.getElementById('campaign-exports');
      const campaignLogs = document.getElementById('campaign-logs');
      const campaignGrid = document.getElementById('campaign-grid');
      const campaignEmpty = document.getElementById('campaign-empty');
      const campaignFilterRoute = document.getElementById('campaign-filter-route');
      const campaignFilterPlacement = document.getElementById('campaign-filter-placement');
      const campaignFilterState = document.getElementById('campaign-filter-state');
      const backToCampaignsBtn = document.getElementById('back-to-campaigns');
      const refreshCampaignDetailBtn = document.getElementById('refresh-campaign-detail');

      const campaignOverlay = document.getElementById('campaign-overlay');
      const campaignOverlayClose = document.getElementById('campaign-overlay-close');
      const campaignOverlayApply = document.getElementById('campaign-overlay-apply');
      const campaignOverlayReset = document.getElementById('campaign-overlay-reset');
      const campaignOverlayState = document.getElementById('campaign-overlay-state');
      const campaignOverlayNotes = document.getElementById('campaign-overlay-notes');
      const campaignOverlayImage = document.getElementById('campaign-overlay-image');
      const campaignOverlayInfo = document.getElementById('campaign-overlay-info');
      const campaignOverlaySubtitle = document.getElementById('campaign-overlay-subtitle');
      const campaignOverlayJson = document.getElementById('campaign-overlay-json');

      const projectSelect = document.getElementById('project-select');
      const projectLabel = document.getElementById('project-label');

      if (projectLabel) {
        projectLabel.textContent = 'Loading projects…';
      }

      const refreshSlotsBtn = document.getElementById('refresh-slots');
      const refreshSlotBtn = document.getElementById('refresh-slot');
      const filterWarningsBtn = document.getElementById('filter-warnings');
      const backToSlotsBtn = document.getElementById('back-to-slots');
      const openSelectedBtn = document.getElementById('open-selected');
      const metadataCloseBtn = document.getElementById('metadata-close');
      const deleteSlotBtn = document.getElementById('delete-slot');

      if (deleteSlotBtn) {
        deleteSlotBtn.disabled = true;
      }

      function showToast(message, kind = 'info') {
        toast.textContent = message;
        toast.dataset.kind = kind;
        toast.classList.remove('hidden');
        toast.classList.add('visible');
        clearTimeout(showToast._timer);
        showToast._timer = setTimeout(() => {
          toast.classList.remove('visible');
        }, 2600);
      }

      function escapeHtml(text) {
        if (text === null || text === undefined) return '';
        return String(text)
          .replace(/&/g, '&amp;')
          .replace(/</g, '&lt;')
          .replace(/>/g, '&gt;')
          .replace(/"/g, '&quot;')
          .replace(/'/g, '&#39;');
      }

      function formatTimestamp(ts) {
        if (!ts) return 'n/a';
        try {
          const date = new Date(ts);
          if (Number.isNaN(date.getTime())) return ts;
          return date.toLocaleString();
        } catch (error) {
          return ts;
        }
      }

      function getProjectById(projectId) {
        if (!projectId) return null;
        return state.projects.find((item) => item.projectId === projectId) || null;
      }

      function getProjectName(projectId) {
        const project = getProjectById(projectId);
        if (!project) return null;
        return project.projectName || project.projectId;
      }

      function updateDocumentTitle() {
        if (state.projectName) {
          document.title = `ImageMCP Gallery · ${state.projectName}`;
        } else {
          document.title = 'ImageMCP Gallery';
        }
      }

      function updateProjectSummary() {
        if (!projectLabel) return;
        if (!state.projectId) {
          projectLabel.textContent = 'No project selected';
          return;
        }
        const label = getProjectName(state.projectId) || state.projectId;
        projectLabel.textContent = `Project: ${label}`;
      }

      function renderProjectSelector() {
        if (!projectSelect) return;
        if (!state.projects.length) {
          projectSelect.innerHTML = '<option value="">No projects</option>';
          projectSelect.disabled = true;
          return;
        }
        projectSelect.disabled = false;
        projectSelect.innerHTML = state.projects
          .map((project) => `<option value="${escapeHtml(project.projectId)}">${escapeHtml(project.projectName || project.projectId)}</option>`)
          .join('');
        if (state.projectId) {
          projectSelect.value = state.projectId;
        }
      }

      function updateUrlState() {
        const params = new URLSearchParams();
        if (state.projectId) {
          params.set('project', state.projectId);
        }
        if (state.slot) {
          params.set('slot', state.slot);
        }
        if (state.selectedCampaignId) {
          params.set('campaign', state.selectedCampaignId);
        }
        const next = params.toString();
        const target = next ? `${window.location.pathname}?${next}` : window.location.pathname;
        const current = `${window.location.pathname}${window.location.search}`;
        if (target !== current) {
          window.history.replaceState(null, '', target);
        }
      }

      function updateViewVisibility() {
        if (tabSlots) {
          tabSlots.dataset.active = state.viewMode === 'slots' ? 'true' : 'false';
        }
        if (tabCampaigns) {
          tabCampaigns.dataset.active = state.viewMode === 'campaigns' ? 'true' : 'false';
        }

        if (state.viewMode === 'slots') {
          const showingDetail = Boolean(state.slot);
          if (slotsView) {
            slotsView.classList.toggle('hidden', showingDetail);
            slotsView.classList.toggle('active', !showingDetail);
          }
          if (slotDetailView) {
            slotDetailView.classList.toggle('hidden', !showingDetail);
            slotDetailView.classList.toggle('active', showingDetail);
          }
          if (campaignsView) {
            campaignsView.classList.add('hidden');
            campaignsView.classList.remove('active');
          }
          if (campaignDetailView) {
            campaignDetailView.classList.add('hidden');
            campaignDetailView.classList.remove('active');
          }
        } else {
          const showingCampaignDetail = Boolean(state.selectedCampaignId && state.campaignDetail);
          if (campaignsView) {
            campaignsView.classList.toggle('hidden', showingCampaignDetail);
            campaignsView.classList.toggle('active', !showingCampaignDetail);
          }
          if (campaignDetailView) {
            campaignDetailView.classList.toggle('hidden', !showingCampaignDetail);
            campaignDetailView.classList.toggle('active', showingCampaignDetail);
          }
          if (slotsView) {
            slotsView.classList.add('hidden');
            slotsView.classList.remove('active');
          }
          if (slotDetailView) {
            slotDetailView.classList.add('hidden');
            slotDetailView.classList.remove('active');
          }
        }
      }

      function setViewMode(mode) {
        if (state.viewMode === mode) {
          updateViewVisibility();
          return;
        }
        state.viewMode = mode;
        updateViewVisibility();
        if (mode === 'campaigns' && !state.campaigns.length && state.projectId) {
          loadCampaigns();
        }
        updateUrlState();
      }

      function resetSlotView() {
        state.slot = null;
        state.sessions = [];
        state.variants = [];
        state.sessionFilter = null;
        state.currentSelection = null;
        sessionList.innerHTML = '';
        sessionSummary.classList.add('hidden');
        sessionWarnings.classList.add('hidden');
        sessionWarnings.innerHTML = '';
        variantGrid.innerHTML = '';
        variantEmpty.classList.add('hidden');
        if (openSelectedBtn) {
          openSelectedBtn.dataset.url = '';
        }
        if (deleteSlotBtn) {
          deleteSlotBtn.disabled = true;
        }
        updateViewVisibility();
      }

      function setProject(projectId, { skipReload = false, updateUrl = true, preserveSlot = false } = {}) {
        if (!projectId) {
          return;
        }
        if (state.projectId === projectId) {
          if (!skipReload) {
            loadSlots();
            if (state.viewMode === 'campaigns') {
              loadCampaigns();
            }
          }
          return;
        }
        const project = getProjectById(projectId);
        state.projectId = projectId;
        state.projectName = project ? (project.projectName || project.projectId) : projectId;
        if (projectSelect) {
          projectSelect.value = projectId;
        }
        state.campaigns = [];
        state.campaignDetail = null;
        state.selectedCampaignId = null;
        state.campaignFilters = { route: 'all', placement: 'all', state: 'all' };
        if (campaignTableBody) {
          campaignTableBody.innerHTML = '';
        }
        if (campaignGrid) {
          campaignGrid.innerHTML = '';
        }
        renderCampaignList();
        updateViewVisibility();
        if (!preserveSlot) {
          resetSlotView();
          state.pendingSlot = null;
          state.slots = [];
          renderSlots();
        }
        updateProjectSummary();
        updateDocumentTitle();
        if (updateUrl) {
          updateUrlState();
        }
        if (!skipReload) {
          loadSlots();
          if (state.viewMode === 'campaigns') {
            loadCampaigns();
          }
        }
      }

      async function loadProjects() {
        try {
          const res = await fetch('/api/projects');
          if (!res.ok) throw new Error('Failed to load projects');
          const data = await res.json();
          state.projects = Array.isArray(data.projects) ? data.projects : [];
          const defaultProjectId = data.defaultProjectId || (state.projects[0] && state.projects[0].projectId) || null;
          renderProjectSelector();
          let desiredProject = initialProjectParam;
          if (!desiredProject || !getProjectById(desiredProject)) {
            desiredProject = state.projectId || defaultProjectId;
          }
          if (desiredProject) {
            const project = getProjectById(desiredProject);
            state.projectId = desiredProject;
            state.projectName = project ? (project.projectName || project.projectId) : desiredProject;
            if (projectSelect) {
              projectSelect.value = desiredProject;
            }
          } else {
            state.projectId = null;
            state.projectName = null;
          }
          updateProjectSummary();
          updateDocumentTitle();
          if (state.projectId) {
            await loadSlots({ initial: true });
            if (state.viewMode === 'campaigns') {
              await loadCampaigns();
            }
          } else {
            renderSlots();
          }
          if ((!initialProjectParam || !getProjectById(initialProjectParam)) && state.projectId) {
            updateUrlState();
          }
          if (projectSelect) {
            projectSelect.disabled = !state.projects.length;
          }
        } catch (error) {
          console.error(error);
          showToast('Unable to load projects', 'error');
        }
      }

      async function loadSlots(options = {}) {
        const { initial = false, forceReload = false } = options;
        if (!state.projectId) {
          state.slots = [];
          renderSlots();
          updateProjectSummary();
          return;
        }
        try {
          const params = new URLSearchParams({ project: state.projectId });
          if (forceReload) {
            params.set('_', Date.now().toString());
          }
          const fetchOptions = forceReload ? { cache: 'no-store' } : {};
          const res = await fetch(`/api/slots?${params.toString()}`, fetchOptions);
          if (!res.ok) throw new Error('Failed to load slots');
          const data = await res.json();
          state.slots = data.slots || [];
          if (data.projectId) {
            state.projectId = data.projectId;
          }
          if (data.projectName) {
            state.projectName = data.projectName;
          } else {
            state.projectName = getProjectName(state.projectId) || state.projectName;
          }
          renderProjectSelector();
          updateProjectSummary();
          updateDocumentTitle();
          renderSlots();
          if (state.slot) {
            const summary = state.slots.find((item) => item.slot === state.slot);
            if (summary && !state.currentSelection && summary.selectedImageUrl) {
              state.currentSelection = { slotImageUrl: summary.selectedImageUrl };
            }
            updateSlotHeader();
          }
          if (initial && state.pendingSlot) {
            const desiredSlot = state.pendingSlot;
            state.pendingSlot = null;
            if (desiredSlot) {
              const summary = state.slots.find((item) => item.slot === desiredSlot);
              if (summary) {
                await selectSlot(desiredSlot);
              }
            }
          }
        } catch (error) {
          console.error(error);
          showToast('Unable to load slots', 'error');
        }
      }

      function renderSlots() {
        const items = state.filterWarnings
          ? state.slots.filter((slot) => slot.warningCount > 0)
          : state.slots;
        filterWarningsBtn.dataset.active = state.filterWarnings ? 'true' : 'false';
        filterWarningsBtn.textContent = state.filterWarnings ? 'Showing warnings only' : 'Warnings only';
        if (!items.length) {
          slotGrid.innerHTML = '';
          if (slotsEmpty) {
            if (!state.projectId) {
              slotsEmpty.textContent = 'Select or initialize a project to view its image slots.';
            } else {
              slotsEmpty.innerHTML = slotsEmptyDefault;
            }
            slotsEmpty.classList.remove('hidden');
          }
          return;
        }
        if (slotsEmpty) {
          slotsEmpty.classList.add('hidden');
          slotsEmpty.innerHTML = slotsEmptyDefault;
        }
        slotGrid.innerHTML = items
          .map((slot) => {
            const warningBadge = slot.warningCount
              ? `<span class="badge badge-warning">⚠ ${slot.warningCount} warning${slot.warningCount === 1 ? '' : 's'}</span>`
              : '';
            const image = slot.selectedImageUrl
              ? `<img src="${slot.selectedImageUrl}" alt="${escapeHtml(slot.slot)} preview">`
              : '<div class="thumb-placeholder">No preview</div>';
            const updated = slot.lastUpdated ? formatTimestamp(slot.lastUpdated) : 'never';
            const active = state.slot && state.slot === slot.slot;
            return `
              <article class="slot-card ${slot.warningCount ? 'has-warning' : ''}" data-slot="${escapeHtml(slot.slot)}" data-active="${active ? 'true' : 'false'}">
                <div class="thumb">${image}</div>
                <div class="slot-meta">
                  <h2>${escapeHtml(slot.slot)}</h2>
                  <span>Sessions: ${slot.sessionCount}</span>
                  <span>Updated: ${escapeHtml(updated)}</span>
                  ${warningBadge}
                </div>
              </article>
            `;
          })
          .join('');
      }

      async function selectSlot(slotId) {
        state.viewMode = 'slots';
        state.slot = slotId;
        updateViewVisibility();
        await loadSlotData(slotId);
      }

      async function loadSlotData(slotId, options = {}) {
        if (!state.projectId) return;
        const { forceReload = false, preserveFilter = false } = options;
        const previousFilter = preserveFilter ? state.sessionFilter : null;
        try {
          const params = new URLSearchParams({ project: state.projectId });
          if (forceReload) {
            params.set('_', Date.now().toString());
          }
          const fetchOptions = forceReload ? { cache: 'no-store' } : {};
          const res = await fetch(`/api/slots/${encodeURIComponent(slotId)}/sessions?${params.toString()}`, fetchOptions);
          if (!res.ok) throw new Error('Failed to load slot data');
          const data = await res.json();
          state.slot = data.slot || slotId;
          if (data.projectId) {
            state.projectId = data.projectId;
          }
          if (data.projectName) {
            state.projectName = data.projectName;
          } else {
            state.projectName = getProjectName(state.projectId) || state.projectName;
          }
          state.sessions = Array.isArray(data.sessions) ? data.sessions : [];
          state.variants = Array.isArray(data.variants) ? data.variants : [];
          if (preserveFilter && previousFilter) {
            const hasFilter = state.sessions.some((session) => session.sessionId === previousFilter);
            state.sessionFilter = hasFilter ? previousFilter : null;
          } else {
            state.sessionFilter = null;
          }
          state.currentSelection = data.currentSelection || null;
          updateProjectSummary();
          updateDocumentTitle();
          updateSlotHeader();
          renderSlots();
          renderSessionList();
          renderSessionSummary();
          renderVariantFeed();
          updateViewVisibility();
          updateUrlState();
        } catch (error) {
          console.error(error);
          showToast('Unable to load slot data', 'error');
        }
      }

      async function requestSlotDeletion(slotId) {
        if (!slotId) return;
        if (deleteSlotBtn) {
          deleteSlotBtn.disabled = true;
        }
        try {
          const params = new URLSearchParams();
          if (state.projectId) {
            params.set('project', state.projectId);
          }
          const query = params.toString();
          const endpoint = `/api/slots/${encodeURIComponent(slotId)}${query ? `?${query}` : ''}`;
          const res = await fetch(endpoint, { method: 'DELETE' });
          if (!res.ok) throw new Error('Failed to delete slot');
          await res.json();
          showToast(`Deleted slot "${slotId}"`);
          resetSlotView();
          state.pendingSlot = null;
          updateUrlState();
          await loadSlots({ forceReload: true });
        } catch (error) {
          console.error(error);
          showToast('Unable to delete slot', 'error');
          if (deleteSlotBtn) {
            deleteSlotBtn.disabled = false;
          }
        }
      }

      function updateSlotHeader() {
        slotTitle.textContent = state.slot || 'Slot';
        if (deleteSlotBtn) {
          deleteSlotBtn.disabled = !state.slot;
        }
        const latestSession = state.sessions.length ? state.sessions[0] : null;
        const subtitleParts = [];
        if (state.projectName || state.projectId) {
          subtitleParts.push(`Project ${state.projectName || state.projectId}`);
        }
        if (latestSession) {
          subtitleParts.push(`Updated ${formatTimestamp(latestSession.completedAt)}`);
        } else {
          subtitleParts.push('No sessions yet');
        }
        slotSubtitle.textContent = subtitleParts.join(' • ');
        const slotUrl = (state.currentSelection && state.currentSelection.slotImageUrl)
          || (state.sessions.length && state.projectId
            ? `/selected?project=${encodeURIComponent(state.projectId)}&slot=${encodeURIComponent(state.slot)}`
            : null);
        openSelectedBtn.dataset.url = slotUrl || '';
        openSelectedBtn.disabled = !slotUrl;
      }

      function renderSessionList() {
        if (!state.sessions.length) {
          sessionList.innerHTML = '';
          sessionsEmpty.classList.remove('hidden');
          return;
        }
        sessionsEmpty.classList.add('hidden');
        const activeSession = state.sessionFilter;
        const latest = state.sessions[0];
        const items = [];
        items.push(`
          <button class="session-item ${activeSession ? '' : 'active'}" data-session="__all__" type="button">
            <strong>All sessions</strong>
            <span>${state.sessions.length} total • Last ${escapeHtml(formatTimestamp(latest.completedAt))}</span>
          </button>
        `);
        state.sessions.forEach((session) => {
          const isActive = activeSession === session.sessionId;
          const warningBadge = session.warnings && session.warnings.length
            ? `<span>⚠ ${session.warnings.length} warning${session.warnings.length === 1 ? '' : 's'}</span>`
            : '';
          items.push(`
            <button class="session-item ${isActive ? 'active' : ''}" data-session="${escapeHtml(session.sessionId)}" type="button">
              <strong>${escapeHtml(formatTimestamp(session.completedAt))}</strong>
              <span>#${session.selectedIndex} • ${session.variantCount} variant${session.variantCount === 1 ? '' : 's'}</span>
              ${warningBadge}
            </button>
          `);
        });
        sessionList.innerHTML = items.join('');
      }

      function renderSessionSummary() {
        if (!state.sessions.length) {
          sessionSummary.classList.add('hidden');
          sessionWarnings.classList.add('hidden');
          sessionSummary.innerHTML = '';
          sessionWarnings.innerHTML = '';
          return;
        }
        const summarySession = state.sessionFilter
          ? state.sessions.find((item) => item.sessionId === state.sessionFilter)
          : state.sessions[0];
        if (!summarySession) {
          sessionSummary.classList.add('hidden');
          sessionWarnings.classList.add('hidden');
          return;
        }
        if (!state.sessionFilter) {
          sessionSummary.innerHTML = `
            <div class="summary-row">
              <div>
                <h2>All Sessions</h2>
                <span>${state.sessions.length} total runs</span>
              </div>
              <div style="font-size:0.82rem;color:var(--text-soft);text-align:right;">
                <div>Latest completed ${escapeHtml(formatTimestamp(summarySession.completedAt))}</div>
                <div>Pick a session to inspect prompts &amp; warnings.</div>
              </div>
            </div>
          `;
          sessionSummary.classList.remove('hidden');
          sessionWarnings.classList.add('hidden');
          sessionWarnings.innerHTML = '';
          return;
        }
        const provider = summarySession.provider || 'provider?';
        const model = summarySession.model || 'model?';
        const size = summarySession.size || 'size?';
        const prompt = summarySession.prompt || 'No prompt recorded';
        const requestText = summarySession.requestText || '—';
        sessionSummary.innerHTML = `
          <div class="summary-row">
            <div>
              <h2>Session ${escapeHtml(summarySession.sessionId)}</h2>
              <span>Completed ${escapeHtml(formatTimestamp(summarySession.completedAt))}</span>
            </div>
            <div style="font-size:0.82rem;color:var(--text-soft);text-align:right;">
              <div>${escapeHtml(provider)} • ${escapeHtml(model)}</div>
              <div>${escapeHtml(size)}</div>
            </div>
          </div>
          <div style="font-size:0.85rem;color:var(--text-soft);">Request: ${escapeHtml(requestText)}</div>
          <div class="prompt-block">${escapeHtml(prompt)}</div>
          <div style="font-size:0.75rem;color:var(--text-soft);">Created ${escapeHtml(formatTimestamp(summarySession.createdAt))}</div>
        `;
        sessionSummary.classList.remove('hidden');
        if (summarySession.warnings && summarySession.warnings.length) {
          sessionWarnings.innerHTML = `
            <strong>Warnings</strong>
            <ul>${summarySession.warnings.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul>
          `;
          sessionWarnings.classList.remove('hidden');
        } else {
          sessionWarnings.classList.add('hidden');
          sessionWarnings.innerHTML = '';
        }
      }

      function renderVariantFeed() {
        let variants = state.variants;
        if (state.sessionFilter) {
          variants = variants.filter((variant) => variant.sessionId === state.sessionFilter);
        }
        if (!variants.length) {
          variantGrid.innerHTML = '';
          variantEmpty.classList.remove('hidden');
          return;
        }
        variantEmpty.classList.add('hidden');
        variantGrid.innerHTML = variants
          .map((variant) => {
            const cropPercent = typeof variant.cropFraction === 'number'
              ? `${(variant.cropFraction * 100).toFixed(1)}%`
              : '0%';
            const originalLabel = variant.original && variant.original.width
              ? `Original ${variant.original.width}×${variant.original.height}`
              : 'Original n/a';
            const badges = [];
            if (variant.isSlotSelected) {
              badges.push('<span class="badge badge-info">Current slot</span>');
            }
            if (!variant.isSlotSelected && variant.isSessionSelected) {
              badges.push('<span class="badge badge-info">Session pick</span>');
            }
            if (variant.sessionWarnings && variant.sessionWarnings.length) {
              badges.push(`<span class="badge badge-warning">⚠ ${variant.sessionWarnings.length}</span>`);
            }
            const providerLine = [
              variant.sessionProvider || 'provider?',
              variant.sessionModel || 'model?',
              variant.sessionSize || 'size?',
            ].filter(Boolean).join(' • ');
            return `
              <article class="variant-card ${variant.isSlotSelected ? 'is-selected' : ''}" data-session="${escapeHtml(variant.sessionId)}" data-index="${variant.variantIndex}">
                <div class="variant-header">
                  <div class="variant-badges">${badges.join('')}</div>
                  <span class="variant-session">${escapeHtml(formatTimestamp(variant.sessionCompletedAt))}</span>
                </div>
                <div class="variant-thumb">
                  ${variant.isSlotSelected ? '<span class="badge-selected">Slot</span>' : ''}
                  <img src="${variant.processed.url}" alt="Variant ${variant.variantIndex}">
                </div>
                <div class="variant-info">
                  <strong>Session ${escapeHtml(variant.sessionId)} · #${variant.variantIndex}</strong>
                  <div>${escapeHtml(providerLine)}</div>
                  <div class="variant-stats">
                    <span>${variant.processed.width}×${variant.processed.height}</span>
                    <span>${escapeHtml(originalLabel)}</span>
                    <span>Crop ${cropPercent}</span>
                  </div>
                </div>
                <div class="variant-actions">
                  ${variant.raw ? `<button class="ghost-button" data-action="open-raw" data-session="${escapeHtml(variant.sessionId)}" data-index="${variant.variantIndex}" type="button">View raw</button>` : ''}
                  <button class="ghost-button" data-action="metadata" data-session="${escapeHtml(variant.sessionId)}" data-index="${variant.variantIndex}" type="button">Metadata</button>
                  <button class="primary-button" data-action="promote" data-session="${escapeHtml(variant.sessionId)}" data-index="${variant.variantIndex}" type="button" ${variant.isSlotSelected ? 'disabled' : ''}>Use this variant</button>
                </div>
              </article>
            `;
          })
          .join('');
      }

      function getVariant(sessionId, index) {
        return state.variants.find(
          (variant) => variant.sessionId === sessionId && variant.variantIndex === Number(index),
        );
      }

      function openMetadata(sessionId, index) {
        const variant = getVariant(sessionId, index);
        if (!variant) return;
        metadataTitle.textContent = `Variant #${variant.variantIndex} · Session ${variant.sessionId}`;
        const rows = [
          ['Slot', variant.slot],
          ['Session completed', formatTimestamp(variant.sessionCompletedAt)],
          ['Variant index', variant.variantIndex],
          ['Processed file', variant.processed.filename],
          ['Processed size', `${variant.processed.width}×${variant.processed.height}`],
          ['Media type', variant.processed.mediaType],
          ['Raw file', variant.raw ? variant.raw.filename : '—'],
          ['Crop fraction', typeof variant.cropFraction === 'number' ? variant.cropFraction.toFixed(3) : '—'],
          ['Original size', variant.original && variant.original.width ? `${variant.original.width}×${variant.original.height}` : '—'],
          ['Provider', variant.sessionProvider || '—'],
          ['Model', variant.sessionModel || '—'],
          ['Requested size', variant.sessionSize || '—'],
          ['Prompt', variant.sessionPrompt || '—'],
          ['Request text', variant.sessionRequest || '—'],
          ['SHA-256', variant.sha256],
        ];
        metadataGrid.innerHTML = rows
          .map(([label, value]) => `<dt>${escapeHtml(label)}</dt><dd>${escapeHtml(value || '—')}</dd>`)
          .join('');
        metadataJson.textContent = JSON.stringify(variant, null, 2);
        metadataOverlay.classList.remove('hidden');
      }

      function closeMetadata() {
        metadataOverlay.classList.add('hidden');
      }

      async function promoteVariant(sessionId, index) {
        const variant = getVariant(sessionId, index);
        if (!variant) return;
        try {
          const body = new URLSearchParams({
            slot: variant.slot,
            session: variant.sessionId,
            index: String(variant.variantIndex),
          });
          if (state.projectId) {
            body.set('project', state.projectId);
          }
          const res = await fetch('/api/select', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body,
          });
          if (!res.ok) throw new Error('Promote failed');
          showToast(`Promoted session ${variant.sessionId} #${variant.variantIndex}`);
          await loadSlotData(variant.slot, { forceReload: true, preserveFilter: true });
          await loadSlots({ forceReload: true });
        } catch (error) {
          console.error(error);
          showToast('Unable to promote variant', 'error');
        }
      }

      function getFilteredCampaignSummaries() {
        const needle = state.campaignSearch.trim().toLowerCase();
        return state.campaigns.filter((campaign) => {
          if (state.campaignStatusFilter !== 'all' && campaign.status !== state.campaignStatusFilter) {
            return false;
          }
          if (!needle) return true;
          const haystack = [
            campaign.name,
            campaign.campaignId,
            Array.isArray(campaign.tags) ? campaign.tags.join(' ') : '',
          ].join(' ').toLowerCase();
          return haystack.includes(needle);
        });
      }

      function renderCampaignList() {
        if (!campaignTableBody) return;
        const items = getFilteredCampaignSummaries();
        const total = state.campaigns.length;
        const selectedId = state.selectedCampaignId;
        campaignTableBody.innerHTML = items
          .map((campaign) => {
            const updated = campaign.updatedAt ? formatTimestamp(campaign.updatedAt) : '—';
            const approvedLabel = `${campaign.approved ?? 0}`;
            const variantsLabel = `${campaign.variants ?? 0}`;
            const isActive = selectedId && selectedId === campaign.campaignId;
            return `
              <tr data-campaign="${escapeHtml(campaign.campaignId)}" data-active="${isActive ? 'true' : 'false'}">
                <td>
                  <div style="display:flex;flex-direction:column;gap:0.25rem;">
                    <span style="font-weight:600;">${escapeHtml(campaign.name || campaign.campaignId)}</span>
                    ${campaign.tags && campaign.tags.length ? `<div class="campaign-list-meta">${campaign.tags.map((tag) => `<span class="campaign-chip">${escapeHtml(tag)}</span>`).join('')}</div>` : ''}
                  </div>
                </td>
                <td>${escapeHtml((campaign.status || '').toUpperCase())}</td>
                <td>${campaign.routes ?? 0}</td>
                <td>${campaign.placements ?? 0}</td>
                <td>${approvedLabel}</td>
                <td>${variantsLabel}</td>
                <td>${escapeHtml(updated)}</td>
              </tr>
            `;
          })
          .join('');
        if (campaignsEmpty) {
          campaignsEmpty.classList.toggle('hidden', Boolean(items.length));
        }
        if (campaignsSubtitle) {
          if (!state.projectId) {
            campaignsSubtitle.textContent = 'Select a project to view campaign workspaces.';
          } else {
            const projectName = getProjectName(state.projectId) || state.projectId;
            campaignsSubtitle.textContent = `${projectName} • ${items.length}/${total} campaigns`;
          }
        }
      }

      function showCampaignList() {
        state.selectedCampaignId = null;
        state.campaignDetail = null;
        state.campaignFilters = { route: 'all', placement: 'all', state: 'all' };
        updateViewVisibility();
        renderCampaignList();
        updateUrlState();
      }

      async function loadCampaigns(options = {}) {
        if (!state.projectId) {
          state.campaigns = [];
          renderCampaignList();
          return;
        }
        const { forceReload = false } = options;
        try {
          const params = new URLSearchParams({ project: state.projectId });
          if (forceReload) {
            params.set('_', Date.now().toString());
          }
          const fetchOptions = forceReload ? { cache: 'no-store' } : {};
          const res = await fetch(`/api/campaigns?${params.toString()}`, fetchOptions);
          if (!res.ok) throw new Error('Failed to load campaigns');
          const data = await res.json();
          state.campaigns = Array.isArray(data.campaigns) ? data.campaigns : [];
          renderCampaignList();
          updateViewVisibility();
          if (state.viewMode === 'campaigns' && state.selectedCampaignId) {
            const exists = state.campaigns.some((item) => item.campaignId === state.selectedCampaignId);
            if (!exists) {
              showCampaignList();
            }
          }
          if (state.pendingCampaign) {
            const pendingId = state.pendingCampaign;
            state.pendingCampaign = null;
            const found = state.campaigns.some((item) => item.campaignId === pendingId);
            if (found) {
              setViewMode('campaigns');
              selectCampaign(pendingId);
            }
          }
          if (forceReload && state.selectedCampaignId) {
            await loadCampaignDetail(state.selectedCampaignId, { forceReload: true });
          }
        } catch (error) {
          console.error(error);
          showToast('Unable to load campaigns', 'error');
        }
      }

      function populateCampaignFilters(detail) {
        if (!detail) return;
        if (campaignFilterRoute) {
          const options = ['<option value="all">All routes</option>']
            .concat((detail.routes || []).map((route) => {
              const active = state.campaignFilters.route === route.routeId;
              return `<option value="${escapeHtml(route.routeId)}" ${active ? 'selected' : ''}>${escapeHtml(route.name || route.routeId)}</option>`;
            }));
          campaignFilterRoute.innerHTML = options.join('');
          if (state.campaignFilters.route && state.campaignFilters.route !== 'all') {
            campaignFilterRoute.value = state.campaignFilters.route;
          }
        }
        if (campaignFilterPlacement) {
          const options = ['<option value="all">All placements</option>']
            .concat((detail.placements || []).map((placement) => {
              const active = state.campaignFilters.placement === placement.placementId;
              return `<option value="${escapeHtml(placement.placementId)}" ${active ? 'selected' : ''}>${escapeHtml(placement.placementId)}</option>`;
            }));
          campaignFilterPlacement.innerHTML = options.join('');
          if (state.campaignFilters.placement && state.campaignFilters.placement !== 'all') {
            campaignFilterPlacement.value = state.campaignFilters.placement;
          }
        }
        if (campaignFilterState) {
          campaignFilterState.value = state.campaignFilters.state;
        }
      }

      function getCampaignMeta(detail) {
        const placementsMeta = new Map();
        (detail.placements || []).forEach((placement) => {
          placementsMeta.set(placement.placementId, placement);
        });
        const routesMeta = new Map();
        (detail.routes || []).forEach((route) => {
          routesMeta.set(route.routeId, route);
        });
        return { placementsMeta, routesMeta };
      }

      function getFilteredCampaignMatrix(detail) {
        if (!detail) return [];
        const { placementsMeta, routesMeta } = getCampaignMeta(detail);
        const placementFilter = state.campaignFilters.placement;
        const routeFilter = state.campaignFilters.route;
        const stateFilter = state.campaignFilters.state;
        const grouped = new Map();
        (detail.matrix || []).forEach((cell) => {
          if (routeFilter !== 'all' && cell.routeId !== routeFilter) return;
          if (placementFilter !== 'all' && cell.placementId !== placementFilter) return;
          const variants = (cell.variants || []).filter((variant) => {
            if (stateFilter === 'all') return true;
            return variant.reviewState === stateFilter;
          });
          if (!variants.length) return;
          const placementId = cell.placementId;
          if (!grouped.has(placementId)) {
            grouped.set(placementId, {
              placement: placementsMeta.get(placementId) || { placementId },
              routes: [],
            });
          }
          const routeMeta = routesMeta.get(cell.routeId) || { routeId: cell.routeId, name: cell.routeId, summary: cell.routeSummary };
          grouped.get(placementId).routes.push({
            routeId: cell.routeId,
            route: routeMeta,
            variants,
          });
        });
        return Array.from(grouped.entries())
          .sort((a, b) => a[0].localeCompare(b[0]))
          .map(([placementId, value]) => ({
          placementId,
          placement: value.placement,
          routes: value.routes.sort((a, b) => {
            const nameA = (a.route && a.route.name) || a.routeId;
            const nameB = (b.route && b.route.name) || b.routeId;
            return nameA.localeCompare(nameB);
          }),
        }));
      }

      function renderCampaignDetail() {
        if (!campaignDetailView) return;
        const detail = state.campaignDetail;
        if (!detail || !state.selectedCampaignId) {
          campaignDetailView.classList.add('hidden');
          campaignDetailView.classList.remove('active');
          return;
        }
        renderCampaignList();
        const campaign = detail.campaign || {};
        const summary = state.campaigns.find((item) => item.campaignId === campaign.campaignId);
        if (summary && detail.stats) {
          summary.updatedAt = campaign.updatedAt || summary.updatedAt;
          summary.approved = detail.stats.approved ?? summary.approved;
          summary.pending = detail.stats.pending ?? summary.pending;
          summary.revise = detail.stats.revise ?? summary.revise;
          summary.variants = detail.stats.total ?? summary.variants;
        }
        campaignTitle.textContent = campaign.name || campaign.campaignId;
        const status = (campaign.status || '').toUpperCase();
        const tagLine = Array.isArray(campaign.tags) && campaign.tags.length
          ? campaign.tags.map((tag) => `<span class="campaign-chip">${escapeHtml(tag)}</span>`).join(' ')
          : '';
        campaignSubtitle.innerHTML = `${escapeHtml(status)} ${tagLine}`;

        if (campaignSummary) {
          const brief = campaign.brief || {};
          const objective = brief.objective ? escapeHtml(brief.objective) : '—';
          const stats = detail.stats || {};
          campaignSummary.innerHTML = `
            <div><strong>Status</strong> ${escapeHtml(status)}</div>
            <div><strong>Default provider</strong> ${escapeHtml(campaign.defaultProvider || '—')}</div>
            <div><strong>Variants</strong> ${stats.total ?? 0} total · ${stats.approved ?? 0} approved</div>
            <div><strong>Objective</strong> ${objective}</div>
            <div><strong>Updated</strong> ${escapeHtml(formatTimestamp(campaign.updatedAt))}</div>
          `;
        }

        if (campaignExports) {
          const exports = detail.exports || [];
          if (!exports.length) {
            campaignExports.innerHTML = '<span style="color:var(--text-soft);">No exports yet.</span>';
          } else {
            campaignExports.innerHTML = exports
              .map((entry) => {
                const includeStates = entry.includeStates || [];
                return `
                  <div class="campaign-export-item">
                    <div style="font-weight:600;">${escapeHtml(entry.platform)} · ${escapeHtml(entry.exportId)}</div>
                    <div>Generated ${escapeHtml(formatTimestamp(entry.generatedAt))}</div>
                    <div>${includeStates.slice().join(', ') || 'approved'}</div>
                    <div>${entry.fileCount ?? 0} files · ${escapeHtml(entry.manifestPath || '')}</div>
                  </div>
                `;
              })
              .join('');
          }
        }

        if (campaignLogs) {
          const logs = detail.logs || [];
          if (!logs.length) {
            campaignLogs.innerHTML = '<span style="color:var(--text-soft);">No batch runs yet.</span>';
          } else {
            campaignLogs.innerHTML = logs
              .map((entry) => `
                <div class="campaign-log-item">
                  <div style="font-weight:600;">${escapeHtml(entry.filename)}</div>
                  <div>${escapeHtml(formatTimestamp(entry.updatedAt))} · ${entry.sizeBytes ?? 0} bytes</div>
                  <div>${escapeHtml(entry.relativePath || '')}</div>
                </div>
              `)
              .join('');
          }
        }

        if (campaignRouteList) {
          const routes = detail.routes || [];
          if (!routes.length) {
            campaignRouteList.innerHTML = '<span style="color:var(--text-soft);">No routes yet.</span>';
          } else {
            campaignRouteList.innerHTML = routes
              .map((route) => {
                const active = state.campaignFilters.route === route.routeId;
                return `
                  <div class="campaign-route-card" data-route="${escapeHtml(route.routeId)}" data-active="${active ? 'true' : 'false'}">
                    <div style="font-weight:600;">${escapeHtml(route.name || route.routeId)}</div>
                    <div style="font-size:0.78rem;color:var(--text-soft);">${escapeHtml(route.summary || '')}</div>
                  </div>
                `;
              })
              .join('');
          }
        }

        populateCampaignFilters(detail);

        const grouped = getFilteredCampaignMatrix(detail);
        if (!grouped.length) {
          campaignGrid.innerHTML = '';
          campaignEmpty.classList.remove('hidden');
        } else {
          campaignEmpty.classList.add('hidden');
          campaignGrid.innerHTML = grouped
            .map((group) => {
              const placement = group.placement || {};
              const counts = placement.counts || {};
              const badge = `<div class="campaign-list-meta"><span class="campaign-chip">APP ${counts.approved ?? 0}</span><span class="campaign-chip">PND ${counts.pending ?? 0}</span><span class="campaign-chip">REV ${counts.revise ?? 0}</span></div>`;
              const routeBlocks = group.routes
                .map((entry) => {
                  const variants = entry.variants || [];
                  const preview = variants
                    .map((variant) => {
                      const thumb = variant.thumbnailUrl
                        ? `<img src="${variant.thumbnailUrl}" alt="Variant ${variant.index}">`
                        : '<div class="thumb-placeholder">No thumb</div>';
                      return `
                        <button type="button" class="campaign-variant-thumb" data-route="${escapeHtml(entry.routeId)}" data-placement="${escapeHtml(group.placementId)}" data-index="${variant.index}" data-state="${escapeHtml(variant.reviewState)}">
                          ${thumb}
                        </button>
                      `;
                    })
                    .join('');
                  return `
                    <div style="display:flex;flex-direction:column;gap:0.5rem;">
                      <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div style="font-weight:600;">${escapeHtml(entry.route.name || entry.routeId)}</div>
                        <span style="font-size:0.7rem;color:var(--text-soft);">${variants.length} variants</span>
                      </div>
                      <div class="campaign-variant-strip">${preview || '<span style="color:var(--text-soft);font-size:0.78rem;">No variants</span>'}</div>
                    </div>
                  `;
                })
                .join('');
              return `
                <div class="campaign-matrix-cell">
                  <div class="campaign-matrix-header">
                    <div>
                      <h2 style="margin:0;">${escapeHtml(group.placementId)}</h2>
                      <span style="font-size:0.75rem;color:var(--text-soft);">${escapeHtml(placement.templateId || '')}</span>
                    </div>
                    ${badge}
                  </div>
                  <div style="display:flex;flex-direction:column;gap:1rem;">
                    ${routeBlocks}
                  </div>
                </div>
              `;
            })
            .join('');
        }

        updateViewVisibility();
        updateUrlState();
      }

      async function selectCampaign(campaignId) {
        if (!campaignId) return;
        state.viewMode = 'campaigns';
        state.selectedCampaignId = campaignId;
        state.campaignFilters = { route: 'all', placement: 'all', state: 'all' };
        renderCampaignList();
        updateViewVisibility();
        await loadCampaignDetail(campaignId);
      }

      async function loadCampaignDetail(campaignId, { forceReload = false } = {}) {
        if (!state.projectId || !campaignId) return;
        try {
          const params = new URLSearchParams({ project: state.projectId });
          if (forceReload) params.set('_', Date.now().toString());
          const fetchOptions = forceReload ? { cache: 'no-store' } : {};
          const res = await fetch(`/api/campaigns/${encodeURIComponent(campaignId)}?${params.toString()}`, fetchOptions);
          if (!res.ok) throw new Error('Failed to load campaign detail');
          const detail = await res.json();
          state.campaignDetail = detail;
          state.campaignFilters = state.campaignFilters || { route: 'all', placement: 'all', state: 'all' };
          updateViewVisibility();
          renderCampaignDetail();
        } catch (error) {
          console.error(error);
          showToast('Unable to load campaign detail', 'error');
          showCampaignList();
        }
      }

      function findCampaignVariant(detail, placementId, routeId, index) {
        if (!detail) return null;
        const cell = (detail.matrix || []).find((entry) => entry.placementId === placementId && entry.routeId === routeId);
        if (!cell) return null;
        return (cell.variants || []).find((variant) => Number(variant.index) === Number(index)) || null;
      }

      function openCampaignVariantOverlay(placementId, routeId, index) {
        const detail = state.campaignDetail;
        const variant = findCampaignVariant(detail, placementId, routeId, index);
        if (!variant) return;
        const placement = (detail.placements || []).find((item) => item.placementId === placementId) || {};
        const route = (detail.routes || []).find((item) => item.routeId === routeId) || {};
        const originalNotes = (variant.notes || '').trim();
        state.activeCampaignVariant = {
          campaignId: state.selectedCampaignId,
          placementId,
          routeId,
          index,
          originalState: variant.reviewState,
          originalNotes,
        };
        campaignOverlaySubtitle.innerHTML = `${escapeHtml(placementId)} • ${escapeHtml(route.name || routeId)}`;
        campaignOverlayState.value = variant.reviewState || 'pending';
        campaignOverlayNotes.value = originalNotes;
        campaignOverlayInfo.innerHTML = `
          <div>Seed: ${escapeHtml(String(variant.seed ?? '—'))}</div>
          <div>${escapeHtml(formatTimestamp(variant.createdAt))}</div>
          <div style="word-break:break-word;">${escapeHtml(variant.prompt || '')}</div>
        `;
        const previewUrl = variant.imageUrl || variant.thumbnailUrl || '';
        campaignOverlayImage.src = previewUrl;
        campaignOverlayJson.textContent = JSON.stringify(variant, null, 2);
        campaignOverlay.classList.remove('hidden');
      }

      function closeCampaignOverlay() {
        state.activeCampaignVariant = null;
        campaignOverlay.classList.add('hidden');
      }

      function resetCampaignOverlayInputs() {
        const active = state.activeCampaignVariant;
        if (!active) return;
        campaignOverlayState.value = active.originalState || 'pending';
        campaignOverlayNotes.value = active.originalNotes || '';
      }

      async function submitCampaignReview() {
        const active = state.activeCampaignVariant;
        if (!active || !state.selectedCampaignId) return;
        try {
          const nextState = campaignOverlayState.value || 'pending';
          const nextNotes = (campaignOverlayNotes.value || '').trim();
          if (nextState === (active.originalState || 'pending') && nextNotes === (active.originalNotes || '')) {
            closeCampaignOverlay();
            return;
          }
          if (campaignOverlayApply) {
            campaignOverlayApply.disabled = true;
          }
          const params = new URLSearchParams();
          if (state.projectId) {
            params.set('project', state.projectId);
          }
          const payload = {
            placementId: active.placementId,
            routeId: active.routeId,
            variantIndex: active.index,
            state: nextState,
            notes: nextNotes,
          };
          const res = await fetch(`/api/campaigns/${encodeURIComponent(state.selectedCampaignId)}/review?${params.toString()}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
          });
          if (!res.ok) throw new Error('Review update failed');
          const data = await res.json();
          const detail = state.campaignDetail;
          if (detail) {
            const cell = (detail.matrix || []).find((entry) => entry.placementId === active.placementId && entry.routeId === active.routeId);
            if (cell) {
              const updated = (cell.variants || []).find((variant) => Number(variant.index) === Number(active.index));
              if (updated && data.variant) {
                Object.assign(updated, data.variant);
              }
            }
            const placement = (detail.placements || []).find((item) => item.placementId === active.placementId);
            if (placement && data.counts) {
              placement.counts = data.counts;
            }
            if (data.stats) {
              detail.stats = data.stats;
            }
          }
          const summary = state.campaigns.find((item) => item.campaignId === state.selectedCampaignId);
          if (summary && data.stats) {
            summary.approved = data.stats.approved ?? summary.approved;
            summary.pending = data.stats.pending ?? summary.pending;
            summary.revise = data.stats.revise ?? summary.revise;
            summary.variants = data.stats.total ?? summary.variants;
          }
          renderCampaignList();
          renderCampaignDetail();
          showToast('Review updated');
          closeCampaignOverlay();
        } catch (error) {
          console.error(error);
          showToast('Unable to update review state', 'error');
        } finally {
          if (campaignOverlayApply) {
            campaignOverlayApply.disabled = false;
          }
        }
      }

      slotGrid.addEventListener('click', (event) => {
        const card = event.target.closest('.slot-card');
        if (!card) return;
        const slotId = card.dataset.slot;
        if (slotId) {
          selectSlot(slotId).catch((error) => console.error(error));
        }
      });

      sessionList.addEventListener('click', (event) => {
        const button = event.target.closest('.session-item');
        if (!button) return;
        const sessionId = button.dataset.session;
        state.sessionFilter = sessionId && sessionId !== '__all__' ? sessionId : null;
        renderSessionList();
        renderSessionSummary();
        renderVariantFeed();
      });

      variantGrid.addEventListener('click', (event) => {
        const button = event.target.closest('button');
        if (!button) return;
        const action = button.dataset.action;
        const sessionId = button.dataset.session;
        const index = button.dataset.index;
        if (!sessionId || index === undefined) return;
        if (action === 'metadata') {
          openMetadata(sessionId, index);
        } else if (action === 'promote') {
          promoteVariant(sessionId, index);
        } else if (action === 'open-raw') {
          const variant = getVariant(sessionId, index);
          if (variant && variant.raw && variant.raw.url) {
            window.open(variant.raw.url, '_blank');
          }
        }
      });

      if (projectSelect) {
        projectSelect.addEventListener('change', (event) => {
          const nextProject = event.target.value;
          if (!nextProject || nextProject === state.projectId) {
            return;
          }
          state.pendingSlot = null;
          setProject(nextProject);
        });
      }

      refreshSlotsBtn.addEventListener('click', () => {
        loadSlots({ forceReload: true });
      });

      refreshSlotBtn.addEventListener('click', async () => {
        if (state.slot) {
          await loadSlotData(state.slot, { forceReload: true, preserveFilter: true });
          await loadSlots({ forceReload: true });
        }
      });

      filterWarningsBtn.addEventListener('click', () => {
        state.filterWarnings = !state.filterWarnings;
        renderSlots();
      });

      backToSlotsBtn.addEventListener('click', () => {
        resetSlotView();
        updateUrlState();
        loadSlots();
      });

      openSelectedBtn.addEventListener('click', () => {
        const url = openSelectedBtn.dataset.url;
        if (url) {
          window.open(url, '_blank');
        }
      });

      if (deleteSlotBtn) {
        deleteSlotBtn.addEventListener('click', () => {
          if (!state.slot) {
            return;
          }
          const message = `Delete slot "${state.slot}"? This removes all sessions and the selected image.`;
          const confirmed = window.confirm(message);
          if (!confirmed) {
            deleteSlotBtn.blur();
            return;
          }
          requestSlotDeletion(state.slot).catch((error) => console.error(error));
        });
      }

      if (tabSlots) {
        tabSlots.addEventListener('click', () => {
          setViewMode('slots');
        });
      }

      if (tabCampaigns) {
        tabCampaigns.addEventListener('click', () => {
          setViewMode('campaigns');
          showCampaignList();
        });
      }

      if (refreshCampaignsBtn) {
        refreshCampaignsBtn.addEventListener('click', () => {
          loadCampaigns({ forceReload: true });
        });
      }

      if (campaignSearchInput) {
        campaignSearchInput.addEventListener('input', (event) => {
          state.campaignSearch = (event.target.value || '').toString();
          renderCampaignList();
        });
      }

      if (campaignStatusFilter) {
        campaignStatusFilter.addEventListener('change', (event) => {
          state.campaignStatusFilter = event.target.value || 'all';
          renderCampaignList();
        });
      }

      if (campaignTableBody) {
        campaignTableBody.addEventListener('click', (event) => {
          const row = event.target.closest('tr[data-campaign]');
          if (!row) return;
          const campaignId = row.dataset.campaign;
          if (campaignId) {
            selectCampaign(campaignId).catch((error) => console.error(error));
          }
        });
      }

      if (campaignFilterRoute) {
        campaignFilterRoute.addEventListener('change', (event) => {
          state.campaignFilters.route = event.target.value || 'all';
          renderCampaignDetail();
        });
      }

      if (campaignRouteList) {
        campaignRouteList.addEventListener('click', (event) => {
          const card = event.target.closest('.campaign-route-card');
          if (!card) return;
          const routeId = card.dataset.route;
          if (!routeId) return;
          state.campaignFilters.route = state.campaignFilters.route === routeId ? 'all' : routeId;
          renderCampaignDetail();
        });
      }

      if (campaignFilterPlacement) {
        campaignFilterPlacement.addEventListener('change', (event) => {
          state.campaignFilters.placement = event.target.value || 'all';
          renderCampaignDetail();
        });
      }

      if (campaignFilterState) {
        campaignFilterState.addEventListener('change', (event) => {
          state.campaignFilters.state = event.target.value || 'all';
          renderCampaignDetail();
        });
      }

      if (backToCampaignsBtn) {
        backToCampaignsBtn.addEventListener('click', () => {
          showCampaignList();
        });
      }

      if (refreshCampaignDetailBtn) {
        refreshCampaignDetailBtn.addEventListener('click', () => {
          if (state.selectedCampaignId) {
            loadCampaignDetail(state.selectedCampaignId, { forceReload: true });
          }
        });
      }

      if (campaignGrid) {
        campaignGrid.addEventListener('click', (event) => {
          const thumb = event.target.closest('.campaign-variant-thumb');
          if (!thumb) return;
          const placementId = thumb.dataset.placement;
          const routeId = thumb.dataset.route;
          const index = thumb.dataset.index;
          if (!placementId || !routeId || index === undefined) return;
          openCampaignVariantOverlay(placementId, routeId, Number(index));
        });
      }

      if (campaignOverlayClose) {
        campaignOverlayClose.addEventListener('click', () => {
          closeCampaignOverlay();
        });
      }

      if (campaignOverlayReset) {
        campaignOverlayReset.addEventListener('click', () => {
          resetCampaignOverlayInputs();
        });
      }

      if (campaignOverlayApply) {
        campaignOverlayApply.addEventListener('click', () => {
          submitCampaignReview();
        });
      }

      if (campaignOverlay) {
        campaignOverlay.addEventListener('click', (event) => {
          if (event.target === campaignOverlay) {
            closeCampaignOverlay();
          }
        });
      }

      metadataCloseBtn.addEventListener('click', closeMetadata);
      metadataOverlay.addEventListener('click', (event) => {
        if (event.target === metadataOverlay) {
          closeMetadata();
        }
      });

      updateViewVisibility();
      loadProjects();
    })();
  </script>
</body>
</html>
"""


__all__ = ["serve_gallery", "GalleryServer"]
