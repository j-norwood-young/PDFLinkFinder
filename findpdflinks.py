import pdflinkfinder
import cjson
import sys

filename=sys.argv
pdf=pdflinkfinder.PdfLinkFinder(filename[1])
if (pdf.hasExternalLinks()):
	links=pdf.findExternalLinks()
print cjson.encode(links)