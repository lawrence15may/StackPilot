# tools/cost_tool.py
from fastapi import APIRouter
import boto3
from datetime import datetime, timedelta

router = APIRouter()
ce = boto3.client("ce")

@router.get("/monthly_cost")
def monthly_cost(days: int = 30):
    end = datetime.utcnow().date()
    start = end - timedelta(days=days)
    res = ce.get_cost_and_usage(TimePeriod={"Start": str(start), "End": str(end)},
                                Granularity="MONTHLY",
                                Metrics=["UnblendedCost"])
    return res.get("ResultsByTime", [])

