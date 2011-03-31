import pdflinkfinder
import cjson

pdf=pdflinkfinder.PdfLinkFinder("newconcept.pdf")
if (pdf.hasExternalLinks()):
	links=pdf.findExternalLinks()
print cjson.encode(links)