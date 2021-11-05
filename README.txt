======================================================

Team Members:

Ethan Bills, Matthew McKelvey, Ben Pooser

Work was allocated equally between all team members.


======================================================

High Level Description:

The program runs by first starting the server. The client
then tries to connect to the server and establishes a 
connection with a valid username. The server then starts
a thread for the specific client, and the client starts
a thread for receiving tweets that they are subscribed 
to. The client waits for user input, checks for a valid 
command, then sends the command to the server. The 
server then does the functionality of the command,
sending back any required information from the command.
If the command was a tweet command, then the server starts
a thread just for sending the tweet to all users that are
subscribed to the hashtag through their thread for receiving
tweets. Then the server and user wait for user command again.
Upon user exiting, all information stored for the specific
user is deleted from the server.


======================================================

How to use Code:


Command for running server:

$ python3 ttweetser.py <Port>

Specific example:

$ python3 ttweetser.py 13000


Command for running client:

$ python3 ttweetcli.py <ServerIP>   <ServerPort>   <Username>

Specific example:

$ python3 ttweetcli.py 127.0.0.1 13000 cxworks


Specific commands for connected client:

Tweet with a message and hashtag:

tweet​ “<150 char max tweet>” <Hashtag>

Subscribe to a specific hashtag:

subscribe​ <Hashtag>

unsubscribe:

unsubscribe​ <Hashtag>

Client's timeline:

timeline

Retrieve name of all clients:

getusers

Retrieve all tweets from a given user:

gettweets ​<Username>

Exit client from the server:

exit

======================================================

Any Dependent Packages:

N/A 

======================================================