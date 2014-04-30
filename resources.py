class ResourceBank(object):
    def __init__(self):
        # 200 of each card
        self.resources = range(1000)
        self.type_starts = {'brick': 0, 'wool': 200, 'ore': 400, 'grain': 600, 'lumber': 800}
        
    
    def index_to_type(self, index):
        if index >= 0 and index < 200: return 'brick'
        if index >= 200 and index < 400: return 'wool'
        if index >= 400 and index < 600: return 'ore'
        if index >= 600 and index < 800: return 'grain'
        if index >= 800 and index < 1000: return 'lumber'
        return None
    
    def get_next_resource(self, tp):
        type_start = self.type_starts[tp]
        while True:
            if type(self.resources[type_start]) == int:
                return type_start
            type_start += 1
            
    def set_resource_owner(self, index, owner):
        self.resources[index] = [True, owner]
    
    def get_resource_owner(self, index):
        if type(self.resources[index]) != list: return None
        return self.resources[index][1]