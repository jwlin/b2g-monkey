
'''x0 =[]
x1 =[]
x2 =[]
x3 =[]
x4 =[]
d = {0:x0,1:x1,2:x2,3:x3,4:x4}
n =num % 5
j = 0
for j<length d[n]:
    if !=d[n][j]:
        j++
    else:
        break
if j == length d[n]:
    list.append(d[n],)'''




class hash:
	def __init__(number):
	    self.d = {}
	    self.number = number
	    for j in xrange(number):
	        x = []
	        self.d[j] = x 	

	
	def put(self,stateid):
        dom = get_dom_by_stateid(stateid)
        hashvalue = hashfunction(dom)
        for uniid  in self.d[hashvalue]:
            if is_equal(uniid,stateid):
                return False
                	
        list.append(self.d[hashvalue],stateid)
        return True

	def hashfunction(self,dom):
        return len(dom)%self.number   

	def get_dom_by_stateid(self,stateid):    
        pass

    def is_equal(self,list_dom,new_dom):
        pass
         
        

 
            	

 