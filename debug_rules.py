#!/usr/bin/env python3

import asyncio
import os
import sys

# Add the package to the path
sys.path.insert(0, '/home/keith/src/monarchmoney')

from monarchmoney import MonarchMoney

async def test_rules():
    """Test transaction rules functionality to debug the issue."""
    mm = MonarchMoney()
    
    # Try to load session if available
    try:
        mm.load_session()
        print("✓ Session loaded successfully")
    except FileNotFoundError:
        print("✗ No session file found - authentication needed")
        return
    except Exception as e:
        print(f"✗ Session load error: {e}")
        return
    
    try:
        # Test 1: Try to get existing rules
        print("\n=== Testing get_transaction_rules ===")
        rules = await mm.get_transaction_rules()
        print(f"✓ Rules retrieved: {len(rules.get('transactionRules', []))} rules found")
        
    except Exception as e:
        print(f"✗ get_transaction_rules failed: {e}")
        print(f"Error type: {type(e)}")
        return
    
    try:
        # Test 2: Try to create a simple rule
        print("\n=== Testing create_transaction_rule ===")
        conditions = [{"field": "merchant", "operation": "contains", "value": "Test Merchant"}]
        actions = [{"type": "set_category", "categoryId": "test-category-id"}]
        
        result = await mm.create_transaction_rule(conditions=conditions, actions=actions)
        print(f"✓ Rule created: {result}")
        
    except Exception as e:
        print(f"✗ create_transaction_rule failed: {e}")
        print(f"Error type: {type(e)}")
        
    try:
        # Test 3: Try the helper method
        print("\n=== Testing create_categorization_rule ===")
        result = await mm.create_categorization_rule(
            merchant_contains="Test Company",
            category_name="Utilities"  # Common category that should exist
        )
        print(f"✓ Categorization rule created: {result}")
        
    except Exception as e:
        print(f"✗ create_categorization_rule failed: {e}")
        print(f"Error type: {type(e)}")

if __name__ == "__main__":
    asyncio.run(test_rules())