import string
from operator import attrgetter
from backend.helpers import readINI as ini
#connectionString = '/home/xvalier/Documents/curatedTSG/connections2.ini'
connectionString = '/home/nikilsunilkumar/sets/curatedTSG/connections.ini'

#ErrorTree Class Implementations-----------------------------------------------
#Encapsulation for each individual symptom/resolution in curation session
class Node:
    #Constructor
    def __init__(self, id, type,description, precision, fromList, toList, score):
        self.id          = str(id)
        self.type        = type
        self.fromList    = fromList
        self.toList      = toList
        self.precision   = precision
        self.description = description
        self.score       = score
    #Internal Attributes
    id = ''
    type = ''
    precision = ''
    fromList = []
    toList= []
    description = ''
    score = 0;

#Treemap/Queue of Nodes for use in curation session
class Session:
    #Constructor
    def __init__(self, symList):
        self.tree       = []
        self.doneFlag   = 0
        self.solvedFlag = 0
        self.connection = ini.readConnectionStringSQL(connectionString)
        self.fillTree(symList)
        self.sortTree(symList)

    #Attributes
    tree       = []
    connection = 0
    doneFlag   = 0
    solvedFlag = 0

    #CREATE Methods********
    #Adds all relevant Nodes to tree based on list of filtered symptoms
    def fillTree(self, symList):
        errorIds = getErrorList(self.connection, symList)
        self.getSymNodes(errorIds)
        self.getResNodes(errorIds)

    #Add all relevant symptoms to tree
    def getSymNodes(self, errorList):
        symptomList = []
        #Get symIds associated with errorId, add to tree
        for entry in errorList:
            tempList = getSymIds(self.connection, entry[0])
            for id in tempList:
                self.addNode(id, 'symptom', entry[1])

    #Add all relevant resolutions to tree
    def getResNodes(self, errorList):
        resolutionList = []
        #Get all resIds associated with errorId, add to tree
        for entry in errorList:
            tempList = getResIds(self.connection, entry[0])
            for id in tempList:
                self.addNode(id, 'resolution', entry[1])

    #Encapsulate symptoms/resolutions as nodes, then add to tree
    #NOTE: Calling database twice for description and precision is probably not efficient, but this code will eventually be replaced by a adjacency list implementation
    def addNode(self, id, type, score):
        if type == 'symptom':
            result      = queryPSQL(self.connection, "SELECT * from symptoms WHERE symId = %s", id)[0]
            description = result[1]
            precision   = result[5]
            fromList    = ['start']
            toList      = getErrorIdsForward(self.connection, id)
        elif type == 'resolution':
            result      = queryPSQL(self.connection, "SELECT * from resolutions WHERE resId = %s", id)[0]
            description = result[2]
            precision   = 0
            fromList    = getErrorIdsBackward(self.connection, id)
            toList      = []
        newNode = Node(id, type, description, precision, fromList, toList,score)
        self.tree.append(newNode)

    #Trim down tree and sort
    def sortTree(self, symList):
        self.removeDuplicates()
        self.displayTree()
        self.removeGeneric()
        self.removeAsked(symList)
        self.tree.sort(key = attrgetter("score","type"), reverse = 1)

    #Remove/combine duplicate entries from tree, but keep their edge properties
    def removeDuplicates(self):
        uniqueList = []
        for index,node in enumerate(self.tree):
            #If node is not already appended, add it to the list
            uniqueNodes = [n.id for n in uniqueList]
            if (node.id not in uniqueNodes):
                uniqueList.append(node)
                #If a duplicate has been found at a different index location
                for otherIndex, otherNode in enumerate(self.tree):
                    if (node.id == otherNode.id) & (index != otherIndex):
                        #Add duplicate node contents to last item in uniqueList
                        #Last item will also be the 'duplicate id'
                        lastIndex   = len(uniqueList) - 1
                        lastNode    = uniqueList[lastIndex]
                        lastNode.score       = max(lastNode.score, otherNode.score)
                        lastNode.toList      = list(set(lastNode.toList + otherNode.toList))
                        lastNode.fromList    = list(set(lastNode.fromList + otherNode.fromList))
        self.tree = uniqueList

    #Remove generic symptoms if a precise symptom already 'covers them' and is ahead in Queue
    def removeGeneric(self):
        filteredList = []
        #Remove edges from nodes which are less precise or generic
        for node in self.tree:
            if (node.precision == 1) | (node.precision == 2):
                self.removeGenericEdges(node)
        #Keep nodes which have remaining edges
        for node in self.tree:
            if (node.toList != []) | (node.type == 'resolution'):
                filteredList.append(node)
        self.tree = filteredList

    #Compares input node's edges against other nodes. Removes other node edges if they are less precise
    def removeGenericEdges(self, node):
        for error in node.toList:
            for comparedNode in self.tree:
                sameEdge = (error in comparedNode.toList)
                if (node.id != comparedNode.id) & sameEdge:
                    if (node.precision < comparedNode.precision) & (node.score >= comparedNode.score):
                        comparedNode.toList.remove(error)

    #Remove symptoms that were already asked on scrolling symptoms list
    def removeAsked(self, symList):
        for n in range(len(self.tree)-1,-1,-1):
            current  = self.tree[n]
            askedIds = [col[0] for col in symList]
            if current.id in askedIds:
                self.popNodeIndex(n)

    #UPDATE Methods********
    #Determine how to modify session tree based on yes/no answer
    def processResponse(self, response):
        if self.tree == []:
            self.doneFlag = 1
        elif response == 0:
            self.removeBranch()
        elif response == 1:
            #If resolution was confirmed to work, close session
            if self.tree[0].type == 'resolution':
                self.doneFlag   = 1
                self.solvedFlag = 1
            self.popNodeIndex(0)

    #Remove a Node and all its children from tree (don't ask questions related to parent)
    def removeBranch(self):
        list = self.tree[0].toList
        for node in self.tree:
            #Remove all nodes with outbound links from recently asked question
            for entry in list:
                if entry in node.fromList:
                    node.fromList.remove(entry)
            #Remove all Nodes which have no incoming branches
            if node.type == 'resolution':
                if len(node.fromList) <=0:
                    self.popNodeId(node.id)
        self.popNodeIndex(0)

    #Remove the most recently asked Node from tree
    def popNodeIndex(self, index):
        self.tree.pop(index)

    #Remove a specific node from tree
    def popNodeId(self, id):
        for n in range(len(self.tree)-1,-1,-1):
            if self.tree[n].id == id:
                self.tree.pop(n)

    #READ Methods*********
    #Get next question to ask
    def nextQuestion(self):
        return self.nextHeader() + self.nextDescription()

    #Access the symptom/resolution description
    def nextDescription(self):
        return self.tree[0].description

    #Determine whether to use symptom or resolution question header
    def nextHeader(self):
        head = self.tree[0].type
        if head == 'symptom':
            header = 'Is the symptom below true? \r\n'
        if head == 'resolution':
            header = 'Does the resolution below work? \r\n'
        return header

    #Displays full tree in terminal
    def displayTree(self):
        for index,node in enumerate(self.tree):
            print("#{0}-{1}--{2}--{3}".format(str(index),str(node.id),str(node.type),str(node.precision)), end = " ")
            for error in node.toList:
                print('{0}'.format(str(error)), end = " ")
            print(" ")

#Gets all errorIds for each symptom in symptom list
def getErrorList(connection, symptomsList):
    errorList = []
    for entry in symptomsList:
        id = entry[0]
        score
        tempList = getErrorIdsForward(connection, entry[0])
        for id in tempList:
            #Create a dict of errorId and associated sym score
            errorList.append([id, entry[1]])
    return errorList
