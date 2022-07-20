from flask import Flask
from flask_restful import Api 
from flask_jwt import JWT
from security import authenticate, identity
from resources.event import Event
from models.event_model import EventModel

from user import UserRegister

app = Flask(__name__)
api = Api(app)
app.secret_key = 'jamesbondisdead'
EventModel.event_config["EVENT_DESTINATION"] = "CLOUDWATCH"

jwt = JWT(app, authenticate, identity) # /auth


api.add_resource(Event, '/event')
api.add_resource(UserRegister, '/register')

if __name__ == '__main__':
	app.run(port=5000, debug=True)

