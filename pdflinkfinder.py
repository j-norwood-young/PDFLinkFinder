"""
This class finds PDF links. Useful for making a digital publication.
It relies on pyPdf
http://pybrary.net/pyPdf/

Copyright 2011 10Layer Software Development Pty (Ltd)
http://10layer.com

Licensed under the MIT license
http://www.opensource.org/licenses/mit-license.php

Example of use:

import pdflinkfinder
import cjson
import sys

filename=sys.argv
pdf=pdflinkfinder.PdfLinkFinder(filename[1])
if (pdf.hasExternalLinks()):
	links=pdf.findExternalLinks()
print cjson.encode(links)

Example of result (Three pages, an internal link on the first to the second page, and an external link on the third):
[[{"dest": 1, "pg": 0, "rect": [34, 362, 380, 34], "external": false}], false, [{"dest": "http://www.10layer.com", "pg": 2, "rect": [82, 929, 686, 610], "external": true}]]
"""
__version__="0.2a"
__author__="Jason Norwood-Young"
__license__="MIT"
import pyPdf

class PdfLinkFinder:
	""" 
	Finds PDF links, and returns the target and rectangular position. Works for internal and URI links at this point.
	"""

	def __init__(self,filename):
		self.filename=filename
		self.pdf=pyPdf.PdfFileReader(file(self.filename, "rb"))
		self.numPages=self.pdf.getNumPages()

	def _hasExternalLinks(self, pgnum):
		""" 
		Internal function for detecting whether a page has links
		"""
		pg = self.pdf.getPage(pgnum)
		if (pg.has_key("/Annots")==False):
			return False
		for annot in pg["/Annots"]:
			annotobj = annot.getObject()
			if annotobj['/Subtype'] in ('/Link') or annotobj.has_key('/URI'):
				return True
		return False

	def hasExternalLinks(self):
		""" Returns True if PDF contains external links
		"""
		for pgnum in range(0, self.numPages):
			if self._hasExternalLinks(pgnum):
				return True
		return False
    
	def _findExternalLinks(self, pgnum):
		pg = self.pdf.getPage(pgnum)
		if (pg.has_key("/Annots")==False):
			return False
		result=[]
		for annot in pg["/Annots"]:
			annotobj = annot.getObject()
			if annotobj['/Subtype'] in ('/Link') or annot.has_key('/URI'):
				external=True
				obj=annotobj['/A'].getObject()
				dest=""
				if (obj.has_key('/D')):
					external=False
					namedDests=self.pdf.getNamedDestinations()
					dest=namedDests[obj['/D']]['/Page'].getObject()
					for tmppgnum in range(0, self.numPages):
						if (dest==self.pdf.flattenedPages[tmppgnum]):
							dest=tmppgnum
				if (obj.has_key('/URI')):
					dest=obj['/URI']
				rect=annotobj['/Rect']
				newrect=[]
				for point in rect:
					newrect.append(int(point))
				link={"rect":newrect, "pg":pgnum, "external":external,"dest": dest}
				result.append(link)
		return result
        
	def findExternalLinks(self):
		""" Returns a set for every page, False if there are no links on a page, else a list of the links. 
		'dest' is the destination (pg num or uri), 
		'pg' is the page we found it on, 
		'external' is True if it's a URI or false if it links to a page,
		'rect' is a set of four points defining the position. 
		Don't forget - it's PDF points,
		so you could from the bottom of the document! """	
		result=[]
		for pgnum in range(0, self.numPages):
			result.append(self._findExternalLinks(pgnum))
		return result

