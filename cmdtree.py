## cmdtree.py
import readline

PROMPT_SYMBOL = '>'
PROMPT_SEPARATOR = ' '

class CommandTree(object):
    def __init__(self, name, notes=None, parse=None, completions=[], parents=[], descendants=[]):
        self.name = name
        self.parse = parse
        self.notes = notes
        self.descendants = list(descendants)
        self.parents = list(parents)
        self.completion_type = "tab: complete"
        self.collection = {}
        self.completions = list(completions)
        self.upcmd = ['up', 'u',]
        self.quitcmd = ['q', 'quit', 'exit']
    
    def add_child(self, baby_ct):
        self.descendants.append(baby_ct)
    
    def add_parent(self, aunt_ct):
        self.parents.append(aunt_ct)

    def insert(self, insert_data):
        if isinstance(insert_data, dict):
            self.collection.update(insert_data)

    def _get_in(self, parent_name):
        prompt = self.name
        if parent_name:
            prompt = PROMPT_SEPARATOR.join([parent_name, self.name])
        prompt = PROMPT_SEPARATOR.join([prompt, PROMPT_SYMBOL, ''])
        res = raw_input(prompt)
        if (res != None) and (res != ''):
            if self.parse:
                return self.parse(res)
            else:
                return res
        return None

    def collect(self, parent_name=None):
        """Depth first collection of tree
        """
        # Do we have data to collect?
        if parent_name == None:
            # We are the top tag!
            self.collection['tag'] = [self.name]

        if self.parse != None:
            self.col_old_completer = readline.get_completer()
            readline.set_completer(self.complete)
            readline.set_completer_delims('\n\r\t;')
            readline.parse_and_bind("tab: complete")

            if self.notes:
                print self.notes
            res = self._get_in(parent_name)

            if parent_name:
                ekey = parent_name + '_' + self.name
            else:
                ekey = self.name

            self.collection.update({ekey: res})
            
            readline.set_completer(self.col_old_completer)

        for child in self.descendants:
            child.collect(self.name)

    def collectable(self):
        """a collectable tree is one with children with parse functions"""
        for child in self.descendants:
            if child.parse != None:
                return True
        return False
        

    def runtree(self, parent_name=None):
        stop = None
        while not stop:
            self.rt_old_completer = readline.get_completer()
            readline.set_completer(self.complete_children)
            readline.set_completer_delims('\n\r\t;')
            readline.parse_and_bind("tab: complete")
            res = self._get_in(parent_name)
            readline.set_completer(self.rt_old_completer)
            if res in self.upcmd:
                stop = True
            elif res in self.quitcmd:
                stop = True
            else:
                for child in self.descendants:
                    if res == child.name:
                        if not child.collectable():
                            child.runtree(self.name)
                        else:
                            child.collect()
                
    def complete(self, text, state):
        if state == 0:
            self.completion_match = [a for a in self.completions if a.startswith(text)]
        try:
            return self.completion_match[state]
        except IndexError:
            return None

    def complete_children(self, text, state):
        if state == 0:
            self.completion_child_match = [a.name for a in self.descendants if a.name.startswith(text)]
        try:
            return self.completion_child_match[state]
        except IndexError:
            return None

    def aggregate(self):
        for child in self.descendants:
            self.merge(child.aggregate())
        return self.collection

    def merge(self, previous):
        for nkey in previous:
            skey = str(nkey)
            if skey == 'tag':
                try:
                    self.collection['tag'].extend(previous[nkey])
                except KeyError:
                    self.collection['tag'] = previous[nkey]
            else:
                self.collection[skey] = previous[nkey]
        

if __name__ == '__main__':
    print 'lulwut'
