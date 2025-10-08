import os
import time
import subprocess
import paramiko
from . import Com
# pip install paramiko		#window库/linux库:ssh操作
import paramiko
# pip install sshtunnel		#window库/linux库:ssh操作
from sshtunnel import SSHTunnelForwarder

#当前脚本所在文件夹
scriptDir = os.path.dirname(__file__)+os.sep

# 初使化, mainDir引用当前文件所对应的脚本所在文件夹
def Init(mainDirP):
	global mainDir
	mainDir=mainDirP

# 远程连接ssh服务器并执行命令;action-被调用函数(接收SshClient-SSH客户端对象,config-配置对象,args-附加参数); ip,port,username,passowrd-SSH连接帐号信息; config-配置对象; args-附加参数
def Run(action,ip,port,username,password,config=None,args=None):
	if ip==None or port==None or username==None or password==None or action==None: return
	# 创建SSH客户端
	client = paramiko.SSHClient()
	# 自动添加主机名和密钥到本地的known_hosts文件
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
 	# 连接到远程主机
	client.connect(ip,port,username,password)
	clientEx=SshClient(client)
	# 调用外部函数
	action(clientEx,config,args)
	# 关闭连接
	client.close()

# 打开SSH隧道
# action-被调用函数(无参数)
# ip,port,username,passowrd-SSH连接帐号信息
# remoteHost,remotePort-远程服务器地址和端口
# localHost,localPort-本地主机和端口
def Forward(action,ip,port,username,password,remoteHost,remotePort,localHost,localPort):
	if ip==None or port==None or username==None or password==None or action==None: return
	# 打开SSH隧道参数
	server = SSHTunnelForwarder(
		ssh_address_or_host=(ip, port),
		ssh_username=username,
		ssh_password=password,
		local_bind_address=(localHost, localPort),
		remote_bind_address=(remoteHost, remotePort)
	)
	# 启动SSH隧道
	server.start()
	if server.is_active:
		print('本地端口{}:{}已转发至远程端口{}:{}'.format(localHost,server.local_bind_port,remoteHost,remotePort))
	else :
		print('本地端口{}:{}转发失败,请重试')
	# 调用外部函数
	action()
	# 关闭连接
	server.close()

# 连接ssh并批量执行python脚本
# action-自定义函数
# configPath-ssh配置所在文件夹
# configName-调用指定配置名称
def RunAction(action,configPath:str,configName:str=None,args:list=None):
	def actionT(config,args):
		Run(action,config.ip,config.port,config.username,config.password,config,args)
	if type(args) == set:args=list(args)
	Com.EachConfigsAction(actionT,configPath,configName,args)

# 连接ssh并批量执行python脚本
# name-模块名(main为入口函数)，如: utils.com 或 com
# configPath-ssh配置所在文件夹
# configName-调用指定配置名称
def RunName(name:str,configPath:str,configName:str=None,args:list=None):
	# 加载要执行脚本
	runScript=Com.ImportScript(name,mainDir)
	# 去除包名
	for dir in name.split("."):
		try:
			obj=getattr(runScript,dir)
		except Exception as e:
			obj=None
		if obj!=None: runScript=obj
	# 调用脚本
	RunAction(runScript.main,configPath,configName,args)
		
# 管理节点：连接ssh并执行python脚本
# nameOrAction-模块名/函数; 模块名-main为入口函数，如: utils.com 或 com; 函数-外部定义
def RunManage(nameOrAction,configName:str=None,args:list=None):
	dir=mainDir+'configs'+os.sep+'managenodes'+os.sep
	if type(nameOrAction) is str:
		RunName(nameOrAction,dir,configName,args)
	else:
		RunAction(nameOrAction,dir,configName,args)

# 工作节点：连接ssh并执行python脚本
# nameOrAction-模块名/函数; 模块名-main为入口函数，如: utils.com 或 com; 函数-外部定义
def RunWork(nameOrAction,configName:str=None,args:list=None):
	dir=mainDir+'configs'+os.sep+'worknodes'+os.sep
	if type(nameOrAction) is str:
		RunName(nameOrAction,dir,configName,args)
	else:
		RunAction(nameOrAction,dir,configName,args)

# 主机节点（即普通节点）：连接ssh并执行python脚本
# nameOrAction-模块名/函数; 模块名-main为入口函数，如: utils.com 或 com; 函数-外部定义
def RunHost(nameOrAction,configName:str=None,args:list=None):
	dir=mainDir+'configs'+os.sep+'hosts'+os.sep
	if type(nameOrAction) is str:
		RunName(nameOrAction,dir,configName,args)
	else:
		RunAction(nameOrAction,dir,configName,args)

# 定义ssh操作类, 命令执行原理：
# 1、第1次执行时，获取之前的执行结果并返回输出，然后执行空命令，获取结束字符串标记
# 2、当执行结果中是否存在结束字符串标记时，结束执行并返回输出
# 3、实例结束时（即最后一次执行完），获取之前的执行结果并返回输出
class SshClient:
	ssh=None
	ftp=None
	chn=None
	# 结束字符串组
	endStrs=None
	# 超时间根据创建连接时间自动生成
	timeout:int=30000
	# 当前命令执行结果
	result:str=""
	# 构造函数
	def __init__(self,ssh):  
		self.ssh=ssh
		self.ftp=ssh.open_sftp()
		startTime=time.time()
		self.chn = ssh.invoke_shell()
		timeout=max((time.time()-startTime)*1000,self.timeout) 
		if timeout>self.timeout: self.timeout=timeout
		self.endStrs=self.readEndStr()
	def __del__(self):
		self.ftp.close()
		self.chn.close()

	# 下载文件
	def get(self,serverFile,localFile):
		try:
			print(f"下载文件: {serverFile} -> {localFile}")
			if os.path.exists(localFile):
				try:os.remove(localFile)
				except Exception as ex: pass
			rst=self.ftp.get(serverFile,localFile)
			print(rst)
		except Exception as e:
			print(e)

	# 下载文件
	def getDir(self, serverDir, localDir):
		try:
			print(f"下载文件夹: {serverDir} -> {localDir}")
			for name in self.ftp.listdir(serverDir):
				serverPath=serverDir+"/"+ name
				serverObj=self.ftp.stat(serverPath)
				# 查看文档linux-st_mode为2字节aaaabbbcccdddeee, 其中aaaa代表文件类型, 0100-目录
				if serverObj.st_mode>>12==4:
					if not os.path.exists(localPath): os.mkdir(localPath)
					self.getDir(serverPath,localPath)
				else:
					localPath=localDir+"\\"+name
					self.get(serverPath, localPath)				
		except Exception as e:
			print(e)

	# 上传文件
	def put(self,localFile,serverFile):
		try:
			print(f"上传文件: {localFile} -> {serverFile}")
			try:self.ftp.remove(serverFile)
			except Exception as ex: pass
			rst=self.ftp.put(localFile,serverFile)
			print(rst)
		except Exception as e:
			print(e)

	# 上传文件夹
	def putDir(self,localDir:str,serverDir:str):
			localDir=localDir.rstrip(os.sep)+os.sep
			serverDir="" if serverDir=="" else serverDir.rstrip(os.sep)+os.sep
			print(f"上传文件夹: {localDir} -> {serverDir}")
			dic={}
			def action(name,absPath,relPath):
				relPathT=relPath.replace(os.sep,"/")
				if dic.get(relPathT,None)==None:
					dic[relPathT]=True
					try:self.ftp.mkdir(relPathT)
					except Exception as ex: 
						pass
				self.put(absPath+name, relPathT+name)
			Com.eachFile(localDir,action,True,serverDir)

	# 读取输入提示符
	def readEndStr(self):
		# 读取信息并打印
		output=self.readResult()
		print(output,end="")
		for i in range(0,3):
			# 尝试读取提示符
			outputx=output.replace("\r","\n")
			labels=outputx.split("\n")
			label=labels[len(labels)-1]
			# 读取信息并打印
			output=self.readResult(self.timeout)
			# 非空则二次尝试读取提示符
			if output!="":
				print(output,end="")
				rst=output.replace("\r","\n")
				labels=rst.split("\n")
				label=labels[len(labels)-1]
			# 去除提示符中的数径
			labelArr=label.split("~")
			if len(labelArr)==2:return labelArr
			# 去除提示符中的数径
			labelArr=label.split("/")
			if len(labelArr)==2:return labelArr
		# 扔出错误
		raise Exception("找不到提示符")
		return None
	
	# 执行命令
	def cmd(self,config):
		# 使用subprocess.Popen来启动ssh命令
		proc = subprocess.Popen(['ssh', '-o', 'StrictHostKeyChecking=no', config.username + '@' + config.ip],
								stdin=subprocess.PIPE,
								stdout=subprocess.PIPE,
								stderr=subprocess.PIPE, text=True)
		time.sleep(3)
		# 发送密码
		proc.stdin.write(config.password + '\n')
		proc.stdin.flush()  # 清空输入缓冲区
	
		# 读取输出
		stdout, stderr = proc.communicate()
	
		# 打印输出结果
		print(stdout.decode())

	# 执行命令
	def run(self,cmd):
		self.chn.send(cmd+'\n')
		while True:
			output=self.readResult(60000)
			print(output,end="")
			if self.isEnd(output): break
		return
	# 是否为结束提示符
	def isEnd(self,output):
		# 将输出添加到结果中
		self.result+=output
		# 检测结果中是否包含结束提示符
		start=self.endStrs[0]
		end=self.endStrs[1]
		index=self.result.rfind('\n')
		if index==-1:
			index=self.result.rfind('\r')
		index=index + 1
		line=self.result[index:]
		ok=line[len(line)-len(end):]==end and start in line
		# 当前命令执行结束时清空结果
		if ok:self.result=""
		return ok

	# 读取执行命令结果
	# timeout-超时时间（毫秒）
	def readResult(self,timeout:int=0):
		if timeout==0:
			while True:
				output=self.chn.recv(256).decode('utf-8','ignore')
				if output!="": return output
		else:
			endTime=time.time()+timeout/1000
			while True:
				output=self.chn.recv(256).decode('utf-8','ignore')
				if output!="" or time.time()>endTime: return output
