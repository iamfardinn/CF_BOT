import asyncio
import logging
import sys
import discord
from discord.ext import commands
import config
import keep_alive

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("bot")

EXTENSIONS = [
    "cogs.codeforces_monitor",
    "cogs.slash_commands",
]

class CodeforcesBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self) -> None:
        for ext in EXTENSIONS:
            try:
                await self.load_extension(ext)
                logger.info(f"Loaded extension: {ext}")
            except Exception as exc:
                logger.error(f"Failed to load extension {ext}: {exc}")
                raise

        synced = await self.tree.sync()
        logger.info(f"Synced {len(synced)} slash command(s).")

    async def on_ready(self) -> None:
        logger.info(f"Logged in as {self.user} ({self.user.id})")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="Codeforces contests"
            )
        )

    async def on_error(self, event_method: str, *args, **kwargs) -> None:
        logger.exception(f"Unhandled exception in {event_method}")


async def main() -> None:
    bot = CodeforcesBot()
    async with bot:
        await bot.start(config.DISCORD_TOKEN)


if __name__ == "__main__":
    keep_alive.keep_alive()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped.")
