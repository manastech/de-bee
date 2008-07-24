from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from model import *
import cgi
import os
import registration as registration
import re

class UrlBuilder:
	def __init__(self, webrequest):
		p = re.compile("[^:]*://[^/]*")
		m = p.match(webrequest.url)
		self.baseUrl = m.group()

	# without trailing /
	def getBaseUrl(self):
		return self.baseUrl
	
	def buildUrl(self, url):
		if url[0] != '/':
			url = "/%s" % url
		return "%s%s" % (self.getBaseUrl(), url)
	