import urllib.request
import json
import sys

token = sys.argv[1]
repo_name = "OBS-Virtual-Camera-App"

req = urllib.request.Request("https://api.github.com/user/repos", data=json.dumps({"name": repo_name, "private": False}).encode("utf-8"), headers={
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json",
    "Content-Type": "application/json"
})

try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        print(f"SUCCESS: {result['clone_url']}")
except urllib.error.HTTPError as e:
    err_msg = e.read().decode()
    if "name already exists" in err_msg:
        # Fetch the existing repo URL
        req2 = urllib.request.Request("https://api.github.com/user", headers={"Authorization": f"token {token}"})
        with urllib.request.urlopen(req2) as res2:
            user_data = json.loads(res2.read().decode())
            print(f"SUCCESS: https://github.com/{user_data['login']}/{repo_name}.git")
    else:
        print(f"FAILED: {e.code} - {err_msg}")
except Exception as e:
    print(f"FAILED: {e}")
