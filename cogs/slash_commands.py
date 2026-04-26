import time
import logging
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

from utils.cf_api import fetch_contests
from utils.helpers import (
    build_ongoing_embed,
    build_upcoming_embed,
    get_division,
    get_division_emoji,
    format_duration,
)

logger = logging.getLogger(__name__)

_DIVISION_CHOICES = [
    app_commands.Choice(name="All Divisions",  value="all"),
    app_commands.Choice(name="Div. 1",         value="Div. 1"),
    app_commands.Choice(name="Div. 2",         value="Div. 2"),
    app_commands.Choice(name="Div. 3",         value="Div. 3"),
    app_commands.Choice(name="Div. 4",         value="Div. 4"),
    app_commands.Choice(name="Educational",    value="Educational"),
    app_commands.Choice(name="Global Round",   value="Global Round"),
    app_commands.Choice(name="Div. 1 + 2",     value="Div. 1 + 2"),
]

class SlashCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="next_contest",
        description="Show upcoming Codeforces contests (optionally filter by division).",
    )
    @app_commands.describe(
        division="Filter by division (default: all)",
        count="Number of contests to show (1–10, default 5)",
    )
    @app_commands.choices(division=_DIVISION_CHOICES)
    async def next_contest(
        self,
        interaction: discord.Interaction,
        division: app_commands.Choice[str] = None,
        count: app_commands.Range[int, 1, 10] = 5,
    ) -> None:
        await interaction.response.defer(thinking=True)

        div_filter = division.value if division else "all"

        async with aiohttp.ClientSession() as session:
            try:
                contests = await fetch_contests(session)
            except RuntimeError:
                await interaction.followup.send("❌ Could not reach the Codeforces API right now. Try again in a moment.", ephemeral=True)
                return

        now_unix = int(time.time())

        upcoming = [
            c for c in contests
            if c.get("phase") == "BEFORE" and c.get("startTimeSeconds", 0) > now_unix
        ]
        upcoming.sort(key=lambda c: c["startTimeSeconds"])

        if div_filter != "all":
            upcoming = [c for c in upcoming if get_division(c["name"]) == div_filter]

        if not upcoming:
            label = f"**{div_filter}**" if div_filter != "all" else "any division"
            await interaction.followup.send(f"📭 No upcoming contests found for {label}.", ephemeral=True)
            return

        results = upcoming[:count]

        embed = discord.Embed(
            title="📅 Upcoming Codeforces Contests",
            description=f"Showing **{len(results)}** contest(s)" + (f" — Division: **{div_filter}**" if div_filter != "all" else ""),
            color=discord.Color.from_str("#4361ee"),
        )

        for c in results:
            div = get_division(c["name"])
            emoji = get_division_emoji(div)
            dur = format_duration(c["durationSeconds"])
            start = c["startTimeSeconds"]
            cf_url = f"https://codeforces.com/contest/{c['id']}"
            embed.add_field(
                name=f"{emoji} {c['name']}",
                value=f"🕐 <t:{start}:F> (<t:{start}:R>)\n⏱ {dur} 🗂 {div}\n[Open contest]({cf_url})",
                inline=False,
            )

        embed.set_footer(text="Times are shown in your local timezone • /next_contest")
        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="ongoing",
        description="Show all Codeforces contests currently in progress.",
    )
    async def ongoing(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)

        async with aiohttp.ClientSession() as session:
            try:
                contests = await fetch_contests(session)
            except RuntimeError:
                await interaction.followup.send("❌ Could not reach the Codeforces API right now.", ephemeral=True)
                return

        live = [c for c in contests if c.get("phase") == "CODING"]

        if not live:
            await interaction.followup.send("✅ No contests are running right now. Check back later!", ephemeral=True)
            return

        embeds = [build_ongoing_embed(c) for c in live]
        await interaction.followup.send(embeds=embeds[:10])

    @app_commands.command(
        name="help_cf",
        description="Learn what this Codeforces bot can do.",
    )
    async def help_cf(self, interaction: discord.Interaction) -> None:
        embed = discord.Embed(
            title="🤖 Codeforces Contest Bot — Help",
            description="I monitor Codeforces and keep you informed about upcoming and ongoing contests.\n\n**Automatic Notifications** are sent to this server's contest channel:",
            color=discord.Color.from_str("#4361ee"),
        )
        embed.add_field(name="⏰ 1-Hour Warning", value="Posted automatically before each contest starts.", inline=False)
        embed.add_field(name="🚀 Contest Started", value="Fired the moment a contest goes live.", inline=False)
        embed.add_field(
            name="📋 Slash Commands",
            value="`/next_contest [division] [count]` — List upcoming contests\n`/ongoing` — Show contests live right now\n`/help_cf` — This message",
            inline=False,
        )
        embed.set_footer(text="Codeforces Contest Bot • Data from codeforces.com/api")
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SlashCommands(bot))
