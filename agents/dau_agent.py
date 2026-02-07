
from stream.bus import publish
from agents.base import enrich
async def ingest(d): await publish("dau",enrich(d))
