from flask import Flask
admin = Flask(__name__)
from manager import ec2
from manager import main
from manager import autoscaling