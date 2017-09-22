import json
import boto3
import datetime
import sys
import logging
from botocore.vendored import requests

ec2 = boto3.resource('ec2',region_name='us-east-2')

log = logging.getLogger()
log.setLevel(logging.INFO)



def lambda_handler(event, context):
	mycode()
	response = send(event, context, "SUCCESS", {}, None)
	return {"Response" : response}

def send(event, context, responseStatus, responseData, physicalResourceId):
	responseUrl = event['ResponseURL']

	log.info("Event: " + str(event))
	log.info("ResponseURL: " + responseUrl)

	responseBody = {}
	responseBody['Status'] = responseStatus
	responseBody['Reason'] = 'See the details in CloudWatch Log Stream: ' + context.log_stream_name
	responseBody['PhysicalResourceId'] = physicalResourceId or context.log_stream_name
	responseBody['StackId'] = event['StackId']
	responseBody['RequestId'] = event['RequestId']
	responseBody['LogicalResourceId'] = event['LogicalResourceId']
	responseBody['Data'] = responseData

	json_responseBody = json.dumps(responseBody)

	log.info("Response body: " + str(json_responseBody))

	headers = {'content-type' : "",'content-length' : str(len(json_responseBody))}

	try:
		response = requests.put(responseUrl, data=json_responseBody, headers=headers)
		log.info("Status code: " + str(response.reason))
		return "SUCCESS"
	except Exception as e:
		log.error("send(..) failed executing requests.put(..): " + str(e))
		return "FAILED"



def mycode():
	if ec2.volumes.all():
		for vol in ec2.volumes.all():
			if  vol.state=='available':
				if vol.tags:
					FOUNDENVUID = False
					for tag in vol.tags:
						if tag['Key'] == 'ENVUID':
							FOUNDENVUID = True
					if not FOUNDENVUID:
						vid=vol.id
						v=ec2.Volume(vol.id)
						v.delete()
						print ("Deleted unattached no ENVUID " +vid)
						continue
				else:
					#unattached no tags
					vid=vol.id
					v=ec2.Volume(vol.id)
					v.delete()
					print ("Deleted unattached no tags " +vid)
