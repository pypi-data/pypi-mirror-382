from PGram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import UpdateType

from xync_bot.store import Store
from xync_bot.routers import last
from xync_bot.routers.main.handler import mr
from xync_bot.routers.pay.handler import pr
from xync_bot.routers.cond import cr
from xync_bot.routers.send import sd


au = [
    UpdateType.MESSAGE,
    UpdateType.CALLBACK_QUERY,
    UpdateType.CHAT_MEMBER,
    UpdateType.MY_CHAT_MEMBER,
]  # , UpdateType.CHAT_JOIN_REQUEST


class XyncBot(Bot):
    def __init__(self, token, cn):
        super().__init__(token, cn, [sd, cr, pr, mr, last], Store(), DefaultBotProperties(parse_mode="HTML"))

    async def start(self, wh_host: str = None):
        await super().start(au, wh_host)
        self.dp.workflow_data["store"].glob = await Store.Global()  # todo: refact store loading
        return self
