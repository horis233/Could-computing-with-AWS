# This is a project for ECE1779 intro to cloud computing in uoft.

## Connect to Database Remotely
Create two new instances using existing ami.

`worker`:  
security group configuration:
```
worker_demo_security_group   
ssh 22 anywhere  
tcp 5000 anywhere  
```

external ip: 54.234.250.254  
internal ip: 172.31.54.162

`database`:  
security group configuration:
```
database_demo_security_group  
ssh 22 anywhere  
tcp 5000 anywhere  
mysql 3306 worker_demo_security_group
```

external ip: 54.197.198.118  
internal ip: 172.31.48.24

change `config.py` database host to internal ip of your database if you are using security group. change it to external ip if you are using anywhere.
for example, if you wrote `mysql 3306 worker_demo_security_group` instead of `mysql 3306 anywhere`, then your `config.py` should be like:
```
db_config = {'user': 'ece1779',
             'password': 'secret',
             'host': '172.31.48.24',
             'database': 'project1'}
```

first do `sudo passwd` to reset your UNIX password
than do `sudo vim mysqld.cnf` to
change configuration file in /etc/mysql/mysql.conf.d/mysqld.cnf  
```
bind-address = 0.0.0.0
```

restart database  
`sudo /etc/init.d/mysql restart`

## Register your Server Host as a Booting Service in your Instance
make a new file in /etc/systemd/system/
which I called it `new.service`

```
[Unit]
Description=Gunicorn instance to serve myproject
After=network.target

[Service]
User=ubuntu
ExecStart = /home/ubuntu/Desktop/ECE1779/project1/run.sh
WorkingDirectory=/home/ubuntu/Desktop/ECE1779/project1
Environment="PATH=/home/ubuntu/Desktop/ECE1779/project1/venv/bin"
[Install]
WantedBy=multi-user.target
```
then do this
`systemctl enable new.service`. 
`systemctl start new.service`. 
`systemctl status new.service`. 
to check whether it is working


`run.sh`  
```
#!/bin/bash
./venv/bin/gunicorn --bind 0.0.0.0:5000 --access-logfile access.log --error-logfile error.log --workers=1 app:webapp
```
