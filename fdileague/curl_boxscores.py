import urllib2
import re
import html5lib

domain = "http://www.pro-football-reference.com"
save_path = "/usr/local/django/fdileague"

class CurlOutput:
    def __init__(self):
        self.contents = ''
    def body_callback(self, buf):
        self.contents += buf

def main():
    index_urls = parse_boxscore_index("%s/boxscores/" % domain )
    box_score_urls = []
    for l in index_urls:
        box_score_urls.extend(parse_year_url(l))
    for box_score_url in box_score_urls:
        get_box_score(box_score_url)
    return box_score_urls

def parse_boxscore_index(index_url):
    doc = html5lib.parse(urllib2.urlopen(index_url), treebuilder="dom")
    tables = doc.getElementsByTagName('table')
    index_urls = []
    extract_clean_file_name = re.compile(r"years\/(\d{4})(_AFL|_AAFC){0,1}/games")
    for t in tables:
        for l in t.getElementsByTagName('a'):
            index_urls.append("%s%s" % (domain, l.attributes.values()[0].value))
#            g = extract_clean_file_name.search(l.attributes.values()[0].value).groups()
#            links.append("%s%s" % (g[0], g[1]))

    return index_urls

def parse_year_url(year_url):
    p = urllib2.urlopen(year_url)
    doc = html5lib.parse(p, treebuilder="dom")
    box_score_urls = []
    for t in doc.getElementsByTagName('table'):
        for l in t.getElementsByTagName('a'):
            l_val = l.attributes.values()[0].value
            if l_val.find('/boxscores/') != -1:
                box_score_urls.append("%s/%s" % (domain, l_val))
    return box_score_urls

def get_box_score(box_score_url):
    box_score_filename = box_score_url.split('/')[-1]
    print box_score_filename
    f = open('%s/%s' % (save_path, box_score_filename), 'w')
    p = urllib2.urlopen(box_score_url)
    f.write(p.read())
    f.close()

if __name__ == "__main__":
    main()
