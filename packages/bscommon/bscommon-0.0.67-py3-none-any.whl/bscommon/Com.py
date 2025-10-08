import sys
import os
import tempfile
import time
import subprocess
import socket
import hmac
import hashlib
import base64
import json as Json
import threading
from urllib.parse import quote, unquote
from typing import Union
from . import Base
# pip install ctypes		#window库/linux库:ssh操作
if Base.IsWindows: import ctypes


#当前脚本所在文件夹
scriptDir = os.path.dirname(__file__)+os.sep

# 引用其它python脚本, name-模块名，如: utils.com
def ImportScript(scriptName:str,scriptPath=None):
	try:
		if(scriptPath==None):scriptPath=scriptDir
		sys.path.append(scriptPath)
		script = __import__(scriptName)
		sys.path.remove(scriptPath)
		return script
	except Exception as e:
		print(f"导入python脚本: {e}")

# 引用其它python脚本, scriptPath-脚本对应文件夹
def ImportScripts(scriptPath:str):
	try:
		sys.path.append(scriptPath)
		scripts=[]
		def action(name:str,path:str,relPath:str):
			# 去掉扩展名
			lastIndex=name.rfind(".")
			scriptName=name[0:lastIndex]
			# 导入脚本
			try:
				script=__import__(scriptName)
				scripts.append(script)
			except Exception as e:
				print(f"导入python脚本: {e}")
		# 循环读取脚本
		EachFile(scriptPath,action)
		sys.path.remove(scriptPath)
		print(scripts)
		return scripts
	except Exception as e:
		print(f"导入python脚本: {e}")

# 通过子进程运行其它python脚本, file-相对或绝对路径, 如：c:\pys\aa.py
def RunScript(file:str):
	try:
		result = subprocess.run(['python', file], capture_output=True)
		print(result.stdout.decode())
	except Exception as e:
		print(f"运行python脚本: {e}")

# 遍历文件夹及子文件夹中所有文件，并调用action, dir-要遍历的文件夹, action-被调用函数(接收fileName-文件名,absDir-所在绝对目录,relDir-所在相对目录). isReadChildren-是否读取子文件夹
def EachFile(dir:str,action,isReadChildren:bool=False,relPath:str=""):
	for name in os.listdir(dir):
		absPath = os.path.join(dir,name)
		if (os.path.isfile(absPath)):
			action(name,dir,relPath)
		else:
			if not isReadChildren: return
			relPatht=os.path.join(relPath,name)+os.sep
			EachFile(absPath+os.sep,action,isReadChildren,relPatht)

# 批量执行python脚本
# action-自定义函数
# configPath-配置所在文件夹
# configName-调用指定配置名称
def EachConfigsAction(action,configPath:str,configName:str=None,args:list=None):
	# 导入ssh配置
	configs=ImportScripts(configPath)
	if configName==None:
		# 调用所有脚本
		for config in configs:
			action(config,args)
	else:
		for config in configs:
			if(config.__name__==configName):
				action(config,args)

# 批量执行python脚本
# moduleFile-模块文件路径(main为入口函数)
# configPath-配置所在文件夹
# configName-调用指定配置名称
def EachConfigsModule(moduleFile:str,configPath:str,configName:str=None,args:list=None):
	# 加载要执行脚本
	path, filename=os.path.split(moduleFile)
	name,exname=os.path.splitext(filename)
	runScript=ImportScript(name,path)
	# 调用脚本
	EachConfigsAction(runScript.main,configPath,configName,args)

# 遍历指定文件夹中的配置(python)文件并执行
# moduleFileOrAction-模块文件路径或函数; 模块名-main为入口函数，如: utils.com 或 com; 函数-外部定义
# configsDir-配置文件所在目录
# configName-调用指定配置名称
def EachConfigs(moduleFileOrAction,configsDir,configName:str=None,args:list=None):
	if type(moduleFileOrAction) is str:
		EachConfigsModule(moduleFileOrAction,configsDir,configName,args)
	else:
		EachConfigsAction(moduleFileOrAction,configsDir,configName,args)

# 读取文件, filename-保存文件名, encoding-编码
def ReadFile(filename, encoding='utf-8'):
	if not os.path.exists(filename): return ""
	with open(filename, "r", encoding=encoding) as file:
		content = file.read()
		return content
	
# 保存文件, filename-保存文件名, content-保存内容, encoding-编码, mode-a添加w重写
def SaveFile(filename, content, encoding='utf-8', mode='w'):
    with open(filename, mode, encoding=encoding) as file:
        file.write(content)

# 读取Json, filename-保存文件名, encoding-编码
def ReadJson(filename, encoding='utf-8'):
	jsonStr=ReadFile(filename, encoding)
	jsonObj=Json.loads("{}" if jsonStr=="" else jsonStr)
	return jsonObj

# 保存文件, filename-保存文件名, jsonObj-保存json对象, encoding-编码, mode-a添加w重写
def SaveJson(filename, jsonObj, encoding='utf-8'):
	jsonStr=Json.dumps(jsonObj,indent=2,ensure_ascii=False)
	SaveFile(filename,jsonStr,encoding)

# 执行命令(等待执行完成后，才会往后执行)
def Cmd(commands:str,isEcho:bool=False):
	t = threading.Thread(target=Bash, args=(commands, isEcho))
	t.start()
	t.join()
	return t.result if hasattr(t, 'result') else None

# 执行命令(新窗口执行不会阻塞)
def Run(commands:str,isEcho:bool=False):
	t = threading.Thread(target=Bash, args=(commands, isEcho))
	t.start()
	return t

# 执行命令
def Bash(commands:str,isEcho:bool=False):
	try:
		platform = sys.platform
		filename="tempbs"
		callname=""
		encodeing=""
		varcurrentdir=""
	
		if 'linux' in platform:
			filename=filename+".sh"
			callname="bash"
			encodeing="utf-8"
			varcurrentdir="$PWD"
		elif 'darwin' in platform:
			filename=filename+".sh"
			callname="bash"
			encodeing="utf-8"
			varcurrentdir="$PWD"
		elif 'win32' in platform or 'win64' in platform:
			filename=filename+".bat"
			callname="call"
			encodeing="gbk"
			varcurrentdir="%cd%"
		else:
			print("未知操作系统,无法执行命令")
			return None
		
		# 读取临时文件路径
		tempdir = tempfile.gettempdir()
		execfile = os.path.join(tempdir, filename)
		if os.path.exists(execfile): os.remove(execfile)
		# 生成执行脚本
		cmd = "@echo "+("on" if isEcho else "off")+"\n"
		cmd += "echo 执行前当前目录: "+varcurrentdir+"\n"
		cmd += commands + '\n'
		cmd += "echo 执行后当前目录: "+varcurrentdir+"\n"
		cmd += 'exit\n'
		with open(execfile, 'w',encoding=encodeing) as f: f.write(cmd)
        # 执行命令
		process = subprocess.Popen(callname+ " " + execfile, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, universal_newlines=True)
		# 输出结果
		while process.poll() is None:
			line = process.stdout.readline()
			if line: print(line,end="")
		# 等待命令执行完成
		returnCode = process.wait()
		if returnCode:
			print(f"########执行错误########\n返回码: {returnCode}")
		else:
			print("########执行完成########")
		# 返回命令执行的结果
		return None
	except Exception as e:
		# 如果命令执行失败，返回错误输出
		print(e)
		return e
# 切换到管理员模式
def ToAdmin(file:str):
	if not Base.IsWindows: return
	isAdmin=False
	try: isAdmin=ctypes.windll.shell32.IsUserAnAdmin()
	except Exception as e: 
		print(e)
	if isAdmin: 
		return
	if(file=="" or file==None): 
		print("切换到管理员模式时,缺少file参数")
		return
	ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, file, None, 1)
	sys.exit()

# 获取本机局域网IP
def GetLanIp():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

# 生成数字HmacSha1签名
def HmacSha1(key: Union[str, bytes], text: Union[str, bytes],encoding="utf-8") -> str:
    if isinstance(key, str):
        key = key.encode(encoding)
    if isinstance(text, str):
        text = text.encode(encoding)
    sha1bytes=hmac.new(key, text, hashlib.sha1).digest()
    return base64.b64encode(sha1bytes).decode(encoding)

# 字典:根据Key重新排序keys
def DictSortByKey(obj: dict, reverse=False):
    return {k: obj[k] for k in sorted(obj.keys(), reverse=reverse)}

# 将字典转成Url参数
def DictToUrlParams(obj: dict, safe_chars='') -> str:
	params = []
	for key, value in obj.items():
		if isinstance(value, (list, tuple)):
			params.extend(f"{quote(str(k), safe=safe_chars)}={quote(str(v), safe=safe_chars)}" 
						for v in value for k in [key])
		else:
			params.append(f"{quote(str(key), safe=safe_chars)}={quote(str(value), safe=safe_chars)}")
	return '&'.join(params)

# 版本号加1, step-增加步长
def VersionAdd(version:str,step:int=1)->str:
	vs=version.split(".")
	vs[-1]=str(int(vs[-1])+step)
	return ".".join(vs)

# 将Url参数转成字典
def UrlParamsToDict(query: str) -> dict:
	from urllib.parse import parse_qs
	return {k: v[0] if len(v) == 1 else v 
			for k, v in parse_qs(unquote(query)).items()}

