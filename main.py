import asyncio
import os

from monarchmoney import MonarchMoney

_SESSION_FILE_ = '.mm/mm_session.pickle'

def main() -> None:
    mm = MonarchMoney()
    asyncio.run(mm.interactive_login())
    subs = asyncio.run(mm.get_subscription_details())
    print(subs)

main()