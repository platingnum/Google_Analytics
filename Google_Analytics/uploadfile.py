"""A simple example of how to access the Google Analytics API."""

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from apiclient.http import MediaFileUpload
from apiclient.errors import HttpError
from azure.datalake.store import core, lib, multithread
import os

# Upload to ADL
def uploadToADL(file_location) :

    # ADL Specific Variables
    #subscriptionId = '1acf0831-5469-4d44-b6b8-dada2a38f9c4'
    adlsAccountName = 'rctbraj'
    RESOURCE = 'https://datalake.azure.net/'

    # Active Directory Specific Variables
    tenant = 'de005ab9-410a-421b-b09a-df30074a2a0f' # Directory Id
    client_id = '6dc493ca-ac45-4ef2-978f-6cdf34d73a58'
    client_secret = 'pXa9Hsmy5X54ritW3CT9Uiy22KZ4ogYxzWDy6eS/UBs='

    # Authenticate and get credentials
    try:
        adlCreds = lib.auth(tenant_id = tenant,
                        client_secret = client_secret,
                        client_id = client_id,
                        resource = RESOURCE)
    except Exception as e:
        print 'Azue Data Lake Store Authentication Error'

    # Create a filesystem client object
    try:
        adlsFileSystemClient = core.AzureDLFileSystem(adlCreds, store_name=adlsAccountName)
    except Exception as e:
        print 'Azue Data Lake Store Client Error'
    try:
        multithread.ADLUploader(adlsFileSystemClient, 
                                lpath=file_location, 
                                rpath='/{}'.format(os.path.basename(file_location)), 
                                nthreads=64, overwrite=True, buffersize=4194304, blocksize=4194304)
        print 'File uploaded to Azue Data Lake Store ...'
    except Exception as e:
        print 'Azue Data Lake Store Upload Error'


# Upload to GA
def uploadToGA(filepath):
    # Define the auth scopes to request.
    scope = 'https://www.googleapis.com/auth/analytics'
    key_file_location = 'client_secrets.json'

    # Authenticate and construct service.
    analytics = get_service(
            api_name='analytics',
            api_version='v3',
            scopes=[scope],
            key_file_location=key_file_location)

    try:
        media = MediaFileUpload(filepath,
                                mimetype='application/octet-stream',
                                resumable=False)
        daily_upload = analytics.management().uploads().uploadData(
            accountId='119798097',
            webPropertyId='UA-119798097-4',
            customDataSourceId='89-6YC5ZSG6RheXop3nc7g',
            media_body=media).execute()
        print 'File uploaded to Google Analytics ...'

    except TypeError, error:
        # Handle errors in constructing a query.
        print 'There was an error in constructing your query : %s' % error

    except HttpError, error:
        # Handle API errors.
        print ('There was an API error : %s : %s' %
                (error.resp.status, error.resp.reason))



def get_service(api_name, api_version, scopes, key_file_location):
    """Get a service that communicates to a Google API.

    Args:
        api_name: The name of the api to connect to.
        api_version: The api version to connect to.
        scopes: A list auth scopes to authorize for the application.
        key_file_location: The path to a valid service account JSON key file.

    Returns:
        A service that is connected to the specified API.
    """

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
            'client_secrets.json', scopes=scopes)

    # Build the service object.
    service = build(api_name, api_version, credentials=credentials)

    return service
# if __name__ == '__main__':
#     main()
