import hmac
from user import User 

def authenticate(username, password):
	user = User.find_user_by_username(username)
	if user and hmac.compare_digest(user.password, password):
		return user
	return None

def identity(payload):
	print ("step2")
	user_id = payload['identity']
	return User.find_user_by_id(user_id)