from flask import render_template, redirect, url_for, request, g
import boto3
import mysql.connector
import config
from datetime import datetime, timedelta
from operator import itemgetter
from manager import admin

ec2 = boto3.setup_default_session(region_name='us-east-1')
elb = boto3.client('elb')

db_config = {'user': 'ece1779',
             'password': 'secret',
             'host': '172.31.62.152',
             'database': 'project1'}

'''

Functions for Database

'''

def connect_to_database():
    return mysql.connector.connect(user=db_config['user'],
                                   password=db_config['password'],
                                   host=db_config['host'],
                                   database=db_config['database'])

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db

@admin.teardown_appcontext
# this will execute every time when the context is closed
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@admin.route('/ec2',methods=['GET'])
# Display an HTML list of all ec2 instances
def ec2_list():

    # create connection to ec2
    ec2 = boto3.resource('ec2')

    # instances = ec2.instances.filter(
    #    Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    #
    # instances = ec2.instances.filter(
    #     Filters=[{'Name':'instance.group-name', 'Values':['worker_demo_security_group']}]
    # )

    instances = ec2.instances.all()

    return render_template("ec2/list.html",title="EC2 Instances",instances=instances)


@admin.route('/ec2/<id>',methods=['GET'])
#Display details about a specific instance.
def ec2_view(id):
    ec2 = boto3.resource('ec2')

    instance = ec2.Instance(id)

    client = boto3.client('cloudwatch')

    metric_name = 'CPUUtilization'

    ##    CPUUtilization, NetworkIn, NetworkOut, NetworkPacketsIn,
    #    NetworkPacketsOut, DiskWriteBytes, DiskReadBytes, DiskWriteOps,
    #    DiskReadOps, CPUCreditBalance, CPUCreditUsage, StatusCheckFailed,
    #    StatusCheckFailed_Instance, StatusCheckFailed_System


    namespace = 'AWS/EC2'
    statistic = 'Average'                   # could be Sum,Maximum,Minimum,SampleCount,Average


    cpu = client.get_metric_statistics(
        Period=1 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName=metric_name,
        Namespace=namespace,  # Unit='Percent',
        Statistics=[statistic],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )
    #print (cpu)
    cpu_stats = []


    for point in cpu['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        cpu_stats.append([time,point['Average']])

    cpu_stats = sorted(cpu_stats, key=itemgetter(0))

    statistic = 'Sum'  # could be Sum,Maximum,Minimum,SampleCount,Average

    network_in = client.get_metric_statistics(
        Period=1 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName='NetworkIn',
        Namespace=namespace,  # Unit='Percent',
        Statistics=[statistic],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )

    net_in_stats = []

    for point in network_in['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        net_in_stats.append([time,point['Sum']])

    net_in_stats = sorted(net_in_stats, key=itemgetter(0))



    network_out = client.get_metric_statistics(
        Period=5 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName='NetworkOut',
        Namespace=namespace,  # Unit='Percent',
        Statistics=[statistic],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )


    net_out_stats = []

    for point in network_out['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        net_out_stats.append([time,point['Sum']])

        net_out_stats = sorted(net_out_stats, key=itemgetter(0))


    return render_template("ec2/view.html",title="Instance Info",
                           instance=instance,
                           cpu_stats=cpu_stats,
                           net_in_stats=net_in_stats,
                           net_out_stats=net_out_stats)


@admin.route('/ec2/create',methods=['POST'])
# Start a new EC2 instance
def ec2_create():

    ec2 = boto3.resource('ec2')

    new_instance = ec2.create_instances(ImageId=config.ami_id,
                                        KeyName='ece1779_project1',
                                        MinCount=1,
                                        MaxCount=1,
                                        InstanceType='t2.small',
                                        Monitoring={'Enabled': True},
                                        SecurityGroupIds=[
                                            'sg-e05d929f',
                                        ]
                                        )
    attachinst = elb.register_instances_with_load_balancer(LoadBalancerName='myelb',
                                                           Instances=[
                                                               {
                                                                   'InstanceId': new_instance[0].id
                                                               }
                                                           ])
    return redirect(url_for('ec2_list'))



@admin.route('/ec2/delete/<id>',methods=['POST'])
# Terminate a EC2 instance
def ec2_destroy(id):
    # create connection to ec2
    ec2 = boto3.resource('ec2')
    elb.deregister_instances_from_load_balancer(LoadBalancerName='myelb',
                                                Instances=[
                                                    {
                                                        'InstanceId': ec2.instances.filter(InstanceIds=[id]).id
                                                    }
                                                ])
    ec2.instances.filter(InstanceIds=[id]).terminate()
    return redirect(url_for('ec2_list'))

@admin.route('/ec2/terminate',methods=['POST'])
#An option for deleting all data. Executing this function should delete application data stored on the database as well as all images stored on S3.
def project_terminate():
    cnx = get_db()
    cursor = cnx.cursor()
    query = '''TRUNCATE TABLE users
            '''
    cursor.execute(query)
    query = '''TRUNCATE TABLE images
                '''
    cursor.execute(query)
    cnx.commit()
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

    s3 = boto3.resource('s3')
    objects_to_delete = s3.meta.client.list_objects(Bucket="ece1779project")
    delete_keys = {'Objects': []}
    delete_keys['Objects'] = [{'Key': k} for k in [obj['Key'] for obj in objects_to_delete.get('Contents', [])]]
    s3.meta.client.delete_objects(Bucket="ece1779project", Delete=delete_keys)

    return redirect(url_for('ec2_list'))
