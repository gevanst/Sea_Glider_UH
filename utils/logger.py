class testData:

#get filename from test.py and timestamp
def __init__self(self,filename = None):
if filename is None: 
  test_name = os.path.splitext(os.path.basename(__file__)[0] #script name w/o .py
  timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
  self.filename - f"{script_name}_{timestamp}.txt" 
else: 
  self.filename = filename
  
self.log_entries = [] # initialize empty log list

def log(self,label,value)
self.log_entries.append((label,value)) # make (label,value) tuple


    

                        
  
