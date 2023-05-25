import os
import json
from datetime import datetime, timedelta

import db.connection

from user import User
import db.users
import db.tokens
import db.admin_events

import services.auth
import services.communication
import services.info


from flask import Flask, jsonify, request, Response
from flask_cors import CORS



app = Flask(__name__)
CORS(app)

@app.route('/api/users/register', methods = ['POST'])
def user_register():
    if not db.tokens.valid_bearer(request.headers.get("Authorization")): 
        return 'Permission denied', 403
    return services.auth.register_user(request)

@app.route('/api/login', methods = ['POST'])
def login():
    return services.auth.login_user(request)

@app.route('/api/users/delete', methods = ['POST'])
def user_delete():
    if not db.tokens.valid_bearer(request.headers.get("Authorization")): 
        return 'Permission denied', 403
    return services.auth.delete_user(request)

@app.route('/api/devices/register', methods = ['POST'])
def device_register():
    return services.auth.register_device(request)

@app.route('/api/admin/approve', methods = ['POST'])
def approve_device():
    if not db.tokens.valid_bearer(request.headers.get("Authorization")): 
        return 'Permission denied', 403
    return services.auth.approve_device(request)


@app.route('/api/admin/get_events', methods = ['POST'])
def get_events():
    if not db.tokens.valid_bearer(request.headers.get("Authorization")): 
        return 'Permission denied', 403
    return db.admin_events.get_events_json(db.tokens.get_username(request.headers.get("Authorization")))

@app.route('/api/admin/read_events', methods = ['POST'])
def read_events():
    if not db.tokens.valid_bearer(request.headers.get("Authorization")): 
        return 'Permission denied', 403
    return services.info.read_events(request)


@app.route('/api/admin/devices', methods = ['GET'])
def devices():
    if not db.tokens.valid(request.args.get('token')): 
        return 'Permission denied', 403
    return services.info.get_unverified_devices(request) if request.args.get('unverified') in ('true', '') else services.info.get_devices(request)

@app.route('/api/devices/wait_for_registration', methods = ['POST'])
def wait():
    return services.communication.device_wait_for_registration(request)

@app.route('/api/devices/refresh', methods = ['POST'])
def refresh():
    if not db.tokens.valid_bearer(request.headers.get("Authorization")): 
        return 'Permission denied', 403
    return services.communication.refresh(request, request.headers.get("Authorization").split()[1])

@app.route('/api/admin/request', methods=['POST'])
def admin_request():
    if not db.tokens.valid_bearer(request.headers.get("Authorization")): 
        return 'Permission denied', 403
    return services.communication.request(request)

    # {"type": "UPDATE", "ids": [0, 2, 5]}
    # {"type": "EXECUTE", "ids": [0, 2, 5], "PROMPT": "reboot"}
    # {"type": "LOCK", "ids": [0, 2, 5]}
    # {"type": "UNLOCK", "ids": [0, 2, 5]}

@app.route('/api/devices/response', methods=['POST'])
def get_response():
    if not db.tokens.valid_bearer(request.headers.get("Authorization")): 
        return 'Permission denied', 403
    return services.communication.response(request, request.headers.get("Authorization").split()[1])

@app.route('/api/admin/statistics_view', methods=['GET'])
def statistics_view():
    if not db.tokens.valid(request.args.get('token')): 
        return 'Permission denied', 403
    
    return f'''<div>statistics</div>
    <script>
        var last_index = 0;
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/api/admin/statistics");
        xhr.setRequestHeader("Authorization", "Bearer {request.args.get('token')}");
        xhr.onprogress = function () {{
            var curr_index = xhr.responseText.length;
            if (last_index == curr_index) return; 
            var s = xhr.responseText.substring(last_index, curr_index);
            last_index = curr_index;
            
            var div = document.createElement('div');
            div.innerHTML = s;
            console.log(s)
            document.body.appendChild(div);

        }};
        xhr.send();
    </script>
    ''', request.args.get('token')

@app.route('/api/admin/statistics', methods = ['POST'])
def statistics():
    if not db.tokens.valid_bearer(request.headers.get("Authorization")): 
        return 'Permission denied', 403
    
    breaktime = datetime.now() + timedelta(minutes=5)

    if request.data:
        data = request.get_json()
        if "breaktime" not in data:
            breaktime = datetime.now() + timedelta(minutes=5)
        else:
            breaktime = datetime.now() + data["breaktime"]

    return Response(services.info.statistics_stream(request, request.headers.get("Authorization").split()[1], breaktime), mimetype="text/event-stream")


if __name__ == '__main__':
    
    if not db.connection.exists():
        print("[DB] No database found.")
        db.connection.create_database()

    app.run(threaded=True, debug=True, host="0.0.0.0")
    CORS(app)