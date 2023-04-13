from dataclasses import dataclass
from typing import Union

import dacite
from pyflake_client.models.describables.snowflake_describable_interface import (
    ISnowflakeDescribable,
)


@dataclass(frozen=True)
class Tag(ISnowflakeDescribable):
    database_name: Union[str, None]
    schema_name: Union[str, None]
    tag_name: Union[str, None]

    def get_describe_statement(self) -> str:
        query = f"SHOW TAGS LIKE '{self.tag_name}' IN SCHEMA {self.database_name}.{self.schema_name}".upper()
        return query

    def is_procedure(self) -> bool:
        return False

    def get_dacite_config(self) -> Union[dacite.Config, None]:
        return None