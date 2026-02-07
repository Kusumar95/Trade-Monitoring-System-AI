
import asyncio, uvicorn
from aggregator.aggregator import run
from api.server import app

async def bg():
    await run()

if __name__ == "__main__":
    asyncio.get_event_loop().create_task(bg())
    uvicorn.run(app, host="0.0.0.0", port=8000)
