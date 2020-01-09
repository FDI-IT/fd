# import os
# import re
# import logging
# import pycurl
#
# BOX_NO = 30
# image_dir = '/tmp/image_ram'
# logger = logging.getLogger(__name__)
# cookie_path = '/tmp/image_ram/cookie.txt'
#
# class CurlOutput:
#     def __init__(self):
#         self.contents = ''
#     def body_callback(self, buf):
#         self.contents += buf
#
# def get_curler():
#     c = pycurl.Curl()
#     c.setopt(pycurl.CONNECTTIMEOUT, 10)
#     c.setopt(c.COOKIEJAR,cookie_path)
#     coutput = CurlOutput()
#     c.setopt(c.WRITEFUNCTION, coutput.body_callback)
#
#     return (c, coutput)
#
# def get_doc_ids(c):
#     try:
#         logger.info("Contacting printer")
#         c.setopt(c.URL, "http://192.168.10.200/")
#         c.perform()
#         c.setopt(c.URL, "http://192.168.10.200/frame.cgi?PageFlag=b_frame.tpl&Dummy=1")
#         c.perform()
#         c.setopt(c.URL, "http://192.168.10.200/box_index.cgi?PageFlag=b_ix30.tpl&Dummy=2")
#         c.perform()
#         c.setopt(c.URL, "http://192.168.10.200/en/pages/b_ubody.htm?Dummy=3")
#         c.perform()
#         c.setopt(c.URL, "http://192.168.10.200/bpbl.cgi?BoxKind=UserBox&Dummy=4")
#         c.perform()
#         c.setopt(c.URL, "http://192.168.10.200/blogin.cgi?BOX_No=%s&Cookie=&Dummy=5" % (BOX_NO,))
#         c.perform()
#         c.setopt(c.URL, "http://192.168.10.200/blogin.cgi?BOX_No=%s&Cookie=&Dummy=6" % (BOX_NO,))
#         c.perform()
#         c.setopt(c.URL, "http://192.168.10.200/bheader.cgi?BOX_No=%s&Dummy=7" % (BOX_NO,))
#         c.perform()
#         coutput.contents = ""
#         c.setopt(c.URL, "http://192.168.10.200/bdocs.cgi?BOX_No=%s&DocStart=1&DIDS=&Dummy=8" % (BOX_NO,))
#         c.perform()
#     except Exception as e:
#         pass
#         #logger.warning("Unable to contact printer. Retrying...")
#         #self.retry(exc=e)
#
#     doc_re = "javascript:doc_pages\('(\d+)'\)"
#     try:
#         doc_ids = set(re.findall(doc_re, coutput.contents))
#     except:
#         print coutput.contents
#         return
#
#     return doc_ids
#
# def main(image_dir="/tmp/image_ram/"):
#     os.chdir(image_dir)
#     c, coutput = get_curler()
#     dummy = 10
#     doc_ids = get_doc_ids(c)
#
#     for doc_id in doc_ids:
#         coutput.contents = ""
#         c.setopt(c.URL, "http://192.168.10.200/bpages.cgi?BOX_No=%s&DocID=%s&PgStart=1&PIDS=&Dummy=%s" % (BOX_NO, doc_id, dummy))
#         dummy += 1
#         c.perform()
#
#         matchcount = coutput.contents.count('dot_blue')
#         matchcount = matchcount / 2
#         for x in range(1,matchcount+1):
#             coutput.contents = ""
#             c.setopt(c.URL, "http://192.168.10.200/image.jbg?B=%s&D=%s&P=%s&M=MV&RX=600&RY=600&Dummy=%s" % (BOX_NO, doc_id, x, dummy))
#             dummy += 1
#             new_image = open('%s.jbg' % x, 'w')
#             c.perform()
#             new_image.write(coutput.contents)
#             new_image.close()
#
#     c.close()
#     return
#
# if __name__ == "__main__":
#     main()
