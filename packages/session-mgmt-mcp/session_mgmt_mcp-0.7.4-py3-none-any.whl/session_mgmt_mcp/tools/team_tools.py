#!/usr/bin/env python3
"""Team collaboration tools for session-mgmt-mcp.

Following crackerjack architecture patterns for knowledge sharing,
team coordination, and collaborative development workflows.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from fastmcp import FastMCP

logger = logging.getLogger(__name__)


async def _create_team_impl(
    team_id: str, name: str, description: str, owner_id: str
) -> str:
    """Create a new team for knowledge sharing."""
    try:
        from session_mgmt_mcp.team_knowledge import TeamKnowledgeManager

        manager = TeamKnowledgeManager()
        await manager.create_team(
            team_id=team_id,
            name=name,
            description=description,
            owner_id=owner_id,
        )

        return f"✅ Team created successfully: {name}"

    except ImportError:
        logger.warning("Team knowledge system not available")
        return "❌ Team collaboration features not available. Install optional dependencies."
    except Exception as e:
        logger.exception(f"Team creation failed: {e}")
        return f"❌ Failed to create team: {e!s}"


def _format_search_result(result: dict[str, Any], index: int) -> str:
    """Format a single search result."""
    output = f"**{index}.** "

    # Add metadata
    if result.get("team_id"):
        output += f"[{result['team_id']}] "
    if result.get("author"):
        output += f"by {result['author']} "
    if result.get("timestamp"):
        output += f"({result['timestamp']}) "

    # Add content preview
    content = result.get("content", "")
    output += f"\n{content[:200]}...\n"

    # Add tags if available
    if result.get("tags"):
        output += f"🏷️ Tags: {', '.join(result['tags'])}\n"

    # Add voting info if available
    if result.get("votes"):
        votes = result["votes"]
        output += f"👍 Votes: {votes} "

    output += "\n"
    return output


def _format_search_scope(team_id: str | None, project_id: str | None) -> str:
    """Format the search scope string."""
    search_scope = "team knowledge"
    if team_id:
        search_scope += f" (team: {team_id})"
    if project_id:
        search_scope += f" (project: {project_id})"
    return search_scope


async def _search_team_knowledge_impl(
    query: str,
    user_id: str,
    team_id: str | None = None,
    project_id: str | None = None,
    tags: list[str] | None = None,
    limit: int = 20,
) -> str:
    """Search team reflections with access control."""
    try:
        from session_mgmt_mcp.team_knowledge import TeamKnowledgeManager

        manager = TeamKnowledgeManager()
        results = await manager.search_team_reflections(
            query=query,
            user_id=user_id,
            team_id=team_id,
            project_id=project_id,
            tags=tags,
            limit=limit,
        )

        if not results:
            search_scope = _format_search_scope(team_id, project_id)
            return f"🔍 No results found in {search_scope} for: {query}"

        output = f"🔍 **{len(results)} team knowledge results** for '{query}'\n\n"

        for i, result in enumerate(results, 1):
            output += _format_search_result(result, i)

        return output

    except ImportError:
        logger.warning("Team knowledge system not available")
        return "❌ Team collaboration features not available. Install optional dependencies."
    except Exception as e:
        logger.exception(f"Team knowledge search failed: {e}")
        return f"❌ Team knowledge search failed: {e!s}"


async def _get_team_statistics_impl(team_id: str, user_id: str) -> str:
    """Get team statistics and activity."""
    try:
        from session_mgmt_mcp.team_knowledge import TeamKnowledgeManager

        manager = TeamKnowledgeManager()
        stats = await manager.get_team_stats(team_id=team_id, user_id=user_id)

        if not stats:
            return "❌ Failed to retrieve team statistics"

        return _format_team_statistics(team_id, stats)

    except ImportError:
        logger.warning("Team knowledge system not available")
        return "❌ Team collaboration features not available. Install optional dependencies."
    except Exception as e:
        logger.exception(f"Error getting team statistics: {e}")
        return f"❌ Error retrieving team statistics: {e}"


def _format_team_statistics(team_id: str, stats: dict[str, Any]) -> str:
    """Format team statistics for display."""
    output = f"📊 **Team Statistics: {team_id}**\n\n"

    output += _format_basic_stats(stats)
    output += _format_activity_stats(stats)
    output += _format_contributor_stats(stats)
    output += _format_popular_tags(stats)

    return output


def _format_basic_stats(stats: dict[str, Any]) -> str:
    """Format basic team statistics."""
    return (
        f"**Members**: {stats.get('member_count', 0)}\n"
        f"**Reflections**: {stats.get('reflection_count', 0)}\n"
        f"**Projects**: {stats.get('project_count', 0)}\n"
        f"**Total Votes**: {stats.get('total_votes', 0)}\n\n"
    )


def _format_activity_stats(stats: dict[str, Any]) -> str:
    """Format recent activity statistics."""
    if not stats.get("recent_activity"):
        return ""

    output = "**Recent Activity**:\n"
    for activity in stats["recent_activity"][:5]:
        output += (
            f"- {activity.get('timestamp', '')}: {activity.get('description', '')}\n"
        )
    return output


def _format_contributor_stats(stats: dict[str, Any]) -> str:
    """Format top contributors statistics."""
    if not stats.get("top_contributors"):
        return ""

    output = "\n**Top Contributors**:\n"
    for contributor in stats["top_contributors"][:5]:
        username = contributor.get("username", "")
        contributions = contributor.get("contributions", 0)
        output += f"- {username}: {contributions} contributions\n"
    return output


def _format_popular_tags(stats: dict[str, Any]) -> str:
    """Format popular tags statistics."""
    if not stats.get("popular_tags"):
        return ""

    tags = ", ".join(stats["popular_tags"][:10])
    return f"\n**Popular Tags**: {tags}\n"


async def _vote_on_reflection_impl(
    reflection_id: str,
    user_id: str,
    vote_delta: int = 1,
) -> str:
    """Vote on a team reflection (upvote/downvote)."""
    try:
        from session_mgmt_mcp.team_knowledge import TeamKnowledgeManager

        manager = TeamKnowledgeManager()
        result = await manager.vote_reflection(
            reflection_id=reflection_id,
            user_id=user_id,
            vote_delta=vote_delta,
        )

        if result:
            output = "✅ Reflection voted on successfully\n"
            output += "📊 Vote recorded\n"
            return output
        return "❌ Failed to vote on reflection"

    except ImportError:
        logger.warning("Team knowledge system not available")
        return "❌ Team collaboration features not available. Install optional dependencies."
    except ValueError as e:
        return f"❌ Vote failed: {e!s}"
    except Exception as e:
        logger.exception(f"Voting failed: {e}")
        return f"❌ Failed to vote on reflection: {e!s}"


def register_team_tools(mcp: FastMCP) -> None:
    """Register all team collaboration MCP tools.

    Args:
        mcp: FastMCP server instance

    """

    @mcp.tool()
    async def create_team(
        team_id: str, name: str, description: str, owner_id: str
    ) -> str:
        """Create a new team for knowledge sharing."""
        return await _create_team_impl(team_id, name, description, owner_id)

    @mcp.tool()
    async def search_team_knowledge(
        query: str,
        user_id: str,
        team_id: str | None = None,
        project_id: str | None = None,
        tags: list[str] | None = None,
        limit: int = 20,
    ) -> str:
        """Search team reflections with access control."""
        return await _search_team_knowledge_impl(
            query, user_id, team_id, project_id, tags, limit
        )

    @mcp.tool()
    async def get_team_statistics(team_id: str, user_id: str) -> str:
        """Get team statistics and activity."""
        return await _get_team_statistics_impl(team_id, user_id)

    @mcp.tool()
    async def vote_on_reflection(
        reflection_id: str,
        user_id: str,
        vote_delta: int = 1,
    ) -> str:
        """Vote on a team reflection (upvote/downvote)."""
        return await _vote_on_reflection_impl(reflection_id, user_id, vote_delta)

    # Additional team utility tools
