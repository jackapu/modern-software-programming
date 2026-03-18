import json
import logging
from datetime import date

from actual.queries import (
    cents_to_decimal,
    get_categories,
    get_transactions,
)

from server.connection import get_actual
from server.main import mcp

logger = logging.getLogger(__name__)


@mcp.tool()
def get_monthly_budget_summary(month: str) -> str:
    """Get a budget summary for a given month including income, expenses, savings rate, and spending by category.

    Args:
        month: Month in YYYY-MM format (e.g. "2025-03").
    """
    try:
        month_date = date.fromisoformat(month + "-01")
        # End of month
        if month_date.month == 12:
            end_date = date(month_date.year + 1, 1, 1)
        else:
            end_date = date(month_date.year, month_date.month + 1, 1)

        with get_actual() as actual:
            txns = get_transactions(
                actual.session, start_date=month_date, end_date=end_date
            )
            categories = get_categories(actual.session)
            income_cat_ids = {c.id for c in categories if c.is_income}

            total_income = 0
            total_expenses = 0
            spending_by_category: dict[str, int] = {}

            for t in txns:
                amount = t.amount or 0
                cat_id = t.category.id if t.category else None

                if cat_id in income_cat_ids:
                    total_income += amount
                elif amount < 0:
                    cat_name = t.category.name if t.category else "Uncategorized"
                    spending_by_category[cat_name] = (
                        spending_by_category.get(cat_name, 0) + amount
                    )
                    total_expenses += amount

            income_dollars = float(cents_to_decimal(total_income))
            expenses_dollars = float(cents_to_decimal(abs(total_expenses)))
            savings = income_dollars - expenses_dollars
            savings_rate = (savings / income_dollars * 100) if income_dollars > 0 else 0.0

            category_breakdown = [
                {"category": name, "amount": float(cents_to_decimal(abs(total)))}
                for name, total in sorted(
                    spending_by_category.items(), key=lambda x: x[1]
                )
            ]

            return json.dumps(
                {
                    "month": month,
                    "income": income_dollars,
                    "expenses": expenses_dollars,
                    "savings": round(savings, 2),
                    "savings_rate": round(savings_rate, 1),
                    "spending_by_category": category_breakdown,
                }
            )
    except ValueError as e:
        return json.dumps({"error": f"Invalid month format: {e}"})
    except Exception as e:
        logger.error("get_monthly_budget_summary failed: %s", e)
        return json.dumps({"error": str(e)})
