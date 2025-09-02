#!/usr/bin/env python3
"""
Test the create_combined_rule function specifically.
"""

import asyncio
from monarchmoney import MonarchMoney

async def test_combined_rule():
    """Test the create_combined_rule function directly."""
    
    mm = MonarchMoney()
    
    # Load session
    try:
        mm.load_session("/Users/keith/.monarchmoney_session")
        print("✅ Session loaded successfully")
    except Exception as e:
        print(f"❌ Could not load session: {e}")
        return
    
    print("\n🧪 Testing create_combined_rule()...")
    
    # Test 1: Simple combined rule
    try:
        result = await mm.create_combined_rule(
            merchant_contains="TEST COMBINED",
            amount=100,
            amount_operator="gt",
            category_name="Miscellaneous",
            apply_to_existing=False
        )
        
        if "transactionRule" in result:
            rule_id = result["transactionRule"]["id"]
            print(f"   ✅ SUCCESS! Created combined rule with ID: {rule_id}")
            
            # Clean up
            await mm.delete_transaction_rule(rule_id)
            print(f"   🗑️  Cleaned up test rule")
        else:
            print(f"   ⚠️  Got response but no transactionRule: {list(result.keys())}")
            
    except Exception as e:
        print(f"   ❌ FAILED: {str(e)[:100]}")
        
        # Let's try to understand what parameters are being passed
        print(f"\n🔍 Let's debug step by step...")
        
        # Test the individual components that make up the combined rule
        print("   Testing merchant criteria alone...")
        try:
            result = await mm.create_transaction_rule(
                merchant_criteria=[{"operator": "contains", "value": "TEST COMBINED"}],
                set_category_action="56073867242937815",  # Miscellaneous category ID
                apply_to_existing_transactions=False
            )
            rule_id = result["transactionRule"]["id"]
            print(f"   ✅ Merchant-only rule works: {rule_id}")
            await mm.delete_transaction_rule(rule_id)
            
        except Exception as e2:
            print(f"   ❌ Merchant-only rule failed: {e2}")
        
        print("   Testing amount criteria alone...")
        try:
            result = await mm.create_transaction_rule(
                amount_criteria={
                    "operator": "gt",
                    "isExpense": True,
                    "value": 100
                },
                set_category_action="56073867242937815",
                apply_to_existing_transactions=False
            )
            rule_id = result["transactionRule"]["id"]
            print(f"   ✅ Amount-only rule works: {rule_id}")
            await mm.delete_transaction_rule(rule_id)
            
        except Exception as e3:
            print(f"   ❌ Amount-only rule failed: {e3}")
        
        print("   Testing combined criteria...")
        try:
            result = await mm.create_transaction_rule(
                merchant_criteria=[{"operator": "contains", "value": "TEST COMBINED"}],
                amount_criteria={
                    "operator": "gt", 
                    "isExpense": True,
                    "value": 100
                },
                set_category_action="56073867242937815",
                apply_to_existing_transactions=False
            )
            rule_id = result["transactionRule"]["id"]
            print(f"   ✅ Combined criteria works: {rule_id}")
            await mm.delete_transaction_rule(rule_id)
            
        except Exception as e4:
            print(f"   ❌ Combined criteria failed: {e4}")
    
    print("\n🔍 Testing different amount operators...")
    
    operators = ["gt", "gte", "lt", "lte", "eq"]
    for op in operators:
        try:
            result = await mm.create_transaction_rule(
                amount_criteria={
                    "operator": op,
                    "isExpense": True,
                    "value": 50
                },
                set_category_action="56073867242937815",
                apply_to_existing_transactions=False
            )
            rule_id = result["transactionRule"]["id"]
            print(f"   ✅ Operator '{op}' works: {rule_id}")
            await mm.delete_transaction_rule(rule_id)
            
        except Exception as e:
            print(f"   ❌ Operator '{op}' failed: {str(e)[:50]}")

if __name__ == "__main__":
    asyncio.run(test_combined_rule())