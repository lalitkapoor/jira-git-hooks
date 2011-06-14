import re
import json
import pycurl
import urllib
import StringIO
from suds.client import Client
from suds import WebFault

import settings

#set this
config = None
__userCache = {}

def verifyIssue(client, auth, comment, author=None, curl=None, addComments=False):
    global config
    commands, issueIDs = _parseMessage(comment)
    if len(commands)<1:
    	print "No commands found"
    
    if len(issueIDs)<1:
    	print "No JIRA issues found in commit message, make sure you prepend a '#' to each issue and command"
    	if config.type=="client":
    	    exit(1) #exit because no issues were specified
    	else:
    	    return
    #check to make sure all issues specified exist:
    for issueID in issueIDs:
    	try:
    		issue = client.service.getIssue(auth, issueID)
    		print "JIRA issue found:", issueID
    		if addComments==True:
    		    try:
    		        #client.service.addComment(auth, issueID, {'body': comment})
    		        _addComment(curl, issueID, comment, _githubUserToJiraUser(author))
    		        print "comment added for JIRA issue:", issueID
    		    except Exception as err:
    		        print "Error adding JIRA comment:", issueID
    		        print err
    	except WebFault as err:
    		print "Error finding JIRA issue:", issueID

def _parseMessage(comment):
    global config
    regex = r"\%s\w*[!-~]*\d*" % (settings.prefix)
    matches = re.findall(regex, comment)

    commands = set()
    issueIDs = set()

    for match in matches:
    	match = match[1:].upper() #remove the hash and make it all uppercase
    	if match in settings.commands:
    		print "command:", match
    		commands.add(match)
    		#do something here, act on the command
    		#do this when the push has completed
    	else:
    		print "JIRA issue:", match
    		#this might be an issue so add to list of issues
    		issueIDs.add(match)
    return (commands, issueIDs)

#you will need to disable websudo inorder for jelly to work
#this is a port of: http://jaredtyrrell.com/blog/2011/05/posting-bulk-jira-issues-with-jirajelly-and-curl/
def _addComment(curl, issueID, comment, commenter):
    global config
    b = StringIO.StringIO()

    xml='<JiraJelly xmlns:jira="jelly:com.atlassian.jira.jelly.enterprise.JiraTagLib"><jira:AddComment comment="'+comment+'" issue-key="'+issueID+'" commenter="'+commenter+'"/></JiraJelly>'

    username=urllib.quote_plus(config.username)
    password=urllib.quote_plus(config.password)

    base_url=config.jelly
    params="os_username="+username+"&os_password="+password+"&Run=Run&filename=&script="+urllib.quote_plus(xml);

    #curl = pycurl.Curl()
    curl.setopt(pycurl.HTTPHEADER, ['X-Atlassian-Token: no-check'])
    #curl.setopt(pycurl.RETURNTRANSFER, False)
    curl.setopt(pycurl.WRITEFUNCTION, b.write)
    curl.setopt(pycurl.FOLLOWLOCATION, True)
    curl.setopt(pycurl.URL, base_url+"?"+params)
    curl.perform()
    #curl.close()

def _githubUserToJiraUser(username):
    global config
    global __userCache
    if username in __userCache:
        return __userCache[username]
    else:
        f = open(config.userdata)
        __userCache = json.loads(f.read())
        f.close()
        if username in __userCache:
            return __userCache[username]
        else:
            print "Error, github user:", username, "does not exist"
            return ""
