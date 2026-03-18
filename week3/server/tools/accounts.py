import json
import logging
from datetime import date

from actual.queries import (
    cents_to_decimal,
    get_account,
    get_accounts,
    get_transactions,
)

from server.connection import get_actual
from server.main import mcp

logger = logging.getLogger(__name__)

MAX_TRANSACTIONS = 500


@mcp.tool()
def list_accounts(include_closed: bool = False, off_budget: bool = False) -> str:
    """List all Actual Budget accounts with their current balances.

    Args:
        include_closed: Include closed accounts in the results.
        off_budget: Include off-budget (tracking) accounts.
    """
    try:
        with get_actual() as actual:
            closed = None if include_closed else False
            off_budget_filter = None if off_budget else False
            accounts = get_accounts(
                actual.session, closed=closed, off_budget=off_budget_filter
            )
            result = []
            for acct in accounts:
                balance = acct.balance
                result.append(
                    {
                        "id": acct.id,
                        "name": acct.name,
                        "balance": float(balance),
                        "off_budget": bool(acct.offbudget),
                        "closed": bool(acct.closed),
                    }
                )
            return json.dumps({"accounts": result, "count": len(result)})
    except Exception as e:
        logger.error("list_accounts failed: %s", e)
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_transactions_tool(
    start_date: str | None = None,
    end_date: str | None = None,
    account: str | None = None,
    category: str | None = None,
    payee: str | None = None,
    limit: int = 50,
) -> str:
    """Query transactions with optional filters.

    Args:
        start_date: Start date in YYYY-MM-DD format (inclusive).
        end_date: End date in YYYY-MM-DD format (inclusive).
        account: Filter by account name.
        category: Filter by category name.
        payee: Filter by payee name.
        limit: Maximum number of transactions to return (default 50, max 500).
    """
    try:
        limit = min(max(1, limit), MAX_TRANSACTIONS)
        start = date.fromisoformat(start_date) if start_date else None
        end = date.fromisoformat(end_date) if end_date else None

        with get_actual() as actual:
            txns = get_transactions(
                actual.session,
                start_date=start,
                end_date=end,
                account=account,
                category=category,
                payee=payee,
            )
            results = []
            for t in txns[:limit]:
                results.append(
                    {
                        "id": t.id,
                        "date": str(t.date),
                        "account": t.account.name if t.account else None,
                        "payee": t.payee.name if t.payee else None,
                        "category": t.category.name if t.category else None,
                        "amount": float(cents_to_decimal(t.amount or 0)),
                        "notes": t.notes,
                        "cleared": bool(t.cleared),
                    }
                )
            return json.dumps(
                {
                    "transactions": results,
                    "count": len(results),
                    "total_available": len(txns),
                }
            )
    except ValueError as e:
        return json.dumps({"error": f"Invalid date format: {e}"})
    except Exception as e:
        logger.error("get_transactions failed: %s", e)
        return json.dumps({"error": str(e)})
