#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################

import indigo

import os
import sys
import datetime
import time
import requests
import shutil
from PIL import Image

DEFAULT_UPDATE_FREQUENCY = 24 # frequency of update check

################################################################################
class Plugin(indigo.PluginBase):
	########################################
	def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
		super(Plugin, self).__init__(pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
		self.debug = pluginPrefs.get("debug", False)
		self.securityspy_ip = pluginPrefs.get("ip", None)
		self.securityspy_port = pluginPrefs.get("port", None)
		self.securityspy_login = pluginPrefs.get("login", None)
		self.securityspy_pass = pluginPrefs.get("password", None)

		self.updateURL()


	########################################
	def startup(self):
		self.debugLog(u"startup called")

	def checkForUpdates(self):
		self.updater.checkForUpdate()

	def updateURL(self):
		self.configured = (self.securityspy_ip is not None) and (self.securityspy_port  is not None)

		if self.configured:
			if self.securityspy_login is not None:
				self.securityspy_url = "http://" + self.securityspy_login + ":" + self.securityspy_pass + "@" +  self.securityspy_ip + ":" + self.securityspy_port
			else:
				self.securityspy_url = "http://" + self.securityspy_ip + ":" + self.securityspy_port

	def closedPrefsConfigUi(self, valuesDict, userCancelled):
		if not userCancelled:
			self.debug = valuesDict["debug"]
			self.securityspy_ip = valuesDict["ip"]
			self.securityspy_port = valuesDict["port"]
			self.securityspy_login = valuesDict["login"]
			self.securityspy_pass = valuesDict["password"]

			self.updateURL()


	def updatePlugin(self):
		self.updater.update()

	def shutdown(self):
		self.debugLog(u"shutdown called")

	# helper functions
	def prepareTextValue(self, strInput):

		if strInput is None:
			return strInput
		else:
			strInput = strInput.strip()

			strInput = self.substitute(strInput)

			#fix issue with special characters
			strInput = strInput.encode('utf8')

			return strInput

	def getImage(self, url, save):
		self.debugLog("getting image: " + url + " and saving it to: " + save)

		try:
			r = requests.get(url, stream=True)

			if r.status_code == 200:
				with open(save, 'wb') as f:
					r.raw.decode_content = True
					shutil.copyfileobj(r.raw, f)

			del r
			return True
		except:
			self.debugLog("error getting image.")
			return False

	def stitchImages(self, images):
		result_height = 0
		result_width = 0
		for image in images:
			(width, height) = image.size

			result_height = result_height + height

			if width > result_width:
				result_width = width

		result = Image.new('RGB', (result_width, result_height))

		curHeight = 0
		for image in images:
			(width, height) = image.size
			result.paste(im=image, box=(0, curHeight))
			curHeight = curHeight + height

		return result

	def stitchImageAction(self, pluginAction, dev):
		if not self.configured:
			return False

		destinationFile = self.prepareTextValue(pluginAction.props["destination"])

		if not os.path.exists(os.path.dirname(destinationFile)):
			self.debugLog("path does not exist: " + os.path.dirname(destinationFile))
			return False

		tempDirectory = os.path.dirname(destinationFile)
		images = []

		image1_url = self.securityspy_url + "/++image?cameraNum=" + pluginAction.props["cam1"]
		image1_file = tempDirectory + "/temp1.jpg"
		if not self.getImage(image1_url, image1_file):
			self.debugLog("error stiching files, aborted")
			return
		images.append(Image.open(image1_file))

		image2_url = None
		image3_url = None
		image4_url = None

		if pluginAction.props["cam2"] != "-1":
			image2_url = self.securityspy_url + "/++image?cameraNum=" + pluginAction.props["cam2"]
			image2_file = tempDirectory + "/temp2.jpg"
			if not self.getImage(image2_url, image2_file):
				self.debugLog("error stiching files, aborted")
				return
			images.append(Image.open(image2_file))

		if pluginAction.props["cam3"] != "-1":
			image3_url = self.securityspy_url + "/++image?cameraNum=" + pluginAction.props["cam3"]
			image3_file = tempDirectory + "/temp3.jpg"
			self.getImage(image3_url, image3_file)
			images.append(Image.open(image3_file))

		if pluginAction.props["cam4"] != "-1":
			image4_url = self.securityspy_url + "/++image?cameraNum=" + pluginAction.props["cam4"]
			image4_file = tempDirectory + "/temp4.jpg"
			if not self.getImage(image4_url, image4_file):
				self.debugLog("error stiching files, aborted")
				return				
			images.append(Image.open(image4_file))

		result = self.stitchImages(images)
		result.save(destinationFile)

		os.remove(image1_file)

		if image2_url != None:
			os.remove(image2_file)

		if image3_url != None:
			os.remove(image3_file)

		if image4_url != None:
			os.remove(image4_file)

	def downloadImage(self, pluginAction, dev):
		if not self.configured:
			return False

		destinationFile = self.prepareTextValue(pluginAction.props["destination"])

		if not os.path.exists(os.path.dirname(destinationFile)):
			self.debugLog("path does not exist: " + os.path.dirname(destinationFile))
			return False

		if pluginAction.props["type"] == "securityspy":
			image1_url = self.securityspy_url + "/++image?cameraNum=" + pluginAction.props["cam1"]

			self.getImage(image1_url, destinationFile)