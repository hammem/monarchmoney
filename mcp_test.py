#!/usr/bin/env python3
"""
MCP-style test for Monarch Money Enhanced v0.3.3+
Tests the specific functions mentioned in your analysis.
"""

import asyncio
import json
from monarchmoney import MonarchMoney

async def test_core_functions():
    """Test the core functions that were failing in v0.3.3"""
    
    # Use the same session approach as the MCP server
    mm = MonarchMoney()
    session_file = "/Users/keith/.monarchmoney_session"
    
    print("MCP Test - Monarch Money Enhanced")
    print("Testing functions that were broken in v0.3.3...")
    
    # Try to load existing session using same method as MCP server
    try:
        mm.load_session(session_file)
        # Test if session is still valid
        me = await mm.get_me()
        print(f"✅ Connected successfully as: {me.get('username', 'Unknown')}")
    except Exception as e:
        print(f"❌ Session expired or invalid: {str(e)[:100]}")
        print("💡 MCP session might be expired. Please use the working MCP server first to establish a fresh session")
        return {"error": "No valid session"}
    
    # Test the five critical functions from your analysis
    tests = [
        {
            "name": "Get net worth history",
            "func": lambda: mm.get_net_worth_history(),
            "expected_keys": ["aggregateSnapshots"]
        },
        {
            "name": "Create amount rule",
            "func": lambda: mm.create_amount_rule(
                amount=115.32,
                operator="eq", 
                is_expense=False,
                category_name="Miscellaneous",
                apply_to_existing=False
            ),
            "expected_keys": ["transactionRule"]
        },
        {
            "name": "Get recent account balances", 
            "func": lambda: mm.get_recent_account_balances(),
            "expected_keys": ["accounts"]
        },
        {
            "name": "Apply rules to existing transactions",
            "func": lambda: mm.apply_rules_to_existing_transactions(limit=0),  # Just test the API call
            "expected_keys": ["processed", "applied"]
        },
        {
            "name": "Get investment performance",
            "func": lambda: mm.get_investment_performance(),
            "expected_keys": ["portfolio"]
        }
    ]
    
    results = {}
    
    for test in tests:
        print(f"\nTesting: {test['name']}")
        try:
            result = await test["func"]()
            # Check if expected keys are present
            success = any(key in result for key in test["expected_keys"])
            if success:
                print(f"✅ SUCCESS - {test['name']}")
                results[test["name"]] = "PASS"
            else:
                print(f"⚠️  PARTIAL - {test['name']} returned data but missing expected keys")
                print(f"   Got keys: {list(result.keys())}")
                results[test["name"]] = "PARTIAL"
        except Exception as e:
            print(f"❌ FAILED - {test['name']}: {str(e)[:100]}")
            results[test["name"]] = "FAIL"
    
    print(f"\n{'='*50}")
    print("SUMMARY:")
    for test_name, result in results.items():
        status_emoji = "✅" if result == "PASS" else "⚠️" if result == "PARTIAL" else "❌"
        print(f"{status_emoji} {test_name}: {result}")
    
    pass_count = sum(1 for r in results.values() if r == "PASS")
    total_count = len(results)
    print(f"\nOverall: {pass_count}/{total_count} tests passing")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(test_core_functions())