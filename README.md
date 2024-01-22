# IRC-Tchat-Coco

This project re-creates some basic features of an IRC tchat system.

## how to run

first fire a terminal and start the server : <br>
	- `chmod +x server.py && ./server.py <server_name>`

start some clients : <br>
	- `chmod +x gui_client.py` <br>
	- `./gui_client.py <user1>` <br>
	- `./gui_client.py <user2>` <br>

## available features

	- **/away [message]** notify all users that your away
	- **/help** prints this text
	- **/invite <nick>** invite a friend to your current channel
	- **/join <canal>** join a channel
	- **/list** prints all the current channels
	- **/msg [canal|nick] message** public or private messages (brackets compulsory)
	- **/names <channel>** returns all users from a channel