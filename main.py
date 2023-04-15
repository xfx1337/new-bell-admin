import os
import json
import db.connection

from user import User
import db.users as users
import db.tokens as tokens
from services.register import register_user
from services.register import register_device
from services.login import login as login_service
from services.refresh import refresh as refresh_service
from services.register import approve_device as approve
from services.info import unverified_devices as unverified_devices
from services.info import devices as alldevices
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def main_page():
    return "Nothing here"

@app.route('/api/users/register', methods = ['POST'])
def user_register():
    return register_user(request)

@app.route('/api/devices/register', methods = ['POST'])
def device_register():
    return register_device(request)

@app.route('/api/admin/approve', methods = ['POST'])
def approve_device():
    data = request.get_json()

    return approve(request) if tokens.valid(tokens.get_from(data)) else ('Permission denied', 403) 

@app.route('/api/admin/devices', methods = ['GET'])
def devices():

    if not tokens.valid(request.args.get('token')): 
        return 'Permission denied', 403
    
    return unverified_devices(request) if request.args.get('unverified') in ('true', '') else alldevices(request)

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
    
    if not db.connection.exists():
        print("[DB] No database found.")
        db.connection.create_database()

    app.run()