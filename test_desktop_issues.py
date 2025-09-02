#!/usr/bin/env python3
"""
Test the specific functions that were broken according to desktop analysis.
Uses the fixed monarchmoney library directly.
"""

import asyncio
import json
from monarchmoney import MonarchMoney

async def test_desktop_reported_issues():
    """Test the exact functions reported as broken in the desktop analysis."""
    
    mm = MonarchMoney()
    
    # Load the working session from MCP server
    try:
        mm.load_session("/Users/keith/.monarchmoney_session")
        print("✅ Session loaded successfully")
    except Exception as e:
        print(f"❌ Could not load session: {e}")
        return
    
    # Test each function that was reported as broken
    broken_functions = [
        {
            "name": "get_net_worth_history",
            "test": lambda: mm.get_net_worth_history(),
            "expected": "aggregateSnapshots"
        },
        {
            "name": "create_amount_rule", 
            "test": lambda: mm.create_amount_rule(
                amount=115.32,
                operator="eq", 
                is_expense=False,
                category_name="Miscellaneous",
                apply_to_existing=False
            ),
            "expected": "transactionRule"
        },
        {
            "name": "create_categorization_rule",
            "test": lambda: mm.create_categorization_rule(
                merchant_contains="TEST MERCHANT v0.3.3+",
                category_name="Miscellaneous", 
                apply_to_existing=False
            ),
            "expected": "transactionRule"
        },
        {
            "name": "apply_rules_to_existing_transactions",
            "test": lambda: mm.apply_rules_to_existing_transactions(limit=1),
            "expected": "processed"
        },
        {
            "name": "get_investment_performance",
            "test": lambda: mm.get_investment_performance(),
            "expected": "portfolio"
        }
    ]
    
    print("\n🧪 Testing Previously Broken Functions from Desktop Analysis")
    print("=" * 60)
    
    results = {}
    rules_to_cleanup = []
    
    for func_info in broken_functions:
        func_name = func_info["name"]
        print(f"\n🔬 Testing {func_name}()...")
        
        try:
            result = await func_info["test"]()
            
            # Check if we got expected data structure
            if func_info["expected"] in result:
                print(f"   ✅ SUCCESS! - Returns {func_info['expected']} data")
                results[func_name] = "✅ FIXED"
                
                # Track rules for cleanup
                if "transactionRule" in result:
                    rule_id = result["transactionRule"].get("id")
                    if rule_id:
                        rules_to_cleanup.append(rule_id)
                        
            else:
                print(f"   ⚠️  PARTIAL - Got response but missing {func_info['expected']}")
                print(f"   Response keys: {list(result.keys())}")
                results[func_name] = "⚠️ PARTIAL"
                
        except Exception as e:
            error_msg = str(e)
            if "Something went wrong while processing: None" in error_msg:
                print(f"   ❌ STILL BROKEN - Same GraphQL parsing error")
                results[func_name] = "❌ STILL BROKEN"
            else:
                print(f"   ❌ FAILED - Different error: {error_msg[:80]}")
                results[func_name] = f"❌ NEW ERROR: {error_msg[:50]}"
    
    # Clean up test rules
    if rules_to_cleanup:
        print(f"\n🧹 Cleaning up {len(rules_to_cleanup)} test rules...")
        for rule_id in rules_to_cleanup:
            try:
                await mm.delete_transaction_rule(rule_id)
                print(f"   🗑️  Deleted rule {rule_id}")
            except:
                print(f"   ⚠️  Could not delete rule {rule_id}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 RESULTS SUMMARY")
    print("=" * 60)
    
    for func_name, status in results.items():
        print(f"{status} {func_name}()")
    
    fixed_count = sum(1 for status in results.values() if "✅" in status)
    total_count = len(results)
    
    print(f"\n🎯 Overall Status: {fixed_count}/{total_count} functions now working")
    
    if fixed_count == total_count:
        print("🎉 ALL PREVIOUSLY BROKEN FUNCTIONS ARE NOW FIXED!")
    elif fixed_count > 0:
        print(f"✨ {fixed_count} functions fixed, {total_count - fixed_count} still need work")
    else:
        print("😞 No functions were successfully fixed")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(test_desktop_reported_issues())