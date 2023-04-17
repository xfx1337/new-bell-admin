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

app = Flask(__name__)

@app.route('/api/users/register', methods = ['POST'])
def user_register():
    if not db.tokens.valid(request.args.get('token')): 
            return 'Permission denied', 403
    return services.auth.register_user(request)

@app.route('/api/login', methods = ['POST'])
def login():
    return services.auth.login_user(request)

@app.route('/api/users/delete', methods = ['POST'])
def user_delete():
    if not db.tokens.valid(request.args.get('token')):
          return 'Peermission denied', 403
    return services.auth.delete_user(request)

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

@app.route('/api/devices/wait_for_registration', methods = ['POST'])
def wait():
    return services.communication.device_wait_for_registration(request)

@app.route('/api/refresh', methods = ['POST'])
def refresh():
    return services.communication.refresh(request)

@app.route('/api/devices/request', methods=['POST'])
def testrequest():
    return db.devices.request(request)

@app.route('/api/admin/statistics_view', methods=['GET'])
def statistics_view():
    if not db.tokens.valid(request.args.get('token')): 
        return 'Permission denied', 403
    
    return f'''<div>statistics</div>
    <script>
        var last_index = 0;
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/api/admin/statistics?token={request.args.get('token')}");
        xhr.onprogress = function () {{
            var curr_index = xhr.responseText.length;
            if (last_index == curr_index) return; 
            var s = xhr.responseText.substring(last_index, curr_index);
            last_index = curr_index;
            
            var div = document.createElement('div');
            div.innerHTML = s;
            document.body.appendChild(div);

        }};
        xhr.send();
    </script>
    ''', request.args.get('token')

@app.route('/api/admin/statistics', methods = ['POST'])
def statistics():
    if not db.tokens.valid(request.args.get('token')): 
        return 'Permission denied', 403
    
    breaktime = datetime.now() + timedelta(minutes=5)

    if request.data:
        data = request.get_json()
        if "breaktime" not in data:
            breaktime = datetime.now() + timedelta(minutes=5)
        else:
            breaktime = datetime.now() + data["breaktime"]

    return Response(services.info.statistics_stream(request, breaktime), mimetype="text/event-stream")


if __name__ == '__main__':
    
    if not db.connection.exists():
        print("[DB] No database found.")
        db.connection.create_database()

    app.run(threaded=True)