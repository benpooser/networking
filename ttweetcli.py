#from socket import *
import socket
import sys
import threading
import time
# The template comes from the book, James F. Kurose, Keith Ross - Computer Networking
# A Top Down Approach, pg. 194
import pickle
# pickle for sending and receiving lists

# To hide traceback output, comment out for debugging:
sys.tracebacklimit = 0

"""
Error checking input
"""

# Checking for incorrect number of arguments
if len(sys.argv) != 4:
	print("error: args should contain <ServerIP>   <ServerPort>   <Username>")
	exit()

# Checking for invalid IP address
serverIP = sys.argv[1]
try:
	socket.inet_aton(serverIP)
except socket.error:
	print("error: server ip invalid, connection refused.")
	exit()

# Checking for invalid port number
serverPort = int(sys.argv[2])
if sys.argv[2].isnumeric():
	serport = serverPort
else:
	print("error: server port invalid, connection refused.")
	exit()
if not(serverPort >= 1024 and serverPort <= 65535):
	print("error: server port invalid, connection refused.")
	exit()

# Checking for valid username
username = sys.argv[3]
if len(username) == 0:
	print("error: username has wrong format, connection refused.")
	exit()
for character in username:
	if not(character.isalpha()) and not(character.isnumeric()):
		print("error: username has wrong format, connection refused.")
		exit()
			

def new_tweets_thread(clientSocket, new_port):
	serverSocket = socket(AF_INET,SOCK_STREAM)
	serverSocket.bind(("127.0.0.1",new_port))
	serverSocket.listen(1)
	while True:
		connectionSocket, addr = serverSocket.accept()
		new_tweet = pickle.loads(connectionSocket.recv(1024))
		print(new_tweet[0] + " " + new_tweet[1] + " ", end='')
		for i in new_tweet[2]:
			print(i,end='')
		print("")
		connectionSocket.close()
		

"""
Connecting to server
"""
from socket import *
# Creating client socket and connecting to server IP
clientSocket = socket(AF_INET, SOCK_STREAM)
# Checking for valid server name and port 
try: 
	# Initiating the TCP connection 
	clientSocket.connect((serverIP,serverPort)) 
except:
	print("connection error, please check your server: Connection refused")
	exit()
# Sends username to server to check if valid
clientSocket.send(username.encode())
username_response = clientSocket.recv(1024).decode()
# If username is already taken
if (username_response == "illegal"):
	print("username illegal, connection refused.")
	clientSocket.close()
	exit()
# If username is available, user stays connected
else:
	print("username legal, connection established.")
	connected = True
	# User gets assigned port for receiving tweets
	new_port = clientSocket.recv(1024).decode()
	if new_port.isnumeric():
		new_port = int(new_port)
	else:
		print(new_port)
		exit()
	# Starting thread for receiving tweets
	news_thread = threading.Thread(target=new_tweets_thread,args = (clientSocket,new_port),daemon=True)
	news_thread.start()
	# While connected to the server
	while(connected):
		# User inputs command
		command = input()
		# If user's command is exit
		if (command == "exit"):
			# Send exit command and end connection
			clientSocket.send(command.encode())
			connected = False
			clientSocket.close()
			print("bye bye")
			exit()
		# If user's command is timeline
		if command == "timeline":
			# Send timeline command to server
			clientSocket.send(command.encode())
			tl_resp = clientSocket.recv(1024).decode()
			clientSocket.send("ack".encode())
			# If resp is has a timeline, load and print
			if tl_resp == "has timeline":
				tl = pickle.loads(clientSocket.recv(131072))
				for line in tl:
					print(line[0] + ": " + line[1] + " ", end='')
					for i in line[2]:
						print(i,end='')
					print("")
			continue
		# If user's command is getusers
		if command == "getusers":
			# Send getusers command to server and load list of users
			clientSocket.send(command.encode())
			get_users_list = clientSocket.recv(1024)
			get_users_list = pickle.loads(get_users_list)
			for i in get_users_list:
				print(i)
			continue
		# If command is none of above, split
		command_split = command.split(" ", 1)
		# If user's command is tweet
		if command_split[0] == "tweet":
			# Split tweet into message and hashtag
			command_split = (command_split[0], command_split[1].rsplit(" ", 1)[0], command_split[1].rsplit(" ",1)[1])
			message = command_split[1]
			hashtag = command_split[2]
			# Check for valid hashtag syntax
			for character in hashtag:
				if not(character.isalpha()) and not(character.isnumeric()) and character != "#":
					print("hashtag format illegal.")
					clientSocket.send("input error".encode())
					continue
			# Check for valid message syntax
			if message == "\"\"":
				print("message format illegal.")
				clientSocket.send("input error".encode())
				continue
			elif len(message.strip("\"")) > 150:
				print("message length illegal, connection refused.")
				clientSocket.send("input error".encode())
				continue
			# Split at hashtag and send command
			hashtag = hashtag.split("#")
			for i in range(len(hashtag)):
				hashtag[i] = "#" + hashtag[i]
			clientSocket.send(command.encode())
			continue
		# If user's command is subscribe
		if command_split[0] == "subscribe":
			hashtag = command_split[1]
			# Send subscribe command to server
			clientSocket.send(command.encode())
			resp = clientSocket.recv(1024).decode()
			# If user is already subscribe to 3 hashtags
			if resp == "illegal":
				print("operation failed: sub " + hashtag + " failed, already exists or exceeds 3 limitation")
			# If user is not already subscribe to 3 hashtags
			else:
				print("operation success")
			continue
		# If user's command is unsubscribe
		if command_split[0] == "unsubscribe":
			hashtag = command_split[1]
			# Send unsubscribe command to server
			clientSocket.send(command.encode())
			print("operation success")
			continue
		# If user's command is gettweets
		if command_split[0] == "gettweets":
			user = command_split[1]
			# Send gettweets command
			clientSocket.send(command.encode())
			resp = clientSocket.recv(1024).decode()
			clientSocket.send("ack".encode())
			# If user is not a user in the server
			if resp == "no user":
				print("no user " + user + " in the system")
			# If user has no tweets
			elif resp == "no tweets":
				continue
			# If user has tweets, load and print
			elif resp == "is a user":
				user_tweets = pickle.loads(clientSocket.recv(4096))
				for tweet in user_tweets:
					print(user + ": " + tweet[0] + " " + tweet[1])
			continue
		