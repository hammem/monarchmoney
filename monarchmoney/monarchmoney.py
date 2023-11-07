import calendar
from datetime import datetime
import os
import pickle
from typing import Any, Dict, Optional, List

from aiohttp import ClientSession
from aiohttp.client import DEFAULT_TIMEOUT
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from graphql import DocumentNode


AUTH_HEADER_KEY = "authorization"
CSRF_KEY = "csrftoken"
ERRORS_KEY = "error_code"
SESSION_FILE = ".mm/mm_session.pickle"


class MonarchMoneyEndpoints(object):
    BASE_URL = "https://api.monarchmoney.com/"

    @classmethod
    def getLoginEndpoint(cls) -> str:
        return cls.BASE_URL + "/auth/login/"

    @classmethod
    def getGraphQL(cls) -> str:
        return cls.BASE_URL + "/graphql"


class RequireMFAException(Exception):
    pass


class LoginFailedException(Exception):
    pass


class MonarchMoney(object):
    def __init__(self, session_file: str = SESSION_FILE, timeout: int = 10) -> None:
        self._cookies = None
        self._headers = {
            "Client-Platform": "web",
        }
        self._session_file = session_file
        self._token = None
        self._timeout = timeout

    @property
    def timeout(self) -> int:
        """The timeout, in seconds, for GraphQL calls."""
        return self._timeout

    def set_timeout(self, timeout_secs: int) -> None:
        """Sets the default timeout on GraphQL API calls, in seconds."""
        self._timeout = timeout_secs

    async def interactive_login(
        self, use_saved_session: bool = True, save_session: bool = True
    ) -> None:
        """Performs an interactive login for iPython and similar environments."""
        email = input("Email: ")
        passwd = input("Password: ")
        try:
            await self.login(email, passwd, use_saved_session, save_session)
        except RequireMFAException:
            await self.multi_factor_authenticate(
                email, passwd, input("Two Factor Code: ")
            )
            if save_session:
                self.save_session(self._session_file)

    async def login(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        use_saved_session: bool = True,
        save_session: bool = True,
    ) -> None:
        """Logs into a Monarch Money account."""
        if use_saved_session and os.path.exists(self._session_file):
            print(f"Using saved session found at {self._session_file}")
            self.load_session(self._session_file)
            return

        if email is None or password is None:
            raise LoginFailedException(
                "Email and password are required to login when not using a saved session."
            )
        await self._login_user(email, password)
        if save_session:
            self.save_session(self._session_file)

    async def multi_factor_authenticate(
        self, email: str, password: str, code: str
    ) -> None:
        """Performs multi-factor authentication to access a Monarch Money account."""
        await self._multi_factor_authenticate(email, password, code)

    async def get_accounts(self) -> Dict[str, Any]:
        """
        Gets the list of accounts configured in the Monarch Money account.
        """
        query = gql(
            """
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
        icon
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
            logo
            __typename
          }
          __typename
        }
        institution {
          id
          name
          logo
          primaryColor
          url
          __typename
        }
        __typename
      }
    """
        )
        return await self.gql_call(
            operation="GetAccounts",
            graphql_query=query,
        )

    async def get_account_holdings(self, account_id: int) -> Dict[str, Any]:
        """
        Get the holdings information for a brokerage or similar type of account.
        """
        query = gql(
            """
      query Web_GetHoldings($input: PortfolioInput) {
        portfolio(input: $input) {
          aggregateHoldings {
            edges {
              node {
                id
                quantity
                basis
                totalValue
                securityPriceChangeDollars
                securityPriceChangePercent
                lastSyncedAt
                holdings {
                  id
                  type
                  typeDisplay
                  name
                  ticker
                  closingPrice
                  isManual
                  closingPriceUpdatedAt
                  __typename
                }
                security {
                  id
                  name
                  type
                  ticker
                  typeDisplay
                  currentPrice
                  currentPriceUpdatedAt
                  closingPrice
                  closingPriceUpdatedAt
                  oneDayChangePercent
                  oneDayChangeDollars
                  __typename
                }
                __typename
              }
              __typename
            }
            __typename
          }
          __typename
        }
      }
    """
        )

        variables = {
            "input": {
                "accountIds": [str(account_id)],
                "endDate": datetime.today().strftime("%Y-%m-%d"),
                "includeHiddenHoldings": True,
                "startDate": datetime.today().strftime("%Y-%m-%d"),
            },
        }

        return await self.gql_call(
            operation="Web_GetHoldings",
            graphql_query=query,
            variables=variables,
        )

    async def get_subscription_details(self) -> Dict[str, Any]:
        """
        The type of subscription for the Monarch Money account.
        """
        query = gql(
            """
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
        )
        return await self.gql_call(
            operation="GetSubscriptionDetails",
            graphql_query=query,
        )

    async def get_transactions(
        self,
        limit: int = 1000,
        offset: Optional[int] = 0,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        search: str = "",
        categories: List[str] = [],
        accounts: List[str] = [],
        tags: List[str] = [],
        has_attachments: bool = False,
        has_notes: bool = False,
        hidden_from_reports: bool = False,
        is_split: bool = False,
        is_recurring: bool = False,
    ) -> Dict[str, Any]:
        """
        Gets transaction data from the account.

        :param limit: the maximum number of transactions to download, defaults to 1000.
        :param offset: the number of transactions to skip (offset) before retrieving results.
        :param start_date: the earliest date to get transactions from, in "yyyy-mm-dd" format.
        :param end_date: the latest date to get transactions from, in "yyyy-mm-dd" format.
        :param search: a string to filter transactions. use empty string for all results.
        :param categories: a list of category ids to filter.
        :param accounts: a list of account ids to filter.
        :param tags: a list of tag ids to filter.
        :param has_attachments: a bool to filter for whether the transactions have attachments.
        :param has_notes: a bool to filter for whether the transactions have notes.
        :param hidden_from_reports: a bool to filter for whether the transactions are hidden from reports.
        :param is_split: a bool to filter for whether the transactions are split.
        :param is_recurring: a bool to filter for whether the transactions are recurring.
        """

        query = gql(
            """
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
              __typename
            }
            isSplitTransaction
            category {
              id
              name
              icon
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
        )

        variables = {
            "offset": offset,
            "limit": limit,
            "orderBy": "date",
            "filters": {
                "search": search,
                "categories": categories,
                "accounts": accounts,
                "tags": tags,
                "hasAttachments": has_attachments,
                "hasNotes": has_notes,
                "hideFromReports": hidden_from_reports,
                "isRecurring": is_recurring,
                "isSplit": is_split,
            },
        }

        if start_date and end_date:
            variables["filters"]["startDate"] = start_date
            variables["filters"]["endDate"] = end_date
        elif bool(start_date) != bool(end_date):
            raise Exception(
                "You must specify both a startDate and endDate, not just one of them."
            )

        return await self.gql_call(
            operation="GetTransactionsList", graphql_query=query, variables=variables
        )

    async def get_transaction_categories(self) -> Dict[str, Any]:
        """
        Gets all the categories configured in the account.
        """
        query = gql(
            """
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
        icon
        systemCategory
        isSystemCategory
        isDisabled
        group {
          id
          name
          type
          __typename
        }
        __typename
      }
    """
        )
        return await self.gql_call(operation="GetCategories", graphql_query=query)

    async def get_transaction_tags(self) -> Dict[str, Any]:
        """
        Gets all the tags configured in the account.
        """
        query = gql(
            """
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
        )
        return await self.gql_call(
            operation="GetHouseholdTransactionTags", graphql_query=query
        )

    async def get_cashflow(
        self,
        limit: int = 1000,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Gets all the categories configured in the account.
        """
        query = gql(
            """
      query Web_GetCashFlowPage($filters: TransactionFilterInput) {
        byCategory: aggregates(filters: $filters, groupBy: ["category"]) {
          groupBy {
            category {
              id
              name
              icon
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
        )

        variables = {
            "limit": limit,
            "orderBy": "date",
            "filters": {
                "search": "",
                "categories": [],
                "accounts": [],
                "tags": [],
            },
        }

        if start_date and end_date:
            variables["filters"]["startDate"] = start_date
            variables["filters"]["endDate"] = end_date
        elif bool(start_date) != bool(end_date):
            raise Exception(
                "You must specify both a startDate and endDate, not just one of them."
            )
        else:
            current_year = datetime.now().year
            current_month = datetime.now().month
            last_date = calendar.monthrange(current_year, current_month)[1]
            variables["filters"]["startDate"] = datetime(
                current_year, current_month, 1
            ).strftime("%Y-%m-%d")
            variables["filters"]["endDate"] = datetime(
                datetime.now().year, datetime.now().month, last_date
            ).strftime("%Y-%m-%d")

        return await self.gql_call(
            operation="Web_GetCashFlowPage", variables=variables, graphql_query=query
        )

    async def get_cashflow_summary(
        self,
        limit: int = 1000,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Gets all the categories configured in the account.
        """
        query = gql(
            """
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
        )

        variables = {
            "limit": limit,
            "orderBy": "date",
            "filters": {
                "search": "",
                "categories": [],
                "accounts": [],
                "tags": [],
            },
        }

        if start_date and end_date:
            variables["filters"]["startDate"] = start_date
            variables["filters"]["endDate"] = end_date
        elif bool(start_date) != bool(end_date):
            raise Exception(
                "You must specify both a startDate and endDate, not just one of them."
            )
        else:
            current_year = datetime.now().year
            current_month = datetime.now().month
            last_date = calendar.monthrange(current_year, current_month)[1]
            variables["filters"]["startDate"] = datetime(
                current_year, current_month, 1
            ).strftime("%Y-%m-%d")
            variables["filters"]["endDate"] = datetime(
                datetime.now().year, datetime.now().month, last_date
            ).strftime("%Y-%m-%d")

        return await self.gql_call(
            operation="Web_GetCashFlowPage", variables=variables, graphql_query=query
        )

    async def gql_call(
        self,
        operation: str,
        graphql_query: DocumentNode,
        variables: Dict[str, Any] = {},
    ) -> Dict[str, Any]:
        """
        Makes a GraphQL call to Monarch Money's API.
        """
        return await self._get_graphql_client().execute_async(
            document=graphql_query, operation_name=operation, variable_values=variables
        )

    def save_session(self, filename: str) -> None:
        """
        Saves the cookies and auth token needed to access a Monarch Money account.
        """
        session_data = {
            "token": self._token,
            "cookies": self._cookies,
        }
        with open(filename, "wb") as fh:
            pickle.dump(session_data, fh)

    def load_session(self, filename: str) -> None:
        """
        Loads pre-existing cookies and auth token from a Python pickle file.
        """
        with open(filename, "rb") as fh:
            data = pickle.load(fh)
            self._cookies = data["cookies"]
            self._token = data["token"]
            self._headers["Authorization"] = f"Token {self._token}"

    async def _login_user(self, email: str, password: str) -> None:
        """
        Performs the initial login to a Monarch Money account.
        """
        data = {
            "password": password,
            "supports_mfa": True,
            "trusted_device": False,
            "username": email,
        }

        async with ClientSession(headers=self._headers) as session:
            async with session.post(
                MonarchMoneyEndpoints.getLoginEndpoint(), data=data
            ) as resp:
                if resp.status == 403:
                    raise RequireMFAException("Multi-Factor Auth Required")
                elif resp.status != 200:
                    raise LoginFailedException(
                        f"HTTP Code {resp.status}: {resp.reason}"
                    )

                response = await resp.json()
                self._cookies = resp.cookies
                self._token = response["token"]
                self._headers["Authorization"] = f"Token {self._token}"

    async def _multi_factor_authenticate(
        self, email: str, password: str, code: str
    ) -> None:
        """
        Performs the MFA step of login.
        """
        data = {
            "password": password,
            "supports_mfa": True,
            "totp": code,
            "trusted_device": False,
            "username": email,
        }

        async with ClientSession(headers=self._headers) as session:
            async with session.post(
                MonarchMoneyEndpoints.getLoginEndpoint(), data=data
            ) as resp:
                if resp.status != 200:
                    response = await resp.json()
                    error_message = (
                        response["error_code"]
                        if response is not None
                        else "Unknown error"
                    )
                    raise LoginFailedException(error_message)

                response = await resp.json()
                self._cookies = resp.cookies
                self._token = response["token"]
                self._headers["Authorization"] = f"Token {self._token}"

    def _get_graphql_client(self) -> Client:
        """
        Creates a correctly configured GraphQL client for connecting to Monarch Money.
        """
        if self._cookies is None or self._headers is None:
            raise LoginFailedException("Make sure you call login() first!")
        transport = AIOHTTPTransport(
            url=MonarchMoneyEndpoints.getGraphQL(),
            cookies=self._cookies,
            headers=self._headers,
            timeout=self._timeout,
        )
        return Client(
            transport=transport,
            fetch_schema_from_transport=False,
            execute_timeout=self._timeout,
        )
