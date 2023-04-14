import json
from common import all_priveleges


class User:
    def __init__(self, username="", password="", privileges="user"):
        self.username = username
        self.password = password
        self.privileges = privileges
    
    def init_by_json(self, data):
        if "username" not in data:
            return "Username not specified"
        
        username = data["username"]
        if type(username) != type(""):
            return "Wrong username type"
        self.username = username

        if "password" not in data:
            return "Password not specified"
        
        password = data["password"]
        if type(password) != type(""):
            return "Wrong password type"
        self.password = password
            
        if "privileges" not in data:
            return "Privileges not specified"
        
        privileges = data["privileges"]
        if type(privileges) != type(""):
            return "Wrong privileges type"
        if privileges not in all_priveleges:
            return "Wrong priveleges"
        self.privileges = privileges

        return 0