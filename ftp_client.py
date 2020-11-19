from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from socket import *
from PIL import Image,ImageTk
import os

cmd_port = 9000  #命令传输端口
data_port = 9001 #数据传输端口

MAX_SIZE_ONE_PACKET = 1024
MAX_CMD_SIZE = 1024
MAX_ONE_PACKET = 1024*2
SybOfSplit_cmddata = "|*|"
SybOfSplit_filename = "|-|"

def isIp(ip): #判断是否符合一个ip的格式
    ippart = ip.split(".")
    len = 0
    for i in ippart:
        if i == '':
           return 0
        num = int(i)
        if not (num <=255 and num>=0):
            return 0
        len = len + 1
    if len != 4:
        return 0
    else:
        return 1


class Mainwin:
    mainwin = Tk()
    local_filewin = Listbox(mainwin)
    remote_filewin = Listbox(mainwin)
    lab_ip_input = Label(mainwin,text="远程ip:")
    btn_connect = Button(mainwin, text = "连接")
    lab_localfile_win = Label(mainwin, text="本地文件:")
    lab_remotefile_win = Label(mainwin, text="远程服务器文件:")
    ent_input_ip = Entry(mainwin)

    def __init__(self):  #布置好基本组件
        self.filemanager = FileManager() #本地文件系统
        self.cmd_conn = Connecter()  #获取命令
        self.data_conn = Connecter()
        self.cwd = os.getcwd()
        
        self.mainwin.title("MyFTP")
        self.mainwin['width'] = 800
        self.mainwin['height'] = 600
        self.mainwin.resizable(False, False)#固定窗体

        self.local_filewin['width'] = 45
        self.local_filewin['height'] = 20
        self.local_filewin.place(x=50,y=120)
        self.local_filewin.bind( "<Double-Button-1>",self.local_filewin_click)
        
        self.remote_filewin['width'] = 45
        self.remote_filewin['height'] = 20
        self.remote_filewin.place(x=430,y=120)
        self.remote_filewin.bind( "<Double-Button-1>",self.remote_filewin_click)

        self.lab_remotefile_IP = Label(self.mainwin, text = "远程主机:")
        self.lab_remotefile_IP.place(x=430, y=10)

        self.lab_ip_input.place(x=20,y=10)
        self.lab_localfile_win.place(x=20,y=50)
        self.ent_input_ip.place(x=70,y=10)

        self.btn_connect = Button(self.mainwin, text = "连接",command = self.btn_connect_click) #连接按钮
        self.btn_connect['width'] = 8
        self.btn_connect.place(x=220,y=5)

        self.btn_backward_local = Button(self.mainwin, text = "←", command = self.btn_backward_local_click )  #后退按钮
        self.btn_backward_local['width'] = 5
        self.btn_backward_local.place(x = 50, y = 80)

        self.btn_backward_remote = Button(self.mainwin, text = "←", command = self.btn_backward_remote_click )  #后退按钮
        self.btn_backward_remote['width'] = 5
        self.btn_backward_remote.place(x = 420, y = 80)
        
        self.lab_localfile_info = Label(self.mainwin, text = "文件信息：")
        self.lab_localfile_info.place(x = 50,y = 490)
        
        self.lab_remotefile_info = Label(self.mainwin, text = "文件信息：")
        self.lab_remotefile_info.place(x = 420, y = 490 )
        
        self.lab_remotefile_win = Label(self.mainwin, text = "远程文件：")
        self.lab_remotefile_win.place(x=420, y=50)
        #imgBtn = PhotoImage(file='freshbuttonimage.jpg')
        #imagebtn = Image.open( 'freshbuttonimage.jpg' )
        #btn_image_ = ImageTk.PhotoImage(imagebtn)
        #imagebtn.show()


        self.btn_freshlist_local = Button(self.mainwin, text = "刷新本地文件",command = self.showfilelist)
        self.btn_freshlist_local.place( x = 100 , y = 80 )

        self.btn_freshlist_remote = Button(self.mainwin, text = "刷新远程文件",command = self.btn_freshlist_remote_click)
        self.btn_freshlist_remote.place(x=480,y=80)

        self.btn_disconnect = Button(self.mainwin, text = "断开", command = self.btn_disconnect_click) #断开
        self.btn_disconnect['width'] = 8
        self.btn_disconnect.place(x = 300, y = 5) 

        self.btn_choose_afile = Button(self.mainwin,text = "打开一个文件夹", command = self.btn_choose_afile_click )
        self.btn_choose_afile.place(x = 200 , y= 80)

        self.btn_upload = Button(self.mainwin, text = "←", command = self.btn_download_click  )
        self.btn_upload['width'] = 5
        self.btn_upload.place( x = 378 , y= 230 )

        self.btn_download = Button(self.mainwin, text = "→", command = self.btn_upload_click )
        self.btn_download['width'] = 5
        self.btn_download.place( x= 378, y = 310 )

        self.lab_upload = Label(self.mainwin, text = "下载")
        self.lab_upload.place(x=385,y=205)
        self.lab_download = Label(self.mainwin, text = "上传")
        self.lab_download.place(x=385, y = 285 )
        
        self.filemanager.open( self.cwd )
        self.showfilelist()
        self.fresh()

    def showfilelist(self):
        dirinfolist,fileinfolist = self.filemanager.getfilelist()
        self.local_filewin.delete(0,END)
        self.local_filewin_dirlist = dirinfolist
        self.local_filewin_filelist = fileinfolist
        for i in dirinfolist:
            infolist = i.split(SybOfSplit_filename)
            insertdata = infolist[0] + "  "+infolist[1]
            self.local_filewin.insert("end",insertdata)
        for i in fileinfolist:
            infolist = i.split(SybOfSplit_filename)
            insertdata = infolist[0] + "  "+infolist[1]
            self.local_filewin.insert("end",insertdata)
        self.dirlist_len = len(dirinfolist)
        self.filelist_len = len(fileinfolist)

    def showfilelist_remote(self,listdata):
        self.remote_filewin.delete(0,END)
        filelist = listdata.split("\n")
        self.remote_cwd = filelist[0]
        fileinfo= filelist[1]
        self.remote_dirlist_len = int(fileinfo.split("_")[0])
        self.remote_filelist_len = int(fileinfo.split("_")[1])
        filelist.remove(self.remote_cwd)
        filelist.remove(fileinfo)
        self.remote_filewin_dirlist = filelist#
        self.lab_remotefile_win['text'] = '远程路径：'+ self.remote_cwd
        if self.remote_dirlist_len+self.remote_filelist_len == 0:
            self.lab_remotefile_info['text'] ='文件信息：文件夹为空'
        else:
            self.lab_remotefile_info['text'] = '文件信息：' + str(self.remote_dirlist_len)+"个文件夹 " + str(self.remote_filelist_len) +"个文件"
        
        for i in filelist:
            infolist = i.split(SybOfSplit_filename)
            insertdata = infolist[0] + "  "+infolist[1]
            self.remote_filewin.insert("end",insertdata)
        
    def btn_connect_click(self):
        ip = self.ent_input_ip.get()
        if not isIp(ip):
            #打印ip格式错误信息
            print("ip error!")
            messagebox.showerror("错误","ip格式错误，请输入正确的ip")
        else:
            self.cmd_conn.connect(ip,cmd_port)
            #如果连接成功
            self.lab_remotefile_IP['text'] = "远程主机：" + str(self.cmd_conn.ip)
            #连接成功以后，获取发送过来的文件列表信息
            listdata = self.cmd_conn.recv().decode("utf-8")
            self.showfilelist_remote(listdata)

    def btn_disconnect_click(self):
        #print(str(self.cmd_conn.ip)+"\n"+str(self.cmd_conn.port))
        self.cmd_conn.close()
        #print(str(self.cmd_conn.ip)+"\n"+str(self.cmd_conn.port))
        self.lab_remotefile_IP['text'] = "远程主机："
        self.remote_filewin.delete(0,END)
        
    def local_filewin_click(self,event):
        #print( self.local_filewin.curselection()[0] )
        dirlist_le = len(self.local_filewin_dirlist)
        curindex = 0
        filename = ''
        if self.local_filewin.curselection()[0]+1 > dirlist_le:
            #curindex = self.local_filewin.curselection()[0]+1 - dirlist_le
            #filename = self.local_filewin_filelist[curindex]
            print('请选择合适的文件夹')
            
        else:
            curindex = self.local_filewin.curselection()[0]
            filename = self.local_filewin_dirlist[curindex]
            filename = filename.split(SybOfSplit_filename)[0]
        #print("!!!!!!!!!" + self.cwd)
            cwd = os.path.join(self.cwd, filename)
            self.filemanager.open( cwd )
            self.cwd = cwd
        #print(self.cwd)
            self.showfilelist()
        self.fresh()
        #打开选中的文件夹
    def remote_filewin_click(self,event):
        dirlist_le = len(self.remote_filewin_dirlist)
        curindex = self.remote_filewin.curselection()[0]
        filename = self.remote_filewin_dirlist[curindex]
        filename = filename.split(SybOfSplit_filename)[0]
        senddata = "forward"+SybOfSplit_cmddata+filename
        self.cmd_conn.send(senddata)
        recvfilelist = self.cmd_conn.recv().decode("utf-8")
        self.showfilelist_remote(recvfilelist)
        self.fresh()

    def btn_backward_local_click(self):
        cwd = self.cwd
        cwd = os.path.join(cwd,os.path.pardir)
        #print(cwd)
        self.filemanager.open(cwd)
        self.showfilelist()
        self.cwd = os.path.abspath(cwd)
        self.fresh()

    def btn_backward_remote_click(self):
        senddata = 'backward'+SybOfSplit_cmddata
        self.cmd_conn.send(senddata)
        recvfilelist = self.cmd_conn.recv().decode("utf-8")
        self.showfilelist_remote(recvfilelist)
        self.fresh()

    def btn_choose_afile_click(self):
        cwd = filedialog.askdirectory()
        if cwd != "":
            self.filemanager.open(cwd)
            self.cwd = cwd
            self.showfilelist()
        else:
            messagebox.showerror("错误","选择文件夹错误")
        self.fresh()

    def btn_upload_click(self):
        senddata = 'post'+SybOfSplit_cmddata
        curindex = self.local_filewin.curselection()[0]
        if curindex+1 <= self.dirlist_len:
            print("请选择合适的文件，而不是文件夹")
            return
        filename = self.local_filewin_filelist[curindex-self.dirlist_len].split(SybOfSplit_filename)[0]
        senddata += filename
        self.cmd_conn.send(senddata)
        response = self.cmd_conn.recv().decode('utf-8')
        if response =='yes':
            self.filemanager.open( os.path.join(self.cwd,filename))
            result,filecontext,filesize = self.filemanager.getfilecontext()
            self.cmd_conn.sendfilecontext( filecontext )
            messagebox.showinfo( '成功','文件\"'+ filename + '\"上传成功' )

    def btn_download_click(self):
        senddata = 'get' + SybOfSplit_cmddata
        curindex = self.remote_filewin.curselection()[0]
        if curindex+1 <= self.remote_dirlist_len:
            #请选择合适的文件，而不是文件夹
            print("请选择合适的文件，而不是文件夹")
            return
        filename = self.remote_filewin_dirlist[curindex].split( SybOfSplit_filename)[0]
        senddata += filename
        self.cmd_conn.send(senddata)
        recvfile = self.cmd_conn.recv()
        #print('recvfile:'+recvfile)
        recvfilelen = int(recvfile.split(SybOfSplit_filename.encode('utf-8'))[0])
        
        #print('recvfilelen:'+str(recvfilelen))
        filecontext = recvfile.split(SybOfSplit_filename.encode('utf-8'))[1] #.encode('utf-8')
        #print( 'filecontext:'+filecontext.decode('utf-8') )
        self.filemanager.open(self.cwd)
        result = self.filemanager.save( filename, filecontext )
        if result:
            messagebox.showinfo("下载完成","文件\""+filename+'\"下载成功')

    def btn_freshlist_remote_click(self):
        #刷新远程文件列表
        senddata = 'fresh'+SybOfSplit_cmddata
        self.cmd_conn.send(senddata)
        recvfilelist = self.cmd_conn.recv().decode("utf-8")
        self.showfilelist_remote(recvfilelist)
        
    def fresh(self):
        self.lab_localfile_win['text'] = '本地路径：' + os.path.abspath(self.cwd)
        if self.local_filewin.size() == 0:
            self.lab_localfile_info["text"] = "文件信息：文件夹为空"
        else:
            self.lab_localfile_info['text'] = "文件信息：" + str(self.dirlist_len)+"个文件夹 " +str(self.filelist_len) + "个文件" 
        
class CMD_interpreter: #
    def __init__(self,cmd):
        self.cmd = cmd
    
class Connecter:
    def __init__(self):
        self.ip = ''
        self.port = -1
        
    
    def connect(self,ip,port):
        #接受异常##############################################
        if self.port == -1:
             self.conn = socket( AF_INET,SOCK_STREAM )
        result = self.conn.connect((ip,port))
        if result == error:
            print("连接失败")
        else:
            self.ip = ip
            self.port = port
            print('连接成功吧？')
            messagebox.showinfo("连接成功","成功连接"+str(self.ip))
        #连接ip
        #pass
    def close(self):
        #如果连接还存在，那么就关闭连接
        if self.port != -1:
            self.conn.close()
            messagebox.showinfo("关闭连接","与"+str(self.ip)+"的连接已关闭")
            self.ip = ''
            self.port = -1
            print("关闭连接")
        else:
            print("连接已关闭，无需重复关闭")
            messagebox.showwarning("警告","连接已关闭，无需重复关闭")
    def recv(self):
        flag = True
        recvdatalen = 0
        recvdata = b''
        while flag:
            onetimerecv = self.conn.recv( MAX_SIZE_ONE_PACKET )
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

    def send(self,senddata):
        if self.port != -1:
            self.conn.send( senddata.encode("utf-8") )
        else:
            messagebox.showerror("错误","连接已经关闭")
    def sendfilecontext(self,filecontext):
        if self.port != -1:
            self.conn.send( filecontext )
        else:
            messagebox.showerror("错误","连接已经关闭")
    

class FileManager:
    #def __init__(self,path):
    #    self.path = path
        
    def open(self,filename):
        #self.workingpath = open(path,"r")
        self.workingpath = filename
        #打开文件I/O
        pass
    def close(self):
        pass

    def getfilelist(self):
        filelistinpath = os.listdir(self.workingpath)
        fileinfolist = []
        dirinfolist = []
        cwd = self.workingpath
        for i in filelistinpath:
            if os.path.isdir( os.path.join(cwd , i) ):
                dirinfolist.append('%s'%i+SybOfSplit_filename+'<dir>')
            else:
                fileinfolist.append( '%s'%i+SybOfSplit_filename+'%d'%os.path.getsize(os.path.join(cwd,i)))
        
        return dirinfolist,fileinfolist
        #pass
    #def getfilelistinfo(self):
        #返回文件列表的信息
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
            print("getfilecontext():onetimereadlen = "+str(onetimereadlen))
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

    
if __name__ == "__main__":
    ftpapp = Mainwin()
    #ftpapp.add()
    ftpapp.mainwin.mainloop()
