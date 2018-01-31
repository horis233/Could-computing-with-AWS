All lecture and tutorial examples require the following in order to work:
    - Python 3.5 (or better)
    - A python virtual environment
    - Flask
    - Boto3 (AWS Python SDK)
    - AWS CLI 

Perform these steps to run the examples:

1) Install python 3.5 by following the instructions for your respective platform available at https://www.python.org/

2) Download and unpack the example sources:

   a) Download the example sources,
   b) Open a shell and navigate to the location of the tar.gz file
   c) Uncompress and untar (e.g., tar -xzf solution.tar.gz)
   d) Go into the example directory (e.g., cd solution)

3) Create a new python virtual environment as follows:

   python -m venv venv

   For some platforms substitute python for python3 or python3.5

4) Install Flask

   venv/bin/pip install flask

5) Install AWS Command Line Interface (CLI)

   Follow instruction in https://aws.amazon.com/cli/

5) Install Boto3

   venv/bin/pip install boto3

7) Before you can begin using Boto 3, you should set up authentication
credentials. Credentials for your AWS account can be found in the IAM
Console at https://console.aws.amazon.com/iam/home?#. You can create
or use an existing user. Go to manage access keys and generate a new
set of keys.  You will need both the aws_access_key_id and
aws_secret_access_key.

8) Configure your credentials

   aws configure


9) Run the example

   run.py

   For some platforms you may need to edit the first line of this file
   to reflect the correct path to the python installation in the
   virtual environment.  The provided file works for Linux and OSX.
    
   
