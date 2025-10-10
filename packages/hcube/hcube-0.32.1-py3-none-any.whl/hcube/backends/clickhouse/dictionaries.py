import hashlib
import json
from dataclasses import dataclass
from typing import List, Optional, Union

from hcube.api.models.cube import Cube
from hcube.api.models.dimensions import IntDimension, StringDimension
from hcube.backends.clickhouse.data_sources import DataSource


@dataclass
class DictionaryAttr:
    name: str
    type: str
    expression: Optional[str] = None
    null_value: str = "NULL"
    injective: bool = False

    def definition_sql(self):
        expression = f"EXPRESSION {self.expression}" if self.expression else ""
        default = f"DEFAULT {self.null_value}" if self.null_value else ""
        type_part = f"Nullable({self.type})" if self.null_value == "NULL" else self.type
        return (
            f"{self.name} {type_part} {default} {expression} "
            f"{'INJECTIVE' if self.injective else ''}"
        )


class DictionaryDefinition:
    def __init__(
        self,
        name: str,
        source: DataSource,
        key: Union[str, List[str]],
        layout: str,
        attrs: [DictionaryAttr],
        lifetime_min: int = 600,
        lifetime_max: int = 720,
    ):
        self.name = name
        # Internally store keys as a list; single key is converted for backward compatibility.
        self.keys: List[str] = [key] if isinstance(key, str) else list(key)
        self.source = source
        self.layout = layout
        self.attrs = attrs
        self.lifetime_min = lifetime_min
        self.lifetime_max = lifetime_max

    def definition_sql(self, database=None):
        db_part = f"{database}." if database else ""
        # Columns: always auto-define all key columns as UInt64
        columns = [f"{k} UInt64" for k in self.keys]
        columns.extend([attr.definition_sql() for attr in self.attrs])
        cols_sql = ",\n".join(columns)
        # primary key
        if len(self.keys) == 1:
            pk_sql = f"PRIMARY KEY {self.keys[0]}"
        else:
            joined = ", ".join(self.keys)
            pk_sql = f"PRIMARY KEY ({joined})"
        return (
            f"CREATE DICTIONARY IF NOT EXISTS {db_part}{self.name} ("
            f"{cols_sql}"
            f") "
            f"{pk_sql} "
            f"{self.source.definition_sql()} "
            f"LAYOUT ({self.layout.upper()}()) "
            f"LIFETIME(MIN {self.lifetime_min} MAX {self.lifetime_max}) "
            f"COMMENT 'blake2:{self.checksum}'"
        )

    @property
    def checksum(self):
        data = {
            "name": self.name,
            "key": self.keys,
            "source": self.source.definition_sql(),
            "layout": self.layout,
            "attrs": [attr.definition_sql() for attr in self.attrs],
            "lifetime_min": self.lifetime_min,
            "lifetime_max": self.lifetime_max,
        }
        return hashlib.blake2b(json.dumps(data).encode("utf-8"), digest_size=32).hexdigest()

    def drop_sql(self, database=None):
        db_part = f"{database}." if database else ""
        return f"DROP DICTIONARY IF EXISTS {db_part}{self.name} SYNC"

    def create_cube(self) -> Cube:
        class Out(Cube):
            class Clickhouse:
                source = self

        # Key columns are numeric (UInt64)
        for k in self.keys:
            setattr(Out, k, IntDimension())
        for attr in self.attrs:
            setattr(Out, attr.name, StringDimension())

        Out._process_attrs()
        return Out
