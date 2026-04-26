"""
test_channel.py
───────────────
Sends a single test embed to your notification channel, then exits.
Run this to confirm the bot token + channel ID are correct and the bot
has permission to post messages.

Usage:
    python test_channel.py
"""

import asyncio
import discord
import config     # loads .env

async def main():
    intents = discord.Intents.default()
    client  = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        channel = client.get_channel(config.NOTIFICATION_CHANNEL_ID)

        if channel is None:
            print(f"\n❌  Channel {config.NOTIFICATION_CHANNEL_ID} not found.")
            print("   → Make sure the bot has been invited to the server and the channel ID is correct.\n")
            await client.close()
            return

        embed = discord.Embed(
            title="✅  Bot connection test — SUCCESS!",
            description=(
                "The bot can see and post to this channel.\n\n"
                "**What happens next:**\n"
                "📣  When Codeforces adds a **new contest** → announcement here\n"
                "⏰  **1 hour before** any contest → warning here\n"
                "🚀  When a contest **goes live** → alert here"
            ),
            color=discord.Color.from_str("#06d6a0"),
        )
        embed.set_footer(text="Codeforces Contest Bot — Test Message")

        await channel.send(embed=embed)
        print(f"\n✅  Test embed sent successfully to #{channel.name}!\n")
        await client.close()

    await client.start(config.DISCORD_TOKEN)

asyncio.run(main())
