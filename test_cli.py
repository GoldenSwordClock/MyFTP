from socket import *

cli = socket(AF_INET,SOCK_STREAM)

cli.bind(('',8889))

cli.connect( ('127.0.0.1',8888) )

first = cli.recv(10)
print( "first recv:" + first.decode('utf-8'))
second = cli.recv(10)
print( 'second recv:'+second.decode('utf-8'))