#Auth Mid-Level -- uses low-level, no libraries
#Auth Low-Level -- Direct Encrypt, requires libraries
#SQL --HIGH LEVEL -- functional, database/implementation agnostic
#SQL --MID LEVEL --uses SQL functions, no need for libraries
#SQL --LOW LEVEL --Direct SQL statements, requires SQL libraries


#SESSION OBJECT FUNCTION
def addNode(self, id, type, score):
    properties, edges = getNodeProperties(self.connection, id, type)
    description       = properties[0]
    if type == 'symptoms':
        precision     = properties[1]
        fromList      = ['start']
        toList        = edges
    elif type == 'resolutions':
        precision     = 0
        fromList      = edges
        toList        = []
    newNode = Node(id, type, description, precision, fromList, toList,score)
    self.tree.append(newNode)
