# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import List

from pyflake_client.models.enums.column_type import ColumnType
from pyflake_client.models.executables.procedure_arg import ProcedureArg
from pyflake_client.models.executables.snowflake_executable_interface import (
    ISnowflakeExecutable,
)


@dataclass(frozen=True)
class AnonymousProcedure(ISnowflakeExecutable):
    procedure_name: str
    procedure_definition: str
    procedure_args: List[ProcedureArg]

    def get_call_statement(self) -> str:
        proc_args = ""
        for arg in sorted(self.procedure_args, key=lambda x: x.positional_order):
            if arg.data_type == ColumnType.VARCHAR:
                proc_args += f"'{str(arg.value)}',"
            elif arg.data_type == ColumnType.INTEGER:
                proc_args += f"{int(arg.value)},"
            else:
                raise ValueError(f"ColumnType ${arg.data_type} is not mapped")
        test = f"{self.procedure_definition}\ncall {self.procedure_name}({proc_args.rstrip(',')});"
        return test
