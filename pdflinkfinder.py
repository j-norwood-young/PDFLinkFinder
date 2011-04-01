"""
This class finds PDF links. Useful for making a digital publication.
It relies on pyPdf
http://pybrary.net/pyPdf/

I nabbed the _hasExternalLiks function from the interwebs and adapted it for my findExternalLinks function.
http://trac.egovmon.no/trac/eGovMon/browser/trunk/WAMs/pdf-wam/pdfStructureMixin.py?rev=2188

At some point I hope to rewrite that so that I don't have to have the GPL license in here.

Here is the license for that code:
#      Copyright 2008-2010 eGovMon
#      This program is distributed under the terms of the GNU General
#      Public License.
#
#  This file is part of the eGovernment Monitoring
#  (eGovMon)
#
#  eGovMon is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  eGovMon is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with eGovMon; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston,
#  MA 02110-1301 USA

Props to Anand B Pillai, whomever you may be.

The rest of the code is Copyright 2011 10Layer Software Development Pty (Ltd)
http://10layer.com

The application is licensed by the MIT license
http://www.opensource.org/licenses/mit-license.php

Example of use:

import pdflinkfinder
import cjson

pdf=pdflinkfinder.PdfLinkFinder("newconcept.pdf")
if (pdf.hasExternalLinks()):
	links=pdf.findExternalLinks()
print cjson.encode(links)

Example of result (Three pages, an internal link on the first to the second page, and an external link on the third):
[[{"dest": 1, "pg": 0, "rect": [34, 362, 380, 34], "external": false}], false, [{"dest": "http://www.10layer.com", "pg": 2, "rect": [82, 929, 686, 610], "external": true}]]
"""
__version__="0.1a"
__author__="Jason Norwood-Young"
__license__="MIT and GPL2"
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
        """ Return whether the page has external links
        (URIs, URLs, email addresses) etc """

        pg = self.pdf.getPage(pgnum)
        # If there is no '/Annots' key, return False
        try:
            annots = pg['/Annots']
        except KeyError:
            return False
        
        if annots is None:
            return False

        # Check Muif annotation is Movie, Sound or Screen types
        for anot in annots:
            anot = anot.getObject()
            # Also for the time being assuming FileAttachments are multimedia types
            if anot['/Subtype'] in ('/Link') or anot.has_key('/URI'):
                return True
            # Check for contents...

        return False

    def hasExternalLinks(self):
        """ Find out if the PDF document contains links (URIs)
        to external objects """
         
        for pgnum in range(0, self.numPages):
            if self._hasExternalLinks(pgnum):
                return True

        return False
    
    def _findExternalLinks(self, pgnum):
    	pg = self.pdf.getPage(pgnum)

        try:
            annots = pg['/Annots']
            result=[]
        except KeyError:
            return False
        for anot in annots:
            anot = anot.getObject()
            if anot['/Subtype'] in ('/Link') or anot.has_key('/URI'):
				external=True
				obj=anot['/A'].getObject()
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
				rect=anot['/Rect']
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

