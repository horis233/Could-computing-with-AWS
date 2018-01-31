import mysql.connector
from flask import Flask, request, render_template, g, url_for, redirect

from manager import admin

db_config = {'user': 'ece1779',
             'password': 'secret',
             'host': '127.0.0.1',
             'database': 'project1_admin'}
# connect to a admin database
# change value in the row of id = 1
# default goes like:
# upperbound float 100
# lowerbound float 0
# expandratio int 1
# shrinkratio int 1

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


@admin.route('/ec2/config',methods=['GET'])
#Return config form
def config_form():
    return render_template("ec2/config.html")

@admin.route('/ec2/config', methods=['GET','POST'])
def project_config():
    if request.method == 'POST':
        upper_bound = request.form.get("upper_bound")
        lower_bound = request.form.get("lower_bound")
        expand_ratio = request.form.get("expand_ratio")
        shrink_ratio = request.form.get("shrink_ratio")

        cnx = get_db()
        cursor = cnx.cursor()
        query = '''UPDATE config_parameters
                   SET upperbound = %s,
                       lowerbound = %s,
                       expandratio = %s,
                       shrinkratio = %s
                   WHERE id = 1
        '''
        cursor.execute(query, (upper_bound,lower_bound,expand_ratio,shrink_ratio))
        cnx.commit()
        return redirect(url_for('main'))
    return render_template("ec2/config.html")
# An option for configuring the auto-scaling policy by setting the following parameters:
# CPU threshold for growing the worker pool
# CPU threshold for shrinking the worker pool
# Ratio by which to expand the worker pool (e.g., a ratio of 2 doubles the number of workers).
# Ratio by which to shrink the worker pool (e.g., a ratio of 4 shuts down 75% of the current workers).