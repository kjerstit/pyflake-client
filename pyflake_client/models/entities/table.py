"""table"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Union

import dacite

from pyflake_client.models.entities.column import Column as ColumnEntity
from pyflake_client.models.entities.snowflake_entity_interface import ISnowflakeEntity
from pyflake_client.models.entities.classification_tag import ClassificationTag


@dataclass(frozen=True)
class Table(ISnowflakeEntity):
    """Table"""

    name: str
    database_name: str
    schema_name: str
    kind: str
    columns: List[ColumnEntity]
    comment: str
    tags: List[ClassificationTag]
    rows: int
    owner: str
    retention_time: int
    created_on: datetime

    @classmethod
    def deserialize(cls, data: Dict[str, Any], config: Union[dacite.Config, None]) -> Table:
        columns = [ColumnEntity.deserialize(c, None) for c in data["columns"]]
        tags = [ClassificationTag.deserialize(t, None) for t in data["tags"]]
        return dacite.from_dict(Table, {
            "name": data["name"],
            "database_name": data["database_name"],
            "schema_name": data["schema_name"],
            "kind": data["kind"],
            "columns": columns,
            "comment": data["comment"],
            "tags": tags,
            "rows": data["rows"],
            "owner": data["owner"],
            "retention_time": data["retention_time"],
            "created_on": data["created_on"],
        }, config)