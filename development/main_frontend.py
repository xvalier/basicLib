from frontend import grpc_client
port = 4040
address = '104.196.188.181'
#address  = 'localhost'

def main():
    #print('Loading current IP from Google Drive...')
    #Google Drive function to import IP txt file REQUIRED HERE LATER
    #gRPC Client Implementation
    #address = input('What is the current IP (can enter localhost too):') #temp method to get ip
    print('Initializing gRPC Stub for communication with backend...')
    print('IP: ' + address + '   PORT: ' + str(port) )
    stub = grpc_client.grpcStub(port, address)
    while(1):
        #Initial Query Page
        response, token  = initialQuestion()
        symptomsList     = grpc_client.sendQuery(stub, response, token)
        #Second page where tuned list of symptoms are selected by user
        feedback         = secondQuestion(symptomsList)
        message          = grpc_client.sendSelection(stub, feedback, token)
        #Curation Loop
        while not (message.doneFlag):
            #If session is not finished, continue asking questions
            print('Continue Loop')
            if not (message.doneFlag):
                response = askNextQuestion(message.input)
                message  = grpc_client.sendFeedback(stub,response, token)
                print("Done?: " + str(message.doneFlag))
            if (message.doneFlag):
                print("Done?: " + str(message.doneFlag))
                print("Solved?: " + str(message.solvedFlag))
                closeSession(message.solvedFlag)

# Terminal Functions------------------------------------------------------------
#User provides description of issue they are facing
def initialQuestion():
    response = input("What is your problem? \r\n")
    token    = input("What is your identity \r\n")
    return response, token

#User trims displayed list of symptoms that system provides
def secondQuestion(symptomsList):
    displaySymptoms(symptomsList)
    response = input('Choose all relevant symptoms using numbers 0-4: \r\n')
    response = sorted(set(response))
    stringResponse = ''
    for char in response:
        stringResponse += char
    return stringResponse

#Displays list of symptoms in terminal
def displaySymptoms(symptomsList):
    #De-encapsulate gRPC ServerList into a list of strings
    tempList = []
    for entry in symptomsList.symptoms:
        tempList.append(entry.input)
    #Display the list on terminal
    print("\r\n------------------------------------\r\n")
    if (tempList == []):
        print("No Matches")
    else:
        for item in tempList:
            print(item)
        print("\r\n------------------------------------\r\n")

#Ask user if symptom/resolution is true, and store feedback
def askNextQuestion(question):
    print(question + '\r\n')
    feedback = 0
    response = ''
    while (response != 'y') & (response != 'n'):
        response  = input('Choose either y or n: ')
    if (response == 'y'):
        feedback = 1
    else:
        feedback = 0
    return feedback

#Send closing message if issue is resolved, or if no more options
def closeSession(solvedFlag):
    if (solvedFlag):
        print('\r\nError is resolved!')
    else:
        print('\r\nNo error match your symptoms, please contact AfterSales.')

main()
