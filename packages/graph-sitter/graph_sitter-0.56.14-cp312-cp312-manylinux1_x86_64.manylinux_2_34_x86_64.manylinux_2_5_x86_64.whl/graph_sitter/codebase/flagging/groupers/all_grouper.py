from graph_sitter.codebase.flagging.code_flag import CodeFlag
from graph_sitter.codebase.flagging.group import Group
from graph_sitter.codebase.flagging.groupers.base_grouper import BaseGrouper
from graph_sitter.codebase.flagging.groupers.enums import GroupBy
from graph_sitter.git.repo_operator.repo_operator import RepoOperator


class AllGrouper(BaseGrouper):
    """Group all flags into one group."""

    type: GroupBy = GroupBy.ALL

    @staticmethod
    def create_all_groups(flags: list[CodeFlag], repo_operator: RepoOperator | None = None) -> list[Group]:
        return [Group(group_by=GroupBy.ALL, segment="all", flags=flags)] if flags else []

    @staticmethod
    def create_single_group(flags: list[CodeFlag], segment: str, repo_operator: RepoOperator | None = None) -> Group:
        if segment != "all":
            msg = f"❌ Invalid segment for AllGrouper: {segment}. Only 'all' is a valid segment."
            raise ValueError(msg)
        return Group(group_by=GroupBy.ALL, segment=segment, flags=flags)
