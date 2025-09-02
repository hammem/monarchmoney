#!/usr/bin/env python3
"""
Test the create_combined_rule function with user-friendly operators.
"""

import asyncio
from monarchmoney import MonarchMoney

async def test_combined_rule_operators():
    """Test the create_combined_rule function with different operator formats."""
    
    mm = MonarchMoney()
    
    # Load session
    try:
        mm.load_session("/Users/keith/.monarchmoney_session")
        print("✅ Session loaded successfully")
    except Exception as e:
        print(f"❌ Could not load session: {e}")
        return
    
    print("\n🧪 Testing create_combined_rule() with user-friendly operators...")
    
    test_cases = [
        {"op": "greater_than", "amount": 200, "desc": "Airbnb over $200 (MCP format)"},
        {"op": "less_than", "amount": 50, "desc": "Small payments under $50"},
        {"op": "equals", "amount": 100, "desc": "Exactly $100 payments"},
        {"op": "gt", "amount": 150, "desc": "Direct gt operator"},
        {"op": "eq", "amount": 75, "desc": "Direct eq operator"}
    ]
    
    created_rules = []
    
    for test in test_cases:
        print(f"\n   Testing: {test['desc']}")
        try:
            result = await mm.create_combined_rule(
                merchant_contains="TEST COMBINED OPERATOR",
                amount=test["amount"],
                amount_operator=test["op"],
                category_name="Miscellaneous",
                apply_to_existing=False
            )
            
            if "transactionRule" in result:
                rule_id = result["transactionRule"]["id"]
                created_rules.append(rule_id)
                print(f"   ✅ SUCCESS! Operator '{test['op']}' works: {rule_id}")
            else:
                print(f"   ⚠️  Got response but no transactionRule")
                
        except Exception as e:
            print(f"   ❌ FAILED with operator '{test['op']}': {str(e)[:80]}")
    
    # Clean up all created rules
    print(f"\n🧹 Cleaning up {len(created_rules)} test rules...")
    for rule_id in created_rules:
        try:
            await mm.delete_transaction_rule(rule_id)
            print(f"   🗑️  Deleted rule {rule_id}")
        except Exception as e:
            print(f"   ⚠️  Could not delete rule {rule_id}: {e}")

if __name__ == "__main__":
    asyncio.run(test_combined_rule_operators())