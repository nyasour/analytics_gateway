from datetime import date, time, datetime, timezone
import boto3, json

AWS_REGION = "us-east-1"
LOG_GROUP = 'event_tracking'
LOG_STREAM='{}-{}'.format(date.today().strftime('%Y-%m-%d'),'logstream')

class EventModel:		
	event_config = {}

	def __init__(self, response_json):
		self.data = response_json

	def log(self):
		if EventModel.event_config["EVENT_DESTINATION"] == "CLOUDWATCH":
			self.log_to_cloudwatch()
			pass
		
		self.log_to_cloudwatch()


	def log_to_cloudwatch(self):
		#create resources. 
		#need to move to __init__ for cloudwatch event logger
		cloudwatch_resource = boto3.client('logs', region_name=AWS_REGION)
		seq_token = None

		try:
			cloudwatch_resource.create_log_group(logGroupName=LOG_GROUP)
		except cloudwatch_resource.exceptions.ResourceAlreadyExistsException:
			pass

		try:
			cloudwatch_resource.create_log_stream(logGroupName=LOG_GROUP, logStreamName=LOG_STREAM)
		except cloudwatch_resource.exceptions.ResourceAlreadyExistsException:
			pass


		response = cloudwatch_resource.describe_log_streams(
			logGroupName=LOG_GROUP,
			logStreamNamePrefix=LOG_STREAM
			)
		
		
		# gateway ts can be different from the client ts if events are batched
		self.data['gateway_timestamp'] = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

		event_log = {
			'logGroupName' : LOG_GROUP,
			'logStreamName' : LOG_STREAM,
			'logEvents' : [
				{
					#'id' : str(uuid.uuid4()),
					'timestamp': int(round(datetime.timestamp(datetime.now())*1000)),
					'message': json.dumps(self.data)
				}
			]
		}

		if len(response['logStreams'])>0 and 'uploadSequenceToken' in response['logStreams'][0]:
			event_log.update({'sequenceToken': response['logStreams'][0] ['uploadSequenceToken']})

		response = cloudwatch_resource.put_log_events(**event_log)
		
