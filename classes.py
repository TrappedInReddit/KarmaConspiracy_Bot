import requests
import simplejson
import time

# Logs into reddit using their API and requests
# Returns an associative array passed from reddit of the
# login information including the cookie and modhash
class Reddit:
	# Declare some default values
  username   = ""
  password   = ""
  api_type   = "json"
  domain     = "http://www.reddit.com"
  section    = ""
  sort       = ""
  time_frame = ""
  limit      = ""
  subreddit  = ""
  sleep_time = 2
  headers    = { "User-Agent" : "A reddit bot" }
  login      = None
  
	# Defines the username and password fields
	# And then logs into the domain
  def __init__(self, username, password, data = None):
  	
  	# In case the user only supplies us with the username and password,
  	# we go ahead and set some values
    # Set the variables
    self.username   = username
    self.password   = password
	  
	  # Implement user-defined variables if given
    if data is not None: 
    	if "domain" in data:
    		self.domain     = data["domain"]
    	if "section" in data:
    		self.section    = data["section"]
    	if "sort" in data:    	
    		self.sort       = data["sort"]
    	if "time_frame" in data:
    		self.time_frame = data["time_frame"]
    	if "limit" in data:
    		self.limit      = data["limit"]
    	if "headers" in data:
    		self.headers    = data["headers"]
    	if "sleep_time" in data:
    		self.sleep_time = data["sleep_time"]
	  
    self.login()
		
	# Logs in to the domain provided with the credentials supplied
	# when the class was initialized
  def login(self):
    # Define the login credentials in the POST format needed
    payload = { "user"     : self.username,
	              "passwd"   : self.password,
                "api_type" : self.api_type }

    # Log into the domain and sleep
    r = requests.post(self.domain + "/api/login/" + self.username, 
    	                data=payload, headers = self.headers)
    self.sleep()
    

    # Parse the data returned (modhash and cookie)
    login = simplejson.loads(r.text)
  
    self.login = login

  # Sets the subreddit with which to work
  def set_subreddit(self, subreddit):
	  self.subreddit = subreddit

  # Returns the listings of a subreddit with the parameters defined by the user
  def get_submissions(self):
    # Grab the cookie, which is needed for requests to private subreddits
    reddit_cookie = self.get_cookie()

    # Parse the URL for the request
    submissions_url = (self.domain + "/r/" + self.subreddit + "/")
    
    # Modifies the URL is a section is given
    if self.section:
    	submissions_url += self.section + "/"
    
    # Appends the request for a JSON file - ALWAYS
    submissions_url += ".json"
    
    # Modifies the URL if a sort method is given
    if self.sort and self.section is not "new":
    	submissions_url += "?sort=" + self.sort
    	
    # Modifies the URL if a time frame is given
    if self.time_frame and self.section is not "new":
    	if self.sort:
    		symbol = "&"
    	else:
    		symbol = "?"
    	submissions_url += symbol + "t=" + self.time_frame
    
    # Modifies the URL if a limit is given
    if self.limit:
      if((self.sort or self.time_frame)
         and self.section is not "new"):
    		symbol = "&"
      else:
    	  symbol = "?"
      submissions_url += symbol + "limit=" + str(self.limit)
        
    # Request the submission's information and sleeps
    r = requests.get(submissions_url, cookies = reddit_cookie,
    	               headers = self.headers)
    self.sleep()

    # Parse the response from reddit
    submissions_data = simplejson.loads(r.text)
    
    # If there was an error, return the error code
    if "error" in submissions_data:
    	return submissions_data["error"]
  
    # Initialize a list
    else:
      submissions = []
  
    # Go through the results and append them to the list
      for submission in submissions_data["data"]["children"]:
      	submission["domain"]     = self.domain
      	submission["sleep_time"] = self.sleep_time
      	submission["login"]      = self.login
      	submission["headers"]    = self.headers
        class_submission         = Submission(submission)
        submissions.append(class_submission)
  
      return submissions
  
  # Returns the highest voted duplicate that is not in the same subreddit
  def get_highest_duplicate(self, duplicates):
  	# Sets up a default Submission to hold our duplicate
    highest_duplicate = None
    
    # Just a pre-emptive move to protect ourselves from
    # searching where there are no duplicates
    if(len(duplicates) is 0):
    	return None
    
    # Searches for the highet scoring duplicate
    for duplicate in duplicates:
  		if((highest_duplicate is None or 
    			duplicate.score > highest_duplicate.score) and
    			duplicate.subreddit is not self.subreddit):
  		  highest_duplicate = duplicate
	  
    return highest_duplicate
  
  # Upvotes the ID provided
  def upvote(self, vote_id):
  	self.vote(vote_id, 1)
  
  # Downvotes the ID provided
  def downvote(self, vote_id):
  	self.vote(vote_id, -1)
  
  # Clears the vote for the ID provided
  def clear(self, vote_id):
  	self.vote(vote_id, 0)
  
  # Votes the ID provided (can be a submission or comment)
  def vote(self, vote_id, vote):
  	# The POST parameters and cookie that need to be set for the API
    vote_url      = self.domain + "/api/vote"
    modhash       = self.get_modhash()
    reddit_cookie = self.get_cookie()
  	
    payload = { "id"  : vote_id,
  		         "dir" : vote,
  	           "uh"  : modhash }
  	
  	# Upvotes the ID and sleeps as not to overload the API
    r = requests.post(vote_url, data=payload, headers = self.headers,
   	                  cookies = reddit_cookie)
    self.sleep()
    
  # Comments on a parent_id (can either be a submission or comment)
  def comment(self, parent_id, comment):
  	# The POST paraments and cookie that need to be set for the API
    comment_url   = self.domain + "/api/comment"
    modhash       = self.get_modhash()
    reddit_cookie = self.get_cookie()
  	
    payload = { "parent" : parent_id,
  	          	"text"   : comment,
                "uh"     : modhash }

    # Add the comment to the parent
    r = requests.post(comment_url, data=payload, headers = self.headers,
    	                cookies = reddit_cookie)
    self.sleep()
  
  # Returns the cookie that the reddit API needs
  def get_cookie(self):
  	return dict(reddit_session = self.login["json"]["data"]["cookie"])
  
  # Returns the modhash that the reddit API needs
  def get_modhash(self):
  	return self.login["json"]["data"]["modhash"]

  # Sleeps so as not to overload the API request limit
  def sleep(self):
  	time.sleep(self.sleep_time)

# The class that holds a submissions data
class Submission:
  #Submission variables
  domain       = "http://www.reddit.com"
  sleep_time   = 2
  kind         = "t3"
  title        = ""
  author       = ""
  subreddit    = ""
  score        = None
  id           = None
  url          = ""
  score        = ""
  over_18      = False
  permalink    = ""
  name         = ""
  created_utc  = ""
  comments     = ""
  comment_sort = "top"
  limit        = ""
  login        = None
  headers    = { "User-Agent" : "A reddit bot" }
  extensions = ["jpg", "jpeg", "gif", "png", "bmp"]
	
	# Initialize the submission
  def __init__(self, submission_data):
	  self.domain      = submission_data["domain"]
	  self.sleep_time  = submission_data["sleep_time"]
 	  self.login       = submission_data["login"]
 	  self.headers     = submission_data["headers"]
 	  self.kind        = submission_data["kind"]
 	  self.title       = submission_data["data"]["title"]
 	  self.author      = submission_data["data"]["author"]
 	  self.subreddit   = submission_data["data"]["subreddit"]
 	  self.score       = submission_data["data"]["score"]
 	  self.url         = submission_data["data"]["url"]
 	  self.over_18     = submission_data["data"]["over_18"]
 	  self.permalink   = submission_data["data"]["permalink"]
 	  self.name        = submission_data["data"]["name"]
 	  self.created_utc = submission_data["data"]["created_utc"]
 	  self.id          = submission_data["data"]["id"]
	
  # Comments on a submisison
  def comment(self, comment):
  	# The POST paraments and cookie that need to be set for the API
    comment_url   = self.domain + "/api/comment"
    modhash       = self.get_modhash()
    reddit_cookie = self.get_cookie()
  	
    payload = { "parent" : self.name,
  	          	"text"   : comment,
                "uh"     : modhash }

    # Add the comment to the parent
    r = requests.post(comment_url, data=payload, headers = self.headers,
    	                cookies = reddit_cookie)
    self.sleep()
    
  # Upvotes a submission
  def upvote(self):
  	self.vote(1)
  
  # Downvotes a submission
  def downvote(self):
  	self.vote(-1)
  	
  # Clears a vote on a submission
  def clear(self):
  	self.vote(0)
  
  # Votes the ID provided (can be a submission or comment)
  def vote(self, vote):
  	# The POST parameters and cookie that need to be set for the API
    vote_url      = self.domain + "/api/vote"
    modhash       = self.get_modhash()
    reddit_cookie = self.get_cookie()
  	
    payload = { "id" : self.name,
  		         "dir" : vote,
  	           "uh"  : modhash }
  	
  	# Upvotes the ID and sleeps as not to overload the API
    r = requests.post(vote_url, data=payload, headers = self.headers,
   	                  cookies = reddit_cookie)
    self.sleep()
    
	# Change the comment sort - "top" sort is the default
  def set_comment_sort(self, comment_sort):
	  self.comment_sort = comment_sort
	
	# Get the comments for a particular
  def get_comments(self):
		# Grab the cookie, which is needed for requests to private subreddits
    reddit_cookie = self.get_cookie()

    # Parse the URL for the request
    comments_url = (self.domain + self.permalink + ".json")
    
    # Modifies the URL if a sort method is given
    if self.comment_sort:
    	comments_url += "?sort=" + self.comment_sort
    	
    # Modifies the URL if a limit is given
    if self.limit:
      if self.comment_sort:
    		symbol = "&"
      else:
    	  symbol = "?"
      comments_url += symbol + "limit=" + str(self.limit)
      
    # Request the subreddit's information and sleeps
    r = requests.get(comments_url, cookies = reddit_cookie,
    	               headers = self.headers)
    self.sleep()

    # Parse the response from reddit
    comments_data = simplejson.loads(r.text)
    
    # If there was an error, return the error code
    if "error" in comments_data:
    	return comments_data["error"]
  
    # Initialize a list
    else:
      comments = []
  
    # Go through the results and append them to the list
      for comment in comments_data[1]["data"]["children"]:
      	comment["domain"]     = self.domain
      	comment["sleep_time"] = self.sleep_time
      	comment["login"]      = self.login
        class_comment         = Comment(comment)
        comments.append(class_comment)
      
      return comments
   
  # Gets any duplicates of the original
  def get_duplicates(self):
  	# Get the cookie for the reddit API
    reddit_cookie = self.get_cookie()
 
    # Format the url for duplicates
    duplicates_url = (self.domain + 
  	                  self.permalink.replace("comments", "duplicates", 1) +
  	                  ".json")
  	
  	# Pull the data from the reddit server
    r = requests.get(duplicates_url, cookies = reddit_cookie,
    	               headers = self.headers)
    duplicates_data = simplejson.loads(r.text)
    self.sleep()

    # Get the duplicates
    duplicates = self.get_duplicates_list(duplicates_data[1]["data"]["children"])
    
    # Test to see if we need to run the extension function
    url_list = self.url.split('.')[-3:]
    if len(url_list) is 3:
    	for extension in self.extensions:
    		if url_list[2] == extension:
    			duplicates_extension = self.get_duplicates_extension(extension)
    			if duplicates_extension is not None:
    				duplicates.extend(duplicates_extension)
    			break
    
    return duplicates
    
  # If the file was a direct image link, search the API duplicates
  # sans the file extension
  def get_duplicates_extension(self, extension):
  	# Get the cookie for the reddit API
    reddit_cookie = self.get_cookie()
    
    # Parse the URL
    split_url = self.url.split('.')[-3:]
    img_url   = "http://"  + split_url[0] + '.' + split_url[1]
      
    # Requests the .json file for the modified search
    request_url = self.domain + "/submit.json?url=" + img_url
    r           = requests.get(request_url, cookies = reddit_cookie,
    	                         headers = self.headers)
    duplicates  = simplejson.loads(r.text)
    
    # Determine if we had one or multiple results
    # If true, we have multiple results
    if "data" in duplicates:
    	duplicates = self.get_duplicates_list(duplicates["data"]["children"])
    
    # If false, we either have one result or an error
    else:
    	# One result
    	if "data" in duplicates[0]:
    		duplicates = self.get_duplicates_list(duplicates[0]["data"]["children"])
    	# No duplicates
    	else:
    	  duplicates = None
    
    if duplicates is not None:
      return duplicates
    
  # Turn duplicate JSON data into class data
  def get_duplicates_list(self, duplicates_data):	
  	# Initialize the empty list
  	duplicates = []
  	
  	# Format the other submissions as instance of class
  	for duplicate in duplicates_data:
  		duplicate["domain"]     = self.domain
  		duplicate["sleep_time"] = self.sleep_time
  		duplicate["login"]      = self.login
  		duplicate["headers"]    = self.headers
  		class_duplicate         = Submission(duplicate)
  		duplicates.append(class_duplicate)
  		
  	return duplicates
  
  def get_cookie(self):
  	return dict(reddit_session = self.login["json"]["data"]["cookie"])
  	
  def get_modhash(self):
  	return self.login["json"]["data"]["modhash"]
  	
  def sleep(self):
  	time.sleep(self.sleep_time)
  	
# A class that contains all of the data and methods
# for a comment
class Comment:
	# The variables of our comments
	domain     = "http://www.reddit.com"
	sleep_time = 2
	kind       = "t1"
	body       = ""
	author     = ""
	name       = ""
	parent_id  = ""
	replies    = None
	ups        = 0
	downs      = 0
	score      = 0
	login      = None
	
	# Initializes each comment
	def __init__(self, comment_data):
		# Assign our inherited and comment values
	  self.domain     = comment_data["domain"]
	  self.sleep_time = comment_data["sleep_time"]
	  self.login      = comment_data["login"]
	  self.body       = comment_data["data"]["body"]
	  self.author     = comment_data["data"]["author"]
	  self.name       = comment_data["data"]["name"]
	  self.parent_id  = comment_data["data"]["parent_id"]
	  self.replies    = comment_data["data"]["replies"]
	  self.ups        = comment_data["data"]["ups"]
	  self.downs      = comment_data["data"]["downs"]
	  self.score      = self.ups - self.downs
	  
	  # If the comment has replies, be recurvisey and get those too
	  if self.replies:
	  	# Initializes a list of replies
	  	replies_list = []
	  	
	  	# Get each reply as a Comment and append it to the list
	  	for reply in self.replies["data"]["children"]:
	  		reply["domain"]     = self.domain
	  		reply["sleep_time"] = self.sleep_time
	  		reply["login"]      = self.login
	  		class_reply         = Comment(reply)
	  		replies_list.append(class_reply)
	  		
	  	self.replies = replies_list
	
	# Returns True if the search string is found in any comment
	# False if it isn't found
	def search(self, search_string, ignore = False):
	  # If this comment contains the string, return True
	  if self.body.find(search_string) > -1:
	  	return True
	  	
	 	# If there are replies, search them
	 	if self.replies and ignore is False:
	 	  return self.replies.search(search_string)
	 	  
	 	return False
