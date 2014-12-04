pyepub
======
使用说明
方法1.
epub = pyEpub("文档标题")
epub.addPage("章节标题", "<div>内容html</div>")
epub.save()
#无图片

方法2.
epub = pyEpub("文档标题")
epub.addImagePage("章节标题", "<div>内容html</div>")
# addImagePage会自动查找 -内容html- 中的img标签中的图片，并下载。

方法3.
content = '<div>balabala...<img src="http//www.landno.com/pyepub.png" />balabala...</div>'
epub = pyEpub("文档标题")
img = urllib2.urlopen("http//www.landno.com/pyepub.png").read()
src = epub.addImage(img)
content = content.replace('http//www.landno.com/pyepub.png', src)
epub.addPage("章节标题", content)
epub.save()
