"""
Exports the results of finding links and multimedia to a file

python findlinks.py sourcefile.pdf destfile.json /path/to/drop/multimedia
"""

import pdflinkfinder
import cjson
import sys

filename=sys.argv[1]
targetfile=sys.argv[2]
targetdir=sys.argv[3]
pdf=pdflinkfinder.PdfLinkFinder(filename)
mm=pdf.findMultimedia(targetdir)
links=pdf.findExternalLinks()
f=open(targetfile,"w")
f.write(cjson.encode({"links":links,"multimedia":mm}))
f.close()
print "All done"