import json
import logging
from datetime import date

from actual.queries import (
    Transactions,
    cents_to_decimal,
    create_transaction,
    decimal_to_cents,
)

from server.connection import get_actual
from server.main import mcp

logger = logging.getLogger(__name__)


@mcp.tool()
def create_transaction_tool(
    date_str: str,
    account: str,
    amount: float,
    payee: str | None = None,
    category: str | None = None,
    notes: str | None = None,
) -> str:
    """Create a new transaction in Actual Budget.

    Args:
        date_str: Transaction date in YYYY-MM-DD format.
        account: Account name to add the transaction to.
        amount: Amount in dollars (negative for expenses, positive for income).
        payee: Payee name.
        category: Category name.
        notes: Optional notes for the transaction.
    """
    try:
        txn_date = date.fromisoformat(date_str)

        with get_actual() as actual:
            txn = create_transaction(
                actual.session,
                date=txn_date,
                account=account,
                amount=amount,
                payee=payee,
                category=category,
                notes=notes or "",
            )
            actual.commit()
            return json.dumps(
                {
                    "id": txn.id,
                    "date": str(txn.date),
                    "account": account,
                    "amount": amount,
                    "payee": payee,
                    "category": category,
                    "notes": notes,
                    "message": "Transaction created successfully",
                }
            )
    except ValueError as e:
        return json.dumps({"error": f"Invalid date format: {e}"})
    except Exception as e:
        logger.error("create_transaction failed: %s", e)
        return json.dumps({"error": str(e)})


@mcp.tool()
def update_transaction(
    transaction_id: str,
    amount: float | None = None,
    payee: str | None = None,
    category: str | None = None,
    notes: str | None = None,
    cleared: bool | None = None,
) -> str:
    """Update an existing transaction.

    Args:
        transaction_id: The ID of the transaction to update.
        amount: New amount in dollars (negative for expenses, positive for income).
        payee: New payee name.
        category: New category name.
        notes: New notes.
        cleared: Whether the transaction is cleared.
    """
    try:
        with get_actual() as actual:
            txn = actual.session.query(Transactions).filter_by(id=transaction_id).first()
            if not txn:
                return json.dumps({"error": f"Transaction '{transaction_id}' not found"})

            if amount is not None:
                txn.amount = decimal_to_cents(amount)
            if notes is not None:
                txn.notes = notes
            if cleared is not None:
                txn.cleared = cleared
            if payee is not None:
                from actual.queries import get_or_create_payee

                payee_obj = get_or_create_payee(actual.session, payee)
                txn.payee = payee_obj
            if category is not None:
                from actual.queries import get_or_create_category

                cat_obj = get_or_create_category(actual.session, category)
                txn.category = cat_obj

            actual.commit()
            return json.dumps(
                {
                    "id": txn.id,
                    "date": str(txn.date),
                    "amount": float(cents_to_decimal(txn.amount or 0)),
                    "notes": txn.notes,
                    "cleared": bool(txn.cleared),
                    "message": "Transaction updated successfully",
                }
            )
    except Exception as e:
        logger.error("update_transaction failed: %s", e)
        return json.dumps({"error": str(e)})
