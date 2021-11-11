from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools
import pprint

#data structures
foldersDict = {}
filesDict = {}
hierarchyLevels = []
parentChildList = {} 
oldNewIndex = {} #holds a bunch of key:value pairs where the the pairs are sourceFolderId:destinationFolderId
startingFolder = [] #will hold the rootFolderID only, but needs to be an array to feed into traversal function as a param
foldersNextLevel = []
hierarchyLevelsWithContents = {}

#variables
# rootFolderId = '1FQVoIaWzySdxkqtM7z_TI7KtRGYoW9kM' #personal test folder (ABCs)
rootFolderId = '1cpo-7jgKSMdde-QrEJGkGxN1QvYdzP9V' #netflix
destinationFolderId = ''

#Authenticates and creates a drive service
def driveAuth():
    # define path variables
    credentials_file_path = './credentials/credentials.json'
    clientsecret_file_path = './credentials/client_secret.json'

    # define API scope
    SCOPE = 'https://www.googleapis.com/auth/drive' #create, edit, delete

    # define store
    store = file.Storage(credentials_file_path)
    credentials = store.get()
    
    # get access token
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(clientsecret_file_path, SCOPE)
        credentials = tools.run_flow(flow, store)

    # define Drive API service
    http = credentials.authorize(Http())
    global drive
    drive = discovery.build('drive', 'v3', http=http)

#Lists all files/folders within a given folder. Disclaimer, I have not ensured that pagination and error handling is accounted for yet.
def listFiles(folder_id):
    query = f"parents = '{folder_id}'"
    fields="nextPageToken, files(id, kind, mimeType, name, parents)"
    response = drive.files().list(q=query,fields=fields).execute()
    # pprint.pprint(response)
    files = response.get('files')
    #pprint.pprint(files)
    return files


#Traverses Google Drive and calls itself recursively until there are no more subfolders
def traverseDrive(folders, currentLevel):

    #set level to current level arg
    level = currentLevel

    print(f"About to iterate through this list of folders: {folders}")
    #iterate through each folder at the current level of the hierarchy
    for folder in folders:
        #get list of all files/folders within the folder we are iterating through
        files = listFiles(folder)

        parentChildList[folder] = {
                'subFolders': [],
                'files': []
                }
        for item in files:
            if item['mimeType'] == "application/vnd.google-apps.folder":
                foldersDict[item['id']] = {
                    'id': item['id'],
                    'kind': item['kind'],
                    'mimeType': item['mimeType'],
                    'name': item['name'],
                    'hierarchyLevel': level+1,
                    'parent': item['parents'] #need to figure out where to get parentID
                }
                #add to the list of folders at the next hierarchical level
                foldersNextLevel.append(item['id'])

                #add as subfolder in parentChildList
                parentChildList[folder]['subFolders'].append(item['id'])
            else:
                filesDict[item['id']] = {
                    'id': item['id'],
                    'kind': item['kind'],
                    'mimeType': item['mimeType'],
                    'name': item['name'],
                    'parentFolderId': folder
                    }
                #add as file in parentChildList
                parentChildList[folder]['files'].append(item['id'])
    level += 1

    print(f"foldersNextLevel: {foldersNextLevel}")

    #exit recursively called function if no more subfolders to fetch files/folders from
    if len(foldersNextLevel) == 0:
        print("Exiting traverse function. Theres no more folders to traverse.")
        countFolderContents()
    #add to our hierarchy level tracker if there are more subfolders 
    else:
        hierarchyLevels.append({
                'level':level,
                'ids': foldersNextLevel.copy()
                })
        nextFoldersToTraverse = foldersNextLevel.copy()
        #clear out any existing elements in foldersNextLevel as this function will be recursively called
        foldersNextLevel.clear()
        traverseDrive(nextFoldersToTraverse,level)

#Adds fileCount and subFolder count
def countFolderContents():
    for i in parentChildList:
        parentChildList[i]['fileCount'] = len(parentChildList[i]['files'])
        parentChildList[i]['subFolderCount'] = len(parentChildList[i]['subFolders'])

#Incomplete - this is a placeholder function for recreating folders in destination folder
#https://developers.google.com/drive/api/v3/reference/files/create
def createSubFolders(parentId, folderName):
    file_metadata = {
    'name': folderName,
    'parents': parentID
    }
    drive_service.files().create(body=file_metadata).execute()

#Incomplete - this is a placeholder function for recreating files in destination folder
# https://developers.google.com/drive/api/v3/reference/files/copy
def copyFile(parentID, fileName):
    file_metadata = {
    'name': fileName,
    'parents': parentID
    }
    drive_service.files().copy(
        fileId=file_metadata,
        body=file_metadata,
    ).execute()

#stores key:value pairs of old:new folderIds. sourceFolderID:destinationFolderID
def updateOldNewIndex():
    return 


#aggregates previously stored metadata with our hierarchyLevels list and store as a dict. This gets printed to terminal as a report.
def showContentsInHierarchy():
    count = 1
    for i in hierarchyLevels:
        hierarchyLevelsWithContents[count] = {}
        for folder in i['ids']:
            hierarchyLevelsWithContents[count][folder] = parentChildList.get(folder)
        count+=1

def printResults():
    #displays a list of all folders nested within root folder, including metadata
    print("\nHeres the folders list")
    pprint.pprint(foldersDict)

    #displays a list of all files nested within root folder, including metadata
    print("H\neres the files list")
    pprint.pprint(filesDict)

    #displays all children files/folders, if any, for each folder
    print("\nHeres the parentChildList")
    pprint.pprint(parentChildList)

    #displays folders in the form of fileIDs at all levels below the root folder. 1 indicates 1 level below root, 2 indicates 2 levels below root, etc
    print("\nHeres the hierarchy list")
    pprint.pprint(hierarchyLevels)

    #a more detailed view of the folders at each level below root. Includes metadata round each folder's subfolders and files. Satisfies assessment #2 of take home.
    print("\nHeres the hierarchy list with metadata at each level of the hierarchy")
    pprint.pprint(hierarchyLevelsWithContents)
    print(f"\nThere are a total of {len(foldersDict)} subfolders and a total of {len(filesDict)} files within the root folder (id: {rootFolderId}) ")

def main():
    driveAuth()
    startingFolder.append(rootFolderId)
    traverseDrive(startingFolder, 0) #pass root folderId in and treat it as the first level of our directory (0)
    showContentsInHierarchy()

    #pseudocode for assessement 3 of take home:
    #Use a loop to iterate through each element within the hierarchyLevels list to recreate subfolders and their subfolders under destination folder. We won't be doing anything with files yet.
    #As we loop and recreate the folders, we will be updating oldNewIndex to track the old folder IDs vs the new folder IDs
    #Now that all nested folders are recreated under our destination root folder, we will need to recreate all files within the destination folders
    #Use a loop to iterate through all files within our filesDict
    #For each file in filesDict, use the parent fileID value to fetch the new destination folderID of the parent from our oldNewIndex dict.
    #Now that we know the parent folderID in the destination folder, we can copy the file over to the correct destination folder
    printResults()


main()
