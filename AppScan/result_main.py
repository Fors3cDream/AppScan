# coding=utf-8

from SaveResult import SaveResult
import os
import time
import hashlib
import utils
from pyfiglet import Figlet
from MatchRule import MatchRule
from AnalysisXMLS.ManifestParser import GetManifestBasicInfo


class GetApkInfo():
	def __init__(self):
		self.apk_info = {}
		self.webview = {}
		self.logdict = {}
		self.allowallhostnameverifier = {}
		self.onreceivedsslerror = {}
		self.dexclassloader = {}
		self.dexclassloader = {}
		self.https = {}


	def getSha1AndMD5(self, filepath):
		apk = open(filepath, 'rb').read()
		sha1_obj = hashlib.sha1()
		sha1_obj.update(apk)
		sha1 = sha1_obj.hexdigest()

		md5_obj = hashlib.md5()
		md5_obj.update(apk)
		md5 = md5_obj.hexdigest()
		return (sha1, md5)

	def getApkDetailInfo(self, apk_info, apk):
		basicInfo = GetManifestBasicInfo(apk)
		apk_info_list = apk_info.readlines()
		apk_info_dict = {}
		pacakge = ''

		for line in apk_info_list:
			if ('application-label' not in line) and ('versionCode' not in line):
				continue
			if 'versioncode' in line:
				package = line.strip().split('\'')[1]
				apk_info_dict['versionCode'] = line.strip.split("'")[3]
				apkt_info_dict['versionName'] = line.strip.split("'")[5]

				# 检测是否获取所有信息
				if apk_info_dict.has_key('application'):
					break
				continue

			if 'application-label' in line:
				apk_info_dict['application'] = line.split('\'')[1]

				if apk_info_dict.has_key('application'):
					break 
				continue

			apk_info_dict['apk'] = apk.split('\\')[-1]
			apk_sha1_md5 = self.getSha1AndMD5(apk)
			
