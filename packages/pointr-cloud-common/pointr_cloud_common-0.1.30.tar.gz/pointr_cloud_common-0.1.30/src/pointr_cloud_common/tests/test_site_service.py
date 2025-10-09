from pathlib import Path
import sys
from typing import Any, Dict, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pointr_cloud_common.api.v8.site_service import SiteApiService as V8SiteApiService
from pointr_cloud_common.api.v9.site_service import SiteApiService as V9SiteApiService


class _DummyApiService:
    def __init__(self) -> None:
        self.client_id = "test-client"
        self.base_url = "https://example.com"
        self.token = "token"
        self.user_email = None

    def _make_request(
        self, method: str, endpoint: str, json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        raise AssertionError("Tests should supply payloads directly")


class _RecordingBuildingService:
    def __init__(self) -> None:
        self.calls = []

    def get_buildings(self, site_fid: str):
        self.calls.append(site_fid)
        return []


class _DummyApiServiceWithPayload(_DummyApiService):
    def __init__(self, payload: Dict[str, Any], building_service: Any) -> None:
        super().__init__()
        self._payload = payload
        self.building_service = building_service

    def _make_request(
        self, method: str, endpoint: str, json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return self._payload


def test_v8_list_sites_with_buildings_preserves_structure() -> None:
    raw_response = {
        "result": {
            "sites": [
                {
                    "siteInternalIdentifier": 1,
                    "siteTitle": "HQ",
                    "siteExternalIdentifier": "site-ext",
                    "siteExtraData": {"foo": "bar"},
                    "geometry": {"type": "Polygon"},
                    "buildings": [
                        {
                            "buildingInternalIdentifier": 10,
                            "buildingTitle": "Tower",
                            "buildingExternalIdentifier": "tower-ext",
                            "buildingExtraData": {"colour": "blue"},
                            "geometry": {"type": "Polygon"},
                            "levels": [
                                {
                                    "levelIndex": 0,
                                    "levelLongTitle": "Ground",
                                    "levelShortTitle": "G",
                                    "geometry": {"type": "Polygon"},
                                }
                            ],
                        }
                    ],
                }
            ]
        }
    }

    service = V8SiteApiService(_DummyApiService())
    sites = service.list_sites_with_buildings(raw_response)

    assert len(sites) == 1
    site = sites[0]
    assert site.fid == "1"
    assert site.name == "HQ"
    assert site.buildings and site.buildings[0].fid == "10"
    assert site.buildings[0].sid == site.fid
    assert site.buildings[0].extraData == {"colour": "blue"}
    assert site.buildings[0].levels and site.buildings[0].levels[0].fid == "0"
    assert site.buildings[0].levels[0].sid == site.fid
    assert "geometry" in raw_response["result"]["sites"][0]


def test_v8_get_sites_skips_fetch_when_buildings_present() -> None:
    payload = {
        "result": {
            "sites": [
                {
                    "siteInternalIdentifier": 1,
                    "siteTitle": "HQ",
                    "siteExternalIdentifier": "site-ext",
                    "buildings": [
                        {
                            "buildingInternalIdentifier": 10,
                            "buildingTitle": "Tower",
                            "buildingExternalIdentifier": "tower-ext",
                            "levels": [],
                        }
                    ],
                }
            ]
        }
    }

    recording_service = _RecordingBuildingService()
    api_service = _DummyApiServiceWithPayload(payload, recording_service)
    service = V8SiteApiService(api_service)

    sites = service.get_sites()

    assert len(sites) == 1
    assert sites[0].buildings and sites[0].buildings[0].fid == "10"
    assert recording_service.calls == []


def test_v8_get_sites_does_not_fetch_when_buildings_missing() -> None:
    payload = {
        "result": {
            "sites": [
                {
                    "siteInternalIdentifier": 1,
                    "siteTitle": "HQ",
                    "siteExternalIdentifier": "site-ext",
                }
            ]
        }
    }

    recording_service = _RecordingBuildingService()
    api_service = _DummyApiServiceWithPayload(payload, recording_service)
    service = V8SiteApiService(api_service)

    sites = service.get_sites()

    assert len(sites) == 1
    assert sites[0].buildings == []
    assert recording_service.calls == []


def test_v9_list_sites_with_buildings_feature_collection() -> None:
    feature_collection = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "typeCode": "building-outline",
                    "fid": "building-1",
                    "sid": "site-1",
                    "name": "Tower",
                    "extra": {"colour": "red"},
                },
                "geometry": {"type": "Polygon"},
            },
            {
                "type": "Feature",
                "properties": {
                    "typeCode": "site-outline",
                    "fid": "site-1",
                    "name": "HQ",
                    "extra": {"foo": "bar"},
                },
                "geometry": {"type": "Polygon"},
            },
            {
                "type": "Feature",
                "properties": {
                    "typeCode": "building-outline",
                    "fid": "building-2",
                    "sid": "site-1",
                    "name": "Annex",
                    "extra": {"colour": "green"},
                },
                "geometry": {"type": "Polygon"},
            },
            {
                "type": "Feature",
                "properties": {
                    "typeCode": "site-outline",
                    "fid": "site-2",
                    "name": "Remote",
                    "extra": {},
                },
                "geometry": {"type": "Polygon"},
            },
        ],
    }

    service = V9SiteApiService(_DummyApiService())
    sites = service.list_sites_with_buildings(feature_collection)

    assert [site.fid for site in sites] == ["site-1", "site-2"]
    first_site = sites[0]
    assert [building.fid for building in first_site.buildings] == ["building-1", "building-2"]
    assert all("geometry" not in building.extraData for building in first_site.buildings)
    assert "geometry" in feature_collection["features"][0]

    assert len(first_site.buildings) == 2
    assert sites[1].buildings == []
