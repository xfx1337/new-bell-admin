import os
import json
import db.connection

from user import User
import db.users
import db.tokens
import db.admin_events

import services.auth
import services.communication
import services.info

from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def main_page():
    return "Nothing here"

@app.route('/api/users/register', methods = ['POST'])
def user_register():
    if not tokens.valid(request.args.get('token')): 
            return 'Permission denied', 403
    return services.auth.register_user(request)

@app.route('/api/login', methods = ['POST'])
def login():
    return services.auth.login_user(request)


@app.route('/api/devices/register', methods = ['POST'])
def device_register():
    return services.auth.register_device(request)

@app.route('/api/admin/approve', methods = ['POST'])
def approve_device():
    if not db.tokens.valid(request.args.get('token')): 
            return 'Permission denied', 403
    return services.auth.approve_device(request)


@app.route('/api/admin/get_events', methods = ['POST'])
def get_events():
    if not db.tokens.valid(request.args.get('token')): 
        return 'Permission denied', 403

    return db.admin_events.get_events_json()


@app.route('/api/admin/devices', methods = ['GET'])
def devices():
    if not db.tokens.valid(request.args.get('token')): 
        return 'Permission denied', 403
    
    return services.info.get_unverified_devices(request) if request.args.get('unverified') in ('true', '') else services.info.get_devices(request)

@app.route('/api/stat')
def stat():
    pass

@app.route('/api/refresh', methods = ['POST'])
def refresh():
    return services.communication.refresh(request)

if __name__ == '__main__':
    
    if not db.connection.exists():
        print("[DB] No database found.")
        db.connection.create_database()

    app.run()