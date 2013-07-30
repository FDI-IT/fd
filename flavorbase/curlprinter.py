import os
import re
import logging
import pycurl

class CurlOutput:
    def __init__(self):
        self.contents = ''
    def body_callback(self, buf):
        self.contents += buf

def main():
    os.chdir("/tmp/image_ram/")
    c = pycurl.Curl()
    c.setopt(pycurl.CONNECTTIMEOUT, 10) 
    c.setopt(c.COOKIEJAR, 'cookie.txt')
    coutput = CurlOutput()
    c.setopt(c.WRITEFUNCTION, coutput.body_callback)
    logger = logging.getLogger(__name__)
    try:
        logger.info("Contacting printer")
        c.setopt(c.URL, "http://192.168.10.200/")
        c.perform()
        c.setopt(c.URL, "http://192.168.10.200/frame.cgi?PageFlag=b_frame.tpl&Dummy=1")
        c.perform()
        c.setopt(c.URL, "http://192.168.10.200/box_index.cgi?PageFlag=b_ix30.tpl&Dummy=2")
        c.perform()
        c.setopt(c.URL, "http://192.168.10.200/en/pages/b_ubody.htm?Dummy=3")
        c.perform()
        c.setopt(c.URL, "http://192.168.10.200/bpbl.cgi?BoxKind=UserBox&Dummy=4")
        c.perform()
        c.setopt(c.URL, "http://192.168.10.200/blogin.cgi?BOX_No=12&Cookie=&Dummy=5")
        c.perform()
        c.setopt(c.URL, "http://192.168.10.200/blogin.cgi?BOX_No=12&Cookie=&Dummy=6")
        c.perform()
        c.setopt(c.URL, "http://192.168.10.200/bheader.cgi?BOX_No=12&Dummy=7")
        c.perform()
        coutput.contents = ""
        c.setopt(c.URL, "http://192.168.10.200/bdocs.cgi?BOX_No=12&DocStart=1&DIDS=&Dummy=8")
        c.perform()
    except Exception as e:
        pass
        #logger.warning("Unable to contact printer. Retrying...")
        #self.retry(exc=e)






    doc_re = "javascript:doc_pages\('(\d+)'\)"
    try:
        doc_id = re.search(doc_re, coutput.contents).group(1)
    except:
        print coutput.contents
        return
    
    coutput.contents = ""
    c.setopt(c.URL, "http://192.168.10.200/bpages.cgi?BOX_No=12&DocID=%s&PgStart=1&PIDS=&Dummy=9" % doc_id)
    c.perform()
    dummy = 10 
    matchcount = coutput.contents.count('dot_blue')
    matchcount = matchcount / 2
    for x in range(1,matchcount+1):
        coutput.contents = ""
        c.setopt(c.URL, "http://192.168.10.200/image.jbg?B=12&D=%s&P=%s&M=MV&RX=600&RY=600&Dummy=%s" % (doc_id, x, dummy))
        dummy += 1
        new_image = open('%s.jbg' % x, 'w')
        c.perform()
        new_image.write(coutput.contents)
        new_image.close()

    c.close()
    return

if __name__ == "__main__":
    main()
