from socket import *
import sys
import threading
import time
import random
# The template comes from the book, James F. Kurose, Keith Ross - Computer Networking
# A Top Down Approach, pg. 196-197
import pickle
# pickle for sending and receiving lists

# To hide traceback output:
sys.tracebacklimit = 0

users = []
# List of users
user_tweets = {}
# dictionary: key with value list of tuples
# key is user, to store all users tweets
# List of tuples is [(tweet,hashtag), (tweet,hashtag)]
# Insert pair in dictionary: user_tweets[user] = [(tweet,hashtag)]
# Add new tweet, hashtag to user: user_tweets[user].append((tweet,hashtag))
# Access list of tweets,hashtags: user_tweets[user]
# Remove user and all its tweets: del user_tweets[user]
user_hashtags = {}
# dictionary: key with value list
# key is user
# List is of subscribed hashtags, at most 3
# Insert pair in dictionary: user_hashtags[user] = [hashtag]
# Add new hashtag to user: user_hashtags[user].append(hashtag)
# Access list of hashtags: user_hashtags[user]
# Remove hashtag from list: user_hashtags[user].remove(hashtag)
# Remove user and all hashtags: del user_hashtags[user]
user_timeline = {}
# dictionary: key with value list of tuples
# Same dictionary format as user_tweets
# Stores everything that has been displayed to the user for timeline
tweets_in_order = []
# List of tuples for all tweets
# Tuple in format: (user, message, hashtag)
# List in format: [(user, message, hashtag), (), ()]
# Used so server knows which tweets to display to each client

# Thread for sending new tweets to subscribed users
def on_new_tweets(sender,message,hashtag):
	hashtag = hashtag.split("#")
	for i in range(len(hashtag)):
		hashtag[i] = "#" + hashtag[i]
	del hashtag[0]
	# Check if hashtag is subscribed to by person
	for person in users:
		subscribed = False
		if person in user_hashtags:
			for tag in user_hashtags[person]:
				for temp in hashtag:
					if tag == temp or tag == "#ALL":
						subscribed = True
		# If user is subscribed to hashtag, connect and send tweet
		if subscribed:
			clientSocket = socket(AF_INET, SOCK_STREAM)
			clientSocket.connect(("127.0.0.1",client_ports[person]))
			clientSocket.send(pickle.dumps((sender,message,hashtag)))
			clientSocket.close()
			if person in user_timeline:
				user_timeline[person].append((sender,message,hashtag))
			else:
				user_timeline[person] = [(sender,message,hashtag)]

# Thread method for new client
def on_new_client(connectionSocket,addr,user):
	print("server read: TweetMessage{username='" + user + "', msg='null', hashTags='null', operation='init'}")
	while True:
		# Receive command from client
		command = connectionSocket.recv(1024).decode()
		# If received command is input error, meaning user input error
		if command == "input error":
			print("server read: input error")
			continue
		# If received command is exit
		if command == "exit":
			print("server read: TweetMessage{username='" + user + "', msg='null', hashTags='null', operation='exit'}")
			# Code for cleaning up exiting user
			users.remove(user)
			del client_ports[user]
			if user in user_tweets:
				del user_tweets[user]
			if user in user_hashtags:
				del user_hashtags[user]
			if user in user_timeline:
				del user_timeline[user]
			return
		# If received command is timeline
		if command == "timeline":
			print("server read: TweetMessage{username='" + user + "', msg='null', hashTags='null', operation='timeline'}")
			# If user has a timeline, dump and send to user
			if user in user_timeline:
				connectionSocket.send("has timeline".encode())
				connectionSocket.recv(1024).decode()
				connectionSocket.send(pickle.dumps(user_timeline[user]))
			# If user does not has a timeline
			else:
				connectionSocket.send("no timeline".encode())
				connectionSocket.recv(1024).decode()
			continue
		# If received command is getusers, dump and send to user
		if command == "getusers":
			connectionSocket.send(pickle.dumps(users))
			print("server read: TweetMessage{username='" + user + "', msg='null', hashTags='null', operation='getusers'}")
			continue
		# If command is none of the above, split command
		command = command.split(" ", 1)
		# If command is tweet
		if command[0] == "tweet":
			# Split command for message and hashtag
			command = (command[0], command[1].rsplit(" ", 1)[0], command[1].rsplit(" ",1)[1])
			message = command[1].strip()
			hashtag = command[2]
			print("server read: TweetMessage{username='" + user + "', msg='" + message + "', hashTags='" + hashtag + "', operation='tweet'}")
			# If user has tweets already
			if (user in user_tweets.keys()):
				user_tweets[user].append((message,hashtag))
			# If first time user is tweeting
			else:
				user_tweets[user] = [(message,hashtag)]
			# Append tweet to list of all tweets
			tweets_in_order.append((user, message, hashtag))
			# Start thread for sending tweet to subscribed users
			news_thread = threading.Thread(target=on_new_tweets,args=(user,message,hashtag),daemon=True)
			news_thread.start()
		# If received command is subscribe
		if command[0] == "subscribe":
			hashtag = command[1]
			print("server read: TweetMessage{username='" + user + "', msg='null', hashTags='" + hashtag + "', operation='subscribe'}")
			# If user is subscribed to hashtags, check if there is room for new hashtag
			if user in user_hashtags.keys():	
				if len(user_hashtags[user]) >= 3:
					connectionSocket.send("illegal".encode())
					continue
				else:
					connectionSocket.send("legal".encode())
					user_hashtags[user].append(hashtag)
			# If first time subscribing to a hashtag
			else:
				connectionSocket.send("legal".encode())
				user_hashtags[user] = [hashtag]
		# If received command is unsubscribe
		if command[0] == "unsubscribe":
			hashtag = command[1]
			print("server read: TweetMessage{username='" + user + "', msg='null', hashTags='" + hashtag + "', operation='unsubscribe'}")
			# Check for #ALL hashtag
			if hashtag == "#ALL":
				user_hashtags[user] = []
			else:
				# Check for user subscribed to hashtag and then remove
				if user in user_hashtags and hashtag in user_hashtags[user]:
					user_hashtags[user].remove(hashtag)
		# If received command is gettweets
		if command[0] == "gettweets":
			user_with_tweets = command[1]
			print("server read: TweetMessage{username='" + user + "', msg='" + user_with_tweets + "', hashTags='null', operation='gettweets'}")
			# If user not in users
			if user_with_tweets not in users:
				connectionSocket.send("no user".encode())
				connectionSocket.recv(1024).decode()
			# If user is in users
			else:
				# If user does not have any tweets
				if user_with_tweets not in user_tweets:
					connectionSocket.send("no tweets".encode())
					connectionSocket.recv(1024).decode()
					continue
				# Send all tweets regardless of number of tweets
				connectionSocket.send("is a user".encode())
				connectionSocket.recv(1024).decode()
				connectionSocket.send(pickle.dumps(user_tweets[user_with_tweets]))
			continue
	connectionSocket.close()


"""
Error checking input
"""

# Checking for incorrect number of arguments
if len(sys.argv) != 2:
	print("Invalid arguments: Incorrect number of arguments")
	exit()
# Checking for invalid port number
if sys.argv[1].isnumeric():
	serverPort = int(sys.argv[1])
else:
	print("Invalid arguments: Invalid Port Number")
	exit()
if not(serverPort >= 1024 and serverPort <= 65535):
	print("Invalid arguments: Invalid Port Number")
	exit()

"""
Running the server
"""

# Creating socket for incoming request
serverSocket = socket(AF_INET,SOCK_STREAM)
# Associating the server port number with the socket
serverSocket.bind(("127.0.0.1",serverPort))
# Waiting for client to ask to make connection
serverSocket.listen(1)
print("server listening at " + str(serverPort))
client_ports = {}
while True:
	# Wait for incoming connection request
	connectionSocket, addr = serverSocket.accept()
	# Receiving from the client whether upload or download
	user = connectionSocket.recv(1024).decode()
	# If username is already in the server
	if (user in users):
		connectionSocket.send("illegal".encode())
		connectionSocket.close()
		continue
	# If username is available
	else:
		users.append(user)
		connectionSocket.send("legal".encode())
		print("server got connection!")
		# Assign user random port for sending tweets and send assignment
		random_port = random.randrange(1024, 65535)
		while random_port == serverPort:
			for i in client_ports:
				if client_ports[i] == random_port:
					random_port = random.randrange(1024, 65535)
		client_ports[user] = random_port
		connectionSocket.send(str(random_port).encode())
		# Start thread for client's command
		running = True
		client_thread = threading.Thread(target=on_new_client, args=(connectionSocket,addr,user))
		client_thread.start()
connectionSocket.close()