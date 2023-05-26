class Device:
    def __init__(self, id=None, name="", host="", password="", region="", institution=""):
        self.id = id
        self.name = name
        self.host = host
        self.password = password
        self.region = region
        self.institution = institution
    
    def init_by_json(self, data):
        if "id" not in data:
            return "ID not specified"
            
        if "name" not in data:
            return "Name not specified"
        
        id = data["id"]
        if type(id) != type(0):
            return "Wrong ID type"
        self.id = id

        name = data["name"]
        if type(name) != type(""):
            return "Wrong name type"
        self.name = name

        if "password" in data:
            password = data["password"]
            if type(password) != type(""):
                return "Wrong password type"
            self.password = password
        
        if "region" in data:
            region = data["region"]
            if type(region) != type(""):
                return "Wrong region type"
            self.region = region
        
        if "institution" in data:
            institution = data["institution"]
            if type(institution) != type(""):
                return "Wrong institution type"
            self.institution = institution

        if "host" in data:
            host = data["host"]
            if type(host) != type(""):
                return "Wrong host type"
            self.host = host

        return 0