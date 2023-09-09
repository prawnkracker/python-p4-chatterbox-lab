from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    messages = []
    for message in Message.query.order_by(Message.created_at.asc()).all():
        messages_dict = {
            "id":message.id,
            "body":message.body,
            "username":message.username,
            "created_at":message.created_at,
            "updated_at":message.updated_at
        }
        messages.append(messages_dict)
    if request.method == 'GET':
        response = make_response(
            messages,
            200
        )
    elif request.method == 'POST':
        json_info = request.get_json()
        new_message = Message(
            body = json_info["body"],
            username = json_info["username"]
        )
        db.session.add(new_message)
        db.session.commit()
        
        new_message_dict = new_message.to_dict()
        response = make_response(
            new_message_dict,
            201
        )
    return response

@app.route('/messages/<int:id>', methods = ['GET', 'PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.filter(Message.id == id).first()
    if request.method == 'PATCH':
        json_info = request.get_json()
        for attr in json_info:
            setattr(message, attr, json_info.get(attr))
        db.session.add(message)
        db.session.commit()

        message_dict = message.to_dict()
        response = make_response(message_dict, 200)
    
    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()

        response_body = {
            "delete_successful": True,
            "message":"Message successfully deleted."
        }
        response = make_response(response_body, 200)
    return response

if __name__ == '__main__':
    app.run(port=5555)
