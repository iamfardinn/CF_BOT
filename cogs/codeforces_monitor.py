import logging
import time
import aiohttp
import discord
from discord.ext import commands, tasks

import config
from utils.cf_api import fetch_contests
from utils.helpers import (
    build_ongoing_embed,
    build_started_embed,
    build_upcoming_embed,
    build_announced_embed,
    get_division,
)
from utils.store import already_notified, mark_notified, prune_old_entries

logger = logging.getLogger(__name__)

_START_WINDOW_SECS = 60 * config.POLL_INTERVAL_MINUTES
_WARN_WINDOW_LOWER = config.NOTIFY_BEFORE_MINUTES * 60
_WARN_WINDOW_UPPER = _WARN_WINDOW_LOWER + _START_WINDOW_SECS

def _role_mention(division: str) -> str:
    role_id = config.DIVISION_ROLES.get(division) or config.DIVISION_ROLES.get("Other")
    if role_id:
        return f"<@&{role_id}> "
    return ""

class CodeForcesMonitor(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.session: aiohttp.ClientSession | None = None
        self.monitor_loop.start()

    def cog_unload(self) -> None:
        self.monitor_loop.cancel()

    @tasks.loop(minutes=config.POLL_INTERVAL_MINUTES)
    async def monitor_loop(self) -> None:
        logger.info("Polling Codeforces API...")

        channel = self.bot.get_channel(config.NOTIFICATION_CHANNEL_ID)
        if channel is None:
            logger.error(f"Notification channel {config.NOTIFICATION_CHANNEL_ID} not found.")
            return

        try:
            contests = await fetch_contests(self.session)
        except RuntimeError as exc:
            logger.error(f"Could not fetch contests: {exc}")
            return

        now_unix = int(time.time())
        active_ids = set()

        for contest in contests:
            phase = contest.get("phase", "")
            cid = contest["id"]
            start = contest.get("startTimeSeconds", 0)

            if phase == "FINISHED":
                continue

            active_ids.add(cid)
            division = get_division(contest["name"])
            mention = _role_mention(division)

            if phase == "BEFORE" and not already_notified(cid, "announced"):
                logger.info(f"Sending ANNOUNCED notification for contest {cid}")
                embed = build_announced_embed(contest)
                await channel.send(content=mention or None, embed=embed)
                mark_notified(cid, "announced")

            if phase == "CODING":
                seconds_since_start = now_unix - start
                if 0 <= seconds_since_start <= _START_WINDOW_SECS:
                    if not already_notified(cid, "started"):
                        logger.info(f"Sending STARTED notification for contest {cid}")
                        embed = build_started_embed(contest)
                        await channel.send(content=f"{mention}@here", embed=embed)
                        mark_notified(cid, "started")
                continue

            if phase == "BEFORE":
                seconds_until = start - now_unix

                if _WARN_WINDOW_LOWER <= seconds_until <= _WARN_WINDOW_UPPER:
                    if not already_notified(cid, "1_hour_warning"):
                        minutes_left = round(seconds_until / 60)
                        logger.info(f"Sending 1-hour warning for contest {cid} ({minutes_left} min left)")
                        embed = build_upcoming_embed(contest, minutes_left)
                        await channel.send(content=mention or None, embed=embed)
                        mark_notified(cid, "1_hour_warning")

                elif seconds_until <= 0 and not already_notified(cid, "started"):
                    logger.info(f"Late STARTED notification for contest {cid}")
                    embed = build_started_embed(contest)
                    await channel.send(content=f"{mention}@here", embed=embed)
                    mark_notified(cid, "started")

        prune_old_entries(active_ids)

    @monitor_loop.before_loop
    async def before_monitor(self) -> None:
        await self.bot.wait_until_ready()
        self.session = aiohttp.ClientSession()
        logger.info(f"Contest monitor ready. Polling every {config.POLL_INTERVAL_MINUTES} min.")

    @monitor_loop.after_loop
    async def after_monitor(self) -> None:
        if self.session and not self.session.closed:
            await self.session.close()

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CodeForcesMonitor(bot))
