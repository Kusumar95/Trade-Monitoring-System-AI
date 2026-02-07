
import asyncio
TOPICS={k:asyncio.Queue() for k in ["dau","trade","completeness"]}
async def publish(t,m): await TOPICS[t].put(m)
async def consume(t): return await TOPICS[t].get()
