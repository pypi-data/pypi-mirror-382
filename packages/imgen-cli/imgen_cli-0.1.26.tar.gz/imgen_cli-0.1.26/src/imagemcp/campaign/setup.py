from __future__ import annotations

from typing import Iterable, List, Optional

import shutil

from .workspace import CampaignWorkspace
from .schemas import CampaignRoute, PlacementRef


def add_route_from_args(
    workspace: CampaignWorkspace,
    route_id: str,
    *,
    name: Optional[str] = None,
    summary: Optional[str] = None,
    prompt_template: Optional[str] = None,
    source: Optional[str] = None,
    prompt_tokens: Optional[Iterable[str]] = None,
    copy_tokens: Optional[Iterable[str]] = None,
    notes: Optional[str] = None,
) -> CampaignRoute:
    route = CampaignRoute(
        route_id=route_id,
        name=name or route_id.replace("_", " ").title(),
        summary=summary or "TODO: fill summary",
        prompt_template=prompt_template or "TODO: fill prompt",
        source=source or "manual",
        prompt_tokens=list(prompt_tokens or ()),
        copy_tokens=list(copy_tokens or ()),
        notes=notes,
    )
    workspace.save_route(route)
    return route


def add_placement_to_campaign(
    workspace: CampaignWorkspace,
    placement_id: str,
    *,
    template_id: Optional[str] = None,
    variants: Optional[int] = None,
    copy_tokens: Optional[Iterable[str]] = None,
    provider: Optional[str] = None,
    notes: Optional[str] = None,
) -> PlacementRef:
    config = workspace.load_config()
    template_slug = template_id or placement_id
    placement_ref = PlacementRef(
        template_id=template_slug,
        override_id=placement_id if placement_id != template_slug else None,
        variants=variants,
        copy_tokens=list(copy_tokens or ()),
        provider=provider,
        notes=notes,
    )
    placements = [ref for ref in config.placements if ref.effective_id != placement_id]
    placements.append(placement_ref)
    config = config.model_copy(update={"placements": placements})
    workspace.save_config(config)
    return placement_ref


def ensure_campaign_exists(workspace: CampaignWorkspace) -> None:
    if not workspace.config_path.exists():
        raise FileNotFoundError(
            f"Campaign '{workspace.campaign_id}' is not initialized."
        )


def list_routes(workspace: CampaignWorkspace) -> List[CampaignRoute]:
    return list(workspace.iter_routes() or [])


def load_route(workspace: CampaignWorkspace, route_id: str) -> CampaignRoute:
    return workspace.load_route(route_id)


def remove_route(
    workspace: CampaignWorkspace,
    route_id: str,
    *,
    delete_assets: bool = False,
) -> Path:
    path = workspace.route_path(route_id)
    if not path.exists():
        raise FileNotFoundError(f"Route '{route_id}' not found")
    route_dir = path.parent
    if delete_assets and route_dir.exists():
        shutil.rmtree(route_dir)
        return route_dir
    path.unlink()
    # clean up parent directory if empty
    try:
        if not any(route_dir.iterdir()):
            route_dir.rmdir()
    except OSError:
        pass
    return path


def list_placements(workspace: CampaignWorkspace) -> List[PlacementRef]:
    config = workspace.load_config()
    return list(config.placements or [])


def get_placement(workspace: CampaignWorkspace, placement_id: str) -> PlacementRef:
    for placement in list_placements(workspace):
        if placement.effective_id == placement_id:
            return placement
    raise FileNotFoundError(f"Placement '{placement_id}' not found in campaign.yaml")


def remove_placement_from_campaign(
    workspace: CampaignWorkspace,
    placement_id: str,
) -> None:
    config = workspace.load_config()
    filtered = [ref for ref in config.placements if ref.effective_id != placement_id]
    if len(filtered) == len(config.placements):
        raise FileNotFoundError(f"Placement '{placement_id}' not found in campaign.yaml")
    config = config.model_copy(update={"placements": filtered})
    workspace.save_config(config)


__all__ = [
    "add_route_from_args",
    "add_placement_to_campaign",
    "ensure_campaign_exists",
    "list_routes",
    "load_route",
    "remove_route",
    "list_placements",
    "get_placement",
    "remove_placement_from_campaign",
]
