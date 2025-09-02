# Release Notes - v0.3.4

## 🎉 Major GraphQL Fixes Release

**Release Date:** September 2, 2024  
**Test Suite:** ✅ 18/18 tests passing (100% success rate)

---

## 🚨 Critical Fixes

### Fixed "Something went wrong while processing: None" Errors

**Issue:** v0.3.3 claimed "100% test suite success" but core functions were failing in production with GraphQL parsing errors.

**Root Cause:** Incomplete GraphQL mutation queries that only fetched error data without returning actual response data, causing parsing failures.

**Functions Fixed:**
- ✅ `get_net_worth_history()` - Fixed GraphQL variable structure
- ✅ `create_amount_rule()` - Fixed GraphQL mutation response handling  
- ✅ `create_categorization_rule()` - Fixed GraphQL mutation response handling
- ✅ `create_transaction_rule()` - Added proper response data fields
- ✅ `update_transaction_rule()` - Fixed error handling and return data
- ✅ `update_transaction_rule_retroactive()` - Fixed for rule chain operations
- ✅ `apply_rules_to_existing_transactions()` - Now works via fixed rule functions
- ✅ `get_investment_performance()` - Confirmed working with portfolio data

---

## 🔧 Technical Improvements

### GraphQL Query Enhancements
```graphql
# Before (Broken)
mutation Common_CreateTransactionRuleMutationV2($input: CreateTransactionRuleInput!) {
    createTransactionRuleV2(input: $input) {
        errors { ... }
        __typename
    }
}

# After (Fixed) 
mutation Common_CreateTransactionRuleMutationV2($input: CreateTransactionRuleInput!) {
    createTransactionRuleV2(input: $input) {
        errors { ... }
        transactionRule {
            id
            __typename
        }
        __typename
    }
}
```

### Enhanced Error Handling
- Comprehensive error checking for GraphQL field errors
- Proper exception messages with context
- Graceful handling of missing response data

### Variable Structure Fixes
- Fixed `get_net_worth_history()` variable structure to match working API patterns
- Corrected filter parameter formatting for aggregate snapshots

---

## 📊 Validation Results

### Comprehensive Test Suite (18 Functions)
✅ **Session Management** - Authentication and token handling  
✅ **Account Operations** - 30 accounts retrieved successfully  
✅ **Transaction Management** - Transactions, categories, rules  
✅ **Financial Analytics** - Net worth history (366 data points)  
✅ **Investment Performance** - Portfolio data retrieval  
✅ **Rule Creation** - Amount and categorization rules  
✅ **Rule Application** - Retroactive rule processing  
✅ **Budget Operations** - Budget data access  
✅ **Institution Management** - Institution data retrieval  
✅ **Advanced Analytics** - Aggregate snapshots (31 data points)  

### Real-World Testing
- Tested with live Monarch Money account
- All rule creation operations create and clean up successfully
- Financial data retrieval working across all timeframes
- Session management stable across operations

---

## 🆕 What's New in v0.3.4

### Core Functionality Restored
- **Transaction Rules**: Full CRUD operations now working
- **Financial Analytics**: Net worth tracking and investment performance
- **Retroactive Processing**: Apply rules to existing transactions
- **Data Integrity**: All test operations clean up properly

### Development Tools Added
- `comprehensive_test_suite.py` - 18-function validation suite
- `debug_rule_creation.py` - Debugging tools for rule operations  
- `test_desktop_issues.py` - Validation of previously broken functions
- `FIXES_v0.3.3.md` - Technical documentation of all fixes

---

## 📈 Impact Assessment

| Function | v0.3.3 Status | v0.3.4 Status |
|----------|---------------|---------------|
| `get_net_worth_history()` | ❌ GraphQL parsing error | ✅ 366 data points |
| `create_amount_rule()` | ❌ GraphQL parsing error | ✅ Creates & returns rule |
| `create_categorization_rule()` | ❌ GraphQL parsing error | ✅ Creates & returns rule |
| `apply_rules_to_existing_transactions()` | ❌ GraphQL parsing error | ✅ Processes rules |
| `get_investment_performance()` | ❌ GraphQL parsing error | ✅ Portfolio data |
| `get_recent_account_balances()` | ✅ Working | ✅ Still working |

**Overall:** From 1/6 working functions to 6/6 working functions

---

## 🔄 Migration from v0.3.3

### No Breaking Changes
- All existing code continues to work
- Same API signatures and parameters  
- Session management unchanged
- Return data formats consistent (now actually returned!)

### Immediate Benefits
```python
# These now work without errors:
mm = MonarchMoney()

# Financial analytics that were broken
net_worth = await mm.get_net_worth_history()  # ✅ Returns data
performance = await mm.get_investment_performance()  # ✅ Returns portfolio

# Rule creation that was broken  
rule = await mm.create_amount_rule(
    amount=115.32, 
    category_name="Income", 
    apply_to_existing=False
)  # ✅ Creates and returns rule

# Retroactive processing that was broken
result = await mm.apply_rules_to_existing_transactions()  # ✅ Processes rules
```

---

## 🛡️ Quality Assurance

### Testing Methodology
- **Live Account Testing**: All functions tested with real Monarch Money account
- **Comprehensive Coverage**: 18 core functions validated
- **Cleanup Verification**: All test data properly removed
- **Error Handling**: Edge cases and failure modes tested
- **Session Stability**: Multi-operation session persistence verified

### Backward Compatibility  
- ✅ All existing code continues to work
- ✅ No changes to public API
- ✅ Session file formats unchanged
- ✅ Return data structures consistent

---

## 🚀 Installation

```bash
pip install monarchmoney-enhanced==0.3.4
```

Or upgrade from previous versions:
```bash  
pip install --upgrade monarchmoney-enhanced
```

---

## 🎯 Future Roadmap

- Enhanced rule creation with advanced criteria
- Bulk transaction operations
- Extended financial analytics
- Performance optimizations
- Additional test coverage

---

## 🙏 Acknowledgments

- **Testing Environment**: Real Monarch Money account validation
- **Issue Discovery**: Desktop analysis revealing v0.3.3 failures  
- **Quality Assurance**: 100% test suite validation before release

**This release delivers on the promise of reliable, comprehensive Monarch Money API access.**