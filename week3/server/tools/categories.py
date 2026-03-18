import json
import logging

from actual.queries import (
    create_category,
    get_categories,
    get_category_groups,
)

from server.connection import get_actual
from server.main import mcp

logger = logging.getLogger(__name__)


@mcp.tool()
def list_categories() -> str:
    """List all category groups and their categories."""
    try:
        with get_actual() as actual:
            groups = get_category_groups(actual.session)
            cats = get_categories(actual.session)

            # Build group -> categories mapping
            group_map: dict[str, list[dict]] = {}
            group_names: dict[str, str] = {}
            for g in groups:
                group_map[g.id] = []
                group_names[g.id] = g.name

            for c in cats:
                group_id = c.cat_group
                if group_id in group_map:
                    group_map[group_id].append(
                        {
                            "id": c.id,
                            "name": c.name,
                            "is_income": bool(c.is_income),
                            "hidden": bool(c.hidden),
                        }
                    )

            result = []
            for g in groups:
                result.append(
                    {
                        "id": g.id,
                        "name": g.name,
                        "is_income": bool(g.is_income),
                        "categories": group_map.get(g.id, []),
                    }
                )

            return json.dumps({"category_groups": result})
    except Exception as e:
        logger.error("list_categories failed: %s", e)
        return json.dumps({"error": str(e)})


@mcp.tool()
def create_category_tool(name: str, group_name: str) -> str:
    """Create a new category in a category group. Creates the group if it doesn't exist.

    Args:
        name: Name of the new category.
        group_name: Name of the category group to add this category to.
    """
    try:
        with get_actual() as actual:
            cat = create_category(actual.session, name=name, group_name=group_name)
            actual.commit()
            return json.dumps(
                {
                    "id": cat.id,
                    "name": cat.name,
                    "group": group_name,
                    "message": f"Category '{name}' created in group '{group_name}'",
                }
            )
    except Exception as e:
        logger.error("create_category failed: %s", e)
        return json.dumps({"error": str(e)})
