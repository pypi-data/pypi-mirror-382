from dataclasses import dataclass

from dataclasses_json import dataclass_json

from graph_sitter.codebase.flagging.code_flag import CodeFlag
from graph_sitter.codebase.flagging.groupers.enums import GroupBy

DEFAULT_GROUP_ID = 0


@dataclass_json
@dataclass
class Group:
    group_by: GroupBy
    segment: str
    flags: list[CodeFlag] | None = None
    id: int = DEFAULT_GROUP_ID
