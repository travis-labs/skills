import json, os, sys, time, urllib.request
KEY = [l.split("=",1)[1].strip() for l in open(os.environ.get("KIE_ENV_FILE", os.path.expanduser("~/kie/.env"))) if l.startswith("KIE_API_KEY=")][0]
H = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json", "Accept": "application/json"}
def call(method, path, body=None):
    req = urllib.request.Request("https://api.kie.ai" + path, data=json.dumps(body).encode() if body else None, headers=H, method=method)
    with urllib.request.urlopen(req, timeout=60) as r: return json.load(r)
if __name__ == "__main__":
    print(call("GET", "/api/v1/chat/credit"))
