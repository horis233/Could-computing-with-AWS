from flask import Flask

webapp = Flask(__name__)

from app import userLogin
from app import index
from app import register
from app import exchange_all
from app import frontpage
from app import exchange_part
from app import expart_process
from app import swap
