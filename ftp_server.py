#from tkinter import *
#from tkinter import messagebox
#from tkinter import filedialog
from socket import *
#from PIL import Image,ImageTk
import os
from threading import *

SybOfSplit_cmddata = "|*|"
SybOfSplit_filename = "|-|"

cmd_port = 9000  #命令传输端口
data_port = 9001 #数据传输端口
ip = ""

MAX_CMD_SIZE = 1024
MAX_ONE_PACKET = 1024*2
MAX_SIZE_ONE_PACKET = 1024

init_file = os.path.join(os.getcwd(),"user")

def recv( clisock ):
    flag = True
    recvdatalen = 0
    recvdata = b''
    while flag:
        onetimerecv = clisock.recv( MAX_SIZE_ONE_PACKET )
        onetimelen = len(onetimerecv)
        recvdata += onetimerecv
        print("onetimelen:" + str(onetimelen) )
        if onetimelen < MAX_SIZE_ONE_PACKET:
            flag = False
        recvdatalen += onetimelen
    #recvdata = recvdata.decode("utf-8")
    #print("recv:")
    #print(recvdata)
    return recvdata

class ServerManager:
    def __init__(self):
        self.filemanager = FileManager()
        #self.filemanager.open(path.join(getcwd(),"user"))
        self.cmd_conn_list = []
        self.ser_sock = socket(AF_INET,SOCK_STREAM)
        self.ser_sock.bind( (ip,cmd_port) )
        self.ser_sock.listen(5)
        #self.cmd_interpreter = CMD_Interpreter()

    def addAConnecter(self,sockinfo): #增加一个
        print("get a new connect:\nip:"+str(sockinfo[1])+ "\nport:" +str(sockinfo[2]))
        sockinfo.append(init_file)  #初始文件夹
        self.cmd_conn_list.append( sockinfo )
    
    def run(self):
        while True:
            print("listen to "+str(ip)+":"+str(cmd_port))
            newcli_sock, newcli_addr = self.ser_sock.accept()
            self.addAConnecter( [newcli_sock,newcli_addr[0],newcli_addr[1]] )
            #多线程处理一个已经连接的sock，等待接收信息
            athread = Thread( target=self.cnnect_run, args=(newcli_sock,newcli_addr[0],newcli_addr[1]) )
            athread.start()
            
    def cnnect_run(self, running_clisock,sock_ip,sock_port):
        self.cmd_init(running_clisock)
        while True:
            #首先给客户端发送初始文件夹的文件列表信息

            #cmddata = running_clisock.recv( MAX_CMD_SIZE ).decode("utf-8")
            try:
                cmddata = running_clisock.recv( MAX_CMD_SIZE ).decode("utf-8")
            except (ConnectionResetError,ConnectionAbortedError):
                print(str(sock_ip) + ":"+str(sock_port)+"  退出连接")
                for i in self.cmd_conn_list:
                    if i[0] == running_clisock:
                        self.cmd_conn_list.remove(i)
                    else:
                        print( "连接列表:"+str( i[1] )+":" + str(i[2])+"   目前访问文件路径为:"+str(i[3]))
                return
            
            if cmddata == '':
                print('接到空数据')
                return
            print("recv data:" + cmddata)
            cmd = cmddata.split(SybOfSplit_cmddata)[0]
            #filepath = cmddata.split("|*|")[1]
            if cmd == "get":
                self.cmd_get(running_clisock,cmddata)
                print( "处理了" + str(sock_ip)+":"+str(sock_port) + "的" +"get请求" )
            elif cmd == "post":
                self.cmd_post(running_clisock,cmddata)
                print( "处理了" + str(sock_ip)+":"+str(sock_port) + "的" +"post请求" )
            elif cmd == "forward":
                self.cmd_forward(running_clisock,cmddata)
                print( "处理了" + str(sock_ip)+":"+str(sock_port) + "的" +"forward请求" )
            elif cmd == "backward":
                self.cmd_backward(running_clisock, cmddata)
                print( "处理了" + str(sock_ip)+":"+str(sock_port) + "的" +"backward请求" )
            elif cmd == 'fresh':
                self.cmd_fresh(running_clisock,cmddata)
                print( "处理了" + str(sock_ip)+":"+str(sock_port) + "的" +"fresh请求" )
            #处理cmd
    
    def cmd_get(self,running_clisock,cmddata):
        targetfilepath = ''
        targetcmd_conn = []
        for i in self.cmd_conn_list:
            if i[0] == running_clisock:
                targetfilepath = i[3]
                targetcmd_conn = i
        filename = cmddata.split(SybOfSplit_cmddata)[1]
        self.filemanager.open( os.path.join(targetfilepath,filename) )
        result,filecontext,filesize = self.filemanager.getfilecontext()
        if result:
            senddata = str(filesize)+SybOfSplit_filename
            senddata = senddata.encode('utf-8')
            senddata += filecontext
            running_clisock.send(senddata)
        else:
            print("打开文件失败:" + os.path.join(targetfilepath,filename))

    def cmd_post(self,running_clisock ,cmddata):
        targetfilepath = ''
        targetcmd_conn = []
        for i in self.cmd_conn_list:
            if i[0] == running_clisock:
                targetfilepath = i[3]
                targetcmd_conn = i
        filename = cmddata.split(SybOfSplit_cmddata)[1]
        
        running_clisock.send( 'yes'.encode('utf-8') )
        self.filemanager.open( targetfilepath)
        recvfilecontext = recv( running_clisock )
        result = self.filemanager.save( filename,recvfilecontext)
        if result:
            print( 'get a post successfully!')
        else:
            print('something wrong!')
        #filename = cmddata
        

    def cmd_forward(self,running_clisock,cmddata):
        targetfilepath = ""
        targetcmd_conn = []
        for i in self.cmd_conn_list: #获取当前连接访问的文件夹位置
            if i[0] == running_clisock:
                targetfilepath = i[3]
                targetcmd_conn = i
                #如果获取成功更改访问文件路径
        filename = cmddata.split(SybOfSplit_cmddata)[1]
        #print
        self.filemanager.open( os.path.join(targetfilepath,filename) )
        dirinfolist, fileinfolist, openresult = self.filemanager.getfilelist()
        targetcmd_conn.remove( targetfilepath )
        targetfilepath = os.path.join(targetfilepath,filename)
        targetcmd_conn.append( targetfilepath )
        senddata = ''
        senddata = targetfilepath+"\n"
        dir_len = len(dirinfolist)
        file_len = len(fileinfolist)
        senddata += str(dir_len)+"_"+str(file_len)+"\n"
        for i in dirinfolist:
            senddata += i+'\n'
        for i in fileinfolist:
            senddata += i+'\n'
        senddata = senddata[:-1]
        running_clisock.send(senddata.encode("utf-8"))
        
    def cmd_backward(self,running_clisock,cmddata):
        targetfilepath = ""
        targetcmd_conn = []
        for i in self.cmd_conn_list: #获取当前连接访问的文件夹位置
            if i[0] == running_clisock:
                targetfilepath = i[3]
                targetcmd_conn = i
        targetfilepath = os.path.abspath( os.path.join(i[3],os.path.pardir) )
        self.filemanager.open(targetfilepath)
        dirinfolist, fileinfolist, openresult = self.filemanager.getfilelist()
        targetcmd_conn.remove( targetcmd_conn[3] )
        targetcmd_conn.append( targetfilepath )
        senddata = ''
        senddata = targetfilepath + '\n'
        dir_len = len(dirinfolist)
        file_len = len(fileinfolist)
        senddata += str(dir_len)+"_"+str(file_len)+"\n"
        for i in dirinfolist:
            senddata += i+'\n'
        for i in fileinfolist:
            senddata += i+'\n'
        senddata = senddata[:-1]
        running_clisock.send(senddata.encode("utf-8"))

    def cmd_fresh(self,running_clisock,cmddata):
        targetfilepath = ""
        targetcmd_conn = []
        for i in self.cmd_conn_list: #获取当前连接访问的文件夹位置
            if i[0] == running_clisock:
                targetfilepath = i[3]
                targetcmd_conn = i
        self.filemanager.open(targetfilepath)
        dirinfolist, fileinfolist, openresult = self.filemanager.getfilelist()
        #targetcmd_conn.remove( targetcmd_conn[3] )
        #targetcmd_conn.append( targetfilepath )
        senddata = ''
        senddata = targetfilepath + '\n'
        dir_len = len(dirinfolist)
        file_len = len(fileinfolist)
        senddata += str(dir_len)+"_"+str(file_len)+"\n"
        for i in dirinfolist:
            senddata += i+'\n'
        for i in fileinfolist:
            senddata += i+'\n'
        senddata = senddata[:-1]
        running_clisock.send(senddata.encode("utf-8"))

    def cmd_init(self,running_clisock):
        self.filemanager.open( init_file )
        dirinfolist, fileinfolist, openresult = self.filemanager.getfilelist()
        #------------------------------------------------如果打开发生错误，则发送错误信息

        senddata = ''
        senddata = init_file+"\n"
        dir_len = len(dirinfolist)
        file_len = len(fileinfolist)
        senddata += str(dir_len)+"_"+str(file_len)+"\n"
        for i in dirinfolist:
            senddata += i+'\n'
        for i in fileinfolist:
            senddata += i+'\n'
        senddata = senddata[:-1]
        running_clisock.send(senddata.encode("utf-8"))

class Connecter: #记录一个连接的信息
    def __init__(self):
        pass
    
class FileManager:
    #def __init__(self,path):
    #    self.path = path
        
    def open(self,path):
        #self.workingpath = open(path,"r")
        self.workingpath = path
        #打开文件I/O

    def close(self):
        pass
    def getcwd(self):
        return self.workingpath

    def getfilelist(self):
        try:
            filelistinpath = os.listdir(self.workingpath)
        except NotADirectoryError:
            return [],[],False

        fileinfolist = []
        dirinfolist = []
        cwd = self.workingpath
        for i in filelistinpath:
            if os.path.isdir( os.path.join(cwd , i) ):
                dirinfolist.append('%s'%i+SybOfSplit_filename+'<dir>')
            else:
                fileinfolist.append( '%s'%i+SybOfSplit_filename+'%d'%os.path.getsize(os.path.join(cwd,i)))
        return dirinfolist,fileinfolist,True
    def getfilecontext(self):
        #try:
            #判断是否是一个文件
        print(self.workingpath)
        openfile = open(self.workingpath,"rb")
        #finally:
        #    openfile.close()
        filecontext = b''
        filesize = 0
        endflag = False
        while endflag == False:
            onetimereaddata = openfile.read( MAX_ONE_PACKET )
            onetimereadlen =len(onetimereaddata)
            if onetimereadlen < MAX_ONE_PACKET:
                endflag = True
            print("onetimereadlen = "+str(onetimereadlen))
            filecontext += onetimereaddata
            filesize += onetimereadlen
        return True,filecontext,filesize

    def save(self, filename, filecontext ):  #filecontext 是二进制码，未解码
        filepath = os.path.join(self.workingpath,filename)
        if os.path.exists( filepath ):
            print("同名文件已经存在")
            return False
            #return False,"同名文件已经存在"
        else:
            openfile = open( filepath, 'wb')
            filecontext_le = len(filecontext)
            print( str(filecontext_le) )
            openfile.write( filecontext )
            openfile.close()
            return True


class CMD_Interpreter:
    # def __init__(self):
    #     pass
    def cmd_analysis(self,cmd):
        cmd = cmd.split("|*|")[0]
        #if cmd = 

if __name__ == "__main__":
    SM = ServerManager()
    SM.run()
