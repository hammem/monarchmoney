#!/usr/bin/env python3
"""
Test script for the fixed Monarch Money functions.
Uses existing session from .mm/mm_session.pickle
"""

import asyncio
import json
import sys
from datetime import datetime
from monarchmoney import MonarchMoney

# Session file path
SESSION_FILE = ".mm/mm_session.pickle"

async def test_fixed_functions():
    """Test all the functions we just fixed."""
    print("🧪 Testing Fixed Monarch Money Functions")
    print("=" * 50)
    
    # Initialize with existing session
    mm = MonarchMoney(session_file=SESSION_FILE)
    
    try:
        # Test 1: Net Worth History (Fixed GraphQL structure)
        print("\n1️⃣ Testing get_net_worth_history()...")
        try:
            net_worth = await mm.get_net_worth_history()
            print(f"   ✅ SUCCESS! Got {len(net_worth.get('aggregateSnapshots', []))} data points")
        except Exception as e:
            print(f"   ❌ FAILED: {str(e)[:100]}")

        # Test 2: Investment Performance (Should work now)
        print("\n2️⃣ Testing get_investment_performance()...")
        try:
            performance = await mm.get_investment_performance()
            print(f"   ✅ SUCCESS! Got portfolio data with keys: {list(performance.keys())}")
        except Exception as e:
            print(f"   ❌ FAILED: {str(e)[:100]}")

        # Test 3: Create Amount Rule (Fixed GraphQL return data)
        print("\n3️⃣ Testing create_amount_rule()...")
        try:
            rule = await mm.create_amount_rule(
                amount=115.32,
                operator="eq",
                is_expense=False,
                category_name="Miscellaneous",
                apply_to_existing=False
            )
            rule_id = rule.get("transactionRule", {}).get("id")
            print(f"   ✅ SUCCESS! Created rule with ID: {rule_id}")
            
            # Clean up - delete the test rule
            if rule_id:
                await mm.delete_transaction_rule(rule_id)
                print(f"   🗑️  Cleaned up test rule")
                
        except Exception as e:
            print(f"   ❌ FAILED: {str(e)[:100]}")

        # Test 4: Create Categorization Rule (Fixed GraphQL return data)
        print("\n4️⃣ Testing create_categorization_rule()...")
        try:
            rule = await mm.create_categorization_rule(
                merchant_contains="TEST MERCHANT v0.3.3",
                category_name="Miscellaneous",
                apply_to_existing=False
            )
            rule_id = rule.get("transactionRule", {}).get("id")
            print(f"   ✅ SUCCESS! Created categorization rule with ID: {rule_id}")
            
            # Clean up - delete the test rule
            if rule_id:
                await mm.delete_transaction_rule(rule_id)
                print(f"   🗑️  Cleaned up test rule")
                
        except Exception as e:
            print(f"   ❌ FAILED: {str(e)[:100]}")

        # Test 5: Apply Rules to Existing Transactions (Fixed chain)
        print("\n5️⃣ Testing apply_rules_to_existing_transactions()...")
        try:
            # Just test with limit=1 to avoid affecting too many transactions
            result = await mm.apply_rules_to_existing_transactions(limit=1)
            processed = result.get("processed", 0)
            applied = result.get("applied", 0)
            print(f"   ✅ SUCCESS! Processed {processed} rules, applied {applied}")
        except Exception as e:
            print(f"   ❌ FAILED: {str(e)[:100]}")

        # Test 6: Get Recent Account Balances (Should still work)
        print("\n6️⃣ Testing get_recent_account_balances()...")
        try:
            balances = await mm.get_recent_account_balances()
            account_count = len(balances.get("accounts", []))
            print(f"   ✅ SUCCESS! Got balances for {account_count} accounts")
        except Exception as e:
            print(f"   ❌ FAILED: {str(e)[:100]}")

    except Exception as e:
        print(f"❌ Failed to initialize or connect: {e}")
        return

    print("\n" + "=" * 50)
    print("🏁 Testing Complete!")

if __name__ == "__main__":
    asyncio.run(test_fixed_functions())