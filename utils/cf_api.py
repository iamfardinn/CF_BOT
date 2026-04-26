import asyncio
import logging
import aiohttp

logger = logging.getLogger(__name__)

CF_API_BASE = "https://codeforces.com/api"
_TIMEOUT = aiohttp.ClientTimeout(total=15)

async def fetch_contests(session: aiohttp.ClientSession, retries: int = 3) -> list[dict]:
    url = f"{CF_API_BASE}/contest.list?gym=false"

    for attempt in range(1, retries + 1):
        try:
            async with session.get(url, timeout=_TIMEOUT) as resp:
                if resp.status != 200:
                    logger.warning(f"CF API returned HTTP {resp.status} (attempt {attempt}/{retries})")
                    await asyncio.sleep(2 ** attempt)
                    continue

                payload = await resp.json(content_type=None)

                if payload.get("status") != "OK":
                    comment = payload.get("comment", "unknown error")
                    logger.warning(f"CF API error: {comment} (attempt {attempt}/{retries})")
                    await asyncio.sleep(2 ** attempt)
                    continue

                return payload["result"]

        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            logger.warning(f"Network error fetching CF contests: {exc} (attempt {attempt}/{retries})")
            await asyncio.sleep(2 ** attempt)

    raise RuntimeError("Codeforces API is unreachable after multiple retries.")
