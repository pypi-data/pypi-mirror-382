# import libs
from pydantic import (
    BaseModel,
    Field,
    ConfigDict
)
# local
from .components import Component


class ComponentThermoDBSource(BaseModel):
    '''
    ThermoDB source containing component thermodb.

    Attributes
    ----------
    component: Component
        Component thermodb
    source: str
        Path to the thermodb file
    '''
    component: Component
    source: str

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow"
    )
