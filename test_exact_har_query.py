#!/usr/bin/env python3

import asyncio
import json
import sys

sys.path.insert(0, "/home/keith/src/monarchmoney")

from monarchmoney import MonarchMoney
from gql import gql


async def test_exact_har_queries():
    """Test using the exact GraphQL queries from HAR files."""
    mm = MonarchMoney()
    
    print("=== Login ===")
    try:
        await mm.interactive_login()
        print("✓ Login successful")
    except Exception as e:
        print(f"✗ Login failed: {e}")
        return
    
    print("\n=== Test Exact HAR Query for GetTransactionRules ===")
    try:
        # Exact query from app.monarchmoney.com.har
        query = gql("""query GetTransactionRules {
  transactionRules {
    id
    order
    ...TransactionRuleFields
    __typename
  }
}

fragment TransactionRuleFields on TransactionRuleV2 {
  id
  merchantCriteriaUseOriginalStatement
  merchantCriteria {
    operator
    value
    __typename
  }
  amountCriteria {
    operator
    isExpense
    value
    valueRange {
      lower
      upper
      __typename
    }
    __typename
  }
  categoryIds
  accountIds
  categories {
    id
    name
    icon
    __typename
  }
  accounts {
    id
    displayName
    icon
    logoUrl
    __typename
  }
  setMerchantAction {
    id
    name
    __typename
  }
  setCategoryAction {
    id
    name
    icon
    __typename
  }
  addTagsAction {
    id
    name
    color
    __typename
  }
  linkGoalAction {
    id
    name
    imageStorageProvider
    imageStorageProviderId
    __typename
  }
  needsReviewByUserAction {
    id
    name
    __typename
  }
  unassignNeedsReviewByUserAction
  sendNotificationAction
  setHideFromReportsAction
  reviewStatusAction
  recentApplicationCount
  lastAppliedAt
  splitTransactionsAction {
    amountType
    splitsInfo {
      categoryId
      merchantName
      amount
      goalId
      tags
      hideFromReports
      reviewStatus
      needsReviewByUserId
      __typename
    }
    __typename
  }
  __typename
}""")
        
        result = await mm.gql_call(
            operation="GetTransactionRules",
            graphql_query=query,
            variables={}
        )
        print(f"✓ HAR query successful: {len(result.get('transactionRules', []))} rules")
        
    except Exception as e:
        print(f"✗ HAR query failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_exact_har_queries())