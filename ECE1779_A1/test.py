import boto3

ec2 = boto3.setup_default_session(region_name='us-east-1')
ec2 = boto3.resource('ec2')

instances = ec2.instances.all()

for instance in instances:
    print(instance.id, instance.instance_type, instance.state)

    # for status in ec2.meta.client.describe_instance_status()['InstanceStatuses']:
#     print(status)
#     # print(status['SystemStatus'])
#     print(status['InstanceStatus']['Details'])

for status in ec2.meta.client.describe_instance_status()['InstanceStatuses']:
    print(status['InstanceStatus']['Status'])
    print(status['SystemStatus']['Status'])


    # {'InstanceStatus': {'Status': 'initializing', 'Details': [{'Status': 'initializing', 'Name': 'reachability'}]},
    #  'SystemStatus': {'Status': 'ok', 'Details': [{'Status': 'passed', 'Name': 'reachability'}]},
    #  'InstanceId': 'i-0c90fea46bd52476f', 'AvailabilityZone': 'us-east-1a',
    #  'InstanceState': {'Name': 'running', 'Code': 16}}
