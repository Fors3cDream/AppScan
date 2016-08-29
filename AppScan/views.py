# coding=utf-8

import sys, shutil
reload(sys)
sys.setdefaultencoding("utf-8")

from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from datetime import datetime
import django
from django.template import RequestContext
import hashlib
if django.__version__ >= "1.8.5":
	from wsgiref.util import FileWrapper
else:
	from django.core.servers.basehttp import FileWrapper

from AppScan.utils import PrintException, filename_from_path
from AppScan.models import RecentScansDB, User
from StaticAnalyzer.models import StaticAnalyzerAndroid
from .forms import UploadFileForm, UserForm


import os, hashlib, platform, json, shutil, re

def PushToRecent(NAME, MD5, URL, username):
	try:
		DB = RecentScansDB.objects.filter(MD5=MD5, USER = username)
		if not DB.exists():
			print u"[INFO] 添加扫描结果到数据库,添加时间 " + datetime.now().strftime("%Y-%m-%d")
			NDB = RecentScansDB(NAME = NAME, MD5 = MD5, URL = URL, USER = username,TS = datetime.now().strftime("%Y-%m-%d"))
			NDB.save()
	except:
		PrintException(u"[ERROR] 添加扫描结果到数据库")

def Users(request):
	try:
		DB = User.objects.all().order_by('username')
		user = request.COOKIES.get('cookie_username', '')
		if DB.exists():
			context = {'title': u'所有用户', 'users': DB}
			template = "users.html"
			return render(request, template, context)
	except:
		PrintException(u"[ERROR] 添加扫描结果到数据库")
	return HttpResponseRedirect('/error/')

def delUser(request):
	try:
		user = request.GET['user']
		if user == 'root':
			pass
		else:
			UDB = User.objects.filter(username = user)
			RDB = RecentScansDB.objects.filter(USER=user)
			SDB = StaticAnalyzerAndroid.objects.filter(USER=user)
			uHome = os.path.join(settings.UPLD_DIR, user)
			uDHome = os.path.join(settings.DWD_DIR, user)
			if UDB.exists():
				UDB.delete()
			else:
				pass
			if RDB.exists():
				RDB.delete()
			else:
				pass
			if SDB.exists():
				SDB.delete()
			else:
				pass
			if os.path.exists(uHome):
				shutil.rmtree(uHome)
			else:
				pass
			if os.path.exists(uDHome):
				shutil.rmtree(uDHome)
			else:
				pass


		return HttpResponseRedirect('/users/')
	except:
		PrintException(u"[ERROR] 删除扫描结果错误")
		return HttpResponseRedirect('/error/')


def delete(request):
	try:
		MD5 = request.GET['md5']
		username = request.GET['username']
		dFile_java = os.path.join(settings.DWD_DIR,user + '/' + MD5 + "-java.zip")
		dFile_smali = os.path.join(settings.DWD_DIR, user + '/' + MD5 + "-smali.zip")
		RDB = RecentScansDB.objects.filter(MD5 = MD5, USER = username)
		SDB = StaticAnalyzerAndroid.objects.filter(MD5 = MD5, USER = username)

		if os.path.isfile(dFile_java):
			os.remove(dFile_java)
		else:
			pass

		if os.path.isfile(dFile_smali):
			os.remove(dFile_smali)
		else:
			pass

		if RDB.exists():
			print u"[INFO] 删除扫描结果 " + "MD5= " + MD5 + " user= " + username
			RDB.delete()
		if SDB.exists():
			print u"[INFO] 删除扫描结果 " + "MD5= " + MD5 + " user= " + username
			SDB.delete()

		APP_DIR = os.path.join(settings.UPLD_DIR, username + '/' + MD5 + '/')
		if os.path.exists(APP_DIR):
			shutil.rmtree(APP_DIR)
		else:
			pass


		return HttpResponseRedirect('/RecentScans/')
	except:
		PrintException(u"[ERROR] 删除扫描结果错误")
		return HttpResponseRedirect('/error/')

def index(request):
	username = request.COOKIES.get('cookie_username', '')
	print "[INFO] Login user is " + username
	return render_to_response('index.html', {'username':username})

def register(request):
	Method = request.method
	if Method == 'POST':
		uf = UserForm(request.POST)
		if uf.is_valid():
			username = uf.cleaned_data['username']
			if username != 'root':
				if len(username) < 6:
					return HttpResponse('用户名长度必须大于等于6位!<br><a href="/register">返回</a>')
			ps = uf.cleaned_data['password']
			if len(ps) < 6:
				return HttpResponse('密码必须大于等于6位!<br><a href="/register">返回</a>')
			passwd = hashlib.md5()
			passwd.update(ps)
			password = passwd.hexdigest()
			try:
				registJudge = User.objects.filter(username = username).get().username
				return render_to_response('register.html', {'registJudge':registJudge})
			except:
				registAdd = User.objects.create(username = username, password = password)
				if registAdd:
					#return HttpResponseRedirect('/login')
					return render_to_response('register.html', {'username': username})
				else:
					return render_to_response('register.html', {'registAdd':registAdd,'username':username})
	else:
		uf = UserForm()
	return render_to_response('register.html', {'uf':uf, 'Method':Method}, context_instance = RequestContext(request))

def login(request):
	if request.method == 'POST':
		uf = UserForm(request.POST)
		if uf.is_valid():
			username = uf.cleaned_data['username']
			ps = uf.cleaned_data['password']
			passwd = hashlib.md5()
			passwd.update(ps)
			password = passwd.hexdigest()

			# 判断用户是否存在
			userJudge = User.objects.filter(username = username)
			if userJudge:
			# 对比用户输入的用户名与密码是否与数据库存储的一致
				userPassJudge = User.objects.filter(username__exact = username, password__exact = password).get().username
				if userPassJudge:
					if username == 'root':
						response = HttpResponseRedirect('/RecentScans/')
						response.set_cookie('cookie_username', username, 3600)
						return response
					else:
						response = HttpResponseRedirect('/up2ana/')
						response.set_cookie('cookie_username', username, 3600)
						return response
				else:
					return HttpResponse(u'登录失败')
			else:
				return HttpResponse(u'用户不存在,请先注册用户。<a href = "../register">注册</a>')
	else:
		uf = UserForm()
	return render_to_response('login.html', {'uf':uf}, context_instance = RequestContext(request))

def logout(request):
	response = HttpResponseRedirect('/index/')
	response.delete_cookie('cookie_username')
	return response

def up2ana(request):
# 	if platform.system != "Windows":
# 		os.system('export LANG="en_US.UTF-8"')
# 		os.system('export LC_ALL="en_US.UTF-8"')
	username = request.COOKIES.get('cookie_username','')
	print "[INFO] Login user is " + username
	if username == '':
		return HttpResponseRedirect('/login/')
	else:
		print "[INFO] Login user is " + username
		context = {'version': settings.APPSCAN_VER}
		template = "up2ana.html"
		return render(request, template, context)

def handle_uploaded_file(f, typ, user):
	md5 = hashlib.md5()
	for chunk in f.chunks():
		md5.update(chunk)
	md5sum = md5.hexdigest()
	ANAL_DIR = os.path.join(settings.UPLD_DIR, user + '/' + md5sum+'/')
	if not os.path.exists(ANAL_DIR):
		os.makedirs(ANAL_DIR)
	with open(ANAL_DIR + md5sum + typ, "wb+") as destination:
		for chunk in f.chunks():
			destination.write(chunk)
	return md5sum

def Upload(request):
	try:
		print u"开始上传文件"
		username = request.COOKIES.get('cookie_username', '')
		user = hashlib.md5()
		user.update(username)
		us = user.hexdigest()
		response_data = {}
		response_data['url'] = ''
		response_data['description'] = ''
		response_data['status'] = ''
		if request.method == 'POST':
			form = UploadFileForm(request.POST, request.FILES)
			if form.is_valid():
				file_type = request.FILES['file'].content_type
				print u"[INFO] MIME Type: " + file_type + " FILE: " + str(request.FILES['file'].name)
				if (file_type == "application/octet-stream" or file_type == "application/vnd.android.package-archive" or file_type == "application/x-zip-compressed") and request.FILES['file'].name.lower().endswith('.apk'):
					md5 = handle_uploaded_file(request.FILES['file'], '.apk', username)
					response_data['url'] = '../StaticAnalyzer/?name=' + request.FILES['file'].name + '&type=apk&checksum=' + md5 + '&us=' + us
					response_data['status'] = 'success'
					response_data['user'] = username
					print u"上传完成"
					PushToRecent(request.FILES['file'].name, md5, response_data['url'], str(username))
					print u"\n[INFO] 开始静态分析Android apk文件"
				#elif (file_type == "application/zip"  or file_type == "application/octet-stream" or file_type == "application/x-zip-compressed") and request.FILES("file").name.lower().endswith(".zip"):
				elif(file_type=="application/zip" or file_type=="application/octet-stream" or file_type=="application/x-zip-compressed") and request.FILES['file'].name.lower().endswith('.zip'):
					md5 = handle_uploaded_file(request.FILES['file'], '.zip', username)
					print u"\n[INFO] 等待跳转"
					response_data['url'] = '../StaticAnalyzer/?name=' + request.FILES['file'].name + '&type=zip&checksum=' + md5 + '&us=' + us
					response_data['status'] = 'success'
					response_data['user'] = username
					PushToRecent(request.FILES['file'].name, md5, response_data['url'], username)
					print u"\n[INFO] 开始静态分析Android 源代码"
				else:
					response_data['url'] = ''
					response_data['description'] = 'File format not Supported!'
					response_data['status'] = 'error'
					print u"\n[ERROR] 文件格式不支持!"

			else:
				response_data['url'] = ''
				response_data['description'] = 'Invalid Form Data!'
				response_data['status'] = 'error'
				print u"\n[ERROR] 非法数据"
		else:
			resposne_data['url'] = ''
			resposne_data['description'] = 'Mehod not Supported!'
			response_data['status'] = 'error'
			print u"\n[ERROR] 上传方法不支持"
			form = UploadFileForm()
		r = HttpResponse(json.dumps(response_data), content_type = 'application/json')
		r['Access-Control-Allow-Origin'] = '*'
		return r
	except:
		PrintException("[ERROR] 上传文件：")

def about(request):
	context = {'title': 'About'}
	template = 'about.html'
	return render(request, template, context)


def error(request):
	context = {'title': 'error'}
	template = 'error.html'
	return render(request, template, context)

def ZIP_FORMAT(request):
	context = {'title':'Zipped Source Intruction'}
	template = 'zip.html'
	return render(request, template, context)

def NotFound(request):
	context = {'title':'Not Found'}
	template = 'not_found.html'
	return render(request, template, context)

def RecentScans(request):
	#DB = RecentScansDB.objects.all().order_by('-TS')
	User = request.COOKIES.get('cookie_username', '')
	if User == 'root':
		DB = RecentScansDB.objects.all().order_by('-TS')
		context = {'title':'Recant Scans', 'entries':DB}
		template = "recent_root.html"
	else:
		DB = RecentScansDB.objects.filter(USER = User).order_by('-TS')
		context = {'title':'Recant Scans', 'entries':DB}
		template = "recent.html"
	return render(request, template, context)

def Search(request):
	MD5 = request.GET['md5']
	User = request.COOKIES.get('cookie_username', '')
	if re.match('[0-9a-f]{32}', MD5):
		DB = RecentScansDB.objects.filter(MD5=MD5, USER = User)
		if DB.exists():
			return HttpResponseRedirect('/' + DB[0].URL)
		else:
			return HttpResponseRedirect('/NotFound')
	return HttpResponseRedirect('/error')

def Download(request):
	try:
		user = request.COOKIES.get('cookie_username', '')
		if user == 'root':
			user = request.GET['user']
		else:
			pass
		md5 = request.GET['md5']
		dwd_file = ''
		if request.method == 'GET':
			allowed_exts = settings.ALLOWED_EXTENSIONS
			filename = request.GET['file']
			if ("../") in filename:
				print "\n[ATTACK] 检测到目录遍历攻击"
				return HttpResponseRedirect('/error/')
			ext = os.path.splitext(filename)[1]
			if (ext in allowed_exts):
				dwd_file = os.path.join(settings.DWD_DIR,user + '/'+ filename)
			if os.path.isfile(dwd_file):
				wrapper = FileWrapper(file(dwd_file))
				response = HttpResponse(wrapper, content_type=allowed_exts[ext])
				response['Content-Length'] = os.path.getsize(dwd_file)
				return response
	except:
		PrintException("下载文件错误")
	return HttpResponseRedirect('/error/')

