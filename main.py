import os
import json

db_exists = True

if not os.path.exists("database.db"):
    print("[DB] No database found.")
    db_exists = False

import db_connection
if db_exists == False:
    db_connection.create_db()

from user_class import User
import users_db
import tokens_db

from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def main_page():
    return "Nothing here"

@app.route('/api/admin/register', methods = ['POST'])
def register():
    if request.method == "POST":
        data = request.get_json()
        ret = tokens_db.validate_token(data)
        if ret != 0:
            return ret, 400
        
        if "user" not in data:
            return "Invalid prompt", 400
        
        user = User()
        ret = user.init_by_json(data["user"])
        if ret != 0:
            return ret, 400
        
        ret = users_db.register(user)
        if ret != 0:
            return ret, 400
        
        ret = tokens_db.register(user.username)
        ret = {"token": ret}
        return json.dumps(ret, indent=4), 200
            
    else:
        return "Invalid request", 400

@app.route('/api/login', methods = ['POST'])
def login():
    if request.method == "POST":
        data = request.get_json()
        ret, token = users_db.login(data)
        if ret != 0:
            return ret, 400
       
        ret = {"token": token}
        return json.dumps(ret, indent=4), 200


if __name__ == '__main__':
    app.run()