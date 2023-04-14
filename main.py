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
        if tokens_db.validate_token(data) != 0:
            return "Auth error", 400
        
        if "user" in data:
            user = User()
            ret = user.init_by_json(data["user"])
            if ret != 0:
                return "Invalid user creditionals", 400
            
            ret = users_db.register(user)
            if ret != 0:
                return "User is already exists", 400
            ret = tokens_db.register(user.username)
            ret = {"token": ret}
            return json.dumps(ret, indent=4), 200
        else:
            return "Invalid prompt", 400
    else:
        return "Invalid prompt", 400

@app.route('/api/login', methods = ['POST'])
def login():
    data = request.get_json()
    ret = users_db.login(data)
    if ret == -1:
        return "Invalid user creditionals", 400
    ret = {"token": ret}
    return json.dumps(ret, indent=4), 200


if __name__ == '__main__':
    app.run()