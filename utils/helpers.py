import re
import discord

_DIVISION_PATTERNS = [
    (re.compile(r"educational",        re.IGNORECASE), "Educational"),
    (re.compile(r"global\s+round",     re.IGNORECASE), "Global Round"),
    (re.compile(r"div\.?\s*1\s*\+\s*2",re.IGNORECASE), "Div. 1 + 2"),
    (re.compile(r"div\.?\s*1",         re.IGNORECASE), "Div. 1"),
    (re.compile(r"div\.?\s*2",         re.IGNORECASE), "Div. 2"),
    (re.compile(r"div\.?\s*3",         re.IGNORECASE), "Div. 3"),
    (re.compile(r"div\.?\s*4",         re.IGNORECASE), "Div. 4"),
]

_DIVISION_COLORS = {
    "Educational":  discord.Color.from_str("#00b4d8"),
    "Global Round": discord.Color.from_str("#f72585"),
    "Div. 1 + 2":   discord.Color.from_str("#7209b7"),
    "Div. 1":       discord.Color.from_str("#e63946"),
    "Div. 2":       discord.Color.from_str("#f4a261"),
    "Div. 3":       discord.Color.from_str("#2a9d8f"),
    "Div. 4":       discord.Color.from_str("#457b9d"),
    "Other":        discord.Color.from_str("#6c757d"),
}

_DIVISION_EMOJI = {
    "Educational":  "📘",
    "Global Round": "🌍",
    "Div. 1 + 2":   "⚡",
    "Div. 1":       "🔴",
    "Div. 2":       "🟠",
    "Div. 3":       "🟢",
    "Div. 4":       "🔵",
    "Other":        "⚪",
}

def get_division(name: str) -> str:
    for pattern, label in _DIVISION_PATTERNS:
        if pattern.search(name):
            return label
    return "Other"

def get_division_color(division: str) -> discord.Color:
    return _DIVISION_COLORS.get(division, _DIVISION_COLORS["Other"])

def get_division_emoji(division: str) -> str:
    return _DIVISION_EMOJI.get(division, "⚪")

def format_duration(seconds: int) -> str:
    h, rem = divmod(seconds, 3600)
    m = rem // 60
    if h and m:
        return f"{h}h {m}m"
    if h:
        return f"{h}h"
    return f"{m}m"

def build_upcoming_embed(contest: dict, minutes_until: int) -> discord.Embed:
    division  = get_division(contest["name"])
    color     = get_division_color(division)
    emoji     = get_division_emoji(division)
    duration  = format_duration(contest["durationSeconds"])
    start_ts  = contest["startTimeSeconds"]
    cf_url    = f"https://codeforces.com/contest/{contest['id']}"

    embed = discord.Embed(
        title=f"{emoji}  {contest['name']}",
        url=cf_url,
        description=f"⏰  **Starting in {minutes_until} minute{'s' if minutes_until != 1 else ''}!**\nSet a reminder and warm up your fingers. 🏃",
        color=color,
    )
    embed.add_field(name="🗂  Division",  value=division,  inline=True)
    embed.add_field(name="⏱  Duration",  value=duration,  inline=True)
    embed.add_field(name="🕐  Starts At", value=f"<t:{start_ts}:F> (<t:{start_ts}:R>)", inline=False)
    embed.add_field(name="🔗  Link", value=f"[Open on Codeforces]({cf_url})", inline=False)
    embed.set_footer(text="Codeforces Contest Bot  •  Times shown in your local timezone")
    return embed

def build_started_embed(contest: dict) -> discord.Embed:
    division = get_division(contest["name"])
    color    = get_division_color(division)
    emoji    = get_division_emoji(division)
    duration = format_duration(contest["durationSeconds"])
    start_ts = contest["startTimeSeconds"]
    end_ts   = start_ts + contest["durationSeconds"]
    cf_url   = f"https://codeforces.com/contest/{contest['id']}"

    embed = discord.Embed(
        title=f"🚀  {emoji}  {contest['name']}  — **LIVE NOW!**",
        url=cf_url,
        description="The contest has started! Good luck to all participants! 🎯",
        color=color,
    )
    embed.add_field(name="🗂  Division",  value=division,  inline=True)
    embed.add_field(name="⏱  Duration",  value=duration,  inline=True)
    embed.add_field(name="🕐  Started",   value=f"<t:{start_ts}:F>", inline=False)
    embed.add_field(name="🏁  Ends At",   value=f"<t:{end_ts}:F> (<t:{end_ts}:R>)", inline=False)
    embed.add_field(name="🔗  Link",      value=f"[Join on Codeforces]({cf_url})", inline=False)
    embed.set_footer(text="Codeforces Contest Bot  •  Times shown in your local timezone")
    return embed

def build_ongoing_embed(contest: dict) -> discord.Embed:
    division = get_division(contest["name"])
    color    = get_division_color(division)
    emoji    = get_division_emoji(division)
    duration = format_duration(contest["durationSeconds"])
    start_ts = contest["startTimeSeconds"]
    end_ts   = start_ts + contest["durationSeconds"]
    cf_url   = f"https://codeforces.com/contest/{contest['id']}"

    embed = discord.Embed(
        title=f"🔴  {emoji}  {contest['name']}  — **Ongoing**",
        url=cf_url,
        description="This contest is currently in progress.",
        color=discord.Color.from_str("#e63946"),
    )
    embed.add_field(name="🗂  Division",  value=division,  inline=True)
    embed.add_field(name="⏱  Duration",  value=duration,  inline=True)
    embed.add_field(name="🏁  Ends At",   value=f"<t:{end_ts}:F> (<t:{end_ts}:R>)", inline=False)
    embed.add_field(name="🔗  Link",      value=f"[Join on Codeforces]({cf_url})", inline=False)
    embed.set_footer(text="Codeforces Contest Bot  •  Times shown in your local timezone")
    return embed

def build_announced_embed(contest: dict) -> discord.Embed:
    division = get_division(contest["name"])
    color    = get_division_color(division)
    emoji    = get_division_emoji(division)
    duration = format_duration(contest["durationSeconds"])
    start_ts = contest["startTimeSeconds"]
    cf_url   = f"https://codeforces.com/contest/{contest['id']}"
    reg_url  = f"https://codeforces.com/contestRegistration/{contest['id']}"

    embed = discord.Embed(
        title=f"📣  New Contest Announced!  {emoji}  {contest['name']}",
        url=cf_url,
        description="A new Codeforces contest has been added to the schedule.\n**Register now** to lock in your spot! 🔐",
        color=discord.Color.from_str("#06d6a0"),
    )
    embed.add_field(name="🗂  Division",  value=division,  inline=True)
    embed.add_field(name="⏱  Duration",  value=duration,  inline=True)
    embed.add_field(name="🕐  Starts At", value=f"<t:{start_ts}:F> (<t:{start_ts}:R>)", inline=False)
    embed.add_field(name="📝  Register",  value=f"[Click here to register]({reg_url})", inline=False)
    embed.set_footer(text="Codeforces Contest Bot  •  Times shown in your local timezone")
    return embed
