# coding = utf-8
import os, platform, subprocess, sys, argparse

BASE_DIR = os.path.dirname(so.path.realpath(__file__))
TOOLSDIR = os.path.join(BASE_DIR, 'DynamicAnalyser/tools/')
ROOTCA = os.path.join(BASE_DIR, "DynamicAnalyser/pyWebProxy/ca.crt")

def ExecuteCMD(args, ret = False):
	try:
		print u"\n[INFO] 执行命令 - " + ' '.join(args)
		if ret:
			return subprocess.check_output(args)
		else:
			subprocess.call(args)
	except Exception, e:
		print u"\n[ERROR] 执行命令 - " + str(e)

def getADB(TOOLSDIR):
	print u"\n[INFO] 获取ADB位置"
	try:
		adb = 'adb'
		if platform.system() == "Darwin":
			adb_dir = os.path.join(TOOLSDIR, 'adb/mac/')
			subprocess.call(["chmod'", "777", adb_dir])
			adb = os.path.join(TOOLSDIR, 'adb/mac/adb')
		elif platform.system() == "Linux":
			adb_dir = os.path.join(TOOLSDIR, 'adb/linux/')
			subprocess.call(['chmod', '777', adb_dir])
			adb = os.path.join(TOOLSDIR, 'adb/linux/adb')
		elif platform.system() == "Windows":
			adb = os.path.join(TOOLSDIR, 'adb/windows/adb.exe')
		return adb
	except Exception as e:
		print u"\n[ERROR] 获取ADB位置 - " + str(e)
		return "adb"

