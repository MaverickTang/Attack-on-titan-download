# -*- coding: utf-8 -*-
import scrapy
import re
import os
import urllib
import zlib
import time
import requests
from urllib.request import urlretrieve

class TitanSpider(scrapy.Spider):
	name = "titan"
	
	
	
	start_urls = ['https://manhua.fzdm.com/39/']#想下载其他动漫的话就改这个url，下面的base处也要改
	
	
	
	
	allowed_domains = ['https://manhua.fzdm.com','http://p2.manhuapan.com/']

	def parse(self, response):
		link_urls = response.xpath('//li/a[1]/@href').extract()
		names = response.xpath('//li/a[1]/@title').extract()
		x=-1
		h=0
		comics_url_list = []
		rnames = []
		
		#想下载其他动漫的话改url，再往下有个保存的地址也要改
		base = 'https://manhua.fzdm.com/39/'
		
		
		
		
		for i in range(len(link_urls)):
			h=bool(re.search(r'\d', link_urls[i]))
			if(h==True):
				x=x+1
				name=names[x]
				url=base + link_urls[i]
				rnames.append(name)
				comics_url_list.append(url)
#				print("%s :https://www.manhuadui.com %s"%(names[4+x],link_urls[i]))
#				print("%s : %s"%(rnames[x],comics_url_list[x]))	
				
		print('\n>>>>>>>>>>>>>>>>>>> current page comics list <<<<<<<<<<<<<<<<<<<<')
		print(comics_url_list)
		
		for url in comics_url_list:
			dont_filter=True
			yield scrapy.Request(url=url, callback=self.comics_parse, dont_filter=True)
			print('>>>>>>>>  parse comics:' + url)
	
	def is_all_chinese(strs):	
		for _char in strs:
			if not '\u4e00' <= _char <= '\u9fa5':
				return False
		return True	
		
	#检验是否含有中文字符
	def is_contains_chinese(strs):
		for _char in strs:
			if '\u4e00' <= _char <= '\u9fa5':
				return True
		return False
				
	def comics_parse(self, response):
		pre_img_url = response.xpath('//script/text()').extract()
		img_url = ''
		ptitle=response.xpath('//title/text()').extract()
		prepage_num=response.xpath('//a[contains(@href, "index")]/text()').extract()
		page_num=''
		a=0
		for j in range(1,len(prepage_num)):
			for _char in prepage_num[j]:
#				print(_char)
				if '\u4e00' <= _char <= '\u9fa5':
					page_num=prepage_num[j]
					if page_num == '下一页':
						page_num='第1页'
#					print("%s",page_num)
					a=1
					break
			if(a==1):
				break	 
		t=ptitle[0]
		index=ptitle[0].find('话')
		title=t[0:(index+1)]
#		matchObj = re.search( r'url=\"()\s*(.*)jpg', line, re.M|re.I)
		for i in range(len(pre_img_url)):
			matchObj = re.search( r'url=\"()\s*(.*)jpg', pre_img_url[i], re.M|re.I)
			if matchObj:
				ppreimgurl = matchObj.group()
				img_url= 'http://p2.manhuapan.com/' + ppreimgurl[5:len(ppreimgurl)]
				self.log('>>>>>>>>>>>开始下载<<<<<<<<<<<<<')
#				self.save_img(page_num[len(page_num)], title, img_url)
				
				
				#保存地址记得改！！！！
				document = '/Users/maverick/Desktop/test/One punch'
				
				
				
				
				comics_path = document + '/' + title
				exists = os.path.exists(comics_path)
				if not exists:
#					self.log('create document: ' + title)
					os.makedirs(comics_path)
				pic_name = comics_path + '/' + page_num + '.jpg'
				exists = os.path.exists(pic_name)
				if not exists:
					time.sleep(0.1)#防止锁ip
					urlretrieve(img_url, pic_name)
				break		
		pages_urls = response.xpath('//a[contains(@href, "index")]/@href').extract()
		page_situation = response.xpath('//a[contains(@href, "index")]/text()').extract()
		ans=0
		for _char in page_situation[len(page_situation)-1]:
			if not '\u4e00' <= _char <= '\u9fa5':
				ans=1
		if(ans==0):
			premyfront = response.request.url
			fenge = premyfront.split('/')
			myfont=''
			for i in range(5):
				myfont=myfont+fenge[i]+'/'
			next_page = myfont+pages_urls[len(pages_urls)-1]
			self.log(next_page)
			yield scrapy.Request(next_page, callback=self.comics_parse, dont_filter=True)		
		else:
			self.log('parse comics:' + title + 'finished.')	
			
#	def save_img(self, img_num, title, img_url):
#		self.log('saving pic: ' + img_url)
#		document = '/Users/maverick/Desktop/test/Attack on titan'
#		comics_path = document + '/' + title
#		exists = os.path.exists(comics_path)
#		if not exists:
#			self.log('create document: ' + title)
#			os.makedirs(comics_path)
#		pic_name = comics_path + '/' + img_mun + '.jpg'
#		exists = os.path.exists(pic_name)
#		if exists:
#			self.log('pic exists: ' + pic_name)
#			return
#		time.sleep(1)#防止锁ip
#		urlretrieve(img_url, pic_name)
		
		
		
		
#	def save_img(self, img_mun, title, img_url):
#			# 将图片保存到本地
#			self.log('saving pic: ' + img_url)
#
#			# 保存漫画的文件夹
#			document = '/Users/maverick/Desktop/test/Attack on titan'
#
#			# 每部漫画的文件名以标题命名
#			comics_path = document + '/' + title
#			exists = os.path.exists(comics_path)
#			if not exists:
#				self.log('create document: ' + title)
#				os.makedirs(comics_path)
#
#			# 每张图片以页数命名
#			pic_name = comics_path + '/' + img_mun + '.jpg'
#
#			# 检查图片是否已经下载到本地，若存在则不再重新下载
#			exists = os.path.exists(pic_name)
#			if exists:
#				self.log('pic exists: ' + pic_name)
#				return
#
#			try:
#				user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
#				headers = { 'User-Agent' : user_agent }
#
#				req = urllib.request.Request(img_url, headers=headers)
#				response = urllib.request.urlopen(req, timeout=30)
#
#				# 请求返回到的数据
#				data = response.read()
#
#				# 若返回数据为压缩数据需要先进行解压
#				if response.info().get('Content-Encoding') == 'gzip':
#					data = zlib.decompress(data, 16 + zlib.MAX_WBITS)
#
#				# 图片保存到本地
#				fp = open(pic_name, "wb")
#				fp.write(data)
#				fp.close
#
#				self.log('save image finished:' + pic_name)
#
#				# urllib.request.urlretrieve(img_url, pic_name)
#			except Exception as e:
#				self.log('save image error.')
#				self.log(e)