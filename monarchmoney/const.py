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

QUERY_GET_AGGREGATE_SNAPSHOTS ="""
            query GetAggregateSnapshots($filters: AggregateSnapshotFilters) {
                aggregateSnapshots(filters: $filters) {
                    date
                    balance
                    __typename
                }
            }
        """