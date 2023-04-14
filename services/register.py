from user import User
import db.tokens as tokens
import db.users as users
import json

def register(request):
    if request.method == "POST":
        data = request.get_json()
        if tokens.validate_token(data) != 0:
            return "Auth error", 400
        
        if "user" in data:
            user = User()
            ret = user.init_by_json(data["user"])
            if ret != 0:
                return "Invalid user creditionals", 400
            
            ret = users.register(user)
            if ret != 0:
                return "User is already exists", 400
            ret = tokens.register(user.username)
            ret = {"token": ret}
            return json.dumps(ret, indent=4), 200
        else:
            return "Invalid prompt", 400
    else:
        return "Invalid prompt", 400