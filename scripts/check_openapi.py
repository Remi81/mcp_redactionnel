from fastapi.testclient import TestClient

from mcp_redactionnel import api

client = TestClient(api.app)
r = client.get("/openapi.json")
print("STATUS", r.status_code)
js = r.json()
print("OPENAPI:", js.get("openapi"))
print("\nPATHS:")
for p in sorted(js.get("paths").keys()):
    print(" -", p)

red = js["paths"]["/redaction"]["post"]
req = red["requestBody"]["content"]["application/json"]["schema"]
print("\n/redaction request schema ref or inline:", req)
if "$ref" in req:
    name = req["$ref"].split("/")[-1]
    schema = js["components"]["schemas"][name]
else:
    schema = req
print("\nSchema properties:", list(schema.get("properties", {}).keys()))
print("'format' present:", "format" in schema.get("properties", {}))
print("\nRedaction example:", schema.get("example"))

# Check mise_en_forme
mef = js["paths"]["/mise_en_forme"]["post"]
mef_req = mef["requestBody"]["content"]["application/json"]["schema"]
if "$ref" in mef_req:
    name = mef_req["$ref"].split("/")[-1]
    mef_schema = js["components"]["schemas"][name]
else:
    mef_schema = mef_req
print(
    "\n/mise_en_forme schema properties:", list(mef_schema.get("properties", {}).keys())
)
