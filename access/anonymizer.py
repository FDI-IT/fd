import Queue

class Anonymizer:
    def __init__(self):
        loremfile = open('/home/stachurski/loremipsum.txt', 'r')
        lorem_line = loremfile.read()
        lorems = lorem_line.split(',')
        lorems = lorems[0:len(lorems)-1]
        self.q = Queue.Queue()
        for word in lorems:
            self.q.put(word)

            
def anonymize(model_list):
    for model in model_list:
        model.anonymize()
    
    
    
        