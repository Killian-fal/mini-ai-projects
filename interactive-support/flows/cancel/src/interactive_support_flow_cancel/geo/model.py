from pydantic import BaseModel, ConfigDict

from interactive_support_flow_api.model.question import Location


class Address(BaseModel):
    """
    An address found by `geocode`.

    label: the address as the Base Adresse Nationale writes it, e.g. "18 Rue Oberkampf 75011 Paris".
    """

    model_config = ConfigDict(frozen=True)

    label: str
    location: Location
