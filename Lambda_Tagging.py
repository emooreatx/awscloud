from __future__ import print_function

import json
import boto3
import logging

#setup simple logging for INFO
logger = logging.getLogger()
logger.setLevel(logging.ERROR)

#define the connection region
ec2 = boto3.resource('ec2', region_name="us-east-2")

#Set this to True if you don't want the function to perform any actions
debugMode = False


def lambda_handler(event, context):
	#EMChange to Subnets
	base = ec2.subnets.all()
	
	#loop through by subnet
	for subnet in base:
		print(subnet.id)
		#Tag the Volumes
		instances=ec2.instances.filter(Filters=[{'Name': 'subnet-id', 'Values': [subnet.id]}])
		for instance in instances:
			if debugMode == True:
				print("[DEBUG] " + str(instance))
				tag_cleanup(subnet, instance)
			else:
				tag = instance.create_tags(Tags=tag_cleanup(subnet, instance))
				print("[INFO]: " + str(tag))
			for vol in instance.volumes.all():
				#print(vol.attachments[0]['Device'])
				if debugMode == True:
					print("[DEBUG] " + str(vol))
					tag_cleanup(subnet, vol)
				else:
					tag = vol.create_tags(Tags=tag_cleanup(subnet, vol))
					print("[INFO]: " + str(tag))
		
			#Tag the Network Interfaces
#			for eni in instance.network_interfaces:
#				#print(eni.attachment['DeviceIndex'])
#				if debugMode == True:
#					print("[DEBUG] " + str(eni))
#					tag_cleanup(subnet, eni)
#				else:
#					tag = eni.create_tags(Tags=tag_cleanup(subnet, "eth"+str(eni.attachment['DeviceIndex'])))
#					print("[INFO]: " + str(tag))
	
#------------- Functions ------------------
#returns the type of configuration that was performed    
		
def tag_cleanup(subnet, detail):
	tempTags=[]
	v={}
	hasname=0
	myenvuid = ""
	#Get the environment UID so we can name things
	for tags in subnet.tags:
		if tags["Key"] == 'ENVUID':
			myenvuid = tags["Value"]
	if myenvuid == "":
		myenvuid = "SUBNETNEEDSENVUID"
	#See if the resource has tags, and if it does if it has a name tag
	if detail.tags:
		for tags in detail.tags:
			if tags['Key'] == 'Name':
				if not tags['Value'] == '':
					hasname = 1
	for t in subnet.tags:
		if t['Key'] == 'ENVUID':
			print("[INFO]: ENVUID Tag " + str(t))
			tempTags.append(t)    
		elif t['Key'] == 'appci':
			print("[INFO]: Application CI " + str(t))
			tempTags.append(t)  
		else:
			print("[INFO]: Skip Tag - " + str(t))
	if hasname == 0:
		print("Doesn't have a name")
		v['Key'] = 'Name'
		v['Value'] = myenvuid + "-" + str(detail.id)
		tempTags.append(v)
	print("[INFO] " + str(tempTags))
	return(tempTags)