#!/usr/bin/env python3
"""
Comprehensive Test Suite for Monarch Money Enhanced
Tests all major functions to validate they work before release.
"""

import asyncio
import json
import sys
from datetime import datetime, date, timedelta
from monarchmoney import MonarchMoney

class TestResults:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
        self.cleanup_items = []

    def add_pass(self, test_name, details=""):
        self.passed.append(f"✅ {test_name}" + (f" - {details}" if details else ""))

    def add_fail(self, test_name, error):
        self.failed.append(f"❌ {test_name} - {str(error)[:100]}")

    def add_warning(self, test_name, details):
        self.warnings.append(f"⚠️  {test_name} - {details}")

    def add_cleanup(self, item_type, item_id):
        self.cleanup_items.append((item_type, item_id))

    def print_summary(self):
        print("\n" + "="*80)
        print("🎯 COMPREHENSIVE TEST SUITE RESULTS")
        print("="*80)
        
        print(f"\n📊 SUMMARY:")
        print(f"   ✅ Passed: {len(self.passed)}")
        print(f"   ❌ Failed: {len(self.failed)}")
        print(f"   ⚠️  Warnings: {len(self.warnings)}")
        
        if self.passed:
            print(f"\n✅ PASSED TESTS ({len(self.passed)}):")
            for test in self.passed:
                print(f"   {test}")
        
        if self.failed:
            print(f"\n❌ FAILED TESTS ({len(self.failed)}):")
            for test in self.failed:
                print(f"   {test}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   {warning}")
        
        total_tests = len(self.passed) + len(self.failed)
        if total_tests > 0:
            success_rate = (len(self.passed) / total_tests) * 100
            print(f"\n🎯 Overall Success Rate: {success_rate:.1f}% ({len(self.passed)}/{total_tests})")
            
            if success_rate >= 95:
                print("🎉 EXCELLENT! Ready for release!")
                return True
            elif success_rate >= 85:
                print("✨ GOOD! Minor issues to address before release")
                return False
            else:
                print("🚨 NEEDS WORK! Major issues must be fixed before release")
                return False
        return False

async def comprehensive_test_suite():
    """Run comprehensive tests on all major MonarchMoney functions."""
    
    print("🧪 COMPREHENSIVE MONARCH MONEY ENHANCED TEST SUITE")
    print("="*80)
    print("Testing all major functions before release...")
    
    results = TestResults()
    mm = MonarchMoney()
    
    # Load session
    try:
        mm.load_session("/Users/keith/.monarchmoney_session")
        results.add_pass("Session Loading", "Successfully loaded existing session")
    except Exception as e:
        results.add_fail("Session Loading", e)
        print("❌ Cannot continue without valid session")
        return results

    # Test 1: Basic Account Operations
    print("\n1️⃣ Testing Basic Account Operations...")
    
    try:
        me = await mm.get_me()
        username = me.get("username", "Unknown")
        results.add_pass("get_me", f"Connected as {username}")
    except Exception as e:
        results.add_fail("get_me", e)
    
    try:
        accounts = await mm.get_accounts()
        account_count = len(accounts.get("accounts", []))
        results.add_pass("get_accounts", f"Retrieved {account_count} accounts")
    except Exception as e:
        results.add_fail("get_accounts", e)
    
    try:
        account_balances = await mm.get_recent_account_balances()
        balance_count = len(account_balances.get("accounts", []))
        results.add_pass("get_recent_account_balances", f"Got balances for {balance_count} accounts")
    except Exception as e:
        results.add_fail("get_recent_account_balances", e)

    # Test 2: Transaction Operations  
    print("\n2️⃣ Testing Transaction Operations...")
    
    try:
        transactions = await mm.get_transactions(limit=10)
        trans_count = len(transactions.get("allTransactions", {}).get("results", []))
        results.add_pass("get_transactions", f"Retrieved {trans_count} transactions")
    except Exception as e:
        results.add_fail("get_transactions", e)
    
    try:
        categories = await mm.get_transaction_categories()
        cat_count = len(categories.get("categories", []))
        results.add_pass("get_transaction_categories", f"Retrieved {cat_count} categories")
    except Exception as e:
        results.add_fail("get_transaction_categories", e)
    
    try:
        rules = await mm.get_transaction_rules()
        rule_count = len(rules.get("transactionRules", []))
        results.add_pass("get_transaction_rules", f"Retrieved {rule_count} rules")
    except Exception as e:
        results.add_fail("get_transaction_rules", e)

    # Test 3: Financial Analytics (Previously Broken)
    print("\n3️⃣ Testing Financial Analytics...")
    
    try:
        net_worth = await mm.get_net_worth_history()
        data_points = len(net_worth.get("aggregateSnapshots", []))
        results.add_pass("get_net_worth_history", f"Retrieved {data_points} data points")
    except Exception as e:
        results.add_fail("get_net_worth_history", e)
    
    try:
        investment_perf = await mm.get_investment_performance()
        has_portfolio = "portfolio" in investment_perf
        results.add_pass("get_investment_performance", f"Portfolio data available: {has_portfolio}")
    except Exception as e:
        results.add_fail("get_investment_performance", e)
    
    try:
        cashflow = await mm.get_cashflow(
            start_date="2024-08-01", 
            end_date="2024-08-31"
        )
        has_summary = "summary" in cashflow
        results.add_pass("get_cashflow", f"Cashflow summary available: {has_summary}")
    except Exception as e:
        results.add_fail("get_cashflow", e)

    # Test 4: Rule Creation (Previously Broken)
    print("\n4️⃣ Testing Transaction Rule Creation...")
    
    # Find a category for testing
    test_category_id = None
    try:
        categories = await mm.get_transaction_categories()
        for cat in categories.get("categories", []):
            if cat.get("name", "").lower() == "miscellaneous":
                test_category_id = cat["id"]
                break
    except:
        pass
    
    if not test_category_id:
        results.add_warning("Rule Testing", "No suitable category found for rule testing")
    else:
        # Test amount rule creation
        try:
            rule_result = await mm.create_amount_rule(
                amount=999.99,
                operator="eq",
                is_expense=False,
                category_name="Miscellaneous",
                apply_to_existing=False
            )
            
            if "transactionRule" in rule_result:
                rule_id = rule_result["transactionRule"]["id"]
                results.add_pass("create_amount_rule", f"Created rule {rule_id}")
                results.add_cleanup("rule", rule_id)
            else:
                results.add_fail("create_amount_rule", "No transactionRule in response")
                
        except Exception as e:
            results.add_fail("create_amount_rule", e)
        
        # Test categorization rule creation
        try:
            rule_result = await mm.create_categorization_rule(
                merchant_contains="TEST COMPREHENSIVE SUITE",
                category_name="Miscellaneous",
                apply_to_existing=False
            )
            
            if "transactionRule" in rule_result:
                rule_id = rule_result["transactionRule"]["id"]
                results.add_pass("create_categorization_rule", f"Created rule {rule_id}")
                results.add_cleanup("rule", rule_id)
            else:
                results.add_fail("create_categorization_rule", "No transactionRule in response")
                
        except Exception as e:
            results.add_fail("create_categorization_rule", e)
        
        # Test apply rules to existing (limit to 1 to avoid impact)
        try:
            apply_result = await mm.apply_rules_to_existing_transactions(limit=1)
            processed = apply_result.get("processed", 0)
            results.add_pass("apply_rules_to_existing_transactions", f"Processed {processed} rules")
        except Exception as e:
            results.add_fail("apply_rules_to_existing_transactions", e)

    # Test 5: Budget Operations
    print("\n5️⃣ Testing Budget Operations...")
    
    try:
        budgets = await mm.get_budgets()
        budget_count = len(budgets.get("budgets", []))
        results.add_pass("get_budgets", f"Retrieved {budget_count} budgets")
    except Exception as e:
        results.add_fail("get_budgets", e)

    # Test 6: Institution Operations
    print("\n6️⃣ Testing Institution Operations...")
    
    try:
        institutions = await mm.get_institutions()
        inst_count = len(institutions.get("institutions", []))
        results.add_pass("get_institutions", f"Retrieved {inst_count} institutions")
    except Exception as e:
        results.add_fail("get_institutions", e)

    # Test 7: Subscription Details
    print("\n7️⃣ Testing Subscription Operations...")
    
    try:
        subscription = await mm.get_subscription_details()
        has_plan = "plan" in subscription
        results.add_pass("get_subscription_details", f"Plan info available: {has_plan}")
    except Exception as e:
        results.add_fail("get_subscription_details", e)

    # Test 8: Advanced Analytics
    print("\n8️⃣ Testing Advanced Analytics...")
    
    try:
        start_date = (date.today() - timedelta(days=30)).isoformat()
        end_date = date.today().isoformat()
        snapshots = await mm.get_aggregate_snapshots(
            start_date=start_date,
            end_date=end_date
        )
        snap_count = len(snapshots.get("aggregateSnapshots", []))
        results.add_pass("get_aggregate_snapshots", f"Retrieved {snap_count} snapshots")
    except Exception as e:
        results.add_fail("get_aggregate_snapshots", e)

    # Cleanup Phase
    print("\n🧹 Cleaning up test data...")
    cleanup_count = 0
    for item_type, item_id in results.cleanup_items:
        try:
            if item_type == "rule":
                await mm.delete_transaction_rule(item_id)
                cleanup_count += 1
                print(f"   🗑️  Deleted test rule {item_id}")
        except Exception as e:
            results.add_warning("Cleanup", f"Could not delete {item_type} {item_id}: {str(e)[:50]}")
    
    if cleanup_count > 0:
        results.add_pass("Cleanup", f"Successfully cleaned up {cleanup_count} test items")

    return results

async def main():
    """Main test runner."""
    results = await comprehensive_test_suite()
    ready_for_release = results.print_summary()
    
    if ready_for_release:
        print("\n🚀 READY FOR RELEASE! All major functions working correctly.")
        sys.exit(0)
    else:
        print("\n🛑 NOT READY FOR RELEASE! Please fix issues before proceeding.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())