
def analyze(state):
    insights=[]
    ratio=state.get("ratio",1)
    vol=state.get("volume",0)
    dau=state.get("value",None)

    # Completeness
    if ratio < 0.9:
        conf = min(0.99, 0.65 + (0.9-ratio)*2.0)  # stronger drop => higher confidence
        insights.append({
            "severity":"HIGH",
            "confidence":round(conf,2),
            "nl":"Data completeness is below the SLA. Immediate action is recommended to avoid incorrect reporting.",
            "impact":"If ignored for 24h, dashboards and ML models may be unreliable; backfills will be larger and slower.",
            "actions":"Backfill data,Check ingestion pipeline,Verify partitioning,Notify data team"
        })
    elif ratio < 0.98:
        conf = 0.72
        insights.append({
            "severity":"MEDIUM",
            "confidence":conf,
            "nl":"Data completeness is slightly below target. Monitor closely and prepare a partial backfill.",
            "impact":"If ignored, minor reporting drift may accumulate and erode trust in KPIs.",
            "actions":"Inspect late arrivals,Check upstream retries,Plan partial backfill"
        })

    # Trade spike
    if vol > 5_000_000:
        conf = 0.82 if vol < 12_000_000 else 0.9
        insights.append({
            "severity":"MEDIUM",
            "confidence":conf,
            "nl":"Trade volume is significantly higher than normal and may indicate duplicates, a market event, or fraud.",
            "impact":"If ignored, risk controls may be bypassed or false positives may trigger downstream alerts.",
            "actions":"Validate trade source,Check dedupe keys,Run fraud detection,Confirm market event"
        })

    # DAU crash
    if dau is not None and dau < 1500:
        insights.append({
            "severity":"HIGH",
            "confidence":0.88,
            "nl":"Active users are unusually low; this may indicate an outage or tracking failure.",
            "impact":"If ignored, customers may be unable to trade; revenue and retention can drop rapidly.",
            "actions":"Check auth/login,Inspect app errors,Verify analytics pipeline,Escalate incident"
        })

    return insights
