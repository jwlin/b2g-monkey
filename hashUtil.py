from dom_analyzer import DomAnalyzer

class Hash :
    def __init__(number, automata):
        self.number = number
        self.automata = automata
        self.d = {}
        for j in xrange(number):
            x = []
            self.d[j] = x 
    
    def put(self, state):
        new_dom = state.get_normalize_dom()
        hashvalue = hashfunction(dom)
        for list_id  in self.d[hashvalue]:
            list_dom = get_dom_by_stateID(stateID)
            if is_normalize_equal(list_dom, new_dom):
                return False, list_id
        if not state.get_id():
            state.set_id( str(len( self.automata .get_states() )) )
        list.append(self.d[hashvalue], state.get_id())
        return True, state.get_id()

    def hashfunction(self, dom):
        return len(dom)%self.number   

    def get_dom_by_stateID(self, stateID):    
        return self.automata.get_state_by_id(stateID).get_normalize_dom()

    def is_normalize_equal(self, list_dom, new_dom):
        return DomAnalyzer.is_normalize_equal(list_dom, new_dom)
         
        

 
                

 