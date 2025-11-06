# tools/iam_tool.py
from fastapi import APIRouter
import boto3

router = APIRouter()
iam = boto3.client("iam")

@router.get("/list_users")
def list_users():
    res = iam.list_users()
    return [{"UserName": u["UserName"], "Arn": u["Arn"], "CreateDate": str(u["CreateDate"])} for u in res.get("Users", [])]

@router.get("/list_roles")
def list_roles():
    res = iam.list_roles()
    return [{"RoleName": r["RoleName"], "Arn": r["Arn"]} for r in res.get("Roles", [])]

@router.post("/create_role")
def create_role(role_name: str, assume_policy_document: dict):
    res = iam.create_role(RoleName=role_name, AssumeRolePolicyDocument=json.dumps(assume_policy_document))
    return {"Role": res["Role"]["RoleName"], "Arn": res["Role"]["Arn"]}

@router.post("/delete_role")
def delete_role(role_name: str):
    iam.delete_role(RoleName=role_name)
    return {"role": role_name, "message": "deleted"}

