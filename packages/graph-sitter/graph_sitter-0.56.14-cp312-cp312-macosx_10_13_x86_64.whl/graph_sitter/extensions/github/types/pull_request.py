from typing import Literal

from pydantic import BaseModel

from .base import GitHubRepository, GitHubUser


class PullRequestRef(BaseModel):
    label: str
    ref: str
    sha: str
    user: GitHubUser
    repo: GitHubRepository


class PullRequestLinks(BaseModel):
    self: dict
    html: dict
    issue: dict
    comments: dict
    review_comments: dict
    review_comment: dict
    commits: dict
    statuses: dict


class Label(BaseModel):
    id: int
    node_id: str
    url: str
    name: str
    description: str | None = None
    color: str
    default: bool


class PullRequest(BaseModel):
    url: str
    id: int
    node_id: str
    html_url: str
    diff_url: str
    patch_url: str
    issue_url: str
    number: int
    state: str
    locked: bool
    title: str
    user: GitHubUser
    body: str | None
    created_at: str
    updated_at: str
    closed_at: str | None
    merged_at: str | None
    merge_commit_sha: str | None
    assignee: GitHubUser | None
    assignees: list[GitHubUser]
    requested_reviewers: list[GitHubUser]
    requested_teams: list[dict]
    labels: list[Label]
    milestone: dict | None
    draft: bool
    head: PullRequestRef
    base: PullRequestRef
    _links: PullRequestLinks
    author_association: str
    auto_merge: dict | None
    active_lock_reason: str | None
    merged: bool
    mergeable: bool | None
    rebaseable: bool | None
    mergeable_state: str
    merged_by: GitHubUser | None
    comments: int
    review_comments: int
    maintainer_can_modify: bool
    commits: int
    additions: int
    deletions: int
    changed_files: int


class PullRequestLabeledEvent(BaseModel):
    action: Literal["labeled"]
    number: int
    pull_request: PullRequest
    label: Label
    repository: dict  # Simplified for now
    sender: dict  # Simplified for now
