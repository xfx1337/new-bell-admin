import json
from common import all_priveleges


class User:
    def __init__(self, username="", pass_md5="", privileges="user"):
        self.username = username
        self.pass_md5 = pass_md5
        self.privileges = privileges
    
    def init_by_json(self, data):
        if "username" not in data:
            return -1
        
        username = data["username"]
        if type(username) != type(""):
            return -1
        self.username = username

        if "password" not in data:
            return -1
        
        pass_md5 = data["password"]
        if type(pass_md5) != type(""):
            return -1
        self.pass_md5 = pass_md5
            
        if "privileges" not in data:
            return -1
        
        privileges = data["privileges"]
        if type(privileges) != type(""):
            return -1
        if privileges not in all_priveleges:
            return -1
        self.privileges = privileges
        
        return 0