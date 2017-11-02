import boto3
ec2 = boto3.resource('ec2',region_name='us-east-2')

def lambda_handler(event, context):
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