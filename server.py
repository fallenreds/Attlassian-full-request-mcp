"""
Atlassian MCP Server for Sidis Group
Jira + Confluence — full CRUD via FastMCP + httpx
Prefect deployment: horizon.prefect.io/sidis-group/servers
"""

import httpx
from fastmcp import FastMCP
from typing import Optional, Any
import json

# ── Config ────────────────────────────────────────────────────────────────────
ATLASSIAN_BASE = "https://sidis-group.atlassian.net"
EMAIL          = "artur.khobotkov@sidis.group"
API_TOKEN      = "ATATT3xFfGF09vwPt8nNY7B_3bTYsdkLad2QgLRBcqx6_LUcB-ciQvMuj0ydaUHf7nL06tfT_duRi-wt-bxcdDWj8ZmCQyw3dGVOI0GRwraLZxVA-aYznhpmBB3fUe7LrEHxu5Zl11mOQxYs3u7B2yKUe6oy87nhonZnd8Dtomm_eN22X3C_tjQ=073E6106"
CLOUD_ID       = "a4284169-a3d9-436a-8434-a036a3bd917b"

AUTH = (EMAIL, API_TOKEN)
JIRA_BASE  = f"{ATLASSIAN_BASE}/rest/api/3"
CONF_V1    = f"{ATLASSIAN_BASE}/wiki/rest/api"
CONF_V2    = f"{ATLASSIAN_BASE}/wiki/api/v2"

mcp = FastMCP(
    name="sidis-atlassian",
    instructions=(
        "MCP server for Sidis Group Atlassian workspace. "
        "Provides full Jira and Confluence access: issues, projects, spaces, pages, search."
    ),
)

# ── HTTP helpers ───────────────────────────────────────────────────────────────

def _client() -> httpx.Client:
    return httpx.Client(auth=AUTH, headers={"Accept": "application/json"}, timeout=30)

def _get(url: str, params: dict = None) -> Any:
    with _client() as c:
        r = c.get(url, params=params)
        r.raise_for_status()
        return r.json()

def _post(url: str, body: dict) -> Any:
    with _client() as c:
        r = c.post(url, json=body, headers={"Content-Type": "application/json"})
        r.raise_for_status()
        return r.json()

def _put(url: str, body: dict) -> Any:
    with _client() as c:
        r = c.put(url, json=body, headers={"Content-Type": "application/json"})
        r.raise_for_status()
        return r.json()

def _delete(url: str) -> str:
    with _client() as c:
        r = c.delete(url)
        r.raise_for_status()
        return "deleted"

def _patch(url: str, body: dict) -> Any:
    with _client() as c:
        r = c.patch(url, json=body, headers={"Content-Type": "application/json"})
        r.raise_for_status()
        return r.json()

# ══════════════════════════════════════════════════════════════════════════════
#  JIRA TOOLS
# ══════════════════════════════════════════════════════════════════════════════

@mcp.tool
def jira_get_issue(issue_key: str) -> dict:
    """Get full details of a Jira issue by key (e.g. SL-4, ADK-119)."""
    return _get(f"{JIRA_BASE}/issue/{issue_key}")


@mcp.tool
def jira_search(jql: str, max_results: int = 20, fields: str = "summary,status,assignee,priority,description,issuetype,created,updated") -> dict:
    """Search Jira issues using JQL query. Returns list of matching issues."""
    return _get(f"{JIRA_BASE}/search", params={
        "jql": jql,
        "maxResults": max_results,
        "fields": fields,
    })


@mcp.tool
def jira_create_issue(
    project_key: str,
    summary: str,
    issue_type: str = "Task",
    description: str = "",
    assignee_account_id: str = "",
    priority: str = "",
    labels: list[str] = [],
    parent_key: str = "",
) -> dict:
    """
    Create a new Jira issue.
    issue_type: Task | Bug | Story | Epic | Sub-task
    priority: Highest | High | Medium | Low | Lowest
    """
    fields: dict = {
        "project": {"key": project_key},
        "summary": summary,
        "issuetype": {"name": issue_type},
    }
    if description:
        fields["description"] = {
            "type": "doc", "version": 1,
            "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}]
        }
    if assignee_account_id:
        fields["assignee"] = {"accountId": assignee_account_id}
    if priority:
        fields["priority"] = {"name": priority}
    if labels:
        fields["labels"] = labels
    if parent_key:
        fields["parent"] = {"key": parent_key}
    return _post(f"{JIRA_BASE}/issue", {"fields": fields})


@mcp.tool
def jira_update_issue(
    issue_key: str,
    summary: str = "",
    description: str = "",
    assignee_account_id: str = "",
    priority: str = "",
    labels: list[str] = [],
) -> dict:
    """Update fields of an existing Jira issue."""
    fields: dict = {}
    if summary:
        fields["summary"] = summary
    if description:
        fields["description"] = {
            "type": "doc", "version": 1,
            "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}]
        }
    if assignee_account_id:
        fields["assignee"] = {"accountId": assignee_account_id}
    if priority:
        fields["priority"] = {"name": priority}
    if labels:
        fields["labels"] = labels
    with _client() as c:
        r = c.put(
            f"{JIRA_BASE}/issue/{issue_key}",
            json={"fields": fields},
            headers={"Content-Type": "application/json"},
        )
        r.raise_for_status()
        return {"updated": issue_key}


@mcp.tool
def jira_transition_issue(issue_key: str, transition_id: str) -> dict:
    """Transition a Jira issue to a new status using transition ID."""
    return _post(f"{JIRA_BASE}/issue/{issue_key}/transitions", {"transition": {"id": transition_id}})


@mcp.tool
def jira_get_transitions(issue_key: str) -> dict:
    """Get all available workflow transitions for a Jira issue."""
    return _get(f"{JIRA_BASE}/issue/{issue_key}/transitions")


@mcp.tool
def jira_add_comment(issue_key: str, comment: str) -> dict:
    """Add a comment to a Jira issue."""
    body = {
        "body": {
            "type": "doc", "version": 1,
            "content": [{"type": "paragraph", "content": [{"type": "text", "text": comment}]}]
        }
    }
    return _post(f"{JIRA_BASE}/issue/{issue_key}/comment", body)


@mcp.tool
def jira_delete_issue(issue_key: str) -> str:
    """Delete a Jira issue permanently."""
    return _delete(f"{JIRA_BASE}/issue/{issue_key}")


@mcp.tool
def jira_get_projects(max_results: int = 50) -> dict:
    """List all Jira projects in the workspace."""
    return _get(f"{JIRA_BASE}/project/search", params={"maxResults": max_results})


@mcp.tool
def jira_get_issue_types(project_key: str) -> dict:
    """Get all issue types available for a specific Jira project."""
    return _get(f"{JIRA_BASE}/project/{project_key}")


@mcp.tool
def jira_assign_issue(issue_key: str, account_id: str) -> dict:
    """Assign a Jira issue to a user by account ID. Use empty string to unassign."""
    with _client() as c:
        r = c.put(
            f"{JIRA_BASE}/issue/{issue_key}/assignee",
            json={"accountId": account_id if account_id else None},
            headers={"Content-Type": "application/json"},
        )
        r.raise_for_status()
        return {"assigned": issue_key, "to": account_id}


@mcp.tool
def jira_get_user(account_id: str) -> dict:
    """Get Jira user details by account ID."""
    return _get(f"{JIRA_BASE}/user", params={"accountId": account_id})


@mcp.tool
def jira_search_users(query: str) -> dict:
    """Search for Jira users by name or email."""
    return _get(f"{JIRA_BASE}/user/search", params={"query": query, "maxResults": 20})


@mcp.tool
def jira_get_comments(issue_key: str) -> dict:
    """Get all comments for a Jira issue."""
    return _get(f"{JIRA_BASE}/issue/{issue_key}/comment")


@mcp.tool
def jira_create_link(
    inward_issue_key: str,
    outward_issue_key: str,
    link_type: str = "Relates",
) -> dict:
    """
    Create a link between two Jira issues.
    link_type examples: Relates, Blocks, Cloners, Duplicate
    """
    body = {
        "type": {"name": link_type},
        "inwardIssue": {"key": inward_issue_key},
        "outwardIssue": {"key": outward_issue_key},
    }
    return _post(f"{JIRA_BASE}/issueLink", body)


@mcp.tool
def jira_get_sprint_issues(board_id: int, sprint_id: int = 0) -> dict:
    """Get issues from a Jira sprint. If sprint_id=0, fetches active sprint."""
    if sprint_id:
        return _get(f"https://sidis-group.atlassian.net/rest/agile/1.0/sprint/{sprint_id}/issue")
    return _get(f"https://sidis-group.atlassian.net/rest/agile/1.0/board/{board_id}/sprint", params={"state": "active"})


# ══════════════════════════════════════════════════════════════════════════════
#  CONFLUENCE TOOLS
# ══════════════════════════════════════════════════════════════════════════════

@mcp.tool
def confluence_get_spaces(limit: int = 50, space_type: str = "global") -> dict:
    """List all Confluence spaces. type: global | personal"""
    return _get(f"{CONF_V1}/space", params={"limit": limit, "type": space_type})


@mcp.tool
def confluence_create_space(key: str, name: str, description: str = "") -> dict:
    """
    Create a new Confluence space.
    key: short alphanumeric key (e.g. STND, VPAL)
    name: full display name
    """
    body = {
        "key": key,
        "name": name,
    }
    if description:
        body["description"] = {
            "plain": {"value": description, "representation": "plain"}
        }
    return _post(f"{CONF_V1}/space", body)


@mcp.tool
def confluence_get_page(page_id: str) -> dict:
    """Get a Confluence page by ID including body content."""
    return _get(f"{CONF_V2}/pages/{page_id}", params={"body-format": "storage"})


@mcp.tool
def confluence_search(cql: str, limit: int = 20) -> dict:
    """
    Search Confluence using CQL.
    Examples:
      title = \"MVP\" AND space = \"PM\"
      type = page AND space.key = \"MLDS\"
      text ~ \"PDF split\"
    """
    return _get(f"{CONF_V1}/content/search", params={"cql": cql, "limit": limit})


@mcp.tool
def confluence_create_page(
    space_key: str,
    title: str,
    body_markdown: str,
    parent_id: str = "",
) -> dict:
    """
    Create a new Confluence page in a space.
    body_markdown: page content in plain text / wiki markup
    parent_id: optional parent page ID for nesting
    """
    content_body = {
        "storage": {
            "value": f"<p>{body_markdown}</p>",
            "representation": "storage",
        }
    }
    payload: dict = {
        "type": "page",
        "title": title,
        "space": {"key": space_key},
        "body": content_body,
    }
    if parent_id:
        payload["ancestors"] = [{"id": parent_id}]
    return _post(f"{CONF_V1}/content", payload)


@mcp.tool
def confluence_create_page_html(
    space_key: str,
    title: str,
    body_html: str,
    parent_id: str = "",
) -> dict:
    """
    Create a Confluence page with full HTML body (tables, headings, lists).
    Use this for rich formatted pages.
    """
    payload: dict = {
        "type": "page",
        "title": title,
        "space": {"key": space_key},
        "body": {
            "storage": {
                "value": body_html,
                "representation": "storage",
            }
        },
    }
    if parent_id:
        payload["ancestors"] = [{"id": parent_id}]
    return _post(f"{CONF_V1}/content", payload)


@mcp.tool
def confluence_update_page(
    page_id: str,
    title: str,
    body_html: str,
    version_number: int,
) -> dict:
    """
    Update an existing Confluence page.
    version_number: must be current version + 1 (get current from confluence_get_page)
    """
    payload = {
        "version": {"number": version_number},
        "title": title,
        "type": "page",
        "body": {
            "storage": {
                "value": body_html,
                "representation": "storage",
            }
        },
    }
    return _put(f"{CONF_V1}/content/{page_id}", payload)


@mcp.tool
def confluence_delete_page(page_id: str) -> str:
    """Delete a Confluence page by ID."""
    return _delete(f"{CONF_V1}/content/{page_id}")


@mcp.tool
def confluence_get_children(page_id: str) -> dict:
    """Get child pages of a Confluence page."""
    return _get(f"{CONF_V1}/content/{page_id}/child/page")


@mcp.tool
def confluence_add_comment(page_id: str, comment: str) -> dict:
    """Add a footer comment to a Confluence page."""
    payload = {
        "type": "comment",
        "container": {"id": page_id, "type": "page"},
        "body": {
            "storage": {
                "value": f"<p>{comment}</p>",
                "representation": "storage",
            }
        },
    }
    return _post(f"{CONF_V1}/content", payload)


@mcp.tool
def confluence_move_page(page_id: str, new_parent_id: str, new_space_key: str = "") -> dict:
    """
    Move a Confluence page to a new parent (and optionally new space).
    Fetches current page first, then updates ancestors.
    """
    current = _get(f"{CONF_V1}/content/{page_id}", params={"expand": "version,ancestors,space"})
    version = current["version"]["number"] + 1
    title = current["title"]
    body = _get(f"{CONF_V1}/content/{page_id}", params={"expand": "body.storage"})
    body_html = body["body"]["storage"]["value"]
    space_key = new_space_key or current["space"]["key"]

    payload = {
        "version": {"number": version},
        "title": title,
        "type": "page",
        "space": {"key": space_key},
        "ancestors": [{"id": new_parent_id}],
        "body": {
            "storage": {
                "value": body_html,
                "representation": "storage",
            }
        },
    }
    return _put(f"{CONF_V1}/content/{page_id}", payload)


@mcp.tool
def confluence_get_space_homepage(space_key: str) -> dict:
    """Get the homepage page ID of a Confluence space."""
    return _get(f"{CONF_V1}/space/{space_key}", params={"expand": "homepage"})


@mcp.tool
def confluence_get_pages_in_space(space_key: str, limit: int = 50, title_filter: str = "") -> dict:
    """List all pages in a Confluence space, optionally filtered by title."""
    params: dict = {
        "spaceKey": space_key,
        "type": "page",
        "limit": limit,
        "expand": "version,ancestors",
    }
    if title_filter:
        params["title"] = title_filter
    return _get(f"{CONF_V1}/content", params=params)


@mcp.tool
def confluence_attach_file_url(page_id: str, file_url: str, file_name: str) -> dict:
    """Attach a file from a public URL to a Confluence page."""
    import urllib.request
    data = urllib.request.urlopen(file_url).read()
    with _client() as c:
        r = c.post(
            f"{CONF_V1}/content/{page_id}/child/attachment",
            headers={"X-Atlassian-Token": "no-check"},
            files={"file": (file_name, data)},
        )
        r.raise_for_status()
        return r.json()


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRYPOINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8080)
