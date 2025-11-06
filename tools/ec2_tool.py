# tools/ec2_tool.py
from fastapi import APIRouter, HTTPException
import boto3
import os

router = APIRouter()

def _session(region=None):
    session = boto3.Session()
    return session.client("ec2", region_name=region)

@router.get("/list")
def list_instances(region: str = None):
    ec2 = _session(region)
    res = ec2.describe_instances()
    out = []
    for r in res.get("Reservations", []):
        for i in r.get("Instances", []):
            out.append({
                "instance_id": i.get("InstanceId"),
                "type": i.get("InstanceType"),
                "state": i.get("State", {}).get("Name"),
                "private_ip": i.get("PrivateIpAddress"),
                "public_ip": i.get("PublicIpAddress"),
                "launch_time": str(i.get("LaunchTime")),
            })
    return out

@router.post("/create")
def create_instance(ami_id: str, instance_type: str = "t3.micro", key_name: str = None, subnet_id: str = None, security_group_ids: list = None, region: str = None):
    ec2 = _session(region)
    params = dict(ImageId=ami_id, InstanceType=instance_type, MinCount=1, MaxCount=1)
    if key_name: params["KeyName"] = key_name
    if subnet_id: params["SubnetId"] = subnet_id
    if security_group_ids: params["SecurityGroupIds"] = security_group_ids
    res = ec2.run_instances(**params)
    iid = res["Instances"][0]["InstanceId"]
    return {"instance_id": iid, "message": "Instance launched"}

@router.post("/terminate")
def terminate_instance(instance_id: str, region: str = None):
    ec2 = _session(region)
    ec2.terminate_instances(InstanceIds=[instance_id])
    return {"instance_id": instance_id, "message": "Termination requested"}

@router.post("/modify")
def modify_instance_type(instance_id: str, new_type: str, region: str = None):
    ec2 = _session(region)
    # Stop -> modify -> start (note: some instance types may not be supported on old Nitro families)
    ec2.stop_instances(InstanceIds=[instance_id])
    waiter = ec2.get_waiter("instance_stopped")
    waiter.wait(InstanceIds=[instance_id])
    ec2.modify_instance_attribute(InstanceId=instance_id, Attribute="instanceType", Value=new_type)
    ec2.start_instances(InstanceIds=[instance_id])
    return {"instance_id": instance_id, "message": f"Modified to {new_type} and started"}

