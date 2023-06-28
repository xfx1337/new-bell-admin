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

from monitoring import Monitoring

from flask import Flask, jsonify, request, Response

from flask_socketio import SocketIO, emit, send, Namespace
from flask_socketio import ConnectionRefusedError
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

# monitoring
mon = Monitoring(app, socketio)

# DONT DELETE
import re
@app.after_request
def after_request(response):
    response.headers.add('Accept-Ranges', 'bytes')
    return response
def get_chunk(byte1=None, byte2=None):
    full_path = "vazelin.mp4"
    file_size = os.stat(full_path).st_size
    start = 0
    
    if byte1 < file_size:
        start = byte1
    if byte2:
        length = byte2 + 1 - byte1
    else:
        length = file_size - start

    with open(full_path, 'rb') as f:
        f.seek(start)
        chunk = f.read(length)
    return chunk, start, length, file_size
@app.route('/')
def get_file():
    range_header = request.headers.get('Range', None)
    byte1, byte2 = 0, None
    if range_header:
        match = re.search(r'(\d+)-(\d*)', range_header)
        groups = match.groups()

        if groups[0]:
            byte1 = int(groups[0])
        if groups[1]:
            byte2 = int(groups[1])
       
    chunk, start, length, file_size = get_chunk(byte1, byte2)
    resp = Response(chunk, 206, mimetype='video/mp4',
                      content_type='video/mp4', direct_passthrough=True)
    resp.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size))
    return resp


@app.route('/api/valid_token', methods=['POST'])
def valid_token():
    if not db.tokens.valid_bearer(request.headers.get("Authorization")): 
        return 'Token is not valid', 403
    return "Token is valid", 200


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

@app.route('/api/admin/create_event', methods = ['POST'])
def create_event():
    if not db.tokens.valid_bearer(request.headers.get("Authorization")): 
        return 'Permission denied', 403
    return services.info.create_event(request)

@app.route('/api/users/info', methods = ['POST'])
def user_info():
    if not db.tokens.valid_bearer(request.headers.get("Authorization")): 
        return 'Permission denied', 403
    return services.info.get_user_info(request)

@app.route('/api/devices/info', methods = ['POST'])
def get_device_info():
    if not db.tokens.valid_bearer(request.headers.get("Authorization")): 
        return 'Permission denied', 403
    return services.info.get_device_info_json(request)

@app.route('/api/admin/devices', methods = ['GET', 'POST'])
def devices():
    if request.method == 'GET':
        if not db.tokens.valid(request.args.get('token')): 
            return 'Permission denied', 403
    elif request.method == 'POST':
        if not db.tokens.valid_bearer(request.headers.get("Authorization")): 
            return 'Permission denied', 403
    return services.info.get_unverified_devices() if request.args.get('unverified') in ('true', '') else services.info.get_devices()

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

@app.route('/api/devices/response', methods=['POST'])
def get_response():
    if not db.tokens.valid_bearer(request.headers.get("Authorization")): 
        return 'Permission denied', 403
    return services.communication.response(request, request.headers.get("Authorization").split()[1])

@app.route('/api/admin/sql_get', methods=["POST"])
def sql_get():
    if not db.tokens.valid_bearer(request.headers.get("Authorization")): 
        return 'Permission denied', 403
    ret, priv = db.users.get_privileges(db.tokens.get_username(request.headers.get('Authorization')))
    if priv != "owner" and priv != "admin":
        return 'Permission denied', 403

    return services.info.get_sql(request)

@app.route('/api/admin/get_processes', methods=["POST", "GET"])
def get_processes():
    if not db.tokens.valid_bearer(request.headers.get("Authorization")): 
        return 'Permission denied', 403
    return services.info.get_processes(request)

@app.route('/api/admin/process_info', methods=["POST"])
def get_process_info():
    if not db.tokens.valid_bearer(request.headers.get("Authorization")): 
        return 'Permission denied', 403
    return services.info.get_process_info(request)

@app.route('/api/admin/get_process_responses', methods=["POST"])
def get_process_responses():
    if not db.tokens.valid_bearer(request.headers.get("Authorization")): 
        return 'Permission denied', 403
    return services.info.get_process_responses(request)

@app.route('/api/devices/sync_processes', methods=["POST"])
def sync_processes():
    if not db.tokens.valid_bearer(request.headers.get("Authorization")): 
        return 'Permission denied', 403
    return services.communication.sync_processes(request)


# for monitoring!
@socketio.on('connect', namespace="/mainIO")
def admin_connect(auth):
    if not db.tokens.valid_bearer(request.headers.get("Authorization")): 
        return 'Permission denied', 403
    ret, priv = db.users.get_privileges(db.tokens.get_username(request.headers.get('Authorization')))
    if priv != "owner" and priv != "admin":
        return 'Permission denied', 403
    #socketio.emit('establish', {'data': 'connected', 'devices': services.info.get_devices()[0], "packets_sent": mon.packets_sent})

@socketio.on('data_reload', namespace="/mainIO")
def admin_data_reload(data):
    socketio.emit('response', {'data': 'reloaded', 'devices': services.info.get_devices()[0], "packets_sent": mon.packets_sent})

@socketio.on('request', namespace="/mainIO")
def admin_request(data):
    mon.req_stream.add(data)

@socketio.on('disconnect', namespace="/mainIO")
def admin_disconnect():
    pass


# for devices
@socketio.on('connect', namespace="/refreshing")
def device_connect(auth):
    if not db.tokens.valid_bearer(request.headers.get("Authorization")): 
        return 'Permission denied', 403
    socketio.emit('response', {'data': 'connected'})

@socketio.on('refresh', namespace="/refreshing")
def device_refresh(data):
    mon.ref_stream.add(data)

@socketio.on('device_response', namespace="/refreshing")
def device_response(data):
    mon.res_stream.add(data)

@socketio.on('disconnect', namespace="/refreshing")
def client_disconnect():
    pass


if __name__ == '__main__':
    
    if not db.connection.exists():
        print("[DB] No database found.")
        db.connection.create_database()

    app.run(threaded=True, debug=True, host="0.0.0.0")
    CORS(app)
    socketio.run(app)