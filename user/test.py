from socket import *

ser = socket(AF_INET,SOCK_STREAM)
ser.bind( ('',8888) )
ser.listen(5)

clisock,addr = ser.accept()
print(addr[0] + ":"+str(addr[1]))
clisock.send( "first:hahahah".encode('utf-8') )
clisock.send( "second:hello".encode('utf-8') )
clisock.close()