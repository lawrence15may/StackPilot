# aws_mcp.py
import os
import json
import logging
from fastapi import FastAPI, WebSocket
import uvicorn
from tools.ec2_tool import router as ec2_router
from tools.s3_tool import router as s3_router
from tools.iam_tool import router as iam_router
from tools.cost_tool import router as cost_router
from tools.vpc_tool import router as vpc_router
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="aws-mcp-server")

# Mount tool routers (each tool provides APIRouter with methods)
app.include_router(ec2_router, prefix="/ec2")
app.include_router(s3_router, prefix="/s3")
app.include_router(iam_router, prefix="/iam")
app.include_router(cost_router, prefix="/cost")
app.include_router(vpc_router, prefix="/vpc")

@app.get("/")
def root():
    return {"server": "aws-mcp", "version": "1.0"}

# (Optional) WebSocket endpoint for MCP-style interactions
@app.websocket("/mcp/ws")
async def mcp_ws(ws: WebSocket):
    await ws.accept()
    await ws.send_text(json.dumps({"message": "aws-mcp websocket ready"}))
    while True:
        data = await ws.receive_text()
        # Very small router - you *should* implement full JSON-RPC for production
        await ws.send_text(json.dumps({"echo": data}))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("MCP_PORT", 8080)))

