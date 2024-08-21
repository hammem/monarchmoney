QUERY_GET_ACCOUNTS = """
  query GetAccounts {
    accounts {
      ...AccountFields
      __typename
    }
    householdPreferences {
      id
      accountGroupOrder
      __typename
    }
  }

  fragment AccountFields on Account {
    id
    displayName
    syncDisabled
    deactivatedAt
    isHidden
    isAsset
    mask
    createdAt
    updatedAt
    displayLastUpdatedAt
    currentBalance
    displayBalance
    includeInNetWorth
    hideFromList
    hideTransactionsFromReports
    includeBalanceInNetWorth
    includeInGoalBalance
    dataProvider
    dataProviderAccountId
    isManual
    transactionsCount
    holdingsCount
    manualInvestmentsTrackingMethod
    order
    logoUrl
    type {
      name
      display
      __typename
    }
    subtype {
      name
      display
      __typename
    }
    credential {
      id
      updateRequired
      disconnectedFromDataProviderAt
      dataProvider
      institution {
        id
        plaidInstitutionId
        name
        status
        __typename
      }
      __typename
    }
    institution {
      id
      name
      primaryColor
      url
      __typename
    }
    __typename
  }
"""


QUERY_GET_ACCOUNT_TYPE_OPTIONS = """
            query GetAccountTypeOptions {
                accountTypeOptions {
                    type {
                        name
                        display
                        group
                        possibleSubtypes {
                            display
                            name
                            __typename
                        }
                        __typename
                    }
                    subtype {
                        name
                        display
                        __typename
                    }
                    __typename
                }
            }
        """


QUERY_GET_ACCOUNT_SNAPSHOTS_BY_TYPE = """
            query GetSnapshotsByAccountType($startDate: Date!, $timeframe: Timeframe!) {
                snapshotsByAccountType(startDate: $startDate, timeframe: $timeframe) {
                    accountType
                    month
                    balance
                    __typename
                }
                accountTypes {
                    name
                    group
                    __typename
                }
            }
        """

QUERY_GET_ACCOUNT_RECENT_BALANCES = """
            query GetAccountRecentBalances($startDate: Date!) {
                accounts {
                    id
                    recentBalances(startDate: $startDate)
                    __typename
                }
            }
        """

QUERY_GET_AGGREGATE_SNAPSHOTS = """
            query GetAggregateSnapshots($filters: AggregateSnapshotFilters) {
                aggregateSnapshots(filters: $filters) {
                    date
                    balance
                    __typename
                }
            }
        """

QUERY_GET_SUBSCRIPTION_DETAILS = """
query GetSubscriptionDetails {
            subscription {
              id
              paymentSource
              referralCode
              isOnFreeTrial
              hasPremiumEntitlement
              __typename
            }
          }
"""

QUERY_GET_TRANSACTIONS_SUMMARY = """
            query GetTransactionsPage($filters: TransactionFilterInput) {
              aggregates(filters: $filters) {
                summary {
                  ...TransactionsSummaryFields
                  __typename
                }
                __typename
              }
            }

            fragment TransactionsSummaryFields on TransactionsSummary {
              avg
              count
              max
              maxExpense
              sum
              sumIncome
              sumExpense
              first
              last
              __typename
            }
        """


QUERY_GET_TRANSACTIONS_LIST = """
query GetTransactionsList($offset: Int, $limit: Int, $filters: TransactionFilterInput, $orderBy: TransactionOrdering) {
allTransactions(filters: $filters) {
  totalCount
  results(offset: $offset, limit: $limit, orderBy: $orderBy) {
    id
    ...TransactionOverviewFields
    __typename
  }
  __typename
}
transactionRules {
  id
  __typename
}
}

fragment TransactionOverviewFields on Transaction {
id
amount
pending
date
hideFromReports
plaidName
notes
isRecurring
reviewStatus
needsReview
attachments {
  id
  extension
  filename
  originalAssetUrl
  publicId
  sizeBytes
  __typename
}
isSplitTransaction
createdAt
updatedAt
category {
  id
  name
  __typename
}
merchant {
  name
  id
  transactionsCount
  __typename
}
account {
  id
  displayName
  __typename
}
tags {
  id
  name
  color
  order
  __typename
}
__typename
}
"""


QUERY_GET_TRANSACTION_CATEGORIES = """
          query GetCategories {
            categories {
              ...CategoryFields
              __typename
            }
          }

          fragment CategoryFields on Category {
            id
            order
            name
            systemCategory
            isSystemCategory
            isDisabled
            updatedAt
            createdAt
            group {
              id
              name
              type
              __typename
            }
            __typename
          }
        """


QUERY_GET_TRANSACTION_CATEGORY_GROUPS = """
          query ManageGetCategoryGroups {
              categoryGroups {
                  id
                  name
                  order
                  type
                  updatedAt
                  createdAt
                  __typename
              }
          }
        """

QUERY_GET_TRANSACTION_TAGS = """
          query GetHouseholdTransactionTags($search: String, $limit: Int, $bulkParams: BulkTransactionDataParams) {
            householdTransactionTags(
              search: $search
              limit: $limit
              bulkParams: $bulkParams
            ) {
              id
              name
              color
              order
              transactionCount
              __typename
            }
          }
        """

QUERY_GET_TRANSACTION_DETAILS = """
          query GetTransactionDrawer($id: UUID!, $redirectPosted: Boolean) {
            getTransaction(id: $id, redirectPosted: $redirectPosted) {
              id
              amount
              pending
              isRecurring
              date
              originalDate
              hideFromReports
              needsReview
              reviewedAt
              reviewedByUser {
                id
                name
                __typename
              }
              plaidName
              notes
              hasSplitTransactions
              isSplitTransaction
              isManual
              splitTransactions {
                id
                ...TransactionDrawerSplitMessageFields
                __typename
              }
              originalTransaction {
                id
                ...OriginalTransactionFields
                __typename
              }
              attachments {
                id
                publicId
                extension
                sizeBytes
                filename
                originalAssetUrl
                __typename
              }
              account {
                id
                ...TransactionDrawerAccountSectionFields
                __typename
              }
              category {
                id
                __typename
              }
              goal {
                id
                __typename
              }
              merchant {
                id
                name
                transactionCount
                logoUrl
                recurringTransactionStream {
                  id
                  __typename
                }
                __typename
              }
              tags {
                id
                name
                color
                order
                __typename
              }
              needsReviewByUser {
                id
                __typename
              }
              __typename
            }
            myHousehold {
              users {
                id
                name
                __typename
              }
              __typename
            }
          }

          fragment TransactionDrawerSplitMessageFields on Transaction {
            id
            amount
            merchant {
              id
              name
              __typename
            }
            category {
              id
              name
              __typename
            }
            __typename
          }

          fragment OriginalTransactionFields on Transaction {
            id
            date
            amount
            merchant {
              id
              name
              __typename
            }
            __typename
          }

          fragment TransactionDrawerAccountSectionFields on Account {
            id
            displayName
            logoUrl
            id
            mask
            subtype {
              display
              __typename
            }
            __typename
          }
        """

QUERY_GET_TRANSACTION_SPLITS = """
          query TransactionSplitQuery($id: UUID!) {
            getTransaction(id: $id) {
              id
              amount
              category {
                id
                name
                __typename
              }
              merchant {
                id
                name
                __typename
              }
              splitTransactions {
                id
                merchant {
                  id
                  name
                  __typename
                }
                category {
                  id
                  name
                  __typename
                }
                amount
                notes
                __typename
              }
              __typename
            }
          }
        """

QUERY_GET_CASHFLOW = """
          query Web_GetCashFlowPage($filters: TransactionFilterInput) {
            byCategory: aggregates(filters: $filters, groupBy: ["category"]) {
              groupBy {
                category {
                  id
                  name
                  group {
                    id
                    type
                    __typename
                  }
                  __typename
                }
                __typename
              }
              summary {
                sum
                __typename
              }
              __typename
            }
            byCategoryGroup: aggregates(filters: $filters, groupBy: ["categoryGroup"]) {
              groupBy {
                categoryGroup {
                  id
                  name
                  type
                  __typename
                }
                __typename
              }
              summary {
                sum
                __typename
              }
              __typename
            }
            byMerchant: aggregates(filters: $filters, groupBy: ["merchant"]) {
              groupBy {
                merchant {
                  id
                  name
                  logoUrl
                  __typename
                }
                __typename
              }
              summary {
                sumIncome
                sumExpense
                __typename
              }
              __typename
            }
            summary: aggregates(filters: $filters, fillEmptyValues: true) {
              summary {
                sumIncome
                sumExpense
                savings
                savingsRate
                __typename
              }
              __typename
            }
          }
        """

QUERY_GET_CASHFLOW_SUMMARY = """
          query Web_GetCashFlowPage($filters: TransactionFilterInput) {
            summary: aggregates(filters: $filters, fillEmptyValues: true) {
              summary {
                sumIncome
                sumExpense
                savings
                savingsRate
                __typename
              }
              __typename
            }
          }
        """


QUERY_GET_RECURRING_TRANSACTIONS = """
            query Web_GetUpcomingRecurringTransactionItems($startDate: Date!, $endDate: Date!, $filters: RecurringTransactionFilter) {
              recurringTransactionItems(
                startDate: $startDate
                endDate: $endDate
                filters: $filters
              ) {
                stream {
                  id
                  frequency
                  amount
                  isApproximate
                  merchant {
                    id
                    name
                    logoUrl
                    __typename
                  }
                  __typename
                }
                date
                isPast
                transactionId
                amount
                amountDiff
                category {
                  id
                  name
                  __typename
                }
                account {
                  id
                  displayName
                  logoUrl
                  __typename
                }
                __typename
              }
            }
        """
