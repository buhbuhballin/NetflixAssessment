# NetflixAssessment

Source folder id: 1cpo-7jgKSMdde-QrEJGkGxN1QvYdzP9V

Assessments:
- Write a script to generate a report that shows number of files and folders in total for the
source folder 
- Write a script to generate a report that shows number of files and folders for each folder
under this folder id (recursively) and a total of nested folders for the source folder
- Write a script to copy the content (nested files/folders) of the source folder to the
destination folder


Instructions:
1. https://console.cloud.google.com/ to create a new GCP project
2. enable Google Drive api
3. create OAuth 2.0 credential for Google Drive API and set type of cred to desktop
4. configure OAuth consent screen
5. download OAuth cred and rename to credentials.json
6. create virtual env
7. activate virtual env
8. pip install google-api-python-client oauth2client
9. within virtual env folder, make another folder called "credentials"
10. move the credentials.json file into "credentials" folder
11. copy https://github.com/buhbuhballin/NetflixAssessment/blob/main/googleDriveTraverseReportCopy.py over to virtual env folder
12. run googleDriveTraverseReportCopy.py
13. observice pprint output to satisfy takehome assessment #1 and #2
14. read script for pseudocode for assessment #3
