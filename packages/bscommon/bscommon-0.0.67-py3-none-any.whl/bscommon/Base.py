import os,sys
Platform = sys.platform
IsLinux = 'linux' in Platform
IsMacos = 'darwin' in Platform
IsWindows = 'win32' in Platform or 'win64' in Platform
IsOther = not (IsLinux or IsMacos or IsWindows)
