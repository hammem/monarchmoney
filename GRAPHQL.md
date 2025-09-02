# GraphQL API Documentation

This document maps the MonarchMoney GraphQL API operations and their implementation status in monarchmoney-enhanced.

## Implementation Status

| Operation | Method | Status | Description |
|-----------|--------|--------|-------------|
| **Accounts** | | | |
| `GetAccounts` | `get_accounts()` | ✅ | Get all accounts with balances, types, and institution info |
| `GetAccountTypeOptions` | `get_account_type_options()` | ✅ | Get available account types and subtypes |
| `GetAccountRecentBalances` | `get_recent_account_balances()` | ✅ | Get recent balance history for accounts |
| `GetSnapshotsByAccountType` | `get_account_snapshots_by_type()` | ✅ | Get balance snapshots grouped by account type |
| `GetAggregateSnapshots` | `get_aggregate_snapshots()` | ✅ | Get aggregated balance snapshots across timeframes |
| `AccountDetails_getAccount` | `get_account_history()` | ✅ | Get detailed account info with transaction history |
| `Web_CreateManualAccount` | `create_manual_account()` | ✅ | Create a new manual account |
| `Common_UpdateAccount` | `update_account()` | ✅ | Update account details |
| `Common_DeleteAccount` | `delete_account()` | ✅ | Delete an account |
| `Common_ForceRefreshAccountsMutation` | `request_accounts_refresh()` | ✅ | Request account data refresh |
| `ForceRefreshAccountsQuery` | `is_accounts_refresh_complete()` | ✅ | Check refresh completion status |
| **User & Profile** | | | |
| `Common_GetMe` | `get_me()` | ✅ | Get user profile information |
| `GetMerchants` | `get_merchants()` | ✅ | Get merchant data with transaction counts |
| `GetSubscriptionDetails` | `get_subscription_details()` | ✅ | Get account subscription status |
| **Transactions** | | | |
| `GetTransactionsPage` | `get_transactions_summary()` | ✅ | Get transaction summary with aggregates |
| `Web_GetTransactionsSummaryCard` | `get_transactions_summary_card()` | ✅ | Get transaction summary card with total count |
| `GetTransactionsList` | `get_transactions()` | ✅ | Get paginated transaction list with filtering |
| `GetTransactionDrawer` | `get_transaction_details()` | ✅ | Get detailed single transaction data |
| `TransactionSplitQuery` | `get_transaction_splits()` | ✅ | Get transaction splits |
| `Common_CreateTransactionMutation` | `create_transaction()` | ✅ | Create a new transaction |
| `Common_DeleteTransactionMutation` | `delete_transaction()` | ✅ | Delete a transaction |
| `Common_SplitTransactionMutation` | `update_transaction_splits()` | ✅ | Update transaction splits |
| `Web_TransactionDrawerUpdateTransaction` | `update_transaction()` | ✅ | Update transaction details |
| **Transaction Rules** | | | |
| `GetTransactionRules` | `get_transaction_rules()` | ⚠️ | Get all transaction rules (EXPERIMENTAL - API endpoints unverified) |
| `CreateTransactionRule` | `create_transaction_rule()` | ⚠️ | Create new transaction rule (EXPERIMENTAL - API endpoints unverified) |
| `UpdateTransactionRule` | `update_transaction_rule()` | ⚠️ | Update existing transaction rule (EXPERIMENTAL - API endpoints unverified) |
| `DeleteTransactionRule` | `delete_transaction_rule()` | ⚠️ | Delete transaction rule (EXPERIMENTAL - API endpoints unverified) |
| `ReorderTransactionRules` | `reorder_transaction_rules()` | ⚠️ | Reorder rule priority (EXPERIMENTAL - API endpoints unverified) |
| **Categories & Tags** | | | |
| `GetCategories` | `get_transaction_categories()` | ✅ | Get all transaction categories |
| `Web_DeleteCategory` | `delete_transaction_category()` | ✅ | Delete a transaction category |
| `ManageGetCategoryGroups` | `get_transaction_category_groups()` | ✅ | Get category groups |
| `Web_CreateCategory` | `create_transaction_category()` | ✅ | Create new transaction category |
| `Web_UpdateCategory` | `update_transaction_category()` | ✅ | Update existing transaction category |
| `Common_CreateTransactionTag` | `create_transaction_tag()` | ✅ | Create new transaction tag |
| `GetHouseholdTransactionTags` | `get_transaction_tags()` | ✅ | Get all transaction tags |
| `Web_SetTransactionTags` | `set_transaction_tags()` | ✅ | Set tags on transactions |
| **Holdings & Investments** | | | |
| `Web_GetHoldings` | `get_account_holdings()` | ✅ | Get investment holdings for account |
| `SecuritySearch` | `get_security_details()` | ✅ | Search for security by ticker |
| `Common_CreateManualHolding` | `create_manual_holding()` | ✅ | Create manual investment holding |
| `Common_DeleteHolding` | `delete_manual_holding()` | ✅ | Delete investment holding |
| **Budgets & Cash Flow** | | | |
| `Common_GetJointPlanningData` | `get_budgets()` | ✅ | Get budget data and planning information |
| `Web_GetCashFlowPage` | `get_cashflow()` / `get_cashflow_summary()` | ✅ | Get cash flow data and summaries |
| `Common_UpdateBudgetItem` | `set_budget_amount()` | ✅ | Update budget amounts |
| **Institutions** | | | |
| `Web_GetInstitutionSettings` | `get_institutions()` | ✅ | Get linked financial institutions |
| **Recurring Transactions** | | | |
| Not specified | `get_recurring_transactions()` | ✅ | Get future recurring transactions |
| **Utility/Upload** | | | |
| Not specified | `upload_account_balance_history()` | ✅ | Upload historical balance data |
| **Goals & Financial Planning** | | | |
| `GetGoals` | `get_goals()` | ✅ | Get financial goals and targets with progress tracking |
| **Net Worth & Analytics** | | | |
| `GetNetWorthHistory` | `get_net_worth_history()` | ✅ | Get net worth tracking over time with breakdown |
| **Bills & Payments** | | | |
| `GetBills` | `get_bills()` | ✅ | Get upcoming bills and payments with due dates |

## Not Yet Implemented

Based on analysis of hammem's repository and common financial API patterns, these operations may be available but not yet implemented:

| Operation | Potential Method | Priority | Description |
|-----------|------------------|----------|-------------|
| `CreateGoal` | `create_goal()` | Medium | Create new financial goal |
| `UpdateGoal` | `update_goal()` | Medium | Update existing goal |
| `DeleteGoal` | `delete_goal()` | Medium | Delete financial goal |
| `GetInsights` | `get_insights()` | Low | Financial insights and recommendations |
| `GetNotifications` | `get_notifications()` | Low | Account notifications and alerts |
| `GetSettings` | `get_settings()` | Low | User account settings |
| `UpdateSettings` | `update_settings()` | Low | Update user preferences |
| `GetInvestmentPerformance` | `get_investment_performance()` | Medium | Investment performance metrics |
| `GetNetWorthHistory` | `get_net_worth_history()` | Medium | Net worth tracking over time |
| `GetCreditScore` | `get_credit_score()` | Low | Credit score monitoring |
| `GetBills` | `get_bills()` | Medium | Upcoming bills and payments |

## Authentication Operations

| Operation | Method | Status | Description |
|-----------|--------|--------|-------------|
| REST `/auth/login/` | `_login_user()` | ✅ | Primary login with 404 fallback |
| REST `/auth/multi/` | `_multi_factor_authenticate()` | ✅ | MFA with 404 fallback |
| GraphQL Login | `_login_user_graphql()` | ✅ | GraphQL login fallback |
| GraphQL MFA | `_mfa_graphql()` | ✅ | GraphQL MFA fallback |

## Implemented Features

### Core Functionality
- **Account Management**: Full CRUD operations for accounts, including manual accounts
- **Transaction Management**: Complete transaction lifecycle (create, read, update, delete, split)
- **Transaction Rules**: Automated categorization and processing rules
- **Investment Holdings**: Manual holdings management for investment accounts
- **Categories & Tags**: Organization and labeling of transactions
- **Budgets**: Budget tracking and amount management
- **Cash Flow**: Income/expense analysis and summaries
- **Authentication**: Robust login with MFA support and session management

### Advanced Features
- **GraphQL Fallback**: Automatic fallback when REST endpoints return 404
- **Retry Logic**: Exponential backoff for rate limiting and transient errors
- **Session Persistence**: Save/load authentication sessions
- **Filtering**: Advanced transaction filtering by amount, type, date, categories
- **SSL Security**: Proper certificate verification for secure connections

### Data Export
- **JSON Format**: All methods return structured JSON data
- **Comprehensive Fields**: Full field coverage for accounts, transactions, budgets
- **Relationship Data**: Linked data (accounts ↔ institutions, transactions ↔ categories)

## Usage Examples

### Basic Usage
```python
from monarchmoney import MonarchMoney

mm = MonarchMoney()
await mm.login(email, password)

# Get account data
accounts = await mm.get_accounts()
transactions = await mm.get_transactions(limit=50)
categories = await mm.get_transaction_categories()
```

### Transaction Rules
```python
# Create categorization rule
await mm.create_categorization_rule(
    merchant_contains="Sentris Network LLC",
    category_name="Shared - Telco"
)

# Get all rules
rules = await mm.get_transaction_rules()
```

### Investment Holdings
```python
# Add manual holding
await mm.create_manual_holding_by_ticker(
    account_id="123",
    ticker="AAPL", 
    quantity=10
)

# Get holdings
holdings = await mm.get_account_holdings(account_id=123)
```

### Budgets & Cash Flow
```python
# Get budget data
budgets = await mm.get_budgets(start_date="2025-01-01", end_date="2025-12-31")

# Get cash flow summary
cashflow = await mm.get_cashflow_summary(start_date="2025-01-01", end_date="2025-03-31")
```

## Contributing

When adding new GraphQL operations:

1. **Follow Naming Conventions**: Use descriptive method names matching the operation purpose
2. **Add Documentation**: Include docstrings with parameter descriptions and return types
3. **Create Tests**: Add unit tests with mock response data
4. **Update This Document**: Add the new operation to the appropriate table
5. **Update CHANGELOG**: Document the new functionality

## References

- [Original MonarchMoney Repository](https://github.com/hammem/monarchmoney)
- [MonarchMoney Web Application](https://app.monarchmoney.com)
- [GraphQL Specification](https://graphql.org/learn/)