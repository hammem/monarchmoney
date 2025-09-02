# Monarch Money

Python library for accessing [Monarch Money](https://www.monarchmoney.com/referral/jtfazovwp9) data.

## 🙏 Acknowledgments

Huge shoutout to [hammem](https://github.com/hammem) for originally starting this project! This is simply a fork of [his hard work](https://github.com/hammem/monarchmoney) to continue development and fix critical authentication issues.

## ✨ Recent Updates

This fork includes **significant improvements** to fix authentication issues:

- **🔧 Fixed 404 Login Errors**: Automatic GraphQL fallback when REST endpoints return 404
- **🛡️ Enhanced Authentication**: Proper headers (device-uuid, Origin) and email OTP support  
- **🔄 Retry Logic**: Exponential backoff for rate limiting and transient errors
- **🧪 Test Suite**: Comprehensive test coverage with 38 passing tests
- **🚀 CI/CD Pipeline**: Automated testing across Python 3.8-3.12

# Installation

## From Source Code

Clone this repository from Git

`git clone https://github.com/keithah/monarchmoney-enhanced.git`

## Via `pip`

`pip install monarchmoney-enhanced`

**Note**: This package is published as `monarchmoney-enhanced` on PyPI to distinguish it from the original `monarchmoney` package while maintaining the same Python import structure.
# Instantiate & Login

There are two ways to use this library: interactive and non-interactive.

## Interactive

If you're using this library in something like iPython or Jupyter, you can run an interactive-login which supports multi-factor authentication:

```python
from monarchmoney import MonarchMoney

mm = MonarchMoney()
await mm.interactive_login()
```
This will prompt you for the email, password and, if needed, the multi-factor token.

## Non-interactive

For a non-interactive session, you'll need to create an instance and login:

```python
from monarchmoney import MonarchMoney

mm = MonarchMoney()
await mm.login(email, password)
```

This may throw a `RequireMFAException`.  If it does, you'll need to get a multi-factor token and call the following method:

```python
from monarchmoney import MonarchMoney, RequireMFAException

mm = MonarchMoney()
try:
        await mm.login(email, password)
except RequireMFAException:
        await mm.multi_factor_authenticate(email, password, multi_factor_code)
```

**Note**: The library automatically detects whether your MFA code is an email OTP (6 digits) or TOTP from an authenticator app, and uses the appropriate authentication field.

Alternatively, you can provide the MFA Secret Key. The MFA Secret Key is found when setting up the MFA in Monarch Money by going to Settings -> Security -> Enable MFA -> and copy the "Two-factor text code". Then provide it in the login() method:
```python
from monarchmoney import MonarchMoney, RequireMFAException

mm = MonarchMoney()
await mm.login(
        email=email,
        password=password,
        save_session=False,
        use_saved_session=False,
        mfa_secret_key=mfa_secret_key,
    )

```

# Use a Saved Session

You can easily save your session for use later on.  While we don't know precisely how long a session lasts, authors of this library have found it can last several months.

```python
from monarchmoney import MonarchMoney, RequireMFAException

mm = MonarchMoney()
mm.interactive_login()

# Save it for later, no more need to login!
mm.save_session()
```

Once you've logged in, you can simply load the saved session to pick up where you left off.

```python
from monarchmoney import MonarchMoney, RequireMFAException

mm = MonarchMoney()
mm.load_session()

# Then, start accessing data!
await mm.get_accounts()
```

# Accessing Data

As of writing this README, the following methods are supported:

## Non-Mutating Methods

- `get_accounts` - gets all the accounts linked to Monarch Money
- `get_me` - gets the current user's profile information (timezone, email, name, MFA status)
- `get_merchants` - gets the list of merchants that have transactions in the account
- `get_account_holdings` - gets all of the securities in a brokerage or similar type of account
- `get_account_type_options` - all account types and their subtypes available in Monarch Money- 
- `get_account_history` - gets all daily account history for the specified account
- `get_institutions` -- gets institutions linked to Monarch Money
- `get_budgets` — all the budgets and the corresponding actual amounts
- `get_goals` - gets all financial goals and targets with progress tracking
- `get_net_worth_history` - gets net worth tracking over time with breakdown by timeframe
- `get_bills` - gets upcoming bills and payments with due dates and amounts
- `get_subscription_details` - gets the Monarch Money account's status (e.g. paid or trial)
- `get_recurring_transactions` - gets the future recurring transactions, including merchant and account details
- `get_transactions_summary` - gets the transaction summary data from the transactions page
- `get_transactions_summary_card` - gets the transaction summary card data with total count information
- `get_transactions` - gets transaction data, defaults to returning the last 100 transactions; can also be searched by date range
- `get_transaction_categories` - gets all of the categories configured in the account
- `get_transaction_category_groups` all category groups configured in the account- 
- `get_transaction_details` - gets detailed transaction data for a single transaction
- `get_transaction_splits` - gets transaction splits for a single transaction
- `get_transaction_tags` - gets all of the tags configured in the account
- `get_cashflow` - gets cashflow data (by category, category group, merchant and a summary)
- `get_cashflow_summary` - gets cashflow summary (income, expense, savings, savings rate)
- `is_accounts_refresh_complete` - gets the status of a running account refresh

## Mutating Methods

- `delete_transaction_category` - deletes a category for transactions
- `delete_transaction_categories` - deletes a list of transaction categories for transactions
- `create_transaction_category` - creates a category for transactions
- `update_transaction_category` - updates an existing transaction category (name, icon, group, rollover settings)
- `request_accounts_refresh` - requests a synchronization / refresh of all accounts linked to Monarch Money. This is a **non-blocking call**. If the user wants to check on the status afterwards, they must call `is_accounts_refresh_complete`.
- `request_accounts_refresh_and_wait` - requests a synchronization / refresh of all accounts linked to Monarch Money. This is a **blocking call** and will not return until the refresh is complete or no longer running.
- `create_transaction` - creates a transaction with the given attributes
- `update_transaction` - modifies one or more attributes for an existing transaction
- `delete_transaction` - deletes a given transaction by the provided transaction id
- `update_transaction_splits` - modifies how a transaction is split (or not)
- `create_transaction_tag` - creates a tag for transactions
- `set_transaction_tags` - sets the tags on a transaction
- `set_budget_amount` - sets a budget's value to the given amount (date allowed, will only apply to month specified by default). A zero amount value will "unset" or "clear" the budget for the given category.
- `create_manual_account` - creates a new manual account
- `delete_account` - deletes an account by the provided account id
- `update_account` - updates settings and/or balance of the provided account id
- `upload_account_balance_history` - uploads account history csv file for a given account

## Session Management Methods

- `validate_session` - validates current session by making a lightweight API call
- `is_session_stale` - checks if session needs validation based on elapsed time  
- `ensure_valid_session` - ensures session is valid, validating if stale
- `get_session_info` - gets session metadata (creation time, last validation, staleness)

## Transaction Rules

Complete transaction rules management:
- `get_transaction_rules` - Get all configured rules with criteria and actions
- `create_transaction_rule` - Create rules with merchant/amount/category/account criteria
- `update_transaction_rule` - Update existing rule criteria and actions
- `delete_transaction_rule` - Delete individual rules
- `reorder_transaction_rules` - Change rule execution order
- `preview_transaction_rule` - Preview rule effects before creating
- `delete_all_transaction_rules` - Delete all rules at once
- `create_categorization_rule` - Helper for simple merchant→category rules

For a complete mapping of GraphQL operations and implementation status, see [GRAPHQL.md](GRAPHQL.md).

# Development & Testing

## Running Tests

This project includes a comprehensive test suite. To run tests:

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=monarchmoney --cov-report=term-missing

# Run specific test categories
pytest -m "api"          # API method tests
pytest -m "auth"         # Authentication tests
pytest -m "unit"         # Unit tests
```

## Test Categories

- **Authentication Tests**: Login, MFA, session management, header validation
- **API Method Tests**: Account/transaction retrieval, GraphQL execution, error handling
- **Integration Tests**: End-to-end functionality and field detection
- **Retry Logic Tests**: Rate limiting, exponential backoff, error handling

## CI/CD

This project uses GitHub Actions for continuous integration:

- **Multi-Python Testing**: Supports Python 3.8 through 3.12
- **Code Quality**: Automated linting with flake8, formatting with black, import sorting with isort
- **Coverage Reporting**: Integrated with Codecov for test coverage tracking

# Contributing

Any and all contributions -- code, documentation, feature requests, feedback -- are welcome!

If you plan to submit up a pull request, you can expect a timely review.  Please ensure you do the following:

  - Configure your IDE or manually run [Black](https://github.com/psf/black) to auto-format the code.
  - Ensure you run the unit tests in this project: `pytest`
    
Actions are configured in this repo to run against all PRs and merges which will block them if a unit test fails or Black throws an error.

# Troubleshooting

## Authentication Issues

If you're experiencing login problems, this fork includes several fixes:

**404 Login Errors**: The library automatically falls back to GraphQL authentication if REST endpoints return 404.

**403 Forbidden Errors**: Ensure you're using the latest version which includes proper browser headers (device-uuid, Origin, User-Agent).

**MFA Problems**: The library automatically detects email OTP vs authenticator app codes:
- 6-digit numeric codes are treated as email OTP
- Other formats are treated as TOTP from authenticator apps

**Rate Limiting**: Built-in retry logic with exponential backoff handles temporary rate limits automatically.

# FAQ

**How do I use this API if I login to Monarch via Google?**

If you currently use Google or 'Continue with Google' to access your Monarch account, you'll need to set a password to leverage this API.  You can set a password on your Monarch account by going to your [security settings](https://app.monarchmoney.com/settings/security).  

Don't forget to use a password unique to your Monarch account and to enable multi-factor authentication!

**What's different in this fork?**

This fork fixes several critical authentication issues that were causing 404 and 403 errors:
- Added GraphQL fallback for authentication endpoints
- Fixed HTTP headers to match browser requests
- Improved MFA field detection (email OTP vs TOTP)
- Added comprehensive retry logic
- Includes full test suite and CI/CD pipeline

