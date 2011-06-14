import re
import pycurl
import urllib
import StringIO
from suds.client import Client
from suds import WebFault

import settings

def parseMessage(comment):
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

def verifyIssue(config, client, auth, comment, author=None, curl=None, addComments=False):
    commands, issueIDs = parseMessage(comment)
    if len(commands)<1:
    	print "No commands found"
    
    print commands
    print issueIDs
    
    if len(issueIDs)<1:
    	print "No JIRA issues found in commit message, make sure you prepend a '#' to each issue and command"
    	exit(1) #exit because no issues were specified
    #check to make sure all issues specified exist:
    for issueID in issueIDs:
    	try:
    		issue = client.service.getIssue(auth, issueID)
    		print "JIRA issue found:", issueID
    		if addComments==True:
    		    try:
    		        #client.service.addComment(auth, issueID, {'body': comment})
    		        addComment(curl, config.username, config.password, issueID, comment, githubUserToJiraUser(author))
    		        print "comment added for JIRA issue:", issueID
    		    except Exception as err:
    		        print "Error adding JIRA comment:", issueID
    	except WebFault as err:
    		print "Error finding JIRA issue:", issueID

#you will need to disable websudo inorder for jelly to work
#this is a port of: http://jaredtyrrell.com/blog/2011/05/posting-bulk-jira-issues-with-jirajelly-and-curl/
def addComment(curl, config, issueID, comment, commenter):
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

def githubUserToJiraUser(github):
    #do a lookup in a json file
    #return jira username
    pass