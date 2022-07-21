from flask_restful import Resource, reqparse, inputs
from flask_jwt import jwt_required
from models.event_model import EventModel

class Event(Resource):
	parser = reqparse.RequestParser()
	parser.add_argument('event_timestamp', type=inputs.datetime_from_iso8601, required=True, help="This field cannot be left blank")
	#parser.add_argument('event_timestamp', type=str, required=True, help="This field cannot be left blank")
	parser.add_argument('event_name', type=str, required=True, help="This field cannot be left blank")
	parser.add_argument('user_id', type=str, required=True, help="This field cannot be left blank")
	parser.add_argument('platform', type=str, required=True, help="This field cannot be left blank")
	parser.add_argument('country', type=str, required=True, help="This field cannot be left blank")
	parser.add_argument('os_version', type=str, required=True, help="This field cannot be left blank")
	parser.add_argument('event_params', type=dict, required=False)
	parser.add_argument('user_properties', type=dict, required=False)

	def post(self):
		event = EventModel(Event.parser.parse_args()).log()
		
		return {'message' : 'event registered'}

class EventLogger:
	seq_token = None

	"""Encapsulates Amazon CloudWatch functions."""
	def __init__(self, aws_logs):

		self.aws_logs_resource = aws_logs

		try:
			self.aws_logs_resource.create_log_group(logGroupName=LOG_GROUP)
		except self.aws_logs_resource.exceptions.ResourceAlreadyExistsException:
			pass

		# self.aws_logs_resource.create_log_stream(
		#    logGroupName = 'impact_tracking',
		#    logStreamName = str(date.today())           

	def log_event(self, data_set):
		try:
			self.aws_logs_resource.create_log_stream(logGroupName=LOG_GROUP, logStreamName=LOG_STREAM)
		except self.aws_logs_resource.exceptions.ResourceAlreadyExistsException:
			pass


		response = self.aws_logs_resource.describe_log_streams(
			logGroupName=LOG_GROUP,
			logStreamNamePrefix=LOG_STREAM
		)
		print(response)
		data_set['gateway_timestamp'] = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

		event_log = {
			'logGroupName' : LOG_GROUP,
			'logStreamName' : LOG_STREAM,
			'logEvents' : [
				{
					#'id' : str(uuid.uuid4()),
					'timestamp': int(round(datetime.timestamp(datetime.now())*1000)),
					'message': json.dumps(data_set)
				}
			]
		}

		if len(response['logStreams'])>0 and 'uploadSequenceToken' in response['logStreams'][0]:
			event_log.update({'sequenceToken': response['logStreams'][0] ['uploadSequenceToken']})

		response = self.aws_logs_resource.put_log_events(**event_log)
		print(response)

