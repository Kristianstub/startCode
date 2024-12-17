Code from the 48 hour hackathon StartCode by Start NTNU. The goal was to set up a reverse SSH connection between raspberry PIS and a server. 
The repository includes the clientside code, the serverside code and the code for the simplistic interface.
The client side code is made to package data from the PI into a json file and make a HTTP request to the server so the server can register it.
The server side code updates the DNS so the PIs can connect and handles registering of and assigning of SSH keys. The server is also the host of the interface
