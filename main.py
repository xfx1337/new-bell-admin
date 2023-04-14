import os
import json

if not os.path.exists("database.db"):
    print("[DB] No database found.")
    connection.create_database()

import db.connection as connection
from user import User
import db.users as users
import db.tokens as tokens
from services.register import register as register_service
from services.login import login as login_service
from services.refresh import refresh as refresh_service

from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def main_page():
    return "Nothing here"

@app.route('/api/admin/register', methods = ['POST'])
def register():
    return register_service(request)

@app.route('/api/login', methods = ['POST'])
def login():
    return login_service(request)

@app.route('/api/stat')
def stat():
    pass

@app.route('/api/refresh', methods = ['POST'])
def refresh():
    return refresh_service(request)

if __name__ == '__main__':
    app.run()