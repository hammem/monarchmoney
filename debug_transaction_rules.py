#!/usr/bin/env python3

import asyncio
import json
import sys
import traceback

sys.path.insert(0, "/home/keith/src/monarchmoney")

from monarchmoney import MonarchMoney


async def test_transaction_rules():
    """Test transaction rules functionality with real API calls."""
    mm = MonarchMoney()

    # Try to load session first, fallback to interactive login
    try:
        mm.load_session()
        print("✓ Session loaded successfully")
    except FileNotFoundError:
        print("No session file found - attempting interactive login...")
        try:
            await mm.interactive_login()
            print("✓ Interactive login successful")
        except Exception as e:
            print(f"✗ Interactive login failed: {e}")
            return
    except Exception as e:
        print(f"✗ Session load error: {e}")
        return

    print("\n=== Testing get_transaction_rules ===")
    try:
        rules = await mm.get_transaction_rules()
        print(f"✓ Successfully retrieved {len(rules.get('transactionRules', []))} rules")
        
        # Show first rule structure if available
        if rules.get('transactionRules'):
            first_rule = rules['transactionRules'][0]
            print(f"Sample rule structure: {json.dumps(first_rule, indent=2)[:500]}...")
            
    except Exception as e:
        print(f"✗ get_transaction_rules failed: {e}")
        print(f"Full traceback:")
        traceback.print_exc()
        return

    print("\n=== Testing get_transaction_categories (for create_categorization_rule) ===")
    try:
        categories = await mm.get_transaction_categories()
        print(f"✓ Successfully retrieved {len(categories.get('categories', []))} categories")
        
        # Find a category we can use for testing
        test_category = None
        for cat in categories.get('categories', []):
            if cat.get('name') in ['Shopping', 'Utilities', 'Restaurants', 'Gas & Electric']:
                test_category = cat
                break
        
        if test_category:
            print(f"Found test category: {test_category['name']} (ID: {test_category['id']})")
        else:
            print("No suitable test category found")
            return
            
    except Exception as e:
        print(f"✗ get_transaction_categories failed: {e}")
        traceback.print_exc()
        return

    print("\n=== Testing preview_transaction_rule ===")
    try:
        preview = await mm.preview_transaction_rule(
            merchant_criteria=[{"operator": "contains", "value": "test"}],
            set_category_action=test_category['id'],
            apply_to_existing_transactions=False
        )
        print(f"✓ Preview successful: {preview.get('transactionRulePreview', {}).get('totalCount', 0)} transactions would be affected")
        
    except Exception as e:
        print(f"✗ preview_transaction_rule failed: {e}")
        traceback.print_exc()

    print("\n=== Testing create_transaction_rule ===")
    try:
        result = await mm.create_transaction_rule(
            merchant_criteria=[{"operator": "contains", "value": "DEBUG_TEST_MERCHANT"}],
            set_category_action=test_category['id'],
            apply_to_existing_transactions=False
        )
        print(f"✓ Rule creation result: {json.dumps(result, indent=2)}")
        
        # Check for errors in response
        if result.get('createTransactionRuleV2', {}).get('errors'):
            errors = result['createTransactionRuleV2']['errors']
            print(f"⚠️ API returned errors: {json.dumps(errors, indent=2)}")
        else:
            print("✓ No errors in create response")
            
    except Exception as e:
        print(f"✗ create_transaction_rule failed: {e}")
        traceback.print_exc()

    print("\n=== Testing create_categorization_rule ===")
    try:
        result = await mm.create_categorization_rule(
            merchant_contains="DEBUG_TEST_HELPER",
            category_name=test_category['name'],
            apply_to_existing=False
        )
        print(f"✓ Categorization rule result: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"✗ create_categorization_rule failed: {e}")
        traceback.print_exc()

    print("\n=== Final rules check ===")
    try:
        final_rules = await mm.get_transaction_rules()
        final_count = len(final_rules.get('transactionRules', []))
        print(f"✓ Final rule count: {final_count}")
        
        # Look for our test rules
        for rule in final_rules.get('transactionRules', []):
            merchant_criteria = rule.get('merchantCriteria', [])
            for criteria in merchant_criteria:
                if 'DEBUG_TEST' in criteria.get('value', ''):
                    print(f"Found test rule: {rule['id']} - {criteria['value']}")
                    
                    # Clean up test rule
                    print(f"Cleaning up test rule {rule['id']}...")
                    deleted = await mm.delete_transaction_rule(rule['id'])
                    print(f"Delete result: {deleted}")
                    
    except Exception as e:
        print(f"✗ Final rules check failed: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_transaction_rules())