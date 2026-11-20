"""MCP server (stdio JSON-RPC, stdlib) exposing place/check/qor tools. Run: python -m layout_qor.mcp_server"""
import json, sys, glob, os
from .netlist import load
from .agent import make_tools

CELLS = {os.path.splitext(os.path.basename(p))[0]: p for p in glob.glob(os.path.join(os.path.dirname(__file__), "..", "examples", "*.sp"))}
TOOLS = [{"name": n, "description": d, "inputSchema": {"type": "object", "properties": {"cell": {"type": "string"}}}}
         for n, d in [("place", "Place a cell (SA)"), ("check", "DRC/LVS check"), ("qor", "Elmore QoR estimate")]]

def handle(req):
    m, rid = req.get("method"), req.get("id")
    if m == "initialize": return {"jsonrpc": "2.0", "id": rid, "result": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "layout-qor", "version": "0.1.0"}}}
    if m == "tools/list": return {"jsonrpc": "2.0", "id": rid, "result": {"tools": TOOLS}}
    if m == "tools/call":
        name = req["params"]["name"]; cell = req["params"].get("arguments", {}).get("cell", "inv")
        nl = load(CELLS[cell]); st = {}; tools = make_tools(nl, st)
        if name == "place": out = tools["place"]()
        else:
            tools["place"](); out = tools[name]()
        return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": json.dumps(out, default=str)}]}}
    return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": "unknown method"}}

def main():
    for line in sys.stdin:
        if line.strip(): print(json.dumps(handle(json.loads(line))), flush=True)
if __name__ == "__main__": main()
