# Actual Budget MCP Server

An MCP (Model Context Protocol) server that connects to your [Actual Budget](https://actualbudget.org/) instance, exposing 7 tools for managing accounts, transactions, budgets, and categories.

## Prerequisites

- Python 3.12+
- A running [Actual Budget](https://actualbudget.org/) server instance
- Poetry for dependency management

## Installation

```bash
cd week3
poetry install
```

## Configuration

Copy `.env.example` to `.env` and fill in your Actual Budget server details:

```bash
cp .env.example .env
```

| Variable | Description | Required |
|----------|-------------|----------|
| `ACTUAL_SERVER_URL` | URL of your Actual Budget server | Yes |
| `ACTUAL_PASSWORD` | Server password | Yes |
| `ACTUAL_FILE` | Budget file name or ID | Yes |
| `ACTUAL_ENCRYPTION_PASSWORD` | End-to-end encryption password (if enabled) | No |

## Running

```bash
poetry run actual-budget-mcp
```

The server uses STDIO transport and waits for MCP protocol messages on stdin.

## Claude Desktop Configuration

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "actual-budget": {
      "command": "poetry",
      "args": ["run", "actual-budget-mcp"],
      "cwd": "/path/to/week3",
      "env": {
        "ACTUAL_SERVER_URL": "http://localhost:5006",
        "ACTUAL_PASSWORD": "your-password",
        "ACTUAL_FILE": "your-budget-file"
      }
    }
  }
}
```

## Tools

### Accounts

**`list_accounts`** — List all accounts with balances.
- `include_closed` (bool): Include closed accounts. Default: false.
- `off_budget` (bool): Include off-budget accounts. Default: false.

**`get_transactions_tool`** — Query transactions with filters.
- `start_date` (string): Start date, YYYY-MM-DD.
- `end_date` (string): End date, YYYY-MM-DD.
- `account` (string): Filter by account name.
- `category` (string): Filter by category name.
- `payee` (string): Filter by payee name.
- `limit` (int): Max results (default 50, max 500).

### Budgets

**`get_monthly_budget_summary`** — Income, expenses, savings rate, and spending by category for a month.
- `month` (string): Month in YYYY-MM format.

### Transactions

**`create_transaction_tool`** — Create a new transaction.
- `date_str` (string): Date, YYYY-MM-DD.
- `account` (string): Account name.
- `amount` (float): Amount in dollars (negative = expense).
- `payee` (string): Payee name.
- `category` (string): Category name.
- `notes` (string): Optional notes.

**`update_transaction`** — Update an existing transaction.
- `transaction_id` (string): Transaction ID.
- `amount` (float): New amount in dollars.
- `payee` (string): New payee.
- `category` (string): New category.
- `notes` (string): New notes.
- `cleared` (bool): Mark as cleared.

### Categories

**`list_categories`** — List all category groups and categories.

**`create_category_tool`** — Create a new category in a group.
- `name` (string): Category name.
- `group_name` (string): Group to add the category to (created if missing).

## Example Flow

1. **List accounts** to see what's available
2. **Get transactions** for the current month to review spending
3. **Get monthly budget summary** to see income vs expenses
4. **Create a transaction** to log a new purchase
5. **List categories** to see available categories for organizing

## Architecture

- **STDIO transport** — communicates via stdin/stdout using the MCP protocol
- **Fresh connection per call** — each tool opens its own connection to Actual Budget for robustness
- **Amounts in dollars** — all tool inputs/outputs use decimal dollars (actualpy stores cents internally)
- **Logging to stderr** — keeps stdout clean for the MCP protocol
