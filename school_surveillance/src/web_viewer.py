from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from .database import load_violations

app = Flask(__name__, template_folder='templates')
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    violations = load_violations()
    return render_template('index.html', violations=violations)

@socketio.on('connect')
def test_connect():
    print("Client connected")
    emit('my response', {'data': 'Connected'})

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

@socketio.on('new_violation')
def handle_new_violation(json):
    print('received new violation: ' + str(json))
    socketio.emit('update_violations', json, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)