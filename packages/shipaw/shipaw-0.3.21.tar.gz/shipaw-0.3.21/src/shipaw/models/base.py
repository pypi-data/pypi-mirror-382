from pydantic import AliasGenerator, BaseModel, ConfigDict
from pydantic.alias_generators import to_pascal


class ShipawBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            alias=to_pascal,
        ),
        populate_by_name=True,
        use_enum_values=True,
    )
