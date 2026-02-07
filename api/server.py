
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, PlainTextResponse
import asyncio, time, random
from agents.dau_agent import ingest as dau
from agents.trade_agent import ingest as trade
from agents.completeness_agent import ingest as comp
from storage.db import fetch

app = FastAPI()

# demo stream task handle
_demo_task = None
_demo_running = False

REGIONS = ["us-east","eu-west","ap-south"]

def _now_ms():
    return int(time.time()*1000)

def _good_payloads():
    return {
        "dau": {"region": random.choice(REGIONS), "value": random.randint(8000, 22000)},
        "trade": {"region": random.choice(REGIONS), "count": random.randint(120, 900), "volume": round(random.uniform(250000, 2500000), 2)},
        "completeness": {"region": random.choice(REGIONS), "expected": 1440, "observed": random.randint(1410, 1440), "ratio": round(random.uniform(0.98, 1.0), 3)},
    }

def _bad_payloads():
    # create issues that trigger AI
    bad_type = random.choice(["completeness","trade","dau"])
    if bad_type == "completeness":
        observed = random.randint(600, 1100)
        return {"completeness": {"region": random.choice(REGIONS), "expected": 1440, "observed": observed, "ratio": round(observed/1440, 3)}}
    if bad_type == "trade":
        return {"trade": {"region": random.choice(REGIONS), "count": random.randint(10, 80), "volume": round(random.uniform(6000000, 15000000), 2)}}
    return {"dau": {"region": random.choice(REGIONS), "value": random.randint(200, 1400)}}

async def _ingest(agent: str, data: dict):
    data["event_ts"] = _now_ms()
    if agent == "dau":
        await dau(data)
    elif agent == "trade":
        await trade(data)
    elif agent == "completeness":
        await comp(data)

async def _demo_loop(mode: str):
    global _demo_running
    _demo_running = True
    while _demo_running:
        if mode == "good":
            payloads = _good_payloads()
        elif mode == "bad":
            payloads = _bad_payloads()
        else:
            # mixed
            payloads = _good_payloads()
            if random.random() < 0.35:
                payloads.update(_bad_payloads())

        for agent, payload in payloads.items():
            await _ingest(agent, payload)

        await asyncio.sleep(0.8)  # fast enough to look live

@app.get("/", response_class=HTMLResponse)
def ui():
    return open("api/ui.html").read()

@app.post("/ingest/{agent}")
async def ingest(agent: str, data: dict):
    await _ingest(agent, data)
    return {"status": "ok"}

@app.post("/demo/start")
async def demo_start(mode: str = "mixed"):
    global _demo_task, _demo_running
    if _demo_task and not _demo_task.done():
        return {"status":"already_running","mode":mode}
    _demo_running = True
    _demo_task = asyncio.create_task(_demo_loop(mode))
    return {"status":"started","mode":mode}

@app.post("/demo/stop")
async def demo_stop():
    global _demo_running
    _demo_running = False
    return {"status":"stopped"}

@app.get("/demo/status")
async def demo_status():
    global _demo_task, _demo_running
    return {"running": bool(_demo_running and _demo_task and not _demo_task.done())}

@app.get("/data/{table}")
def data(table: str):
    return fetch(table, limit=30)

@app.get("/incident/report", response_class=PlainTextResponse)
def report():
    ai = fetch("ai", limit=1)
    if not ai:
        return "No incidents detected."
    i = ai[0]
    return f"""INCIDENT REPORT

Severity: {i[0]}
Confidence: {int(i[1]*100)}%

Summary:
{i[2]}

Impact:
{i[3]}

Recommended Actions:
{i[4]}
"""
