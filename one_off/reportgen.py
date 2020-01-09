import mailbox
import re
from datetime import datetime, date
m = mailbox.mbox('/home/stachurski/gmail-archive/gmail-backup.mbox')
raw_messages = []
messages = []

def myreplfunc(matchobj):
    #print matchobj.group(0)
    if matchobj.group(0) == ',,': return '","","'
    else: return '","%s' % matchobj.group(1)

def main():
    for mail in m:
        try:
            if mail.get_from().find('contactus@flavordynamics.com') != -1:
                msg_date_str = mail.get('Date')
                msg_date = datetime.strptime(msg_date_str[:16], '%a, %d %b %Y').date()
                try:
                    msg = mail.get_payload()[0].get_payload()[174:-1].replace('"',"'")
                except:
                    msg = mail.get_payload()[174:-1].replace('"',"'")
                raw_messages.append(msg)
                msg = '"%s"' % msg
                msg = re.sub(r',(\S)', myreplfunc, msg, 11)
                # msg = msg.replace(',', '","',11)
                msg = re.sub('\n+', '; ', msg)
                msg += ',"%s"' % msg_date
                messages.append(msg)
        except Exception as e:
            import pdb; pdb.set_trace()
    
    report = open('/home/stachurski/contactus.csv', 'w')
    
    for x in messages:
        report.write("%s\n" % x)
    
    
    report.close()
    
    return raw_messages
if __name__ == "__main__":
    main()
