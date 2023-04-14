import json
import db.users

def login(request):
    data = request.get_json()
    ret = db.users.login(data)
    if ret == -1:
        return "Invalid user creditionals", 400
    ret = {"token": ret}
    return json.dumps(ret, indent=4), 200