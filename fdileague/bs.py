#import urllib2
#from BeautifulSoup import BeautifulSoup
#import re
#
#page = urllib2.urlopen("http://www.fdileague.com/")
#soup = BeautifulSoup(page)
#
#record_link_set = set()
#for record_link in soup.findAll('a', href=re.compile('records\.html')):
#    record_link_set.add(record_link.attrMap['href'])
#    
#        
#for record_link in record_link_set:
#    record_page = urllib2.urlopen("http://www.fdileague.com/%s" % record_link)
#    record_soup = BeautifulSoup(page)
#    
#    position = s = soup.find('div', id=re.compile("\w{0,2}title")).attrMap['id'][:-5]
#    for 