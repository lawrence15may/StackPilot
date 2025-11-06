# tools/vpc_tool.py
from fastapi import APIRouter
import boto3

router = APIRouter()
ec2 = boto3.client("ec2")

@router.get("/list_subnets")
def list_subnets(region: str = None):
    client = boto3.client("ec2", region_name=region)
    res = client.describe_subnets()
    return [{"SubnetId": s["SubnetId"], "VpcId": s["VpcId"], "CidrBlock": s["CidrBlock"]} for s in res.get("Subnets", [])]

@router.post("/create_sg")
def create_sg(vpc_id: str, name: str, description: str = "MCP SG", ingress: list = None):
    res = ec2.create_security_group(GroupName=name, Description=description, VpcId=vpc_id)
    gid = res["GroupId"]
    if ingress:
        ec2.authorize_security_group_ingress(GroupId=gid, IpPermissions=ingress)
    return {"GroupId": gid}

