#!/usr/bin/env python

from classes import *
from utilities import *

# User-defined variables
username   = ""
password   = ""

# Optional-user defined variables
domain     = "http://www.reddit.com"
user_agent = ""
subreddit  = "KarmaConspiracy"
section    = "new"
sort       = ""
time_frame = ""
limit      = 25
sleep_time = 2

# Packaging everything up nicely
headers   = { "User-Agent": user_agent }
data      = { "domain"     : domain,
             	"section"    : section,
             	"sort"       : sort,
	            "time_frame" : time_frame,
	            "limit"      : limit,
	            "sleep_time" : sleep_time,
              "headers"    : headers }

# Here's where the real code jumps in
# Logs into reddit, sets the subreddit to work with, and
# gets all the submissions according to the parameters supplied
reddit = Reddit(username, password, data)
reddit.set_subreddit(subreddit)
submissions = reddit.get_submissions()

# Now we go to work on each submission
for submission in submissions:
	# First, grab all the duplicates
	duplicates = submission.get_duplicates()
	
	# Then grab the highest scoring duplicate
	highest_duplicate = reddit.get_highest_duplicate(duplicates)
	if highest_duplicate is not None:
		
		# Now grab all of the duplicates comments
		comments = submission.get_comments()
		
		# Get the link for the original (highest duplicate) and see if it's
		# already been posted in the comments
		original_link = highest_duplicate.domain + highest_duplicate.permalink
		already_posted = search_comments(comments, original_link)
		
  	if already_posted is False:
  		link = ("**[" + highest_duplicate.title + "](" + 
  			highest_duplicate.domain + highest_duplicate.permalink + ")**")
  		text = ("*The context of this conspiracy:*\n\n" + link + "\n\n" + 
  	  	"Submitted by " + highest_duplicate.author + " to r/" + 
  	  	highest_duplicate.subreddit)
  	  
  	  # Produces a link to the post in question
  	 	post_link = submission.permalink
  	 	
  	 	# The subject of the message that we send
  	 	subject = "Error:\%20" + submission.id
  	 	
  	 	# The body of the message that we send
  	 	message = ("Post\%20in\%20question:\%20" + post_link + "\%0A\%0A" + 
  	 		"Correct\%20link:\%20")
  	 	
  	 	# Produces a link to the message poster
  	 	message_link = ("[^Message ^me](" + submission.domain + 
  	 		"/message/compose/?to=" + reddit.username + "&subject=" + subject + 
  	 		"&message=" + message + ")")
  	 	tagline = ("^Did ^the ^bot ^make ^a ^mistake? " + message_link + 
  	 		" ^with ^the ^correct ^link.")
  	 	
  	 	# The final formatted text
  	 	text += "\n\n" + tagline
  	 	
  	 	# Finally gets around the posting the comment
  	 	# and upvoting the submission
  	 	submission.comment(text)
  	 	submission.upvote()
