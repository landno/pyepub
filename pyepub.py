import zipfile
import imghdr
import os
import urllib2
from bs4 import BeautifulSoup

HTML = '''<?xml version="1.0" encoding="utf-8" standalone="no"?>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh-CN">
	<head>
		<link href="../stylesheet.css" rel="stylesheet" type="text/css" />
		<title>%s</title>
	</head>
	<body>
		<div id="title"><h2>%s</h2></div>
		<hr />
		<div id="content">%s</div>
	</body>
</html>'''

CSS = '''body {line-height: 1.7;}
.content {margin: 1em;}'''

META = '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
	<rootfiles>
		<rootfile full-path="Content.opf" media-type="application/oebps-package+xml" />
	</rootfiles>
</container>'''

OPF = '''<?xml version='1.0' encoding='utf-8'?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookID" version="2.0">
	<metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
		<dc:title>%(title)s</dc:title>
		<dc:creator>landno.com</dc:creator>
		<dc:identifier id="BookID" opf:scheme="UUID">urn:uuid:Date2014-02-12</dc:identifier>
		<dc:language>zh-CN</dc:language>
		<dc:publisher>landno.com</dc:publisher>
		<meta name="cover" content="cover-image" />
	</metadata>
	<manifest>
		<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml" />
		<item id="cover-image" href="Images/cover.jpg" media-type="image/jpeg"/>
		<item id="css" href="stylesheet.css" media-type="text/css"/>
		%(manifest)s
	</manifest>
	<spine toc="ncx">
		%(spine)s
	</spine>
</package>'''

NCX = '''<?xml version='1.0' encoding='utf-8'?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
	<head>
		<meta name="dtb:uid" content="urn:uuid:Date2014-02-12"/>
		<meta name="dtb:depth" content="1"/>
		<meta name="dtb:totalPageCount" content="0"/>
		<meta name="dtb:maxPageNumber" content="0"/>
	</head>
	<docTitle>
		<text>%(title)s</text>
	</docTitle>
	<navMap>
		%(navPoint)s
	</navMap>
</ncx>'''

NAV = '<navPoint id="navpoint-%(order)s" playOrder="%(order)s"><navLabel><text>%(title)s</text></navLabel><content src="Text/%(filename)s"/></navPoint>'



class pyEpub():
	def __init__(self, title):
		self.title = title
		self.filename = title + '.epub'

		if os.path.exists(self.filename):
			print '%s-file exists' % (self.filename)
			exit()
		
		self.epub = zipfile.ZipFile(self.filename, 'w')
		self.epub.writestr('mimetype', 'application/epub+zip')
		self.epub.writestr('stylesheet.css', CSS)
		self.epub.writestr('META-INF/container.xml', META)

		self.manifest = []
		self.spine = []
		self.navpoint = []

		self.pageIndex = 1
		self.imageIndex = 1


	def addPage(self, title, content):
		html = HTML % (title, title, content)
		fileName = 't'+str(self.pageIndex)+'.html'
		self.epub.writestr('Text/'+fileName, html)
		self.spine.append('<itemref idref="%s" />' % fileName)
		self.manifest.append('<item id="%(fileName)s" href="Text/%(fileName)s" media-type="application/xhtml+xml"/>' % {'fileName': fileName})
		self.navpoint.append(NAV % {
				'order' : self.pageIndex, \
				'title' : title, \
				'filename' : fileName, \
				})
		self.pageIndex += 1
		return '../Text/'+fileName

	def addImagePage(self, title, content):
		soup = BeautifulSoup(content)
		for item in soup.find_all('img'):
			print 'downloading-%s' % item['src']
			img = urllib2.urlopen(item['src']).read()	
			item['src'] = self.addImage(img)

		self.addPage(title, soup.body.contents[0])
		self.save()

	def addImage(self, img):
		fp = open('com.pyepub.temp', 'w')
		fp.write(img)
		fp.close()
		if imghdr.what('com.pyepub.temp'):
			img_type = imghdr.what('com.pyepub.temp')
		else:
			img_type = 'jpeg'
		os.remove('com.pyepub.temp')
		fileName = 'i'+str(self.imageIndex)+'.'+img_type
		self.epub.writestr('Images/' + fileName, img)
		self.manifest.append('<item id="%(fileName)s" href="Images/%(fileName)s" media-type="image/%(type)s"/>' % {'fileName': fileName, 'type': img_type})
		self.imageIndex += 1
		return '../Images/'+fileName

	def save(self):
		ooppff = OPF % {'title':self.title.decode('utf-8'),'manifest': "\n".join(self.manifest),'spine': "\n".join(self.spine),}
		nnccxx = NCX % {'title':self.title,'navPoint': "\n".join(self.navpoint),}
		self.epub.writestr('Content.opf', ooppff.encode('utf-8')) 
		self.epub.writestr('toc.ncx', nnccxx)