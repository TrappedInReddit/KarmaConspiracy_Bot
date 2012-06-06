from classes import *

""" These utility functions just act as middlemen between a list of
    classes that I can work with and my data on the other end      """

# Searches a list of comments for a specific string
def search_comments(comments, search_string, ignore = False):
	# Searches each comment
	for comment in comments:
		found = comment.search(search_string, ignore)			
		if found is True:
			return True
		
	return False
