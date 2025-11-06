# tools/s3_tool.py
from fastapi import APIRouter
import boto3

router = APIRouter()

s3 = boto3.client("s3")

@router.get("/list")
def list_buckets():
    res = s3.list_buckets()
    return [b["Name"] for b in res.get("Buckets", [])]

@router.post("/create")
def create_bucket(name: str, region: str = None):
    kwargs = {"Bucket": name}
    if region and region != "us-east-1":
        kwargs["CreateBucketConfiguration"] = {"LocationConstraint": region}
    s3.create_bucket(**kwargs)
    return {"bucket": name, "message": "created"}

@router.post("/delete")
def delete_bucket(name: str):
    # safe-delete: attempt to empty bucket first (careful)
    # Caller responsibility to confirm destructive actions
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=name):
        if "Contents" in page:
            objs = [{"Key": c["Key"]} for c in page["Contents"]]
            s3.delete_objects(Bucket=name, Delete={"Objects": objs})
    s3.delete_bucket(Bucket=name)
    return {"bucket": name, "message": "deleted"}

