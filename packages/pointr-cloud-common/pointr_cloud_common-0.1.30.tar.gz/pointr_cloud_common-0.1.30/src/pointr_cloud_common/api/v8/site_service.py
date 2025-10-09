from typing import Dict, Any, List, Optional
import logging
from pointr_cloud_common.dto.v9 import SiteDTO, BuildingDTO, LevelDTO
from pointr_cloud_common.dto.v9.validation import ensure_dict, ValidationError
from pointr_cloud_common.api.v8.base_service import BaseApiService, V8ApiError


DEFAULT_GEOMETRY = {
    "type": "Polygon",
    "coordinates": [[[0.0, 0.0], [0.0, 0.001], [0.001, 0.001], [0.001, 0.0], [0.0, 0.0]]],
}


def _strip_geometry(obj: Any) -> Any:
    """Recursively remove geometry objects from dictionaries/lists."""

    if isinstance(obj, dict):
        return {key: _strip_geometry(value) for key, value in obj.items() if key != "geometry"}
    if isinstance(obj, list):
        return [_strip_geometry(item) for item in obj]
    return obj


class SiteApiService(BaseApiService):
    """Service for site-related V8 API operations."""

    def __init__(self, api_service):
        super().__init__(api_service)
        self.logger = logging.getLogger(__name__)

    def _fetch_source_geometry(self, fid: str, source_api_service: Any) -> Optional[Dict[str, Any]]:
        """Fetch geometry for the given site fid from the source API service."""
        try:
            data = source_api_service._make_request("GET", f"api/v8/sites/{fid}/draft")
            result = data.get("result", data)
            geometry = result.get("geometry")
            if geometry:
                self.logger.info(f"Successfully retrieved geometry for site {fid} from source API")
                return geometry
            self.logger.warning(f"No geometry found for site {fid} in source API")
        except Exception as e:
            self.logger.error(f"Failed to retrieve geometry for site {fid} from source API: {str(e)}")
        return None

    def _to_site_dto(self, data: Dict[str, Any]) -> SiteDTO:
        """Convert a raw V8 API site object into a SiteDTO."""

        # Parse nested buildings if present.  The `/clients/{id}/sites` endpoint
        # may include a ``buildings`` array with level information.  We mirror
        # the logic from ``BuildingApiService._building_from_v8`` here instead
        # of importing the service to keep this method self-contained.

        site_fid = str(data.get("siteInternalIdentifier"))
        buildings: List[BuildingDTO] = []
        for b in data.get("buildings", []):
            levels: List[LevelDTO] = []
            for l in b.get("levels", []):
                try:
                    level_dto = LevelDTO(
                        fid=str(l.get("levelIndex")),
                        name=l.get("levelLongTitle", ""),
                        shortName=l.get("levelShortTitle"),
                        levelNumber=l.get("levelIndex"),
                        typeCode="level-outline",
                        sid=site_fid,
                        bid=str(b.get("buildingInternalIdentifier")),
                    )
                    levels.append(level_dto)
                except ValidationError as e:
                    self.logger.error(f"Failed to parse level: {str(e)}")
                    raise V8ApiError(f"Failed to parse level: {str(e)}")

            try:
                building_dto = BuildingDTO(
                    fid=str(b.get("buildingInternalIdentifier")),
                    name=b.get("buildingTitle", ""),
                    typeCode="building-outline",
                    sid=site_fid,
                    bid=b.get("buildingExternalIdentifier"),
                    extraData=ensure_dict(b.get("buildingExtraData"), "buildingExtraData"),
                    levels=levels,
                )
                buildings.append(building_dto)
            except ValidationError as e:
                self.logger.error(f"Failed to parse building: {str(e)}")
                raise V8ApiError(f"Failed to parse building: {str(e)}")

        try:
            return SiteDTO(
                fid=site_fid,
                name=data.get("siteTitle", ""),
                typeCode="site-outline",
                sid=data.get("siteExternalIdentifier"),
                extraData=ensure_dict(data.get("siteExtraData"), "siteExtraData"),
                buildings=buildings,
            )
        except ValidationError as e:
            self.logger.error(f"Failed to parse site: {str(e)}")
            raise V8ApiError(f"Failed to parse site: {str(e)}")

    def list_sites_with_buildings(
        self, data: Optional[Dict[str, Any]] = None
    ) -> List[SiteDTO]:
        """Return SiteDTO objects (with nested buildings) from a raw V8 payload."""

        if data is None:
            endpoint = f"api/v8/clients/{self.client_id}/sites/draft"
            self.logger.info(
                "Fetching V8 sites payload for list_sites_with_buildings: %s", endpoint
            )
            data = self._make_request("GET", endpoint)

        if not isinstance(data, dict):
            self.logger.warning(
                "V8 list_sites_with_buildings received non-dict payload: %s", type(data)
            )
            return []

        result_container = data.get("result", data)
        sites_raw = []
        if isinstance(result_container, dict):
            sites_raw = result_container.get("sites", []) or []

        sites: List[SiteDTO] = []
        for raw_site in sites_raw:
            if not isinstance(raw_site, dict):
                self.logger.debug("Skipping non-dict site entry: %s", raw_site)
                continue

            sanitized_site = _strip_geometry(raw_site)
            try:
                site_dto = self._to_site_dto(sanitized_site)
            except V8ApiError:
                raise
            except Exception as exc:
                self.logger.error("Unexpected error parsing site: %s", exc)
                raise
            sites.append(site_dto)

        return sites

    def get_sites(self) -> List[SiteDTO]:
        """Get all sites for the client along with their buildings."""
        endpoint = f"api/v8/clients/{self.client_id}/sites/draft"
        self.logger.info(
            "Making V8 API call to get sites with nested buildings: %s", endpoint
        )
        data = self._make_request("GET", endpoint)

        sites = self.list_sites_with_buildings(data)
        self.logger.info(f"Converted {len(sites)} sites to DTOs")

        return sites

    def get_site_by_fid(self, site_fid: str) -> SiteDTO:
        endpoint = f"api/v8/sites/{site_fid}/draft"
        data = self._make_request("GET", endpoint)
        site_data = data.get("result", data)
        try:
            site = self._to_site_dto(site_data)
            return site
        except Exception as e:
            raise

    def create_site(self, site: SiteDTO, source_api_service: Optional[Any] = None) -> str:
        geometry = DEFAULT_GEOMETRY
        if source_api_service:
            fetched = self._fetch_source_geometry(site.fid, source_api_service)
            if fetched:
                geometry = fetched
        payload = {
            "siteTitle": site.name,
            "siteExternalIdentifier": site.sid,
            "siteExtraData": site.extraData,
            "geometry": geometry,
        }
        payload = {k: v for k, v in payload.items() if v is not None}
        endpoint = f"api/v8/clients/{self.client_id}/sites"
        data = self._make_request("POST", endpoint, payload)
        return str(data.get("result", {}).get("siteInternalIdentifier", ""))

    def update_site(self, site_id: str, site: SiteDTO, source_api_service: Optional[Any] = None) -> str:
        endpoint = f"api/v8/sites/{site_id}"
        geometry = DEFAULT_GEOMETRY
        if source_api_service:
            fetched = self._fetch_source_geometry(site.fid, source_api_service)
            if fetched:
                geometry = fetched
        payload = {
            "siteTitle": site.name,
            "siteExternalIdentifier": site.sid,
            "siteExtraData": site.extraData,
            "geometry": geometry,
        }
        payload = {k: v for k, v in payload.items() if v is not None}
        try:
            self._make_request("PATCH", endpoint, payload)
        except Exception as e:
            raise
        return site_id

    def update_site_extra_data(self, site_fid: str, extra_data: Dict[str, Any]) -> bool:
        try:
            # Get the current site to retrieve the title
            current_site = self.get_site_by_fid(site_fid)
            payload = {
                "siteTitle": current_site.name,
                "siteExtraData": extra_data
            }
            endpoint = f"api/v8/sites/{site_fid}"
            self._make_request("PATCH", endpoint, payload)
            return True
        except Exception as e:
            self.logger.error(f"Error updating site extra data for {site_fid}: {str(e)}")
            raise
