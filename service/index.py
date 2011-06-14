#!/usr/bin/python
import sys
sys.path = ['..'] + sys.path

import json
import pycurl
#import logging
from flask import Flask
from flask import request
from pprint import pprint
from suds.client import Client

import config
import utils

#logging.basicConfig(level=logging.INFO, filename='jira.log', format='%(asctime)s %(levelname)s\n%(message)s\n\n')

utils.config = config

app = Flask(__name__)

@app.route("/", methods=['GET','POST'])
def post():
    print request.method
    data = json.loads(request.form['payload'])
    
    client = Client(config.wsdl)
    auth = client.service.login(config.username, config.password)
    
    curl = pycurl.Curl()
    for commit in data['commits']:
        message = commit['message']+"\n\n"
        #message += "author: "+commit['author']['username']+"\n"
        message += "changeset: "+commit['url']
        utils.verifyIssue(client, auth, message, commit['author']['username'], curl, True)
    curl.close()
    return "Hello World!"

if __name__ == "__main__":
    app.run()
