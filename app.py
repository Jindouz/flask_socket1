from flask import Flask, request, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS

app = Flask(__name__, static_folder='../frontend/build')
app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")

# Enable CORS for all routes
CORS(app)

# Dictionary to store user names and their corresponding rooms
users = {}

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@socketio.on('join')
def handle_join(data):
    username = data['username']
    room = data.get('room', 'default_room')  # If room is not provided, default to 'default_room'
    users[request.sid] = {'username': username, 'room': room}
    join_room(room)
    message = f"{username} has joined the room."
    emit('message', {'message': message}, room=room)

@socketio.on('leave')
def handle_leave():
    if request.sid in users:
        username = users[request.sid]['username']
        room = users[request.sid]['room']
        leave_room(room)
        del users[request.sid]
        message = f"{username} has left the room."
        emit('message', {'message': message}, room=room)

@socketio.on('send_message')
def handle_message(data):
    if request.sid in users:
        username = users[request.sid]['username']
        room = users[request.sid]['room']
        message = data['message']
        emit('message', {'username': username, 'message': message}, room=room, broadcast=True)
    else:
        print("User has not joined any room yet, message ignored.")

if __name__ == '__main__':
    socketio.run(app, debug=True)
