#coding=utf-8

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import hashlib
import io
import platform
import plistlib
import shutil
import sqlite3 as sq
import subprocess
import zipfile
from xml.dom import minidom
from datetime import datetime


import ntpath
import os
import re
from django.conf import settings
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.defaulttags import register
from django.template.loader import get_template
from django.utils.html import escape

from MalwareAnalyzer.views import MalwareCheck
from AppScan.utils import PrintException, python_list, python_dict, isDirExists, isFileExists
from StaticAnalyzer.dvm_permissions import DVM_PERMISSIONS
from StaticAnalyzer.models import StaticAnalyzerAndroid

from weasyprint import HTML, CSS
# Create your views here.


try:
	import StringIO
	StringIO = StringIO.StringIO
except Exception:
	from io import StringIO

@register.filter
def key(d, key_name):
	return d.get(key_name)

def PDF(request):
    try:
        MD5=request.GET['md5']
        TYP=request.GET['type']
        m=re.match('[0-9a-f]{32}',MD5)
        if m:
            if (TYP=='APK' or TYP=='ANDZIP'):
                DB=StaticAnalyzerAndroid.objects.filter(MD5=MD5)
                if DB.exists():
                    print "\n[INFO] 从数据中获取数据生成PDF报告(Android)"
                    context = {
                    'title' : DB[0].TITLE,
                    'name' : DB[0].APP_NAME,
                    'size' : DB[0].SIZE,
                    'md5': DB[0].MD5,
                    'sha1' : DB[0].SHA1,
                    'sha256' : DB[0].SHA256,
                    'packagename' : DB[0].PACKAGENAME,
                    'mainactivity' : DB[0].MAINACTIVITY,
                    'targetsdk' : DB[0].TARGET_SDK,
                    'maxsdk' : DB[0].MAX_SDK,
                    'minsdk' : DB[0].MIN_SDK,
                    'androvername' : DB[0].ANDROVERNAME,
                    'androver': DB[0].ANDROVER,
                    'manifest': DB[0].MANIFEST_ANAL,
                    'permissions' : DB[0].PERMISSIONS,
                    'files' : python_list(DB[0].FILES),
                    'certz' : DB[0].CERTZ,
                    'activities' : python_list(DB[0].ACTIVITIES),
                    'receivers' : python_list(DB[0].RECEIVERS),
                    'providers' : python_list(DB[0].PROVIDERS),
                    'services' : python_list(DB[0].SERVICES),
                    'libraries' : python_list(DB[0].LIBRARIES),
                    'act_count' : DB[0].CNT_ACT,
                    'prov_count' : DB[0].CNT_PRO,
                    'serv_count' : DB[0].CNT_SER,
                    'bro_count' : DB[0].CNT_BRO,
                    'certinfo': DB[0].CERT_INFO,
                    'issued':DB[0].ISSUED,
                    'native' : DB[0].NATIVE,
                    'dynamic' : DB[0].DYNAMIC,
                    'reflection' : DB[0].REFLECT,
                    'crypto': DB[0].CRYPTO,
                    'obfus': DB[0].OBFUS,
                    'api': DB[0].API,
                    'dang': DB[0].DANG,
                    'urls': DB[0].URLS,
                    'domains': python_dict(DB[0].DOMAINS),
                    'emails': DB[0].EMAILS,
                    'strings': python_list(DB[0].STRINGS),
                    'zipped' : DB[0].ZIPPED,
                    'mani': DB[0].MANI,
					'webview' : DB[0].WEBVIEW,
					'debug' : DB[0].DEBUG,
					'log' : DB[0].LOG,
					'backup' : DB[0].BACKUP,
					'hardcode' : DB[0].HARDCODE,
                    'date': DB[0].DATE,
                    }
                    # if TYP=='APK':
                        #template= get_template("static_analysis_pdf.html")
                    template = get_template("pdf_02.html")
                    #template = "pdf_02.html"
                    # else:
                    #     template= get_template("static_analysis_zip_pdf.html")
            else:
                return HttpResponseRedirect('/error/')

            html = template.render(context)
            # result = StringIO()
            # pdf = pisa(StringIO( "{0}".format(html.encode('utf-8'))), result, encoding='utf-8')
            # if not pdf.err:
            #     return HttpResponse(result.getvalue(), content_type='application/pdf')
            # else:
            #     return HttpResponseRedirect('/error/')

            css = CSS(settings.STATIC_ROOT + 'css/style.css')
            pdf = HTML(string=html).write_pdf(stylesheets=[css])
            #pdf = HTML(string=html, url_fetcher=url_fetcher).write_pdf(stylesheets=[css])
            http_response = HttpResponse(pdf, content_type='application/pdf')
            http_response['Content-Disposition'] = 'filename=' + DB[0].APP_NAME + '"report.pdf"'
            #pdf.close()
            return http_response
            #return render(request, template, context)

        else:
            return HttpResponseRedirect('/error/')
    except:

        PrintException("[ERROR] PDF Report Generation Error")
        return HttpResponseRedirect('/error/')
        
def url_fetcher(url):
    if url.startswith('../img/'):
        url = url[len('../'):]
        url = os.path.join(settings.STATIC_ROOT,url)
    if url.startswith('../static/'):
        url = url[len('../static/'):]
        url = os.path.join(settings.STATIC_ROOT, url)
    return weasyprint.default_url_fetcher(url)

def Java(request):
    try:
        m = re.match('[0-9a-f]{32}', request.GET['md5'])
        typ = request.GET['type']
        user = request.COOKIES.get('cookie_username', '')
	if user == 'root':
	    user = request.GET['user']
        if m:
            MD5 = request.GET['md5']
            if typ == 'eclipse':
                SRC = os.path.join(settings.UPLD_DIR, user + '/' + MD5 + '/src/')
                t = typ
            elif typ == "studio":
                SRC = os.path.join(settings.UPLD_DIR, user + '/' + MD5 + '/app/src/main/java/')
                t = typ
            elif typ == "apk":
                SRC = os.path.join(settings.UPLD_DIR, user + '/' + MD5 + '/java_source/')
                t = typ
            else:
                return HttpResponseRedirect('/error/')

            html = ''
            for dirName, subDir, files in os.walk(SRC):

                for jfile in files:
                    if jfile.endswith(".java"):
                        file_path = os.path.join(SRC, dirName, jfile)
                        if "+" in jfile:
                            fp2 = os.path.join(SRC, dirName, jfile.replace("+", "x"))
                            shutil.move(file_path, fp2)
                            file_path = fp2
                        fileparam = file_path.replace(SRC, '')
                        if (any(cls in fileparam for cls in settings.SKIP_CLASSES) == False):
                            html += '<tr><td><a target="_blank"' + " href='../ViewSource/?file="+escape(fileparam)+"&md5="+MD5+"&type="+t+"'>"+escape(fileparam)+"</a></td></tr>"

        context = {'title':'Java Source',
                   'files': html,
                   'md5' : MD5,
                   'type': typ,
                   }
        template = "java.html"
        return render(request, template, context)
    except:
        PrintException("[ERROR] 获取Java文件")
        return HttpResponseRedirect('/error/')


def Smali(request):
	try:
		m = re.match('[0-9a-f]{32}', request.GET['md5'])
		user = request.COOKIES.get('cookie_username', '')
		if user == 'root':
			user = request.GET['user']
		if m:
			MD5 = request.GET['md5']
			SRC = os.path.join(settings.UPLD_DIR, user + '/' + MD5 + '/smali_source/')
			html = ''
			for dirName, subDir, files in os.walk(SRC):
				for jfile in files:
					if jfile.endswith('.smali'):
						file_path = os.path.join(SRC, dirName, jfile)
						if "+" in jfile:
							fp2 = os.path.join(SRC, dirName, jfile.replace("+", "x"))
							shutil.move(file_path, fp2)
						fileparam = file_path.replace(SRC, '')
						html += '<tr><td><a target = "_blank" ' + "href='../ViewSource/?file=" + escape(fileparam) + "&md5=" + MD5 + "' >" + escape(fileparam) + "</a></td></tr>"
		context = {'title' : 'Smali Source',
					'files' : html,
					'md5' : MD5,
					}

		template = "smali.html"
		return render(request, template, context)
	except:
		PrintException(u"[ERROR] 获取smali文件")
		return HttpResponseRedirect('/error/')

def Find(request):
	try:
		m = re.match('[0-9a-f]{32}', request.POST['md5'])
		try:
			user = request.COOKIES.get('cookie_username', '')
		except:
			pass
		print u"[INFO] User is " + user
		if m:
			MD5 = request.POST['md5']
			q = request.POST['q']
			code = request.POST['code']
			matches = []
			if code == 'java':
				SRC = os.path.join(settings.UPLD_DIR, user + '/' + MD5 + '/java_source/')
				ext = '.java'
			elif code == 'smali':
				SRC = os.path.join(settings.UPLD_DIR, user + '/' + MD5 + '/smali_source/')
				ext = ".smali"
			else:
				return HttpResponseRedirect('/error/')

			print u"[INFO] SRC = " + SRC

			for dirName, subDir, files in os.walk(SRC):
				for jfile in files:
					if jfile.endswith(ext):
						file_path = os.path.join(SRC, dirName, jfile)
						if "+" in jfile:
							fp2 = os.path.join(SRC, dirName, jfile.replace("+", "x"))
							shutil.move(file_path, fp2)
							file_path = fp2
						fileparam = file_path.replace(SRC, '')
						with io.open(file_path, mode = 'r', encoding = 'utf8', errors = "ignore") as f:
							dat = f.read()
						if q in dat:
							matches.append('<a target="_blank" ' + "href='../ViewSource/?file=" + escape(fileparam) + "&md5=" + MD5 + "type=apk'" + '>' + escape(fileparam) + '</a>')
		flz = len(matches)
		context = {'title' : 'Search Results',
					'matches' : matches,
					'term' : q,
					'found' : str(flz),
					}
		template = "search.html"
		return render(request, template, context)
	except:
		PrintException(u"[ERROR] Searching Failed")
		return HttpResponseRedirect('/error/')

def ViewSource(request):
    try:
        fil=''
        user = request.COOKIES.get('cookie_username', '')
	if user == 'root':
	    user = request.GET['user']
        m=re.match('[0-9a-f]{32}',request.GET['md5'])
        if m and (request.GET['file'].endswith('.java') or request.GET['file'].endswith('.smali')):
            fil=request.GET['file']
            MD5=request.GET['md5']
            if (("../" in fil) or ("%2e%2e" in fil) or (".." in fil) or ("%252e" in fil)):
                return HttpResponseRedirect('/error/')
            else:
                if fil.endswith('.java'):
                    typ=request.GET['type']
                    if typ=='eclipse':
                        SRC=os.path.join(settings.UPLD_DIR, user + '/' + MD5+'/src/')
                    elif typ=='studio':
                        SRC=os.path.join(settings.UPLD_DIR, user + '/' + MD5+'/app/src/main/java/')
                    elif typ=='apk':
                        SRC=os.path.join(settings.UPLD_DIR, user + '/' + MD5+'/java_source/')
                    else:
                        return HttpResponseRedirect('/error/')
                elif fil.endswith('.smali'):
                    SRC=os.path.join(settings.UPLD_DIR, user + '/' + MD5+'/smali_source/')
                sfile=os.path.join(SRC,fil)
                dat=''
                with io.open(sfile, mode='r',encoding="utf8",errors="ignore") as f:
                    dat=f.read()
        else:
            return HttpResponseRedirect('/error/')
        context = {'title': escape(ntpath.basename(fil)),
                   'file': escape(ntpath.basename(fil)),
                   'dat': dat}
        template="view_source.html"
        return render(request,template,context)
    except:
        PrintException("[ERROR] 查看源码")
        return HttpResponseRedirect('/error/')


def ManifestView(request):
	try:
		DIR = settings.BASE_DIR
		MD5 = request.GET['md5']
		user = request.GET['user']
        #print "[INFO] user is " + USER
		TYP = request.GET['type']
		BIN = request.GET['bin']
		m = re.match('[0-9a-f]{32}', MD5)
		if m and (TYP == 'eclipse' or TYP == 'studio' or TYP == 'apk') and (BIN == '1' or BIN == '0'):
			APP_DIR = os.path.join(settings.UPLD_DIR, user + '/' + MD5 + '/')
			TOOLS_DIR = os.path.join(DIR, 'StaticAnalyzer/tools/')
			if BIN == '1':
				x = True
			elif BIN == '0':
				x = False
			MANI = ReadManifest(APP_DIR, TOOLS_DIR, TYP, x)
			context = {'title' : 'AndroidManifest.xml',
						'file' : 'AndroidManifest.xml',
						'dat' : MANI}
			template  = "view_mani.html"
			return render(request, template, context)
	except:
		PrintException(u"[ERROR] 查看 AndroidManifest.xml")
		return HttpResponseRedirect('/error/')

def StaticAnalyzer(request):
    try:
        #Input validation
        TYP=request.GET['type']
        m=re.match('[0-9a-f]{32}',request.GET['checksum'])
        username = request.GET['us']
        user = request.COOKIES.get('cookie_username', '')
        if ((m) and (request.GET['name'].lower().endswith('.apk') or request.GET['name'].lower().endswith('.zip')) and ((TYP=='zip') or (TYP=='apk'))):
            DIR=settings.BASE_DIR        #BASE DIR
            APP_NAME=request.GET['name'] #APP ORGINAL NAME
            MD5=request.GET['checksum']  #MD5
            APP_DIR=os.path.join(settings.UPLD_DIR, user + '/' + MD5+'/') #APP DIRECTORY
            TOOLS_DIR=os.path.join(DIR, 'StaticAnalyzer/tools/')  #TOOLS DIR
            DWD_DIR = settings.DWD_DIR
            print "[INFO] 开始分析 : "+APP_NAME
            RESCAN= str(request.GET.get('rescan', 0))
            if TYP=='apk':
                #Check if in DB
                DB = StaticAnalyzerAndroid.objects.filter(MD5=MD5, HASHUSER = username)
                if DB.exists() and RESCAN=='0':
                    print "\n[INFO] 分析完毕. 从数据库获取信息..."
                    context = {
                    'title' : DB[0].TITLE,
                    'name' : DB[0].APP_NAME,
                    'size' : DB[0].SIZE,
                    'hashuser' : DB[0].HASHUSER,
					'user' : DB[0].USER,
                    'md5': DB[0].MD5,
                    'sha1' : DB[0].SHA1,
                    'sha256' : DB[0].SHA256,
                    'packagename' : DB[0].PACKAGENAME,
                    'mainactivity' : DB[0].MAINACTIVITY,
                    'targetsdk' : DB[0].TARGET_SDK,
                    'maxsdk' : DB[0].MAX_SDK,
                    'minsdk' : DB[0].MIN_SDK,
                    'androvername' : DB[0].ANDROVERNAME,
                    'androver': DB[0].ANDROVER,
                    'manifest': DB[0].MANIFEST_ANAL,
                    'permissions' : DB[0].PERMISSIONS,
                    'files' : python_list(DB[0].FILES),
                    'certz' : DB[0].CERTZ,
                    'activities' : python_list(DB[0].ACTIVITIES),
                    'receivers' : python_list(DB[0].RECEIVERS),
                    'providers' : python_list(DB[0].PROVIDERS),
                    'services' : python_list(DB[0].SERVICES),
                    'libraries' : python_list(DB[0].LIBRARIES),
                    'act_count' : DB[0].CNT_ACT,
                    'prov_count' : DB[0].CNT_PRO,
                    'serv_count' : DB[0].CNT_SER,
                    'bro_count' : DB[0].CNT_BRO,
                    'certinfo': DB[0].CERT_INFO,
                    'issued': DB[0].ISSUED,
                    'native' : DB[0].NATIVE,
                    'dynamic' : DB[0].DYNAMIC,
                    'reflection' : DB[0].REFLECT,
                    'crypto': DB[0].CRYPTO,
                    'obfus': DB[0].OBFUS,
                    'api': DB[0].API,
                    'dang': DB[0].DANG,
                    'urls': DB[0].URLS,
                    'domains': python_dict(DB[0].DOMAINS),
                    'emails': DB[0].EMAILS,
                    'strings': python_list(DB[0].STRINGS),
                    'zipped' : DB[0].ZIPPED,
                    'mani': DB[0].MANI,
                    'e_act': DB[0].E_ACT,
                    'e_ser': DB[0].E_SER,
                    'e_bro': DB[0].E_BRO,
                    'e_cnt': DB[0].E_CNT,
                    'debug' : DB[0].DEBUG,
                    'backup' : DB[0].BACKUP,
                    'log' : DB[0].LOG,
                    'hardcode' : DB[0].HARDCODE,
                    'date' : DB[0].DATE,
                    }
                else:
                    APP_FILE=MD5 + '.apk'        #NEW FILENAME
                    APP_PATH=APP_DIR+APP_FILE    #APP PATH
                    #ANALYSIS BEGINS
                    SIZE=str(FileSize(APP_PATH)) + 'MB'   #FILE SIZE
                    SHA1, SHA256= HashGen(APP_PATH)       #SHA1 & SHA256 HASHES

                    Date = datetime.now().strftime("%Y-%m-%d")
                    FILES=Unzip(APP_PATH,APP_DIR)
                    CERTZ, HardCode = GetHardcodedCertKeystore(FILES)
                    print "[INFO] APK Extracted"
                    PARSEDXML= GetManifest(APP_DIR,TOOLS_DIR,'',True) #Manifest XML
                    MANI='../ManifestView/?md5='+MD5+'&type=apk&bin=1&user=' + user
                    SERVICES,ACTIVITIES,RECEIVERS,PROVIDERS,LIBRARIES,PERM,PACKAGENAME,MAINACTIVITY,MIN_SDK,MAX_SDK,TARGET_SDK,ANDROVER,ANDROVERNAME=ManifestData(PARSEDXML,APP_DIR)
                    MANIFEST_ANAL,EXPORTED_ACT,EXPORTED_CNT,Debug,Backup=ManifestAnalysis(PARSEDXML,MAINACTIVITY)
                    PERMISSIONS=FormatPermissions(PERM)
                    CNT_ACT =len(ACTIVITIES)
                    CNT_PRO =len(PROVIDERS)
                    CNT_SER =len(SERVICES)
                    CNT_BRO = len(RECEIVERS)

                    CERT_INFO,ISSUED=CertInfo(APP_DIR,TOOLS_DIR)
                    Dex2Jar(APP_PATH,APP_DIR,TOOLS_DIR)
                    Dex2Smali(APP_DIR,TOOLS_DIR)
                    Jar2Java(APP_DIR,TOOLS_DIR)

                    API,DANG,URLS,DOMAINS,EMAILS,CRYPTO,OBFUS,REFLECT,DYNAMIC,NATIVE,Log,Webview=CodeAnalysis(APP_DIR,MD5,PERMISSIONS,"apk")
                    print "\n[INFO] 生成Java and Smali 下载文件"
                    GenDownloads(APP_DIR,MD5, user)
                    STRINGS=Strings(APP_FILE,APP_DIR,TOOLS_DIR)
                    ZIPPED='&type=apk'

                    print "\n[INFO] 连接数据库"
                    try:
                        #SAVE TO DB
                        if RESCAN=='1':
                            print "\n[INFO] 更新数据库...更新时间" + Date
                            StaticAnalyzerAndroid.objects.filter(MD5=MD5, USER=username).update(TITLE = 'Static Analysis',
                            APP_NAME = APP_NAME,
                            SIZE = SIZE,
                            HASHUSER = username,
							USER = user,
                            MD5= MD5,
                            SHA1 = SHA1,
                            SHA256 = SHA256,
                            PACKAGENAME = PACKAGENAME,
                            MAINACTIVITY= MAINACTIVITY,
                            TARGET_SDK = TARGET_SDK,
                            MAX_SDK = MAX_SDK,
                            MIN_SDK = MIN_SDK,
                            ANDROVERNAME = ANDROVERNAME,
                            ANDROVER= ANDROVER,
                            MANIFEST_ANAL= MANIFEST_ANAL,
                            PERMISSIONS = PERMISSIONS,
                            FILES = FILES,
                            CERTZ = CERTZ,
                            ACTIVITIES = ACTIVITIES,
                            RECEIVERS = RECEIVERS,
                            PROVIDERS = PROVIDERS,
                            SERVICES = SERVICES,
                            LIBRARIES = LIBRARIES,
                            CNT_ACT = CNT_ACT,
                            CNT_PRO = CNT_PRO,
                            CNT_SER = CNT_SER,
                            CNT_BRO = CNT_BRO,
                            CERT_INFO= CERT_INFO,
                            ISSUED=ISSUED,
                            NATIVE = NATIVE,
                            DYNAMIC = DYNAMIC,
                            REFLECT = REFLECT,
                            CRYPTO= CRYPTO,
                            OBFUS= OBFUS,
                            API= API,
                            DANG= DANG,
                            URLS= URLS,
                            DOMAINS= DOMAINS,
                            EMAILS= EMAILS,
                            STRINGS= STRINGS,
                            ZIPPED= ZIPPED,
                            MANI= MANI,
                            EXPORTED_ACT=EXPORTED_ACT,
                            E_ACT=EXPORTED_CNT["act"],
                            E_SER=EXPORTED_CNT["ser"],
                            E_BRO=EXPORTED_CNT["bro"],
                            E_CNT=EXPORTED_CNT["cnt"],
                            DEBUG = Debug,
                            BACKUP = Backup,
                            LOG = Log,
                            WEBVIEW = Webview,
                            HARDCODE = HardCode,
                            DATE = Date)
                        elif RESCAN=='0':
                            print "\n[INFO] 保存到数据库"
                            STATIC_DB=StaticAnalyzerAndroid(TITLE = 'Static Analysis',
                            APP_NAME = APP_NAME,
                            SIZE = SIZE,
                            MD5= MD5,
							USER = user,
                            HASHUSER = username,
                            SHA1 = SHA1,
                            SHA256 = SHA256,
                            PACKAGENAME = PACKAGENAME,
                            MAINACTIVITY= MAINACTIVITY,
                            TARGET_SDK = TARGET_SDK,
                            MAX_SDK = MAX_SDK,
                            MIN_SDK = MIN_SDK,
                            ANDROVERNAME = ANDROVERNAME,
                            ANDROVER= ANDROVER,
                            MANIFEST_ANAL= MANIFEST_ANAL,
                            PERMISSIONS = PERMISSIONS,
                            FILES = FILES,
                            CERTZ = CERTZ,
                            ACTIVITIES = ACTIVITIES,
                            RECEIVERS = RECEIVERS,
                            PROVIDERS = PROVIDERS,
                            SERVICES = SERVICES,
                            LIBRARIES = LIBRARIES,
                            CNT_ACT = CNT_ACT,
                            CNT_PRO = CNT_PRO,
                            CNT_SER = CNT_SER,
                            CNT_BRO = CNT_BRO,
                            CERT_INFO= CERT_INFO,
                            ISSUED=ISSUED,
                            NATIVE = NATIVE,
                            DYNAMIC = DYNAMIC,
                            REFLECT = REFLECT,
                            CRYPTO= CRYPTO,
                            OBFUS= OBFUS,
                            API= API,
                            DANG= DANG,
                            URLS= URLS,
                            DOMAINS= DOMAINS,
                            EMAILS= EMAILS,
                            STRINGS= STRINGS,
                            ZIPPED= ZIPPED,
                            MANI= MANI,
                            EXPORTED_ACT=EXPORTED_ACT,
                            E_ACT=EXPORTED_CNT["act"],
                            E_SER=EXPORTED_CNT["ser"],
                            E_BRO=EXPORTED_CNT["bro"],
                            E_CNT=EXPORTED_CNT["cnt"],
                            DEBUG = Debug,
                            BACKUP = Backup,
                            LOG = Log,
                            WEBVIEW = Webview,
                            HARDCODE = HardCode,
                            DATE = Date)
                            STATIC_DB.save()
                    except:
                        PrintException("[ERROR] 保存到数据库失败")
                        pass
                    context = {
                    'title' : 'Static Analysis',
                    'name' : APP_NAME,
                    'size' : SIZE,
                    'hashuser' : username,
					'user' : user,
                    'md5': MD5,
                    'sha1' : SHA1,
                    'sha256' : SHA256,
                    'packagename' : PACKAGENAME,
                    'mainactivity' : MAINACTIVITY,
                    'targetsdk' : TARGET_SDK,
                    'maxsdk' : MAX_SDK,
                    'minsdk' : MIN_SDK,
                    'androvername' : ANDROVERNAME,
                    'androver': ANDROVER,
                    'manifest': MANIFEST_ANAL,
                    'permissions' : PERMISSIONS,
                    'files' : FILES,
                    'certz' : CERTZ,
                    'activities' : ACTIVITIES,
                    'receivers' : RECEIVERS,
                    'providers' : PROVIDERS,
                    'services' : SERVICES,
                    'libraries' : LIBRARIES,
                    'act_count' : CNT_ACT,
                    'prov_count' : CNT_PRO,
                    'serv_count' : CNT_SER,
                    'bro_count' : CNT_BRO,
                    'certinfo': CERT_INFO,
                    'issued':ISSUED,
                    'native' : NATIVE,
                    'dynamic' : DYNAMIC,
                    'reflection' : REFLECT,
                    'crypto': CRYPTO,
                    'obfus': OBFUS,
                    'api': API,
                    'dang': DANG,
                    'urls': URLS,
                    'domains': DOMAINS,
                    'emails': EMAILS,
                    'strings': STRINGS,
                    'zipped' : ZIPPED,
                    'mani': MANI,
                    'e_act': EXPORTED_CNT["act"],
                    'e_ser': EXPORTED_CNT["ser"],
                    'e_bro': EXPORTED_CNT["bro"],
                    'e_cnt': EXPORTED_CNT["cnt"],
                    'debug': Debug,
                    'log' : Log,
                    'webview' : Webview,
                    'backup' : Backup,
                    'hardcode' : HardCode,
                    'date' : Date,
                    }
                template="static_analysis.html"
                return render(request,template,context)
            elif TYPE == "zip":
                # 检测是否存在数据库中
                DB=StaticAnalyzerAndroid.objects.filter(MD5=MD5, USER=username)
                if DB.exists() and RESCAN=='0':
                    print "\n[INFO] 分析完毕. 从数据库获取数据..."
                    context = {
                    'title' : DB[0].TITLE,
                    'name' : DB[0].APP_NAME,
                    'size' : DB[0].SIZE,
					'hashuer' : DB[0].HASHUSER,
					'user' : DB[0].USER,
                    'md5': DB[0].MD5,
                    'sha1' : DB[0].SHA1,
                    'sha256' : DB[0].SHA256,
                    'packagename' : DB[0].PACKAGENAME,
                    'mainactivity' : DB[0].MAINACTIVITY,
                    'targetsdk' : DB[0].TARGET_SDK,
                    'maxsdk' : DB[0].MAX_SDK,
                    'minsdk' : DB[0].MIN_SDK,
                    'androvername' : DB[0].ANDROVERNAME,
                    'androver': DB[0].ANDROVER,
                    'manifest': DB[0].MANIFEST_ANAL,
                    'permissions' : DB[0].PERMISSIONS,
                    'files' : python_list(DB[0].FILES),
                    'certz' : DB[0].CERTZ,
                    'activities' : python_list(DB[0].ACTIVITIES),
                    'receivers' : python_list(DB[0].RECEIVERS),
                    'providers' : python_list(DB[0].PROVIDERS),
                    'services' : python_list(DB[0].SERVICES),
                    'libraries' : python_list(DB[0].LIBRARIES),
                    'act_count' : DB[0].CNT_ACT,
                    'prov_count' : DB[0].CNT_PRO,
                    'serv_count' : DB[0].CNT_SER,
                    'bro_count' : DB[0].CNT_BRO,
                    'native' : DB[0].NATIVE,
                    'dynamic' : DB[0].DYNAMIC,
                    'reflection' : DB[0].REFLECT,
                    'crypto': DB[0].CRYPTO,
                    'obfus': DB[0].OBFUS,
                    'api': DB[0].API,
                    'dang': DB[0].DANG,
                    'urls': DB[0].URLS,
                    'domains': python_dict(DB[0].DOMAINS),
                    'emails': DB[0].EMAILS,
                    'mani': DB[0].MANI,
                    'e_act': DB[0].E_ACT,
                    'e_ser': DB[0].E_SER,
                    'e_bro': DB[0].E_BRO,
                    'e_cnt': DB[0].E_CNT,
					'debug' : DB[0].DEBUG,
					'backup' : DB[0].BACKUP,
					'log' : DB[0].LOG,
					'webview' : DB[0].WEBVIEW,
					'hardecode' : DB[0].HARDCODE,
					'date' : DB[0].DATE,
                    }
                else:
                    APP_FILE=MD5 + '.zip'        #NEW FILENAME
                    APP_PATH=APP_DIR+APP_FILE    #APP PATH
                    print "[INFO] 解压 ZIP"
                    FILES = Unzip(APP_PATH,APP_DIR)
                    #Check if Valid Directory Structure and get ZIP Type
                    pro_type,Valid=ValidAndroidZip(APP_DIR+"/" + APP_NAME.replace(".zip", "/"))
                    CERTZ,HardCode = GetHardcodedCertKeystore(FILES)
                    Date = datetime.now().strftime("%Y-%m-%d")
                    print "[INFO] ZIP 类型 - " + pro_type
                    if Valid and (pro_type=='eclipse' or pro_type=='studio'):
                        #ANALYSIS BEGINS
                        SIZE=str(FileSize(APP_PATH)) + 'MB'   #FILE SIZE
                        SHA1,SHA256= HashGen(APP_PATH)        #SHA1 & SHA256 HASHES
                        PARSEDXML= GetManifest(APP_DIR+"/" + APP_NAME.replace(".zip", "/"),TOOLS_DIR,pro_type,False)   #Manifest XML
                        MANI='../ManifestView/?md5='+MD5+'&type='+pro_type+'&bin=0' + '&user=' + user
                        SERVICES,ACTIVITIES,RECEIVERS,PROVIDERS,LIBRARIES,PERM,PACKAGENAME,MAINACTIVITY,MIN_SDK,MAX_SDK,TARGET_SDK,ANDROVER,ANDROVERNAME=ManifestData(PARSEDXML,APP_DIR+"/" + APP_NAME.replace(".zip", "/"))
                        MANIFEST_ANAL,EXPORTED_ACT,EXPORTED_CNT,Debug,Backup=ManifestAnalysis(PARSEDXML,MAINACTIVITY)
                        PERMISSIONS=FormatPermissions(PERM)
                        CNT_ACT =len(ACTIVITIES)
                        CNT_PRO =len(PROVIDERS)
                        CNT_SER =len(SERVICES)
                        CNT_BRO = len(RECEIVERS)
                        API,DANG,URLS,DOMAINS,EMAILS,CRYPTO,OBFUS,REFLECT,DYNAMIC,NATIVE, Log, Webview=CodeAnalysis(APP_DIR+"/" + APP_NAME.replace(".zip", "/"),MD5,PERMISSIONS,pro_type)
                        print "\n[INFO] Connecting to Database"
                        try:
                            #SAVE TO DB
                            if RESCAN=='1':
                                print "\n[INFO] Updating Database..."
                                StaticAnalyzerAndroid.objects.filter(MD5=MD5, USER=username).update(TITLE = 'Static Analysis',
                                APP_NAME = APP_NAME,
                                SIZE = SIZE,
								HASHUSER = username,
								USER = user,
                                MD5= MD5,
                                SHA1 = SHA1,
                                SHA256 = SHA256,
                                PACKAGENAME = PACKAGENAME,
                                MAINACTIVITY= MAINACTIVITY,
                                TARGET_SDK = TARGET_SDK,
                                MAX_SDK = MAX_SDK,
                                MIN_SDK = MIN_SDK,
                                ANDROVERNAME = ANDROVERNAME,
                                ANDROVER= ANDROVER,
                                MANIFEST_ANAL= MANIFEST_ANAL,
                                PERMISSIONS = PERMISSIONS,
                                FILES = FILES,
                                CERTZ = CERTZ,
                                ACTIVITIES = ACTIVITIES,
                                RECEIVERS = RECEIVERS,
                                PROVIDERS = PROVIDERS,
                                SERVICES = SERVICES,
                                LIBRARIES = LIBRARIES,
                                CNT_ACT = CNT_ACT,
                                CNT_PRO = CNT_PRO,
                                CNT_SER = CNT_SER,
                                CNT_BRO = CNT_BRO,
                                CERT_INFO= "",
                                ISSUED="",
                                NATIVE = NATIVE,
                                DYNAMIC = DYNAMIC,
                                REFLECT = REFLECT,
                                CRYPTO= CRYPTO,
                                OBFUS= OBFUS,
                                API= API,
                                DANG= DANG,
                                URLS= URLS,
                                DOMAINS= DOMAINS,
                                EMAILS= EMAILS,
                                STRINGS= "",
                                ZIPPED= "",
                                MANI= MANI,
                                EXPORTED_ACT=EXPORTED_ACT,
                                E_ACT=EXPORTED_CNT["act"],
                                E_SER=EXPORTED_CNT["ser"],
                                E_BRO=EXPORTED_CNT["bro"],
                                E_CNT=EXPORTED_CNT["cnt"],
								DEBUG = Debug,
								LOG = Log,
								WEBVIEW = Webview,
								HARDCODE = HardCode,
								DATE = Date,)
                            elif RESCAN=='0':
                                print "\n[INFO] Saving to Database"
                                STATIC_DB=StaticAnalyzerAndroid(TITLE = 'Static Analysis',
                                APP_NAME = APP_NAME,
                                SIZE = SIZE,
								HASHUSER = username,
								USER = user,
                                MD5= MD5,
                                SHA1 = SHA1,
                                SHA256 = SHA256,
                                PACKAGENAME = PACKAGENAME,
                                MAINACTIVITY= MAINACTIVITY,
                                TARGET_SDK = TARGET_SDK,
                                MAX_SDK = MAX_SDK,
                                MIN_SDK = MIN_SDK,
                                ANDROVERNAME = ANDROVERNAME,
                                ANDROVER= ANDROVER,
                                MANIFEST_ANAL= MANIFEST_ANAL,
                                PERMISSIONS = PERMISSIONS,
                                FILES = FILES,
                                CERTZ = CERTZ,
                                ACTIVITIES = ACTIVITIES,
                                RECEIVERS = RECEIVERS,
                                PROVIDERS = PROVIDERS,
                                SERVICES = SERVICES,
                                LIBRARIES = LIBRARIES,
                                CNT_ACT = CNT_ACT,
                                CNT_PRO = CNT_PRO,
                                CNT_SER = CNT_SER,
                                CNT_BRO = CNT_BRO,
                                CERT_INFO= "",
                                ISSUED="",
                                NATIVE = NATIVE,
                                DYNAMIC = DYNAMIC,
                                REFLECT = REFLECT,
                                CRYPTO= CRYPTO,
                                OBFUS= OBFUS,
                                API= API,
                                DANG= DANG,
                                URLS= URLS,
                                DOMAINS= DOMAINS,
                                EMAILS= EMAILS,
                                STRINGS= "",
                                ZIPPED= "",
                                MANI= MANI,
                                EXPORTED_ACT=EXPORTED_ACT,
                                E_ACT=EXPORTED_CNT["act"],
                                E_SER=EXPORTED_CNT["ser"],
                                E_BRO=EXPORTED_CNT["bro"],
                                E_CNT=EXPORTED_CNT["cnt"],
								DEBUG = Debug,
								LOG = Log,
								WEBVIEW = Webview,
								HARDCODE = HardCode,
								DATE = Date)
                                STATIC_DB.save()
                        except:
                            PrintException("[ERROR] 保存到数据库失败")
                            pass
                        context = {
                        'title' : 'Static Analysis',
                        'name' : APP_NAME,
                        'size' : SIZE,
						'hashuser' : username,
						'user' : user,
                        'md5': MD5,
                        'sha1' : SHA1,
                        'sha256' : SHA256,
                        'packagename' : PACKAGENAME,
                        'mainactivity' : MAINACTIVITY,
                        'targetsdk' : TARGET_SDK,
                        'maxsdk' : MAX_SDK,
                        'minsdk' : MIN_SDK,
                        'androvername' : ANDROVERNAME,
                        'androver': ANDROVER,
                        'manifest': MANIFEST_ANAL,
                        'permissions' : PERMISSIONS,
                        'files' : FILES,
                        'certz' : CERTZ,
                        'activities' : ACTIVITIES,
                        'receivers' : RECEIVERS,
                        'providers' : PROVIDERS,
                        'services' : SERVICES,
                        'libraries' : LIBRARIES,
                        'act_count' : CNT_ACT,
                        'prov_count' : CNT_PRO,
                        'serv_count' : CNT_SER,
                        'bro_count' : CNT_BRO,
                        'native' : NATIVE,
                        'dynamic' : DYNAMIC,
                        'reflection' : REFLECT,
                        'crypto': CRYPTO,
                        'obfus': OBFUS,
                        'api': API,
                        'dang': DANG,
                        'urls': URLS,
                        'domains': DOMAINS,
                        'emails': EMAILS,
                        'mani': MANI,
                        'e_act': EXPORTED_CNT["act"],
                        'e_ser': EXPORTED_CNT["ser"],
                        'e_bro': EXPORTED_CNT["bro"],
                        'e_cnt': EXPORTED_CNT["cnt"],
						'debug' : Debug,
						'log' : Log,
						'webview' : Webview,
						'hardcode' : HardCode,
						'date' : Date,
                        }
                    else:
                        return HttpResponseRedirect('/ZIP_FORMAT/')
                #template="static_analysis_android_zip.html"
                template = "static_analysis.html"
                return render(request,template,context)
            else:
                print "\n[ERROR]目前只支持APK,AndroidSource code压缩文件!"
        else:
            return HttpResponseRedirect('/error/')

    except Exception as e:
        PrintException("[ERROR] Static Analyzer")
        context = {
        'title' : 'Error',
        'exp' : e.message,
        'doc' : e.__doc__
        }
        template="error.html"
        return render(request,template,context)

def GetHardcodedCertKeystore(files):
	try:
		HardCode = False
		print u"[INFO] 从 Certificats/Keystores 中获取硬编码信息"
		dat = ''
		certz = ''
		ks = ''
		for f in files:
			ext = f.split('.')[-1]
			if re.search("cer|perm|cert|crt|pub|key|pfx|p12", ext):
				certz += escape(f) + "</br>"
			if re.search("jks | bks", ext):
				ks += escape(f) + "</br>"
		if len(certz) > 1:
			dat += u"<tr><td>APP中存在硬编码Certificate/Key文件.</td><td>" + certz + "</td><tr>"
			HardCode = True
		if len(ks) > 1:
			dat += u"<tr><td>未找到硬编码密钥对.</td><td>" + ks + "</td><tr>"
		return dat, HardCode
	except:
		PrintException("[ERROR] 获取硬编码Certificates/Keystores")

def ReadManifest(APP_DIR, TOOLS_DIR, TYP, BIN):
	try:
		dat = ''

		if BIN == True:
			print u"[INFO] 获取二进制Manifest文件"
			print u"[INFO] AXML -> XML"
			manifest = os.path.join(APP_DIR, "AndroidManifest.xml")
			if len(settings.AXMLPRINTER_BINARY) > 0 and isFileExists(settings.AXMLPRINTER_BINARY):
				CP_PATH = settings.AXMLPRINTER_BINARY
			else:
				CP_PATH = os.path.join(TOOLS_DIR, 'AXMLPrinter2.jar')
			args = [settings.JAVA_PATH + 'java', '-jar', CP_PATH, manifest]
			dat = subprocess.check_output(args)
		else:
			print u"[INFO] 从源代码获取Manifest"
			if TYP == "eclipse":
				manifest = os.path.join(APP_DIR, "AndroidManifest.xml")
			elif TYP == "studio":
				manifest = os.path.join(APP_DIR, "app/src/main/AndroidManifest.xml")
			with io.open(manifest, mode = 'r', encoding = 'utf8', errors = 'ignore') as f:
				dat = f.read()
		return dat
	except:
		PrintException("[ERROR] 读取Manifest文件")

def GetManifest(APP_DIR, TOOLS_DIR, TYP, BIN):
	try:
		dat = ''
		mfest = ''
		dat = ReadManifest(APP_DIR, TOOLS_DIR, TYP, BIN).replace("\n", "")
		try:
			print u"[INFO] 正在解析AndroidManifest.xml"
			mfest = minidom.parseString(dat)
		except:
			PrintException(u"[ERROR] 解析 AndroidManifest.xml")
			mfest = minidom.parseString(r'<?xml version="1.0" encoding="utf-8"?><manifest xmlns:android="http://schemas.android.com/apk/res/android" android:versionCode="Failed"  android:versionName="Failed" package="Failed"  platformBuildVersionCode="Failed" platformBuildVersionName="Failed XML Parsing" ></manifest>')
			print u"[WARNING] 使用Fake XML继续分析"
		return mfest
	except:
		PrintException(u"[ERROR] 解析Manifest文件")

def ValidAndroidZip(APP_DIR):
	try:
		print u"[INFO] 检测ZIP类型及模式"
		# eclipse mode
		man = os.path.isfile(os.path.join(APP_DIR, "AndroidManifest.xml"))
		src = os.path.exists(os.path.join(APP_DIR, "src/"))
		if man and src:
			return 'eclipse', True

		# Studio mode
		man = os.path.isfile(os.path.join(APP_DIR, "app/src/main/AndroidManifest.xml"))
		src = os.path.exists(os.path.join(APP_DIR, "app/src/main/java"))
		if man and src:
			return 'studio', True
        #print u"[INFO] 检测完毕"
		return False
	except:
		PrintException(u"[ERROR] 检测上传文件类型")

def HashGen(APP_PATH):
	try:
		print u"[INFO] 生成HASH值"
		sha1 = hashlib.sha1()
		sha256 = hashlib.sha256()
		BLOCKSIZE = 65536
		with io.open(APP_PATH, mode = 'rb') as afile:
			buf = afile.read(BLOCKSIZE)
			while len(buf) > 0:
				sha1.update(buf)
				sha256.update(buf)
				buf = afile.read(BLOCKSIZE)
		sha1val = sha1.hexdigest()
		sha256val = sha256.hexdigest()
		return sha1val, sha256val
	except:
		PrintException(u"[ERROR] 生成哈希值")

def FileSize(APP_PATH):
	return round(float(os.path.getsize(APP_PATH)) / (1024 * 1024), 2)

def GenDownloads(APP_DIR, MD5, user):
	try:
		print u"[INFO] 生成下载 APPDIR " + APP_DIR
		# Java文件
		print u"[INFO] 生成下载 JAVA"
		DIR = os.path.join(APP_DIR, 'java_source/')
		DDIR = os.path.join(settings.DWD_DIR,user)
		DWD = os.path.join(settings.DWD_DIR,user + '/' + MD5 + '-java.zip')
		#ZipJava = DWD + '/' + MD5 + '-java.zip'
		if (os.path.exists(DDIR)):
			zipf = zipfile.ZipFile(DWD, 'w')
			zipdir(DIR, zipf)
			zipf.close()
		else:
			os.makedirs(DDIR)
			try:
				zipf = zipfile.ZipFile(DWD, 'w')
				zipdir(DIR, zipf)
			except:
				return HttpResponse("ZipFile error!")
			zipf.close()

		# smali文件
		print u"[INFO] 生成下载 Smali"
		DIR = os.path.join(APP_DIR, 'smali_source/')
		DWD = os.path.join(settings.DWD_DIR, user + '/' + MD5 + '-smali.zip')
		if (os.path.exists(DDIR)):
			zipf = zipfile.ZipFile(DWD, 'w')
			zipdir(DIR, zipf)
			zipf.close()
		else:
			os.makedirs(DDIR)
			zipf = zipfile.ZipFile(DWD, 'w')
			zipdir(DIR,zipf)

	except:
		PrintException(u"[ERROR] 生成下载文件")

def zipdir(path, zip):
	try:
		print u"[INFO] 压缩ing.."
		for root, dirs, files in os.walk(path):
			for file in files:
				zip.write(os.path.join(root, file))
	except:
		PrintException("[ERROR] 压缩")

def Unzip(APP_PATH, EXT_PATH):
	print u"[INFO] 解压ing"
	try:
		files = []
		with zipfile.ZipFile(APP_PATH, 'r') as z:
			z.extractall(EXT_PATH)
			files = z.namelist()
		return files
	except:
		PrintException(u"[ERROR] 解压错误")
		if platform.system() == "Windows":
			print u"\n[INFO] 没有相应解压命令"
		else:
			print u"\n[INFO] 使用系统默认解压工具"
			try:
				subprocess.call(['unzip', '-o', '-q', APP_PATH, '-d', EXT_PATH])
				dat = subprocess.check_output(['unzip', '-qq', '-l', APP_PATH])
				dat = dat.split('\n')
				x = ['Length	Date 	Time 	Name']
				x = x + dat
				return x
			except:
				PrintException(u"[ERROR] 解压错误")

def FormatPermissions(PERMISSIONS):
	try:
		print u"[INFO] 格式化Permissions"
		DESC = ''
		for per in PERMISSIONS:
			DESC = DESC + '<tr><td>' + per + '</td>'
			for l in PERMISSIONS[per]:
				DESC = DESC + '<td>' + l + '</td>'
			DESC = DESC + '</tr>'
		DESC = DESC.replace('dangerous', '<span class= "label label-danger">高危</span>').replace('normal', '<span class="label label-info">正常</span>').replace('signatureOrSystem', '<span class="label label-warning">系统签名</span>').replace('signature', '<span class="label label-success">应用签名</span>').replace('unknown', '<span class="label label-warning">未知权限</span>')
		return DESC
	except:
		PrintException(u"[ERROR] Formating Error")

def CertInfo(APP_DIR,TOOLS_DIR):
    try:
        print "[INFO] 获取代码签名证书"
        cert=os.path.join(APP_DIR,'META-INF/')
        CP_PATH=TOOLS_DIR + 'CertPrint.jar'
        files = [ f for f in os.listdir(cert) if os.path.isfile(os.path.join(cert,f)) ]
        if "CERT.RSA" in files:
            certfile=os.path.join(cert,"CERT.RSA")
        else:
            for f in files:
                if f.lower().endswith(".rsa"):
                    certfile=os.path.join(cert,f)
                elif f.lower().endswith(".dsa"):
                    certfile=os.path.join(cert,f)

        args=[settings.JAVA_PATH+'java','-jar', CP_PATH, certfile]
        dat=''
        issued='good'
        dat=escape(subprocess.check_output(args)).replace('\n', '</br>')
        if re.findall("Issuer: CN=Android Debug|Subject: CN=Android Debug",dat):
            issued="bad"
        return dat,issued
    except:
        PrintException("[ERROR] 获取代码签名证书")

def WinFixJava(TOOLS_DIR):
	try:
		print u"[INFO] Windows下运行Java路径修复"
		DMY = os.path.join(TOOLS_DIR, 'd2js/d2j_invoke.tmp')
		ORG = os.path.join(TOOLS_DIR, 'd2j2/d2j_invoke.bat')
		dat = ''
		with open(DMY, 'r') as f:
			dat = f.read().replace("[xxx]", settings.JAVA_PATh + "java")
		with open(ORG, 'w') as f:
			f.write(dat)
	except:
		PrintException(u"[ERROR] Windows下运行Java路径修复")

def WinFixPython3(TOOLS_DIR):
	try:
		print u"[INFO] Windows下运行python3路径修复"
		PYTHON3_PATH = ""
		if len(settings.PYTHON3_PATH) > 2:
			PYTHON3_PATH = settings.PYTHON3_PATH
		else:
			pathev = os.environ["path"]
			if pathenv:
				paths = pathenv.split(";")
				for path in paths:
					if "python3" in path.lower():
						PYTHON3_PATH = path
		PYTHON3 = os.path.join(PYTHON3_PATH, "python")
		DMY = os.path.join(TOOLS_DIR, 'enjarify/enjarify.tmp')
		ORG = os.path.join(TOOLS_DIR, 'enjarify/enjarify.bat')
		dat = ''
		with open(DMY, 'r') as f:
			dat = f.read().replace("[xxx]", PYTHON3)
		with open(ORG, 'w') as f:
			f.write(dat)
	except:
		PrintException(u"[ERROR] Windows下运行python3路径修复")

def Dex2Jar(APP_PATH, APP_DIR, TOOLS_DIR):
	try:
		print u"[INFO] DEX -> JAR"
		args = []
		working_dir = False
		if settings.JAR_CONVERTER == "d2j":
			print u"[INFO] 使用 JAR转换器 - dex2jar"
			if platform.system() == "Windows":
				WinFixJava(TOOLS_DIR)
				D2J = os.path.join(TOOLS_DIR, 'd2j2/d2j-dex2jar.bat')
			else:
				INV = os.path.join(TOOLS_DIR, 'd2j2/d2j_invoke.sh')
				D2J = os.path.join(TOOLS_DIR, 'd2j2/d2j-dex2jar.sh')
				subprocess.call(['chmod', '777', D2J])
				subprocess.call(['chmod', '777', INV])
			if len(settings.DEX2JAR_BINARY) > 0 and isFileExists(settings.DEX2JAR_BINARY):
				D2J = settings.DEX2JAR_BINARY
			args = [D2J, APP_DIR + 'classes.dex', '-f', '-o', APP_DIR + 'classes.jar']
		elif settings.JAR_CONVERTER == "enjarify":
			print u"[INFO] 使用JAR转换器 - Google enjarify"
			if len(settings.ENJARIFY_DIRECTORY) > 0 and isDirExists(settings.ENJARIFY_DIRECTORY):
				WD = settings.ENJARIFY_DIRECTORY
			else:
				WD = os.path.join(TOOLS_DIR, 'enjarify/')
			if platform.system() == "Windows":
				WinFixPython3(TOOLS_DIR)
				EJ = os.path.join(WD, 'enjarify.bat')
				args = [EJ, APP_PATH, '-f', '-o', APP_DIR + 'classes.jar']
			else:
				working_dir = True
				if len(settings.PYTHON3_PATH) > 2:
					PYTHON3 = os.path.join(settings.PYTHON3_PATH, "python3")
				else:
					PYTHON3 = "python3"
				args = [PYHTON3, '-O', '-m', 'enjarify.main', APP_PATH, '-f', '-o', APP_DIR + 'classes.jar']
		if working_dir:
			subprocess.call(args, cws = WD)
		else:
			subprocess.call(args)
	except:
		PrintException(u"[ERROR] 转换Dex -> JAR")

def Dex2Smali(APP_DIR, TOOLS_DIR):
	try:
		print u"[INFO] DEX -> SMALI"
		DEX_PATH = APP_DIR + 'classes.dex'
		if len(settings.BACKSMALI_BINARY) > 0 and isFileExists(settings.BACKSMALI_BINARY):
			BS_PATH = settings.BACKSMALI_BINARY
		else:
			BS_PATH = os.path.join(TOOLS_DIR, 'baksmali.jar')
		OUTPUT = os.path.join(APP_DIR, 'smali_source/')
		args = [settings.JAVA_PATH + 'java', '-jar', BS_PATH, DEX_PATH, '-o', OUTPUT]
		subprocess.call(args)
	except:
		PrintException(u"[ERROR] 转换 DEX -> SMALI")

def Jar2Java(APP_DIR, TOOLS_DIR):
	try:
		print u"[INFO] JAR -> JAVA"
		JAR_PATH = APP_DIR + 'classes.jar'
		OUTPUT = os.path.join(APP_DIR, 'java_source/')
		if settings.DECOMPILER == 'jd-core':
			if len(settings.JD_CORE_DECOMPILER_BINARY) > 0 and isFileExists(settings.JD_CORE_DECOMPILER_BINARY):
				JD_PATH = settings.JD_CORE_DECOMPILER_BINARY
			else:
				JD_PATH = os.path.join(TOOLS_DIR, 'jd-core.jar')
			args = [settings.JAVA_PATH + 'java', '-jar', JD_PATH, JAR_PATH, OUTPUT]
		elif settings.DECOMPILER == 'cfr':
			if len(settings.CFR_DECOMPILER_BINARY) > 0 and isFileExists(settings.CFR_DECOMPILER_BINARY):
				JD_PATH = settings.CFR_DECOMPILER_BINARY
			else:
				JD_PATH = os.path.join(TOOLS_DIR, 'cfr_0_115.jar')
			args = [settings.JAVA_PATH + 'java', '-jar', JD_PATH, JAR_PATH, '--outputdir', OUTPUT]
		elif settings.DECOMPILIER == 'procyon':
			if len(settings.PROCYON_DECOMPILER_BINARY) > 0 and isFileExists(settings.PROCYON_DECOMPILER_BINARY):
				PD_PATH = settings.PROCYON_DECOMPILER_BINARY
			else:
				PD_PATH = os.path.join(TOOLS_DIR, 'procyon-decompiler-0.5.30.jar')
			args = [settings.JAVA_PATH + 'java', '-jar', PD_PATH, JAR_PATH, '-o', OUTPUT]
		subprocess.call(args)
	except:
		PrintException(u"[ERROR] 转换 JAR -> JAVA")

def Strings(APP_FILE, APP_DIR, TOOLS_DIR):
	try:
		print u"[INFO] 从APK中获取字符串"
		strings = TOOLS_DIR + 'strings_from_apk.jar'
		args = [settings.JAVA_PATH + 'java', '-jar', strings, APP_DIR + APP_FILE, APP_DIR]
		subprocess.call(args)
		dat = ''
		try:
			with io.open(APP_DIR + 'string.json', mode = 'r', encoding = 'utf8', errors = 'ignore') as f:
				dat = f.read()
		except:
			pass
		dat = dat[1:-1].split(",")
		return dat
	except:
		PrintException(u"[ERROR] 从APK中获取字符串")

def ManifestData(mfxml,app_dir):
    try:
        print "[INFO] Extracting Manifest Data"
        SVC=[]
        ACT=[]
        BRD=[]
        CNP=[]
        LIB=[]
        PERM=[]
        DP={}
        package=''
        minsdk=''
        maxsdk=''
        targetsdk=''
        mainact=''
        androidversioncode=''
        androidversionname=''
        permissions = mfxml.getElementsByTagName("uses-permission")
        manifest = mfxml.getElementsByTagName("manifest")
        activities = mfxml.getElementsByTagName("activity")
        services = mfxml.getElementsByTagName("service")
        providers = mfxml.getElementsByTagName("provider")
        receivers = mfxml.getElementsByTagName("receiver")
        libs = mfxml.getElementsByTagName("uses-library")
        sdk=mfxml.getElementsByTagName("uses-sdk")
        for node in sdk:
            minsdk=node.getAttribute("android:minSdkVersion")
            maxsdk=node.getAttribute("android:maxSdkVersion")
            targetsdk=node.getAttribute("android:targetSdkVersion")
        for node in manifest:
            package = node.getAttribute("package")
            androidversioncode=node.getAttribute("android:versionCode")
            androidversionname=node.getAttribute("android:versionName")
        for activity in activities:
            act = activity.getAttribute("android:name")
            ACT.append(act)
            if len(mainact)<1:
                # ^ Fix for Shitty Manifest with more than one MAIN
                for sitem in activity.getElementsByTagName("action"):
                    val = sitem.getAttribute("android:name")
                    if val == "android.intent.action.MAIN" :
                        mainact=activity.getAttribute("android:name")
                if mainact=='':
                    for sitem in activity.getElementsByTagName("category") :
                        val = sitem.getAttribute( "android:name" )
                        if val == "android.intent.category.LAUNCHER" :
                            mainact=activity.getAttribute("android:name")
        for service in services:
            sn = service.getAttribute("android:name")
            SVC.append(sn)

        for provider in providers:
            pn = provider.getAttribute("android:name")
            CNP.append(pn)

        for receiver in receivers:
            re = receiver.getAttribute("android:name")
            BRD.append(re)

        for lib in libs:
            l = lib.getAttribute("android:name")
            LIB.append(l)

        for permission in permissions:
            perm= permission.getAttribute("android:name")
            PERM.append(perm)

        for i in PERM:
            prm = i
            pos = i.rfind(".")
            if pos != -1 :
                prm = i[pos+1:]
                print prm
            try :
                DP[ i ] = DVM_PERMISSIONS["MANIFEST_PERMISSION"][ prm ]
            except KeyError :
                DP[ i ] = [ "unknown", "android系统未知权限", "android系统未知权限" ]
        else:
            pass
        return SVC,ACT,BRD,CNP,LIB,DP,package,mainact,minsdk,maxsdk,targetsdk,androidversioncode,androidversionname
    except:
        PrintException("[ERROR] 获取Manifest数据")

def ManifestAnalysis(mfxml,mainact):
    try:
        print "[INFO] Manifest配置文件分析开始"
        Debug = False
        Backup = False
        exp_count = dict.fromkeys(["act", "ser", "bro", "cnt"], 0)
        manifest = mfxml.getElementsByTagName("manifest")
        services = mfxml.getElementsByTagName("service")
        providers = mfxml.getElementsByTagName("provider")
        receivers = mfxml.getElementsByTagName("receiver")
        applications = mfxml.getElementsByTagName("application")
        datas = mfxml.getElementsByTagName("data")
        intents = mfxml.getElementsByTagName("intent-filter")
        actions = mfxml.getElementsByTagName("action")
        granturipermissions = mfxml.getElementsByTagName("grant-uri-permission")
        permissions = mfxml.getElementsByTagName("permission")
        for node in manifest:
            package = node.getAttribute("package")
        RET=''
        EXPORTED=[]
        PERMISSION_DICT = dict()
        ##PERMISSION
        for permission in permissions:
            if permission.getAttribute("android:protectionLevel"):
                protectionlevel = permission.getAttribute("android:protectionLevel")
                if protectionlevel == "0x00000000":
                    protectionlevel = "normal"
                elif protectionlevel == "0x00000001":
                    protectionlevel = "dangerous"
                elif protectionlevel == "0x00000002":
                    protectionlevel = "signature"
                elif protectionlevel == "0x00000003":
                    protectionlevel = "signatureOrSystem"

                PERMISSION_DICT[permission.getAttribute("android:name")] = protectionlevel
            elif permission.getAttribute("android:name"):
                PERMISSION_DICT[permission.getAttribute("android:name")] = "normal"

        ##APPLICATIONS
        for application in applications:

            if application.getAttribute("android:debuggable") == "true":
                RET=RET+ '<tr><td>APP开启可调试功能 <br>[android:debuggable=true]</td><td><span class="label label-danger">高</span></td><td>应用可调试标签被开启可导致逆向工程通过HOOK方式对应用进行源代码级调试.</td></tr>'
                Debug = True
            if application.getAttribute("android:allowBackup") == "true":
                RET=RET+ '<tr><td>APP开启了可备份功能<br>[android:allowBackup=true]</td><td><span class="label label-warning">中</span></td><td>可备份标签被打开将允许任何人通过adb备份应用数据,并允许用户通过USB调试器从设备上复制应用数据.</td></tr>'
                Backup = True
            elif application.getAttribute("android:allowBackup") == "false":
                pass
            else:
                RET=RET+ '<tr><td>App数据可被备份<br>[android:allowBackup]标签缺失,默认值为可备份.</td><td><span class="label label-warning">medium</span></td><td>[android:allowBackup]应该被设置为false.其默认值为true,将会导致应用数据可被备份,且能通过USB调试器从设备上复制应用的数据.</td></tr>'
                Backup = True
            if application.getAttribute("android:testOnly")== "true":
                RET=RET+ '<tr><td>App为测试模式 <br>[android:testOnly=true]</td><td><span class="label label-danger">high</span></td><td> 测试模式将会暴露功能性或数据以外的信息导致存在安全漏洞.</td></tr>'
            for node in application.childNodes:
                ad=''
                if node.nodeName == 'activity':
                    itmname= 'Activity'
                    cnt_id= "act"
                    ad='n'
                elif node.nodeName == 'activity-alias':
                    itmname ='Activity-Alias'
                    cnt_id= "act"
                    ad='n'
                elif node.nodeName == 'provider':
                    itmname = 'Content Provider'
                    cnt_id= "cnt"
                elif node.nodeName == 'receiver':
                    itmname = 'Broadcast Receiver'
                    cnt_id= "bro"
                elif node.nodeName == 'service':
                    itmname = 'Service'
                    cnt_id= "ser"
                else:
                    itmname = 'NIL'
                item=''
                ads = {'A':'一', 'An':'一'}
                #Task Affinity
                if ((itmname =='Activity' or itmname=='Activity-Alias') and (node.getAttribute("android:taskAffinity"))):
                    item=node.getAttribute("android:name")
                    RET=RET+ '<tr><td>Activity设置为TaskAffinity</br>('+item + ')</td><td><span class="label label-danger">high</span></td><td>如果设置Activity的taskAffinity,其他应用可读发送给属于其他任务的Activities的Intents. 总是使用默认设置根据包名保持紧密的联系,以防止敏感信息在发送或接收Intent时由另一个应用程序读取.</td></tr>'
                #LaunchMode
                if ((itmname =='Activity' or itmname=='Activity-Alias') and ((node.getAttribute("android:launchMode")=='singleInstance') or (node.getAttribute("android:launchMode")=='singleTask'))):
                    item=node.getAttribute("android:name")
                    RET=RET+ '<tr><td>Activity的启动模式 ('+item + ')不是标准的启动模式.</td><td><span class="label label-danger">高</span></td><td>一个Activity不应该设置启动模式属性为"singleTask/singleInstance",此属性将会是它成为root Activity并且可以使它被其他应用读取calling Intent的内容. 所以在Intentt中包含敏感信息时需要使用 "standard" 启动模式.</td></tr>'
                #Exported Check
                item=''
                isInf = False
                isPermExist = False
                if ('NIL' != itmname):
                    if (node.getAttribute("android:exported") == 'true'):
                        perm=''
                        item=node.getAttribute("android:name")
                        if node.getAttribute("android:permission"):
                            #permission exists
                            perm = '<strong>Permission: </strong>'+node.getAttribute("android:permission")
                            isPermExist = True
                        if item!=mainact:
                            if isPermExist:
                                prot = ""
                                if node.getAttribute("android:permission") in PERMISSION_DICT:
                                    prot = "</br><strong>protectionLevel: </strong>" + PERMISSION_DICT[node.getAttribute("android:permission")]
                                RET=RET +'<tr><td><strong>'+itmname+'</strong> (' + item + ')被专有权限保护.</br>'+perm+prot+' <br>[android:exported=true]</td><td><span class="label label-info">info</span></td><td> '+ ad + ' '+itmname+'设置为exported, 但是被其专有权限所保护.</td></tr>'
                            else:
                                if (itmname =='Activity' or itmname=='Activity-Alias'):
                                    EXPORTED.append(item)
                                print ad
                                RET=RET +'<tr><td><strong>'+itmname+'</strong> (' + item + ') 未被保护. <br>[android:exported=true]</td><td><span class="label label-danger">高</span></td><td>'+ ad + ' '+itmname+'与其他app共享,可导致被设备上其他app直接访问此组件.</td></tr>'
                                exp_count[cnt_id] = exp_count[cnt_id] + 1
                    elif (node.getAttribute("android:exported") != 'false'):
                        #Check for Implicitly Exported
                        #Logic to support intent-filter
                        intentfilters = node.childNodes
                        for i in intentfilters:
                            inf=i.nodeName
                            if inf=="intent-filter":
                                isInf=True
                        if isInf:
                            item=node.getAttribute("android:name")
                            if node.getAttribute("android:permission"):
                                #permission exists
                                perm = '<strong>Permission: </strong>'+node.getAttribute("android:permission")
                                isPermExist = True
                            if item!=mainact:
                                if isPermExist:
                                    prot = ""
                                    if node.getAttribute("android:permission") in PERMISSION_DICT:
                                        prot = "</br><strong>protectionLevel: </strong>" + PERMISSION_DICT[node.getAttribute("android:permission")]
                                    RET=RET +'<tr><td><strong>'+itmname+'</strong> (' + item + ')被专有权限保护.</br>'+perm+prot+' <br>[android:exported=true]</td><td><span class="label label-info">info</span></td><td>'+ad+' '+itmname+'设置为exported,但被其专有权限保护.</td></tr>'
                                else:
                                    if (itmname =='Activity' or itmname=='Activity-Alias'):
                                        EXPORTED.append(item)
                                    RET=RET +'<tr><td><strong>'+itmname+'</strong> (' + item + ')未被保护.<br>intent-filter被配置.</td><td><span class="label label-danger">高</span></td><td> '+ad+' '+itmname+'与其他app共享,可导致被设备上其他app直接访问此组件. 其intent-filter标明 '+itmname+' 属性为exported.</td></tr>'
                                    exp_count[cnt_id] = exp_count[cnt_id] + 1

        ##GRANT-URI-PERMISSIONS
        title = 'Improper Content Provider Permissions'
        desc = ('一个内容接收权限被设置为循序设备上其他app访问. Content providers包含关于一个应用的敏感信息时不应该被设置为shared.')
        for granturi in granturipermissions:
            if granturi.getAttribute("android:pathPrefix") == '/':
                RET=RET+ '<tr><td>' + title + '<br> [pathPrefix=/] </td>' + '<td><span class="label label-danger">high</span></td><td>'+ desc+'</td></tr>'
            elif granturi.getAttribute("android:path") == '/':
                RET=RET+ '<tr><td>' + title + '<br> [path=/] </td>' + '<td><span class="label label-danger">high</span></td><td>'+ desc+'</td></tr>'
            elif granturi.getAttribute("android:pathPattern") == '*':
                RET=RET+ '<tr><td>' + title + '<br> [path=*]</td>' + '<td><span class="label label-danger">high</span></td><td>'+ desc +'</td></tr>'

        ##DATA
        for data in datas:
            if data.getAttribute("android:scheme") == "android_secret_code":
                xmlhost = data.getAttribute("android:host")
                desc = ("在manifest中发现一个秘密的代码. 当拨号器中调用这些代码时,代码将被允许访问包含敏感信息的信息.")
                RET=RET +  '<tr><td>Dailer Code: ' + xmlhost + 'Found <br>[android:scheme="android_secret_code"]</td><td><span class="label label-danger">high</span></td><td>'+ desc + '</td></tr>'
            elif data.getAttribute("android:port"):
                dataport = data.getAttribute("android:port")
                title = "Data SMS Receiver Set"
                desc = "一个二进制的SMS接收器被配置为监听在某个端口上. 二进制SMS信息发送到设备上执行什么功能是由开发者决定的.SMS信息中的数据必须是经过应用验证的. 另外, 应用应当假定这个信息来源与一个不可信的源码."
                RET=RET+  '<tr><td> on Port: ' + dataport +  'Found<br>[android:port]</td><td><span class="label label-danger">高</span></td><td>'+ desc +'</td></tr>'

        ##INTENTS

        for intent in intents:
            if intent.getAttribute("android:priority").isdigit():
                value = intent.getAttribute("android:priority")
                if int(value) > 100:
                    RET=RET+ '<tr><td>High Intent Priority ('+ value +')<br>[android:priority]</td><td><span class="label label-warning">中</span></td><td>通过设置Intent的优先级比另一个Intent的高,此应用将会有效的复写另外的请求.</td></tr>'
        ##ACTIONS
        for action in actions:
            if action.getAttribute("android:priority").isdigit():
                value = action.getAttribute("android:priority")
                if int(value) > 100:
                    RET=RET + '<tr><td>High Action Priority (' + value+')<br>[android:priority]</td><td><span class="label label-warning">中</span></td><td>通过设置Intent的优先级比另一个Intent的高,此应用将会有效的复写另外的请求.</td></tr>'
        if len(RET)< 2:
            RET='<tr><td>None</td><td>None</td><td>None</td><tr>'
        return RET,EXPORTED,exp_count, Debug, Backup
    except:
        PrintException("[ERROR] 进行Manifest分析")

def CodeAnalysis(APP_DIR,MD5,PERMS,TYP):
    try:
        print u"[INFO] 开始静态分析Android源码"
        c = {key: [] for key in (
            'inf_act','inf_ser','inf_bro','log','fileio','rand','d_hcode','d_app_tamper',
            'dex_cert','dex_tamper','d_rootcheck','d_root','d_ssl_pin','dex_root',
            'dex_debug_key','dex_debug','dex_debug_con','dex_emulator','d_prevent_screenshot',
            'd_webviewdisablessl','d_webviewdebug','d_sensitive','d_ssl','d_sqlite',
            'd_con_world_readable','d_con_world_writable','d_con_private','d_extstorage',
            'd_tmpfile','d_jsenabled','gps','crypto','exec','server_socket','socket',
            'datagramp','datagrams','ipc','msg','webview_addjs','webview','webviewget',
            'webviewpost','httpcon','urlcon','jurl','httpsurl','nurl','httpclient',
            'notify','cellinfo','cellloc','subid','devid','softver','simserial','simop',
            'opname','contentq','refmethod','obf','gs','bencode','bdecode','dex','mdigest',
            'sqlc_password','d_sql_cipher','d_con_world_rw','ecb','rsa_no_pad','weak_iv'
            )}
        crypto=False
        obfus=False
        reflect=False
        dynamic=False
        native=False
        Log = False
        Webview = False
        EmailnFile=''
        URLnFile=''
        ALLURLSLST = list()
        DOMAINS = dict ()
        log = False
        if TYP=="apk":
            JS=os.path.join(APP_DIR, 'java_source/')
        elif TYP=="studio":
            JS=os.path.join(APP_DIR, 'app/src/main/java/')
        elif TYP=="eclipse":
            JS=os.path.join(APP_DIR, 'src/')
        print "[INFO] Code Analysis Started on - " + JS
        for dirName, subDir, files in os.walk(JS):
            for jfile in files:
                jfile_path=os.path.join(JS,dirName,jfile)
                if "+" in jfile:
                    p2=os.path.join(JS,dirName,jfile.replace("+","x"))
                    shutil.move(jfile_path,p2)
                    jfile_path=p2
                repath=dirName.replace(JS,'')
                if jfile.endswith('.java') and (any(cls in repath for cls in settings.SKIP_CLASSES) == False):
                    dat=''
                    with io.open(jfile_path,mode='r',encoding="utf8",errors="ignore") as f:
                        dat=f.read()
                    #Initialize
                    URLS=[]
                    EMAILS=[]

                    #Code Analysis
                    #print "[INFO] Doing Code Analysis on - " + jfile_path
                    #==========================Android Security Code Review =================================
                    if (re.findall('MODE_WORLD_READABLE|Context.MODE_WORLD_READABLE',dat) or re.findall('openFileOutput\(\s*".+"\s*,\s*1\s*\)',dat)):
                        c['d_con_world_readable'].append(jfile_path.replace(JS,''))
                    if (re.findall('MODE_WORLD_WRITABLE|Context.MODE_WORLD_WRITABLE',dat) or re.findall('openFileOutput\(\s*".+"\s*,\s*2\s*\)',dat)):
                        c['d_con_world_writable'].append(jfile_path.replace(JS,''))
                    if re.findall('openFileOutput\(\s*".+"\s*,\s*3\s*\)',dat):
                        c['d_con_world_rw'].append(jfile_path.replace(JS,''))
                    if (re.findall('MODE_PRIVATE|Context.MODE_PRIVATE',dat)):
                        c['d_con_private'].append(jfile_path.replace(JS,''))
                    if ((('WRITE_EXTERNAL_STORAGE') in PERMS) and (('.getExternalStorage') in dat or ('.getExternalFilesDir(') in dat)):
                        c['d_extstorage'].append(jfile_path.replace(JS,''))
                    if (('WRITE_EXTERNAL_STORAGE') in PERMS) and (('.createTempFile(') in dat):
                        c['d_tmpfile'].append(jfile_path.replace(JS,''))
                    if (('setJavaScriptEnabled(true)') in dat and ('.addJavascriptInterface(') in dat ):
                        c['d_jsenabled'].append(jfile_path.replace(JS,''))
                        Webview = True
                    if (('.setWebContentsDebuggingEnabled(true)') in dat and ('WebView') in dat ):
                        c['d_webviewdebug'].append(jfile_path.replace(JS,''))
                    if (('onReceivedSslError(WebView') in dat and ('.proceed();') in dat ):
                        c['d_webviewdisablessl'].append(jfile_path.replace(JS,''))
                    if ((('rawQuery(') in dat or ('execSQL(') in dat) and (('android.database.sqlite') in dat)):
                        c['d_sqlite'].append(jfile_path.replace(JS,''))
                    if ((('javax.net.ssl') in dat) and (('TrustAllSSLSocket-Factory') in dat or ('AllTrustSSLSocketFactory') in dat or ('NonValidatingSSLSocketFactory')  in dat or('ALLOW_ALL_HOSTNAME_VERIFIER') in dat or ('.setDefaultHostnameVerifier(') in dat or ('NullHostnameVerifier(') in dat)):
                        c['d_ssl'].append(jfile_path.replace(JS,''))
                    if (('password = "') in dat.lower() or ('secret = "') in dat.lower() or ('username = "') in dat.lower() or ('key = "') in dat.lower()):
                        c['d_sensitive'].append(jfile_path.replace(JS,''))
                    if (('import dexguard.util') in dat and ('DebugDetector.isDebuggable') in dat):
                        c['dex_debug'].append(jfile_path.replace(JS,''))
                    if (('import dexguard.util') in dat and ('DebugDetector.isDebuggerConnected') in dat):
                        c['dex_debug_con'].append(jfile_path.replace(JS,''))
                    if (('import dexguard.util') in dat and ('EmulatorDetector.isRunningInEmulator') in dat):
                        c['dex_emulator'].append(jfile_path.replace(JS,''))
                    if (('import dexguard.util') in dat and ('DebugDetector.isSignedWithDebugKey') in dat):
                        c['dex_debug_key'].append(jfile_path.replace(JS,''))
                    if (('import dexguard.util') in dat and ('RootDetector.isDeviceRooted') in dat):
                        c['dex_root'].append(jfile_path.replace(JS,''))
                    if (('import dexguard.util') in dat and ('TamperDetector.checkApk') in dat):
                        c['dex_tamper'].append(jfile_path.replace(JS,''))
                    if (('import dexguard.util') in dat and ('CertificateChecker.checkCertificate') in dat):
                        c['dex_cert'].append(jfile_path.replace(JS,''))
                    if (('org.thoughtcrime.ssl.pinning') in dat and (('PinningHelper.getPinnedHttpsURLConnection') in dat or ('PinningHelper.getPinnedHttpClient') in dat or ('PinningSSLSocketFactory(') in dat)):
                        c['d_ssl_pin'].append(jfile_path.replace(JS,''))
                    if ('PackageManager.GET_SIGNATURES' in dat) and ('getPackageName(' in dat):
                        c['d_app_tamper'].append(jfile_path.replace(JS,''))
                    if (('com.noshufou.android.su') in dat or ('com.thirdparty.superuser') in dat or ('eu.chainfire.supersu') in dat or ('com.koushikdutta.superuser') in dat or ('eu.chainfire.') in dat):
                        c['d_root'].append(jfile_path.replace(JS,''))
                    if (('.contains("test-keys")') in dat or ('/system/app/Superuser.apk') in dat or ('isDeviceRooted()') in dat or ('/system/bin/failsafe/su') in dat or ('/system/sd/xbin/su') in dat or ('"/system/xbin/which", "su"') in dat or ('RootTools.isAccessGiven()') in dat):
                        c['d_rootcheck'].append(jfile_path.replace(JS,''))
                    if (re.findall('java.util.Random',dat)):
                        c['rand'].append(jfile_path.replace(JS,''))
                    if (re.findall('Log.|System.out.print',dat)):
                        c['log'].append(jfile_path.replace(JS,''))
                        Log = True
                    if (".hashCode()" in dat):
                        c['d_hcode'].append(jfile_path.replace(JS,''))
                    if ("getWindow().setFlags(" in dat) and (".FLAG_SECURE" in dat):
                        c['d_prevent_screenshot'].append(jfile_path.replace(JS,''))
                    if ("SQLiteOpenHelper.getWritableDatabase(" in dat):
                        c['sqlc_password'].append(jfile_path.replace(JS,''))
                    if ("SQLiteDatabase.loadLibs(" in dat) and ("net.sqlcipher." in dat):
                        c['d_sql_cipher'].append(jfile_path.replace(JS,''))
                    if (re.findall('Cipher\.getInstance\(\s*"\s*AES\/ECB',dat)):
                        c['ecb'].append(jfile_path.replace(JS,''))
                    if (re.findall('ccipher\.getinstance\(\s*"rsa/.+/nopadding',dat.lower())):
                        c['rsa_no_pad'].append(jfile_path.replace(JS,''))
                    if ("0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00" in dat) or ("0x01,0x02,0x03,0x04,0x05,0x06,0x07" in dat):
                        c['weak_iv'].append(jfile_path.replace(JS,''))

                    #Inorder to Add rule to Code Analysis, add identifier to c, add rule here and define identifier description and severity the bottom of this function.
                    #=========================Android API Analysis =========================
                    #API Check

                    if (re.findall("System.loadLibrary\(|System.load\(", dat)):
                        native=True
                    if (re.findall('dalvik.system.DexClassLoader|java.security.ClassLoader|java.net.URLClassLoader|java.security.SecureClassLoader',dat)):
                        dynamic=True
                    if (re.findall('java.lang.reflect.Method|java.lang.reflect.Field|Class.forName',dat)):
                        reflect=True
                    if (re.findall('javax.crypto|kalium.crypto|bouncycastle.crypto',dat)):
                        crypto=True
                        c['crypto'].append(jfile_path.replace(JS,''))
                    if (('utils.AESObfuscator') in dat and ('getObfuscator') in dat):
                        c['obf'].append(jfile_path.replace(JS,''))
                        obfus=True

                    if (('getRuntime().exec(') in dat and ('getRuntime(') in dat):
                        c['exec'].append(jfile_path.replace(JS,''))
                    if (('ServerSocket') in dat and ('net.ServerSocket') in dat):
                        c['server_socket'].append(jfile_path.replace(JS,''))
                    if (('Socket') in dat and ('net.Socket') in dat):
                        c['socket'].append(jfile_path.replace(JS,''))
                    if (('DatagramPacket') in dat and ('net.DatagramPacket') in dat):
                        c['datagramp'].append(jfile_path.replace(JS,''))
                    if (('DatagramSocket') in dat and ('net.DatagramSocket') in dat):
                        c['datagrams'].append(jfile_path.replace(JS,''))
                    if (re.findall('IRemoteService|IRemoteService.Stub|IBinder|Intent',dat)):
                        c['ipc'].append(jfile_path.replace(JS,''))
                    if ((('sendMultipartTextMessage') in dat or  ('sendTextMessage') in dat or ('vnd.android-dir/mms-sms') in dat) and (('telephony.SmsManager') in dat)):
                        c['msg'].append(jfile_path.replace(JS,''))
                    if (('addJavascriptInterface') in dat and ('WebView') in dat and ('android.webkit') in dat):
                        c['webview_addjs'].append(jfile_path.replace(JS,''))
                        Webview = True
                    if (('WebView') in dat and ('loadData') in dat and ('android.webkit') in dat):
                        c['webviewget'].append(jfile_path.replace(JS,''))
                    if (('WebView') in dat and ('postUrl') in dat and ('android.webkit') in dat):
                        c['webviewpost'].append(jfile_path.replace(JS,''))
                    if ((('HttpURLConnection') in dat or ('org.apache.http') in dat) and (('openConnection') in dat or ('connect') in dat or ('HttpRequest') in dat)):
                        c['httpcon'].append(jfile_path.replace(JS,''))
                    if ((('net.URLConnection') in dat) and (('connect') in dat or ('openConnection') in dat or ('openStream') in dat)):
                        c['urlcon'].append(jfile_path.replace(JS,''))
                    if ((('net.JarURLConnection') in dat) and (('JarURLConnection') in dat or ('jar:') in dat)):
                        c['jurl'].append(jfile_path.replace(JS,''))
                    if ((('javax.net.ssl.HttpsURLConnection') in dat)and (('HttpsURLConnection') in dat or ('connect') in dat)):
                        c['httpsurl'].append(jfile_path.replace(JS,''))
                    if (('net.URL') and ('openConnection' or 'openStream')) in dat:
                        c['nurl'].append(jfile_path.replace(JS,''))
                    if (re.findall('http.client.HttpClient|net.http.AndroidHttpClient|http.impl.client.AbstractHttpClient',dat)):
                        c['httpclient'].append(jfile_path.replace(JS,''))
                    if (('app.NotificationManager') in dat and ('notify') in dat):
                        c['notify'].append(jfile_path.replace(JS,''))
                    if (('telephony.TelephonyManager') in dat and ('getAllCellInfo') in dat):
                        c['cellinfo'].append(jfile_path.replace(JS,''))
                    if (('telephony.TelephonyManager') in dat and ('getCellLocation') in dat):
                        c['cellloc'].append(jfile_path.replace(JS,''))
                    if (('telephony.TelephonyManager') in dat and ('getSubscriberId') in dat):
                        c['subid'].append(jfile_path.replace(JS,''))
                    if (('telephony.TelephonyManager') in dat and ('getDeviceId') in dat):
                        c['devid'].append(jfile_path.replace(JS,''))
                    if (('telephony.TelephonyManager') in dat and ('getDeviceSoftwareVersion') in dat):
                        c['softver'].append(jfile_path.replace(JS,''))
                    if (('telephony.TelephonyManager') in dat and ('getSimSerialNumber') in dat):
                        c['simserial'].append(jfile_path.replace(JS,''))
                    if (('telephony.TelephonyManager') in dat and ('getSimOperator') in dat):
                        c['simop'].append(jfile_path.replace(JS,''))
                    if (('telephony.TelephonyManager') in dat and ('getSimOperatorName') in dat):
                        c['opname'].append(jfile_path.replace(JS,''))
                    if (('content.ContentResolver') in dat and ('query') in dat):
                        c['contentq'].append(jfile_path.replace(JS,''))
                    if (('java.lang.reflect.Method') in dat and ('invoke') in dat):
                        c['refmethod'].append(jfile_path.replace(JS,''))
                    if (('getSystemService') in dat):
                        c['gs'].append(jfile_path.replace(JS,''))
                    if ((('android.util.Base64') in dat) and (('.encodeToString') in dat or ('.encode') in dat)):
                        c['bencode'].append(jfile_path.replace(JS,''))
                    if (('android.util.Base64') in dat and ('.decode') in dat):
                        c['bdecode'].append(jfile_path.replace(JS,''))
                    if ((('dalvik.system.PathClassLoader') in dat or ('dalvik.system.DexFile') in dat or ('dalvik.system.DexPathList') in dat or ('dalvik.system.DexClassLoader') in dat) and (('loadDex') in dat or ('loadClass') in dat or ('DexClassLoader') in dat or ('loadDexFile') in dat)):
                        c['dex'].append(jfile_path.replace(JS,''))
                    if ((('java.security.MessageDigest') in dat) and (('MessageDigestSpi') in dat or ('MessageDigest') in dat)):
                        c['mdigest'].append(jfile_path.replace(JS,''))
                    if ((('android.location') in dat )and (('getLastKnownLocation(') in dat or ('requestLocationUpdates(') in dat or ('getLatitude(') in dat or ('getLongitude(') in dat)):
                        c['gps'].append(jfile_path.replace(JS,''))
                    if (re.findall('OpenFileOutput|getSharedPreferences|SharedPreferences.Editor|getCacheDir|getExternalStorageState|openOrCreateDatabase',dat)):
                        c['fileio'].append(jfile_path.replace(JS,''))
                    if (re.findall('startActivity\(|startActivityForResult\(',dat)):
                        c['inf_act'].append(jfile_path.replace(JS,''))
                    if (re.findall('startService\(|bindService\(',dat)):
                        c['inf_ser'].append(jfile_path.replace(JS,''))
                    if (re.findall('sendBroadcast\(|sendOrderedBroadcast\(|sendStickyBroadcast\(',dat)):
                        c['inf_bro'].append(jfile_path.replace(JS,''))

                    fl=jfile_path.replace(JS,'')
                    base_fl=ntpath.basename(fl)

                    #URLs My Custom regex
                    p = re.compile(ur'((?:https?://|s?ftps?://|file://|javascript:|data:|www\d{0,3}[.])[\w().=/;,#:@?&~*+!$%\'{}-]+)', re.UNICODE)
                    urllist=re.findall(p, dat.lower())
                    ALLURLSLST.extend(urllist)
                    uflag=0
                    for url in urllist:
                        if url not in URLS:
                            URLS.append(url)
                            uflag=1
                    if uflag==1:
                        URLnFile+="<tr><td>" + "<br>".join(URLS) + "</td><td><a " + 'target="_blank"' + " href='../ViewSource/?file=" + escape(fl)+"&md5="+MD5+"&type="+TYP+"'>"+escape(base_fl)+"</a></td></tr>"

                    #Email Etraction Regex

                    regex = re.compile("[\w.-]+@[\w-]+\.[\w.]+")
                    eflag=0
                    for email in regex.findall(dat.lower()):
                        if ((email not in EMAILS) and (not email.startswith('//'))):
                            EMAILS.append(email)
                            eflag=1
                    if eflag==1:
                        EmailnFile+="<tr><td>" + "<br>".join(EMAILS) + "</td><td><a " + 'target="_blank"' + " href='../ViewSource/?file=" + escape(fl)+"&md5="+MD5+"&type="+TYP+"'>"+escape(base_fl)+"</a></td></tr>"

        #Domain Extraction and Malware Check
        print "[INFO] 开始进行恶意文件检测和获取domain"
        DOMAINS = MalwareCheck(ALLURLSLST)
        print "[INFO] 完成代码分析, 获取Email和URL"
        #API Description
        dc ={'gps':u'GPS定位',
            'crypto':u'加密API',
            'exec': u'执行系统命令 ',
            'server_socket':u'TCP服务器Socket ' ,
            'socket': u'TCP Socket ',
            'datagramp': u'UDP数据包 ',
            'datagrams': u'UDP数据包Socket ',
            'ipc': u'进程间通信 ',
            'msg': u'发送SMS ',
            'webview_addjs':u'WebView JavaScript Interface(webview漏洞) ',
            'webview': u'WebView加载HTML/JavaScript ',
            'webviewget': u'WebView GET Request ',
            'webviewpost': u'WebView POST Request ',
            'httpcon': u'HTTP连接',
            'urlcon':u'URL连接到file/http/https/ftp/jar ',
            'jurl':u'JAR URL连接 ',
            'httpsurl':u'HTTPS连接 ',
            'nurl':u'URL连接,支持 file,http,https,ftp and jar ',
            'httpclient':u'HTTP Requests, Connections和Sessions ',
            'notify': u'Android通知 ',
            'cellinfo':u'获取蜂窝通信信息 ',
            'cellloc':u'获取蜂窝通信地址 ',
            'subid':u'获取订阅者ID ',
            'devid':u'获取设备 ID, IMEI,MEID/ESN等. ',
            'softver':u'获取软件 Version, IMEI/SV etc. ',
            'simserial': u'获取SIM序列号 ',
            'simop': u'获取SIM卡提供者信息 ',
            'opname':u'获取SIM运营商信息',
            'contentq':u'查询SMS数据库, Contacts数据库等. ',
            'refmethod':u'Java反射方法调用 ',
            'obf': u'混淆 ',
            'gs':u'获取System Service ',
            'bencode':u'Base64编码 ',
            'bdecode':u'Base64解码 ',
            'dex':u'加载和操作Dex文件 ',
            'mdigest': u'消息摘要 ',
            'fileio': u'本地File I/O操作',
            'inf_act': u'启动Activity',
            'inf_ser': u'启动Service',
            'inf_bro': u'发送Broadcast'
            }
        html=''
        for ky in dc:
            if c[ky]:
                link=''
                hd="<tr><td>"+dc[ky]+"</td><td>"
                for l in c[ky]:
                    link+="<a "+'target="_blank"' + " href='../ViewSource/?file="+ escape(l) +"&md5="+MD5+"&type="+TYP+"'>"+escape(ntpath.basename(l))+"</a> "
                html+=hd+link+"</td></tr>"

        #Security Code Review Description
        dg={'d_sensitive' : u"文件包含硬编码敏感信息,例如usernames, passwords, 加密解密keys 等.",
            'd_ssl': u'不安全的SSL传输. 信任所有证书或者接受自签名证书是一个严重的安全漏洞. 应用可被中间人攻击',
            'd_sqlite': u'应用使用SQLite数据库并执行原始SQL查询. 恶意的用户输入可导致sql注入攻击. 且敏感信息需要加密后存储到数据库中.',
            'd_con_world_readable':u'文件全局可读. 任何应用都能从文件中读取数据',
            'd_con_world_writable':u'文件全局可写. 任何应用都能向文件中写数据',
            'd_con_world_rw': u'文件全局可读写. 任何应用都能向文件中读写数据',
            'd_con_private':u'应用可向应用目录写数据. 敏感信息应该被加密后存储.',
            'd_extstorage': u'应用可向外部存储器读写数据. 任何应用都能向外部存储器读写数据.',
            'd_tmpfile': u'应用可创建临时文件. 敏感信息不能写入到临时文件中.',
            'd_jsenabled':u'不安全的WebView实现. 在webview中执行用户可控的代码是严重的安全漏洞.',
            'd_webviewdisablessl':u'不安全的WebView实现. WebView忽略SSL证书错误并且接受任何SSL证书. 应用可被中间攻击',
            'd_webviewdebug':u'允许远程WebView调试.',
            'dex_debug': u'DexGuard检测应用是否可被调试检测代码可被识别.',
            'dex_debug_con':u'DexGuard调试器检测代码可被识别.',
            'dex_debug_key':u'DecGuard检测应用使用调试证书发布代码可被识别.',
            'dex_emulator': u'DexGuard模拟器检测代码可被识别.',
            'dex_root': u'DexGuard Root检测代码可被识别.',
            'dex_tamper' : u'DexGuard 应用被篡改检测代码可被识别.',
            'dex_cert' : u'DexGuard 签名证书被篡改监测代码可被识别.',
            'd_ssl_pin': u' 应用使用SSL Pinning 库(org.thoughtcrime.ssl.pinning)实现在安全信道防止中间人攻击.',
            'd_root' : u'T应用请求root (Super User)权限.',
            'd_rootcheck' : u'应用可检测设备是否root.',
            'd_hcode' : u'应用使用Java Hash Code. 安全的加密实现中不该使用如此弱的哈希函数.',
            'rand' : u'应用使用不安全的随机数生成器.',
            'log' : u'应用启用日志记录功能. 敏感信息不该在日志中出现.',
            'd_app_tamper' : u'应用使用包签名防篡改.',
            'd_prevent_screenshot' :u'应用防截屏.',
            'd_sql_cipher' : u'应用使用SQL Cipher. SQLCipher为sqlite数据库文件提供 256-bit AES加密.',
            'sqlc_password' : u'T应用使用SQL Cipher. 但可能硬编码密码等信息.',
            'ecb' : u'应用在Cryptographic encryption算法中使用ECB模式. 但ECB模式是脆弱的，因为它会导致明文出现相同的密文块.',
            'rsa_no_pad' : u'应用使用没有OAEP padding的RSA加密算法. 填充的目的是为了防止一些针对在加密是未使用填充的RSA加密的攻击',
            'weak_iv' : u'应用使用较弱的IVs,如"0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00" 或者 "0x01,0x02,0x03,0x04,0x05,0x06,0x07". 没使用随机IV将会导致密文可被字典暴力破解攻击.',
            }



        dang=''
        spn_dang='<span class="label label-danger">high</span>'
        spn_info='<span class="label label-info">info</span>'
        spn_sec='<span class="label label-success">secure</span>'
        spn_warn='<span class="label label-warning">warning</span>'

        for k in dg:
            if c[k]:
                link=''
                if (re.findall('d_con_private|log',k)):
                    hd='<tr><td>'+dg[k]+'</td><td>'+spn_info+'</td><td>'
                elif (re.findall('d_sql_cipher|d_prevent_screenshot|d_app_tamper|d_rootcheck|dex_cert|dex_tamper|dex_debug|dex_debug_con|dex_debug_key|dex_emulator|dex_root|d_ssl_pin',k)):
                    hd='<tr><td>'+dg[k]+'</td><td>'+spn_sec+'</td><td>'
                elif (re.findall('d_jsenabled',k)):
                    hd='<tr><td>'+dg[k]+'</td><td>'+spn_warn+'</td><td>'
                else:
                    hd='<tr><td>'+dg[k]+'</td><td>'+spn_dang+'</td><td>'

                for ll in c[k]:
                    link+="<a "+ 'target="_blank"' + " href='../ViewSource/?file="+ escape(ll) +"&md5="+MD5+"&type="+TYP+"'>"+escape(ntpath.basename(ll))+"</a> "

                dang+=hd+link+"</td></tr>"

        return html,dang,URLnFile,DOMAINS,EmailnFile,crypto,obfus,reflect,dynamic,native,Log,Webview
    except:
        PrintException("[ERROR] Performing Code Analysis")

