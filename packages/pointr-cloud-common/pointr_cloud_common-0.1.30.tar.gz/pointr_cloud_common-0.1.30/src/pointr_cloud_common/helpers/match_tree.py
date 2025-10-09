"""Utilities for building consistent site/building trees across API versions."""

from typing import Any, Dict, Iterable, List, Optional

from pointr_cloud_common.dto.v9.site_dto import SiteDTO
from pointr_cloud_common.dto.v9.building_dto import BuildingDTO
from pointr_cloud_common.dto.v9.validation import ensure_dict


def _serialise_sdk_configs(configs: Optional[Iterable[Any]]) -> List[Dict[str, Any]]:
    """Convert SDK configuration DTOs/dicts to serialisable dictionaries."""
    serialised: List[Dict[str, Any]] = []
    if not configs:
        return serialised

    for cfg in configs:
        if hasattr(cfg, "to_api_json"):
            serialised.append(cfg.to_api_json())  # type: ignore[call-arg]
        elif isinstance(cfg, dict):
            serialised.append(cfg)
    return serialised


def _serialise_levels(levels: Optional[Iterable[Any]]) -> List[Dict[str, Any]]:
    """Return lightweight level payloads without geometry information."""
    if not levels:
        return []

    serialised: List[Dict[str, Any]] = []
    for level in levels:
        if hasattr(level, "to_api_json"):
            serialised.append(level.to_api_json())  # type: ignore[call-arg]
        elif isinstance(level, dict):
            serialised.append(level)
    return serialised


def _build_building_entry(site_fid: str, building: BuildingDTO) -> Dict[str, Any]:
    """Transform a BuildingDTO into the payload expected by the frontend."""
    return {
        "type": "building",
        "name": building.name,
        "fid": building.fid,
        "levels": _serialise_levels(getattr(building, "levels", [])),
        "extraData": ensure_dict(getattr(building, "extraData", {}), "building.extraData"),
        "sdkConfigurations": _serialise_sdk_configs(getattr(building, "sdkConfigurations", [])),
        "options": ensure_dict(getattr(building, "options", {}), "building.options"),
    }


def _build_site_entry(site: SiteDTO, buildings: List[BuildingDTO]) -> Dict[str, Any]:
    """Transform a SiteDTO plus building DTOs into the payload expected by the frontend."""
    filtered_buildings = [
        b for b in buildings if getattr(b, "typeCode", "") == "building-outline"
    ]
    building_entries = [_build_building_entry(site.fid, b) for b in filtered_buildings]

    return {
        "type": "site",
        "name": site.name,
        "fid": site.fid,
        "buildings": building_entries,
        "extraData": ensure_dict(getattr(site, "extraData", {}), "site.extraData"),
        "sdkConfigurations": _serialise_sdk_configs(getattr(site, "sdkConfigurations", [])),
        "options": ensure_dict(getattr(site, "options", {}), "site.options"),
    }


def build_site_building_tree(api_service: Any) -> List[Dict[str, Any]]:
    """Return a consistent site/building tree for both V8 and V9 API services."""
    sites: List[SiteDTO] = api_service.get_sites()
    tree: List[Dict[str, Any]] = []

    for site in sites:
        buildings: List[BuildingDTO] = list(getattr(site, "buildings", []) or [])
        if not buildings:
            try:
                buildings = api_service.get_buildings(site.fid)
            except Exception:
                buildings = []
        tree.append(_build_site_entry(site, buildings))

    return tree
