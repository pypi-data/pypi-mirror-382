import logging
from asyncio import run

from PGram import Bot
from aiogram.client.default import DefaultBotProperties
from x_model import init_db

from xync_bot.store import Store
from xync_bot.routers.main.handler import mr
from xync_bot.routers.cond import cr
from xync_bot.routers.pay.handler import pr
from xync_bot.routers import last
from xync_bot.routers.send import sd
from xync_bot.loader import TOKEN


if __name__ == "__main__":
    from xync_bot.loader import TORM

    logging.basicConfig(level=logging.INFO)

    async def main() -> None:
        cn = await init_db(TORM)
        bot = Bot(TOKEN, cn, [sd, cr, pr, mr, last], DefaultBotProperties(parse_mode="HTML"))

        await bot.start()
        bot.dp.workflow_data["store"].glob = await Store.Global()  # todo: refact store loading

    run(main())
