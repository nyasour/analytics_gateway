from datetime import date, time, timezone
import datetime
import boto3, json

AWS_REGION = "us-east-1"
LOG_GROUP = 'event_tracking'
LOG_STREAM='{}-{}'.format(date.today().strftime('%Y-%m-%d'),'logstream')

class EventModel:		
	event_config = {}

	def __init__(self, response_json):
		self.data = response_json
		self.event_name = self.data["event_name"]
		self.event_timestamp = self.data["event_timestamp"]
		self.platform = self.data["platform"]
		self.country = self.data["country"]
		self.os_version = self.data["os_version"]
		self.event_params = self.data["event_params"]
		self.user_properties = self.data["user_properties"]

		#Parse timestamp to GLUE

	def log(self):
		if EventModel.event_config["EVENT_DESTINATION"] == "CLOUDWATCH":
			self.log_to_cloudwatch()
		else: 	#default logging method 		
			self.log_to_cloudwatch()


	def log_to_cloudwatch(self):
		print("log_to_cloudwatch")
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
		
		#Parse timestamp to AWS Glue timestamp default format
		#This is done inside the Cloudwatch logger since other loggers may not use Glue and doesnt require the conversion
		self.data["event_timestamp"] = self.data["event_timestamp"].strftime("%Y-%m-%d %H:%M:%S")


		#Record the timestamp in which the event was logged by the API
		self.data['gateway_timestamp'] = datetime.datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

		event_log = {
			'logGroupName' : LOG_GROUP,
			'logStreamName' : LOG_STREAM,
			'logEvents' : [
				{
					#'id' : str(uuid.uuid4()),
					'timestamp': int(round(datetime.datetime.timestamp(datetime.datetime.now())*1000)),
					'message': json.dumps(self.data)
				}
			]
		}

		if len(response['logStreams'])>0 and 'uploadSequenceToken' in response['logStreams'][0]:
			event_log.update({'sequenceToken': response['logStreams'][0] ['uploadSequenceToken']})

		response = cloudwatch_resource.put_log_events(**event_log)
		
