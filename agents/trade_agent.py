
from stream.bus import publish
from agents.base import enrich
async def ingest(d): await publish("trade",enrich(d))
