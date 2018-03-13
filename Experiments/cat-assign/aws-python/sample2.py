import boto
from boto.mturk.connection import MTurkConnection
from boto.mturk.question import HTMLQuestion
import boto.mturk.qualification
# Create your connection to MTurk
#mtc = MTurkConnection(aws_access_key_id='your_access_key_here',
#aws_secret_access_key='your_secret_key_here',
HOST = 'mechanicalturk.sandbox.amazonaws.com'
mtc = boto.mturk.connection.MTurkConnection(host=HOST)

#host='mechanicalturk.sandbox.amazonaws.com'
# question_html_value = """
# <html>
# <head>
# <meta http-equiv='Content-Type' content='text/html; charset=UTF-8'/>
# <script src='https://s3.amazonaws.com/mturk-public/externalHIT_v1.js' type='text/javascript'></script>
# </head>
# <body>
# <!-- HTML to handle creating the HIT form -->
# <form name='mturk_form' method='post' id='mturk_form' action='https://workersandbox.mturk.com/mturk/externalSubmit'>
# <input type='hidden' value='' name='assignmentId' id='assignmentId'/>
# <!-- This is where you define your question(s) --> 
# <h1>Please name the company that created the iPhone</h1>
# <p><textarea name='answer' rows=3 cols=80></textarea></p>
# <!-- HTML to handle submitting the HIT -->
# <p><input type='submit' id='submitButton' value='Submit' /></p></form>
# <script language='Javascript'>turkSetAssignmentID();</script>
# </body>
# </html>
# """
# Prepare link to survery
# configuration for the external HIT
externalconfig = dict(
		#url = "https://alab.psych.wisc.edu/experiments/generate-categories/",
                url = "https://alab.psych.wisc.edu/experiments/catassign/",#"https://alab.psych.wisc.edu/experiments/catgen/",
		frame_height = 600, 
)


# config for the worker qualifications
qualifications =  boto.mturk.qualification.Qualifications()

#Good worker requirement
qualifications.add( 
	boto.mturk.qualification.PercentAssignmentsApprovedRequirement(
	comparator = "GreaterThan", integer_value = "95", required_to_preview = True)
)

#USA Requirement
qualifications.add( 
	boto.mturk.qualification.LocaleRequirement(
			comparator = "EqualTo", locale = "US", required_to_preview = True)
)



# The first parameter is the HTML content
# The second is the height of the frame it will be shown in
# Check out the documentation on HTMLQuestion for more details
#html_question = HTMLQuestion(question_html_value, 500)
# These parameters define the HIT that will be created
# question is what we defined above
# max_assignments is the # of unique Workers you're requesting
# title, description, and keywords help Workers find your HIT
# duration is the # of seconds Workers have to complete your HIT
# reward is what Workers will be paid when you approve their work
# Check out the documentation on CreateHIT for more details
response = mtc.create_hit(question=boto.mturk.question.ExternalQuestion( 
    externalconfig['url'], externalconfig['frame_height'] ),
                          max_assignments=1,
                          title="Answer a simple question",
                          description="Help research a topic",
                          keywords="question, answer, research",
                          duration=3600, #3600 s in 1 hour
                          reward=1.00,
                          qualifications = qualifications)
# The response included several fields that will be helpful later
hit_type_id = response[0].HITTypeId
hit_id = response[0].HITId
print "Your HIT has been created. You can see it at this link:"
print "https://workersandbox.mturk.com/mturk/preview?groupId={}".format(hit_type_id)
print "Your HIT ID is: {}".format(hit_id)
