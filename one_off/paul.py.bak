#author - Paul Rossbach
import sys
import inspect
from ticket_booth import Ticket, SecurityBreach

class main_program(object):
    #creates and opens the log file
    def __init__(self, the_log_file):
        global log_file
        log_file = open(the_log_file, 'w')
        print("log file opened")
        log_file.write("test")

    #calls the actual function
    def __call__(self, *args):
        print("calling main")
        return args[0]

#my old approach, contains my exception code and the like to be moved when I get the new one working
#def privilege(min_clearance):
# def check(func):
#  print(func)
#  def checkArgs(*args):
  #the code never gets inside of here
 #  print(args)
 #  if args[0] < min_clearance:
 #   for x in sys.argv:
 #    if x == "--naked": naked=true
 #   if naked != true:
 #    raise SecurityBreach(min_clearance, args[0])
 #    return 0
 #   else: return func(args)
 #return check

class privilege(object):
    #vars for the min clearance and function to call
    __slots__=("minclear", "func")

    #what i am trying to do here is to intercept the actual
    #call to the function so I can do my comparison
    #but no matter what I do it doesn't seem to work
    #should i use something other than __call__?
    def __call__(self, func, *args):
        print("called the function")

    #this part seems to fire just after decoration time, when the function
    #that is being decorated is being defined. I store the function and spit
    #out the clearance level and the function for debug purposes,
    #this looks to be working correctly
    def __call__(self, func):
        self.func = func
        print("minclear " + str(self.minclear))
        print("func " + str(self.func))
        return self.func

    #stores the clearance level at decoration time
    #seems to be working
    def __init__(self, min_clearance):
        self.minclear = min_clearance