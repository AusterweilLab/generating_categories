# Set the HOST on AWS
HOST = 'mechanicalturk.sandbox.amazonaws.com'
# HOST = 'mechanicalturk.amazonaws.com'

# configuration for the external HIT
externalconfig = dict(
		url = "https://alab.psych.wisc.edu/experiments/generate-categories/",
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

# set HIT config
hitconfig = dict(
	title = "Category learning experiment (10-15min)",
	description = "Learn a new category in a quick HIT.",
	keywords = ["category", "learning", "psychology", "experiment"],
	reward = 1.5,
	qualifications = qualifications,
	duration = datetime.timedelta(minutes = 30),
	lifetime = datetime.timedelta(days = 7),
	max_assignments = 60,
	response_groups = "Minimal",
	question = boto.mturk.question.ExternalQuestion( 
			externalconfig['url'], externalconfig['frame_height'] )
)

# quick function to print HIT info
def printHIT(hit):
		print('\t' + 'Title\t\t\t\t\t' + hit.Title)
		print('\t' + 'HITId\t\t\t\t\t' + hit.HITId)
		print('\t' + 'HITStatus\t\t\t\t'  + hit.HITStatus)
		print('\t' + 'CreationTime\t\t\t'  + hit.CreationTime)
		print('\t' + 'Available Assignments\t'  + hit.NumberOfAssignmentsAvailable)
		print('\t' + 'Completed Assignments\t'  + hit.NumberOfAssignmentsCompleted)