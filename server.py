import socket
import thread
import cPickle as cp
from thread import *
PortOfServer = 7734
SocketOfServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
NameOfSocket=socket.gethostbyname(socket.gethostname())
SocketOfServer.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
SocketOfServer.bind((NameOfSocket, PortOfServer))
SocketOfServer.listen(4)
print 'Server is ready to go.'
PeerDictionary = {}
TitleDictionary = {}
HostDictionary = {}

def AddingToDictionary(hostname, data):
	global PeerDictionary
	PeerDictionary[hostname] = data

def AddRFCfunc(NumberOfRFC, NameOfClient, PortNumOfClient, TitleOfRFC):
	global HostDictionary,TitleDictionary	
	if NumberOfRFC in TitleDictionary:		
		RFConHost = HostDictionary.get(NumberOfRFC)
		RFConHost=RFConHost+str(NameOfClient) + "-"
		HostDictionary[NumberOfRFC] = RFConHost
	else:
		TitleDictionary[NumberOfRFC] = TitleOfRFC
		HostDictionary[NumberOfRFC] = NameOfClient+"-"
		

def ListRFC(NameOfClient, PortNameOfClient):
	global HostDictionary,TitleDictionary,PeerDictionary	

	listOfRFC=HostDictionary.keys()
	if len(listOfRFC)!=0:
		message = "P2P-CI/1.0 200 OK"
		for rfc in listOfRFC:
			ListOfRFChost=HostDictionary.get(rfc)
			individualhosts=ListOfRFChost.split('-')
			l=len(individualhosts)

			for i in range(l-1):
				temp = "RFC "+str(rfc)+" "+str(TitleDictionary.get(rfc))+" "+str(individualhosts[i])+" "+str(PortNameOfClient)
				message = message + "\r\n" + temp
		message=message+"\r\n"
	else:
		message = "P2P-CI/1.0 404 Not Found\r\n"
	return message

def lookupFunc(NumberOfRFC, NameOfClient, PortNumOfClient, TitleOfRFC):
	global HostDictionary,TitleDictionary, PeerDictionary,lookupmsg	
	if NumberOfRFC in TitleDictionary and TitleDictionary[NumberOfRFC] == TitleOfRFC:
		lookupmsg = "P2P-CI/1.0 200 OK"
		ListOfRFChost = HostDictionary.get(NumberOfRFC)
		individualhosts=ListOfRFChost.split('-')
		l=len(individualhosts)
		for i in range(l-1):
			temp = "RFC "+str(NumberOfRFC)+" "+str(TitleOfRFC)+" "+str(individualhosts[0])+" "+str(PortNumOfClient)
			lookupmsg = lookupmsg + "\r\n" + temp
		lookupmsg=lookupmsg+"\r\n"
	else:
		lookupmsg = "P2P-CI/1.0 404 Not Found\r\n"
	return lookupmsg

def initialization(connection, addr):
	global HostDictionary,TitleDictionary,PeerDictionary
	data = cp.loads(connection.recv(1024))
	hostname=addr[0]+":"+str(data[0])
	AddingToDictionary(hostname, data)
	
	while 1:
		ReceivedMessage = connection.recv(1024)
		ClientMessage = cp.loads(ReceivedMessage)
		print 'message received from client for, ' + str(ClientMessage[0])
		if ClientMessage[0][0] == 'A':
			split = ClientMessage[0].split('\r\n')
			print '##########################################'+split[0][split[0].find("C ")+2:split[0].find(" P")]+'######################3'
			if 'P2P-CI/1.0' in split[0]:
				if len(split) == 5 and "ADD RFC " in split[0] and "Host: " in split[1] and "Port: " in split[2] and "Title: " in split[3]:
					
					NumberOfRFC=split[0][split[0].find("C ")+2:split[0].find(" P")]
					NameOfClient=split[1][split[1].find("Host: ")+6:]
					
					PortNumOfClient=split[2][split[2].find("Port: ")+6:]
					
					TitleOfRFC=split[3][split[3].find("Title: ")+7:]		
					p2p_version=split[0][split[0].find(" P")+1:]
					AddRFCfunc(NumberOfRFC, NameOfClient, PortNumOfClient, TitleOfRFC)	
					message = "P2P-CI/1.0 200 OK\r\n"+split[1]+"\r\n"+split[2]+"\r\n"+split[3]+"\r\n"
					connection.send(message)
				else:
					message="400 Bad Request\r\n"
					connection.send(message)
			else:
				message = "505 P2P-CI Version Not Supported\r\n"
				connection.send(message)
		elif ClientMessage[0][0] == 'L':
			if ClientMessage[0][1] == 'I':
				split_data = ClientMessage[0].split('\r\n')
				if 'P2P-CI/1.0' in split_data[0]:
					if len(split_data) == 4 and "LIST ALL " in split_data[0] and "Host: " in split_data[1] and "Port: " in split_data[2]:
						NameOfClient=split_data[1][split_data[1].find("Host: ")+6:]
						PortNumOfClient=split_data[2][split_data[2].find("Port: ")+6:]
						message=ListRFC(NameOfClient, PortNumOfClient)
						connection.send(message)
					else:
						message="400 Bad Request\r\n"
						connection.send(message)
				else:
					message = "505 P2P-CI Version Not Supported\r\n"
					connection.send(message)
			elif ClientMessage[0][1] == 'O':
				split_data = ClientMessage[0].split('\r\n')
				if 'P2P-CI/1.0' in split_data[0]:
					print split_data[0]
					print split_data[1]
					print split_data[2]
					print split_data[3]
					length_of_split = len(split_data)
					if len(split_data) == 5 and "LOOKUP RFC " in split_data[0] and "Host: " in split_data[1] and "Port: " in split_data[2] and "Title: " in split_data[3]:
						NumberOfRFC=split_data[0][split_data[0].find("C ")+2:split_data[0].find(" P")]
						NameOfClient=split_data[1][split_data[1].find("Host: ")+6:]
						PortNumOfClient=split_data[2][split_data[2].find("Port: ")+6:]
						TitleOfRFC=split_data[3][split_data[3].find("Title: ")+7:]	
						print TitleOfRFC 
						p2p_version=split_data[0][split_data[0].find(" P")+1:]
						reqmessage=lookupFunc(NumberOfRFC, NameOfClient, PortNumOfClient, TitleOfRFC)
						connection.send(reqmessage)
					else:
						message="400 Bad Request\r\n"
						connection.send(message)
				else:
					message = "505 P2P-CI Version Not Supported\r\n"
					connection.send(message)
		elif ClientMessage[0][0] == 'E':
			split_data = ClientMessage[0].split('\r\n')
			NameOfClient=split_data[1][split_data[1].find("Host: ")+6:]
			PortNumOfClient=split_data[2][split_data[2].find("Port: ")+6:]

			listOfRFC = HostDictionary.keys()
			print "Exit RFC"
			for rfc in listOfRFC:		
				ListOfRFChost = HostDictionary.get(rfc)
				individualhosts=ListOfRFChost.split('-')
				l=len(individualhosts)
				
				if l==2 and NameOfClient in individualhosts[0]:
					TitleDictionary.pop(rfc,None)
					HostDictionary.pop(rfc,None)
				else:
					for i in range(0,l-1):
						if NameOfClient in individualhosts[i]:
							print NameOfClient
							variable = i
							individualhosts.remove(NameOfClient)
							
							temp=""
							for j in range(0,l-2):
								temp=temp+individualhosts[j]+"-"
							HostDictionary[rfc] = temp
			if PeerDictionary.has_key(NameOfClient):	
				PeerDictionary.pop(NameOfClient,None)
			connection.close()
			break
while 1:
	connection, addr = SocketOfServer.accept()
	print 'Got incoming connection request from ', addr
	start_new_thread(initialization, (connection, addr))
SocketOfServer.close()





