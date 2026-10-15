"""
Finds a French address with the geocoding API of IGN's Géoplateforme (Base Adresse Nationale): free, no key, 50 requests per second per IP.
"""

from typing import Literal
from urllib.parse import urlencode
from urllib.request import urlopen

from pydantic import BaseModel

from interactive_support_flow_api.model.question import Location
from interactive_support_flow_cancel.geo.model import Address

_URL = "https://data.geopf.fr/geocodage/search"
_TIMEOUT_SECONDS = 5
# measured on the API: an existing address scores above 0.89, a wrong city around 0.49
_MIN_SCORE = 0.7


class _Point(BaseModel):
    coordinates: tuple[float, float]  # GeoJSON order: longitude, latitude


class _Properties(BaseModel):
    label: str
    score: float
    type: str


class _Feature(BaseModel):
    geometry: _Point
    properties: _Properties


class _Results(BaseModel):
    type: Literal["FeatureCollection"]
    features: list[_Feature]


def geocode(address: str) -> Address | None:
    """
    The French address `address` designates, down to the house number. None when there is none.
    """
    if not (3 <= len(address) <= 200 and address[0].isalnum()):
        return None  # the API refuses to search it
    return _search(address)


def _search(address: str) -> Address | None:
    query = urlencode({"q": address, "limit": 1})
    with urlopen(f"{_URL}?{query}", timeout=_TIMEOUT_SECONDS) as response:
        results = _Results.model_validate_json(response.read())

    match results.features:
        case [best] if (
            best.properties.type == "housenumber"
            and best.properties.score >= _MIN_SCORE
        ):
            longitude, latitude = best.geometry.coordinates
            return Address(
                label=best.properties.label,
                location=Location(latitude=latitude, longitude=longitude),
            )
        case _:
            return None
