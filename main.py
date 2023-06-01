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

from flask_socketio import SocketIO, emit, send
from flask_socketio import ConnectionRefusedError
from flask_cors import CORS

#import eventlet

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)
#eventlet.monkey_patch() # i dont fucken know what it is and why we need it

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

    # {"type": "UPDATE", "ids": [0, 2, 5]}
    # {"type": "EXECUTE", "ids": [0, 2, 5], "PROMPT": "reboot"}
    # {"type": "LOCK", "ids": [0, 2, 5]}
    # {"type": "UNLOCK", "ids": [0, 2, 5]}

@app.route('/api/devices/response', methods=['POST'])
def get_response():
    if not db.tokens.valid_bearer(request.headers.get("Authorization")): 
        return 'Permission denied', 403
    return services.communication.response(request, request.headers.get("Authorization").split()[1])


# for monitoring!
@socketio.on('connect', namespace="/monitoring")
def client_connect(auth):
    if not db.tokens.valid_bearer(request.args.get('token')):
       raise ConnectionRefusedError('unauthorized!')
    socketio.emit('response', {'data': 'connected', 'devices': services.info.get_devices()[0], "packets_sent": mon.packets_sent})

@socketio.on('data_reload')
def data_reload(data):
    socketio.emit('response', {'data': 'connected', 'devices': services.info.get_devices()[0], "packets_sent": mon.packets_sent})

@socketio.on('request')
def message(data):
    emit("response", {'data': 'read'})

@socketio.on('disconnect')
def client_disconnect():
    pass


if __name__ == '__main__':
    
    if not db.connection.exists():
        print("[DB] No database found.")
        db.connection.create_database()

    app.run(threaded=True, debug=True, host="0.0.0.0")
    CORS(app)
    socketio.run(app)