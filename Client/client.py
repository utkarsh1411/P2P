import socket
import os
import random
import thread
import cPickle as cp
from thread import *
import platform
import time
import email.utils
import sys
serverPort = int(sys.argv[1])
serverName = sys.argv[2]

def registerFirst(sockClient):
	    
	listOfFiles = os.listdir(os.getcwd())
    	
	for filename in listOfFiles:
		
		if 'rfc' in filename:
			rfcNum=filename[filename.find("c")+1:filename.find(".")]
			titleOfRFC=filename
			requestmsg = "ADD RFC "+str(rfcNum)+" P2P-CI/1.0\r\n"\
			  "Host: "+str(clientHostname)+"\r\n"\
			  "Port: "+str(clientPortNumber)+"\r\n"\
			  "Title: "+str(titleOfRFC)+"\r\n"
			print "Server receives ADD Request"
			print requestmsg
			info_add = cp.dumps([requestmsg], -1)
			sockClient.send(info_add)
			respRec = sockClient.recv(1024)
			print "Server sends ADD Response "
			print respRec
sockClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sockClient.connect((serverName,serverPort))
print 'Connected to server at address: '+str(serverName)+" and port: "+str(serverPort)
clientHostname=sockClient.getsockname()[0]


def RFCsend():
	uploadSocket = socket.socket()
	host='0.0.0.0'
	uploadSocket.bind((host,clientPortNumber))
	uploadSocket.listen(5)
	while 1:
		downloadSocket,downloadAddress = uploadSocket.accept()
		message = downloadSocket.recv(1024)
		sepData=message.split('\r\n')
		if len(sepData)==4 and "GET RFC " in sepData[0] and "Host: " in sepData[1] and "OS: " in sepData[2]:
			if 'P2P-CI/1.0' in sepData[0]:
				request=sepData[0].split(" ")
				if request[0]=='GET':
					rfcNum=request[2]
					pathOfRFC = os.getcwd()+"/rfc"+rfcNum+".txt"
					openTheFile = open(pathOfRFC,'r')
					data = openTheFile.read()
					reply_message = "P2P-CI/1.0 200 OK\r\n"\
							  "Date: "+str(email.utils.formatdate(usegmt=True))+"\r\n"\
							  "OS: "+str(platform.platform())+"\r\n"\
							  "Last-Modified: "+str(time.ctime(os.path.getmtime(pathOfRFC)))+"\r\n"\
							  "Content-Length: "+str(len(data))+"\r\n"\
							  "Content-Type: text/plain\r\n"
					reply_message=reply_message+data
					downloadSocket.sendall(reply_message)
			else:
				reply_message="505 P2P-CI Version Not Supported\r\n"
				downloadSocket.send(reply_message)
		else:
			reply_message="400 Bad Request\r\n"
			downloadSocket.send(reply_message)
			
def DownloadRFC(requestmsg,peer_host_name,peer_port_number,rfc_number):

	requestPeerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	requestPeerSocket.connect((peer_host_name,int(peer_port_number)))
	
	print 'Connection established'
	requestPeerSocket.sendall(requestmsg)
	get_reply=""
	get_reply=requestPeerSocket.recv(1024)
	if 'P2P-CI/1.0 200 OK' in get_reply.split("\r\n")[0]:
		print 'P2P-CI/1.0 200 OK'
		content_line=(get_reply.split("\r\n"))[4]
		content_length=int(content_line[content_line.find('Content-Length: ')+16:])
		get_reply=get_reply+requestPeerSocket.recv(content_length)
		pathOfRFC = os.getcwd()+"/rfc"+rfc_number+".txt"
		data=get_reply[get_reply.find('text/plain\r\n')+12:]

		with open(pathOfRFC,'w') as file:
			file.write(data)
		print 'File downloaded and stored'
		mess= "success"
	elif 'Version Not Supported' in get_reply.split("\r\n")[0]:
		print get_reply
		mess= "fail"
	elif 'Bad Request' in get_reply.split("\r\n")[0]:
		print get_reply
		mess= "fail"
	requestPeerSocket.close()
	
def inputFromUser():

	print "Enter from the following options: ADD, GET, LIST, LOOKUP or EXIT:"
	service = raw_input()

	if service == "ADD":

		print "Enter RFC Number"
		client_rfc_num = raw_input()
		print "Enter Title"
		client_rfc_title = raw_input()

		pathOfRFC = os.getcwd()+"/rfc"+client_rfc_num+".txt"
		if os.path.isfile(pathOfRFC):
			
			requestmsg = "ADD RFC "+str(client_rfc_num)+" P2P-CI/1.0\r\n"\
			  "Host: "+str(clientHostname)+"\r\n"\
			  "Port: "+str(clientPortNumber)+"\r\n"\
			  "Title: "+str(client_rfc_title)+"\r\n"
			print "Server receives ADD Request"
			print requestmsg
			info_add = cp.dumps([requestmsg], -1)
			sockClient.send(info_add)
			response_received = sockClient.recv(1024)
			print "Server sends ADD Response"
			print response_received
		else:
			print "File not found"

		inputFromUser()

	elif service == "GET":

		print "Enter RFC Number"
		client_rfc_num = raw_input()
		print "Enter Title"
		client_rfc_title = raw_input()
		requestmsg = "LOOKUP RFC "+str(client_rfc_num)+" P2P-CI/1.0\r\n"\
			  "Host: "+str(clientHostname)+"\r\n"\
			  "Port: "+str(clientPortNumber)+"\r\n"\
			  "Title: "+str(client_rfc_title)+"\r\n"
		print "LOOKUP Request to be sent to the server for completing the GET request"
		print requestmsg


		info_add = cp.dumps([requestmsg], -1)
		sockClient.sendall(info_add)
		response_received = sockClient.recv(1024)
		sepData=response_received.split('\r\n')

		print "LOOKUP Response sent from the server"
		
		if '404 Not Found' in sepData[0]:
			print response_received
		elif 'Version Not Supported' in sepData[0]:
			print response_received
		elif 'Bad Request' in sepData[0]:
			print response_received
		else:
			print response_received
			sepData=sepData[1].split(" ")
			peer_host_name=sepData[3]
			peer_port_number=sepData[4]
			requestmsg = "GET RFC "+str(client_rfc_num)+" P2P-CI/1.0\r\n"\
						"Host: "+str(clientHostname)+"\r\n"\
						"OS: "+platform.platform()+"\r\n"
			
			print "GET Request to be sent to the peer holding the RFC File"
			print requestmsg

			start_new_thread(DownloadRFC,(requestmsg,peer_host_name,peer_port_number,client_rfc_num))


			pathOfRFC = os.getcwd()+"/rfc"+client_rfc_num+".txt"
			if os.path.isfile(pathOfRFC):
				requestmsg = "ADD RFC "+str(client_rfc_num)+" P2P-CI/1.0\r\n"\
			  "Host: "+str(clientHostname)+"\r\n"\
			  "Port: "+str(clientPortNumber)+"\r\n"\
			  "Title: "+str(client_rfc_title)+"\r\n"
				print "ADD Request to be sent to the server"
				print requestmsg
				info_add = cp.dumps([requestmsg], -1)
				sockClient.send(info_add)
				response_received = sockClient.recv(1024)
				print "ADD Response sent from the server"
				print response_received
		inputFromUser()

	elif service == "LIST":		
		requestmsg = "LIST ALL P2P-CI/1.0\r\n"\
			  "Host: "+str(clientHostname)+"\r\n"\
			  "Port: "+str(clientPortNumber)+"\r\n"
		print "LIST Request to be sent to the server"
		print requestmsg
		info_add = cp.dumps([requestmsg], -1)
		sockClient.send(info_add)
		response_received = sockClient.recv(1024)

		print "LIST Response sent from the server"
		print response_received

		inputFromUser()

	elif service == "LOOKUP":

		print "Enter RFC Number"
		client_rfc_num = raw_input()
		print "Enter Title"
		client_rfc_title = raw_input()
		
		requestmsg = "LOOKUP RFC "+str(client_rfc_num)+" P2P-CI/1.0\r\n"\
			  "Host: "+str(clientHostname)+"\r\n"\
			  "Port: "+str(clientPortNumber)+"\r\n"\
			  "Title: "+str(client_rfc_title)+"\r\n"
		print "LOOKUP Request to be sent to the server"
		print requestmsg
		info_add = cp.dumps([requestmsg], -1)
		sockClient.send(info_add)
		response_received = sockClient.recv(1024)

		print "LOOKUP Response sent from the server"		
		print response_received

		inputFromUser()

	elif service == "EXIT":
		message = "EXIT P2P-CI/1.0\r\nHost: "+str(clientHostname)+"\r\nPort: "+str(clientPortNumber)
		info_add = cp.dumps([message], -1)
		sockClient.send(info_add)
		sockClient.close()
	else:
		print 'Wrong input. Please try again.'
		inputFromUser()
clientPortNumber = 60000 + random.randint(1,100)
data = cp.dumps([clientPortNumber])
sockClient.send(data)
sockClient.close

registerFirst(sockClient)


start_new_thread(RFCsend,())
inputFromUser()


