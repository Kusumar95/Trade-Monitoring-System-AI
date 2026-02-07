
import asyncio, time
from stream.bus import consume
from storage.db import insert
from agents.ai_agent import analyze

state = {}

async def run():
    while True:
        for t in ["dau","trade","completeness"]:
            try:
                m = await asyncio.wait_for(consume(t), 0.05)
                # persist raw metric
                insert(t, tuple(m.values()))
                # update state
                state.update(m)
                # AI insights
                for i in analyze(state):
                    insert("ai", (i["severity"], i["confidence"], i["nl"], i["impact"], i["actions"], int(time.time()*1000)))
            except Exception:
                pass
        await asyncio.sleep(0.05)
