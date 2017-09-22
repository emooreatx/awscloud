from __future__ import print_function

import json
import boto3
import logging

#use tag_cleanup_client if the resource only has a client interface, vs tag_cleanup_resource for objects supported as resources in boto3
#TODO: convert all calls to client instead of resource
#setup simple logging for INFO
logger = logging.getLogger()
logger.setLevel(logging.ERROR)

#define the connection region
ec2 = boto3.resource('ec2', region_name="us-east-2")
elb = boto3.client('elb', region_name="us-east-2")
rds = boto3.client('rds', region_name="us-east-2")

#Set this to True if you don't want the function to perform any actions
debugMode = False



def lambda_handler(event, context):
	#EMChange to Subnets
	base = ec2.subnets.all()
	
	#loop through resources by subnet
	for subnet in base:
		print(subnet.id)
		#Tag the Volumes
		instances=ec2.instances.filter(Filters=[{'Name': 'subnet-id', 'Values': [subnet.id]}])
		for instance in instances:
			if debugMode == True:
				print("[DEBUG] " + str(instance))
				tag_cleanup_resource(subnet, instance)
			else:
				tag = instance.create_tags(Tags=tag_cleanup_resource(subnet, instance))
				print("[INFO]: " + str(tag))
			for vol in instance.volumes.all():
				#print(vol.attachments[0]['Device'])
				if debugMode == True:
					print("[DEBUG] " + str(vol))
					tag_cleanup_resource(subnet, vol)
				else:
					tag = vol.create_tags(Tags=tag_cleanup_resource(subnet, vol))
					print("[INFO]: " + str(tag))
	
	#list ELBs and tag them
	loadbalancers = elb.describe_load_balancers()
	for lb in loadbalancers['LoadBalancerDescriptions']:
		subnet = ec2.Subnet(lb['Subnets'][0])
		if debugMode == True:
			print("[DEBUG] " + lb['LoadBalancerName'])
			tag_cleanup_client(subnet)
		else:
			tag = elb.add_tags(LoadBalancerNames=[lb['LoadBalancerName']] , Tags=tag_cleanup_client(subnet))
			print("[INFO]: " + str(tag))
	
	#list RDS instances and tag them
	mysubnet=""
	databases = rds.describe_db_instances()
	for db in databases['DBInstances']:
		subnetgroup = db['DBSubnetGroup']
		subnets = subnetgroup['Subnets']
		for subnet in subnets:
			if subnet['SubnetAvailabilityZone']['Name'] == 'us-east-2a':
				mysubnet = ec2.Subnet(subnet['SubnetIdentifier'])
		if debugMode == True:
			print("[DEBUG] " + db['DBInstanceIdentifier'])
			tag_cleanup_client(mysubnet)
		else:
			tag = rds.add_tags_to_resource(ResourceName=db['DBInstanceArn'], Tags=tag_cleanup_client(mysubnet))
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
		
def tag_cleanup_resource(subnet, detail):
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

	
def tag_cleanup_client(subnet):
	tempTags=[]
	v={}
	myenvuid = ""
	#Get the environment UID so we can name things
	for tags in subnet.tags:
		if tags["Key"] == 'ENVUID':
			myenvuid = tags["Value"]
	if myenvuid == "":
		myenvuid = "SUBNETNEEDSENVUID"
	#See if the resource has tags, and if it does if it has a name tag
	for t in subnet.tags:
		if t['Key'] == 'ENVUID':
			print("[INFO]: ENVUID Tag " + str(t))
			tempTags.append(t)    
		elif t['Key'] == 'appci':
			print("[INFO]: Application CI " + str(t))
			tempTags.append(t)  
		else:
			print("[INFO]: Skip Tag - " + str(t))
	print("[INFO] " + str(tempTags))
	return(tempTags)
	
lambda_handler("", "")