from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import os

app = FastAPI()

# Enable CORS for POST from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load telemetry data
file_path = os.path.join(os.path.dirname(__file__), "../telemetry.csv")
df = pd.read_csv(file_path)

@app.post("/api/latency")
async def analyze_latency(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)

    filtered = df[df["region"].isin(regions)]

    results = {}

    for region in regions:
        region_data = filtered[filtered["region"] == region]

        if region_data.empty:
            continue

        avg_latency = float(region_data["latency_ms"].mean())
        p95_latency = float(np.percentile(region_data["latency_ms"], 95))
        avg_uptime = float(region_data["uptime"].mean())
        breaches = int((region_data["latency_ms"] > threshold).sum())

        results[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches
        }

    return results
