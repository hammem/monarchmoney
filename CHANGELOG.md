# Changelog

All notable changes to this project will be documented in this file.

## [0.3.1] - 2025-09-02

### ✨ Added
- **Financial Insights**: Added `get_insights()` for financial recommendations and analysis
- **Notifications**: Added `get_notifications()` for account alerts and notifications
- **Credit Monitoring**: Added `get_credit_score()` for credit score tracking and history
- **User Settings**: Added `get_settings()` and `update_settings()` for account preferences
  - Timezone, currency, date format configuration
  - Notification preferences (email, push, SMS)
  - Privacy settings management

### 📚 Documentation
- **Complete API Coverage**: Now implements 50+ GraphQL operations
- **Updated Documentation**: GRAPHQL.md reflects comprehensive API implementation

## [0.3.0] - 2025-09-02

### ✨ Added
- **Goal Management**: Added complete financial goal management functionality
  - `create_goal()` - Create new financial goals with target amounts and dates
  - `update_goal()` - Update existing goal details (name, amount, date, description)
  - `delete_goal()` - Delete financial goals
- **Investment Analytics**: Added `get_investment_performance()` for detailed investment tracking
  - Portfolio performance metrics (total value, gains, percentages)
  - Account-level performance breakdown
  - Individual holding performance data
  - Date range filtering and account filtering
- **Advanced Transaction Rules**: Enhanced transaction rules with complete action support
  - **Amount-based rules**: `create_amount_rule()` for exact amount matching (e.g., $115.32)
  - **Combined conditions**: `create_combined_rule()` for merchant + amount rules (e.g., "Airbnb + amount > $200")
  - **Tax deductible marking**: `create_tax_deductible_rule()` for automatic tax categorization
  - **Ignore from everything**: `create_ignore_rule()` for hiding transactions from all reports
  - **Retroactive application**: `apply_rules_to_existing_transactions()` to process all existing transactions
- **Advanced Rule Actions**: Full support for all MonarchMoney rule actions
  - Transaction hiding from reports (`set_hide_from_reports_action`)
  - Review status assignment (`review_status_action`)
  - User review assignment (`needs_review_by_user_action`)
  - Goal linking (`link_goal_action`)
  - Notification triggers (`send_notification_action`)

### 📚 Documentation
- **GraphQL Documentation**: Updated GRAPHQL.md with new goal and investment operations
- **API Coverage**: Now covers 45+ GraphQL operations with comprehensive goal and investment management

## [0.2.5] - 2025-09-02

### 🔧 Fixed
- **Required Headers**: Added missing MonarchMoney API headers for transaction rules functionality
  - Added `x-cio-client-platform: web`
  - Added `x-cio-site-id: 2598be4aa410159198b2`
  - Added `x-gist-user-anonymous: false`
  - These headers are required for transaction rules API access

## [0.2.4] - 2025-09-02

### 🔧 Fixed
- **Transaction Rules GraphQL**: Fixed GraphQL fragment structure to match MonarchMoney's actual API
  - Added missing `PayloadErrorFields` fragment to all mutation queries
  - Updated `get_transaction_rules()` to use correct `TransactionRuleFields` fragment structure
  - Improved error handling for GraphQL responses with detailed error messages
  - Fixed query structure to exactly match HAR file analysis

## [0.2.3] - 2025-09-02

### 🔧 Fixed
- **Transaction Rules API**: Fixed all transaction rules functionality with correct GraphQL operations from HAR analysis
  - Updated `create_transaction_rule()` to use `Common_CreateTransactionRuleMutationV2`
  - Updated `update_transaction_rule()` to use `Common_UpdateTransactionRuleMutationV2` 
  - Updated `delete_transaction_rule()` to use `Common_DeleteTransactionRule`
  - Updated `reorder_transaction_rules()` to use `Web_UpdateRuleOrderMutation`
  - Fixed parameter structure to match MonarchMoney's actual API requirements
  - Added `apply_to_existing_transactions` parameter for retroactive rule application

### ✨ Added
- **Transaction Rules Preview**: Added `preview_transaction_rule()` to preview rule effects before creating
- **Bulk Rule Management**: Added `delete_all_transaction_rules()` for removing all rules at once

### 📚 Documentation
- **Transaction Rules**: Updated documentation to reflect working functionality, removed experimental warnings
- **GraphQL Documentation**: Updated GRAPHQL.md with correct operation names and implementation status

## [0.2.2] - 2025-09-02

### 🔧 Fixed
- **Mutable Default Arguments**: Fixed get_transactions method parameters to use None instead of empty lists, preventing shared state issues ([PR #147](https://github.com/hammem/monarchmoney/pull/147))

### ✨ Added  
- **Transaction Amount Filtering**: Added `is_credit` and `abs_amount_range` parameters to `get_transactions()` for filtering by credit/debit and amount ranges ([PR #148](https://github.com/hammem/monarchmoney/pull/148))
- **Holdings Management**: Added `get_security_details()`, `create_manual_holding()`, `create_manual_holding_by_ticker()`, and `delete_manual_holding()` methods for programmatic investment holdings management ([PR #151](https://github.com/hammem/monarchmoney/pull/151))
- **Transaction Rules**: Added comprehensive transaction rules functionality:
  - `get_transaction_rules()` - Get all configured rules
  - `create_transaction_rule()` - Create new rules with conditions and actions
  - `update_transaction_rule()` - Update existing rules
  - `delete_transaction_rule()` - Delete rules
  - `reorder_transaction_rules()` - Change rule priority order
  - `create_categorization_rule()` - Helper method for merchant-based categorization rules
- **Transaction Summary Card**: Added `get_transactions_summary_card()` method to retrieve transaction summary card data with total count information ([PR #140](https://github.com/hammem/monarchmoney/pull/140))

### 📚 Documentation
- **GraphQL API Mapping**: Created comprehensive GRAPHQL.md documenting all 40+ implemented operations with usage examples and contribution guidelines

## [Unreleased] - 2025-09-02

### ✨ Added
- **Session Validation**: Enhanced session management with validation and refresh mechanisms
  - `validate_session()` - validates session with lightweight API call
  - `is_session_stale()` - checks if validation is needed based on time
  - `ensure_valid_session()` - automatically validates stale sessions
  - `get_session_info()` - provides session metadata and status
- **Goals Management**: Added `get_goals()` method to retrieve financial goals and targets with progress tracking
- **Net Worth Tracking**: Added `get_net_worth_history()` method for net worth analysis over time with customizable timeframes
- **Bills Management**: Added `get_bills()` method to retrieve upcoming bills and payments with due dates
- **Category Updates**: Added `update_transaction_category()` method to update category names, icons, and settings without deletion

### 🔧 Enhanced
- **Session Format**: Enhanced session files with metadata (creation time, validation timestamps, version)
- **Backward Compatibility**: Maintains support for legacy session file formats

## [0.2.1] - 2025-09-02

**Package Renamed**: Published as `monarchmoney-enhanced` on PyPI to distinguish from the original `monarchmoney` package while maintaining the same import structure.

**Repository Renamed**: GitHub repository renamed to match PyPI package name.

## [0.2.0] - 2025-09-02

### 🔧 Fixed
- **Authentication 404 Errors**: Added automatic GraphQL fallback when REST endpoints return 404
- **Authentication 403 Errors**: Fixed missing HTTP headers (device-uuid, Origin, User-Agent)
- **MFA Field Detection**: Automatic detection of email OTP vs TOTP based on code format
- **GraphQL Client Bug**: Fixed execute_async parameter order compatibility
- **Token Management**: Fixed set_token() method to properly update Authorization header
- **Authentication Validation**: Improved _get_graphql_client() to properly check for authentication

### ✨ Added
- **Retry Logic**: Exponential backoff with jitter for rate limiting and transient errors
- **Test Suite**: Comprehensive pytest-based test coverage (38 tests)
  - Authentication tests (login, MFA, GraphQL fallback)
  - API method tests (accounts, transactions, error handling)
  - Integration tests (end-to-end functionality)
  - Session management tests
  - Retry logic tests
- **CI/CD Pipeline**: GitHub Actions workflow with multi-Python version testing (3.8-3.12)
- **Code Quality**: Automated linting (flake8), formatting (black), and import sorting (isort)
- **Coverage Reporting**: Integrated with Codecov for test coverage tracking
- **User Profile API**: New `get_me()` method to retrieve user information (timezone, email, name, MFA status)
- **Merchants API**: New `get_merchants()` method to retrieve merchant data with transaction counts

### 🛡️ Enhanced
- **Browser Compatibility**: Updated User-Agent to match Chrome browser
- **Header Management**: Added required headers for Monarch Money API compatibility
- **Error Handling**: Improved error messages and exception handling
- **Session Management**: Better session file handling and validation

### 📚 Documentation
- Updated README with troubleshooting section
- Added development and testing guidelines
- Documented new features and fixes
- Added this CHANGELOG

## Previous Versions

See the original repository's commit history for changes prior to this fork.