from user import User
import db.tokens
import db.users
import db.devices
import json

def register_user(request):
    if request.method == "POST":
        data = request.get_json()
        if not db.tokens.valid(data):
            return "Auth error", 400
        
        if "user" in data:
            user = User()
            ret = user.init_by_json(data["user"])
            if ret != 0:
                return "Invalid user creditionals", 400
            
            ret = db.users.register(user)
            if ret != 0:
                return "User is already exists", 400
            ret = db.tokens.register(user.username)
            ret = {"token": ret}
            return json.dumps(ret, indent=4), 200
        else:
            return "Invalid prompt", 400
    else:
        return "Invalid prompt", 400
        
def register_device(request):
    data = request.get_json()

    db.devices.add_unverified(name=data['name'], password=data['password'])

    return 'Ok'

def approve_device(request):
    data = request.get_json()


    return 'Ok'