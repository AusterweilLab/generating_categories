# this script adds the main 'generating-categories' directory to the path
# enabling the user to import the Modules.
# 
# It is assumed that this script is executed in a subdirectory of the
# 'generating-categories' repository, and so it is simply a matter of
# finding the correct outer directory.


def _add_modules_path():
	import os
	import sys

	# keep moving up until the folder is the main path.
	splitted = os.path.split(os.getcwd())
	while splitted[1] != 'generating-categories':
		splitted = os.path.split(splitted[0])

	# recombine and insert
	mainpath = os.path.join(splitted[0], splitted[1])
	sys.path.insert(0, mainpath) 


if __name__ == "__main__":
	_add_modules_path()