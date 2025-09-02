#!/usr/bin/env python3
"""
Debug script to understand why rule creation is still failing.
"""

import asyncio
import json
from monarchmoney import MonarchMoney

async def debug_rule_creation():
    """Debug the rule creation functions to understand the exact failure."""
    
    mm = MonarchMoney()
    
    # Load session
    try:
        mm.load_session("/Users/keith/.monarchmoney_session")
        print("✅ Session loaded successfully")
    except Exception as e:
        print(f"❌ Could not load session: {e}")
        return
    
    print("\n🔍 DEBUGGING RULE CREATION FAILURES")
    print("=" * 50)
    
    # First, let's get categories to ensure we have a valid category
    print("\n1️⃣ Getting available categories...")
    try:
        categories = await mm.get_transaction_categories()
        misc_category = None
        for cat in categories.get("categories", []):
            if cat.get("name", "").lower() == "miscellaneous":
                misc_category = cat
                break
        
        if misc_category:
            print(f"   ✅ Found Miscellaneous category: ID={misc_category['id']}")
        else:
            print("   ⚠️  No Miscellaneous category found, using first available category")
            first_cat = categories.get("categories", [{}])[0]
            misc_category = first_cat
            print(f"   📝 Using category: {first_cat.get('name', 'Unknown')} (ID={first_cat.get('id', 'None')})")
            
    except Exception as e:
        print(f"   ❌ Failed to get categories: {e}")
        return
    
    # Now let's try the create_transaction_rule directly with detailed error info
    print(f"\n2️⃣ Testing create_transaction_rule() directly...")
    try:
        # Test amount criteria
        amount_criteria = {
            "operator": "eq",
            "value": 115.32,
            "isExpense": False
        }
        
        result = await mm.create_transaction_rule(
            amount_criteria=amount_criteria,
            set_category_action=misc_category["id"],
            apply_to_existing_transactions=False
        )
        
        print(f"   ✅ create_transaction_rule() succeeded!")
        print(f"   Response keys: {list(result.keys())}")
        if "transactionRule" in result:
            rule_id = result["transactionRule"]["id"]
            print(f"   Rule ID: {rule_id}")
            
            # Clean up
            try:
                await mm.delete_transaction_rule(rule_id)
                print(f"   🗑️  Cleaned up test rule")
            except:
                print(f"   ⚠️  Could not clean up rule")
        
    except Exception as e:
        print(f"   ❌ create_transaction_rule() failed: {e}")
        
        # Let's examine the raw error
        error_str = str(e)
        if "Something went wrong while processing: None" in error_str:
            print(f"   🔍 This is the classic GraphQL parsing error")
            print(f"   💡 Our fixes may not be applied or there's still an issue with the mutation")
        else:
            print(f"   🔍 Different error type: {error_str[:200]}")
    
    # Test the merchant-based rule too
    print(f"\n3️⃣ Testing merchant-based rule creation...")
    try:
        merchant_criteria = [{"operator": "contains", "value": "DEBUG TEST MERCHANT"}]
        
        result = await mm.create_transaction_rule(
            merchant_criteria=merchant_criteria,
            set_category_action=misc_category["id"],
            apply_to_existing_transactions=False
        )
        
        print(f"   ✅ Merchant rule creation succeeded!")
        if "transactionRule" in result:
            rule_id = result["transactionRule"]["id"] 
            # Clean up
            try:
                await mm.delete_transaction_rule(rule_id)
                print(f"   🗑️  Cleaned up test rule")
            except:
                print(f"   ⚠️  Could not clean up rule")
                
    except Exception as e:
        print(f"   ❌ Merchant rule creation failed: {e}")
    
    print(f"\n4️⃣ Testing helper function create_amount_rule()...")
    try:
        result = await mm.create_amount_rule(
            amount=115.32,
            operator="eq",
            is_expense=False,
            category_name="Miscellaneous",
            apply_to_existing=False
        )
        print(f"   ✅ create_amount_rule() helper succeeded!")
        
    except Exception as e:
        print(f"   ❌ create_amount_rule() helper failed: {e}")

if __name__ == "__main__":
    asyncio.run(debug_rule_creation())