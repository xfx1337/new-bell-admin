import json
import db.devices
import db.tokens

def refresh(req):
    validation_results = db.tokens.valid(req.get_json())
    if validation_results != 0:
        return validation_results, 400
    
    db.devices.refresh(req.get_json())
    return 'Ok', 300