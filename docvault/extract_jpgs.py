#!/usr/bin/env python

import sys, zlib
import Image
from pdftools import pdffile

if __name__ == "__main__":

    if len(sys.argv) != 3:
        sys.stderr.write("Usage: %s <PDF file> <file prefix>\n" % sys.argv[0])
        sys.exit(1)

    path = sys.argv[1]
    prefix = sys.argv[2]

    try:
        document = pdffile.PDFDocument(path)
        for i in range(document.count_pages()):
            page = document.read_page(i + 1)
            counter = 0
            resources = document._dereference(page.page_dict["Resources"])
            if not resources.has_key("XObject"):
                continue

            for xobject in resources["XObject"].values():

                xdict, stream = document._dereference(xobject)

                try:
                    if xdict["Subtype"].name != "Image":
                        continue

                    if xdict["Filter"].name == "DCTDecode":

                        data = document.file[stream.start:stream.end]
                        file_name ="%s-%i-%i.jpg" % (prefix, i + 1, counter)
                        print "Writing", file_name
                        open(file_name, "w").write(data)

                    elif xdict["Filter"].name == "FlateDecode":

                        if isinstance(xdict["ColorSpace"], pdffile.name) and \
                            xdict["ColorSpace"].name == "DeviceRGB":

                            data = zlib.decompress(document.file[stream.start:stream.end])
                            image = Image.fromstring(
                                "RGB", (xdict["Width"], xdict["Height"]), data
                                )
                            file_name ="%s-%i-%i.png" % (prefix, i + 1, counter)
                            print "Writing", file_name
                            image.save(file_name)

                    else:
                        continue

                    counter += 1

                except (KeyError, IOError):
                    continue

    except pdffile.PDFError:
        sys.stderr.write("Failed to read the PDF file: %s\n" % path)
        raise
        sys.exit(1)

    sys.exit()