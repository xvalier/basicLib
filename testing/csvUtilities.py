import csv
import numpy as np
import string

#Open csv file as numpy array
def importCSV(file):
    csvFile = open(file)
    rawData = csv.reader(csvFile, delimiter=',',quotechar='"')
    cleanedData = cleanCSV(rawData)
    numpyArray  = np.array(cleanedData)
    return numpyArray

#Helper function for pre-processing of csv before numpy conversion
def cleanCSV(data):
    cleanedData = []
    for row in data:
        processedEntry = []
        #Normalize quotation, commas. Remove endlines and backslashes
        for entry in row:
            entry = entry.replace('"','')
            entry = entry.replace(',',';')
            entry = entry.replace('\r\n', ' ... ')
            entry = entry.replace('\n',' ... ')
            entry = entry.replace("\\",'/')
            processedEntry.append(entry)
        cleanedData.append(processedEntry)
    return cleanedData

#Export numpy file into a csv file
def exportCSV(file, data):
    cleanedData = cleanSpreadsheet(data)
    outputCSV = open(file, 'w')
    writer = csv.writer(outputCSV, delimiter=",", quotechar='"')
    writer.writerows(cleanedData)

#Helper function for pre-processing of numpy array before csv conversoin before numpy conversion
def cleanSpreadsheet(data):
    cleanedData = []
    for row in data:
        processedEntry = []
        #Revert endlines, revert backslashes for file paths
        for entry in row:
            entry = entry.replace('...', ' \r\n ')
            entry = entry.replace('/', "\\")
            processedEntry.append(entry)
        cleanedData.append(processedEntry)
    return cleanedData
