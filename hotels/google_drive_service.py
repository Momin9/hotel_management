import json
import os
from io import BytesIO
from django.core.files.storage import default_storage
from django.conf import settings

try:
    from googleapiclient.discovery import build
    from google.oauth2 import service_account
    from googleapiclient.http import MediaIoBaseUpload
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False

class GoogleDriveService:
    def __init__(self, hotel):
        self.hotel = hotel
        self.service = None
        
        if not GOOGLE_DRIVE_AVAILABLE:
            raise Exception("Google Drive API libraries not installed. Run: pip install google-api-python-client google-auth")
        
        if not hotel.google_drive_enabled:
            raise Exception("Google Drive integration is not enabled for this hotel")
        
        if not hotel.google_service_account_key or not hotel.google_drive_folder_id:
            raise Exception("Google Drive configuration is incomplete")
        
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Drive API using service account"""
        try:
            # Parse the JSON key
            service_account_info = json.loads(self.hotel.google_service_account_key)
            
            # Create credentials
            credentials = service_account.Credentials.from_service_account_info(
                service_account_info,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            
            # Build the service
            self.service = build('drive', 'v3', credentials=credentials)
            
        except json.JSONDecodeError:
            raise Exception("Invalid Google Service Account JSON key")
        except Exception as e:
            raise Exception(f"Failed to authenticate with Google Drive: {str(e)}")
    
    def upload_file(self, file_obj, filename, guest_name=None):
        """Upload file to Google Drive"""
        try:
            # Create a subfolder for the guest if guest_name is provided
            folder_id = self.hotel.google_drive_folder_id
            
            if guest_name:
                # Create or get guest folder
                guest_folder_name = f"Guest_{guest_name.replace(' ', '_')}"
                folder_id = self._get_or_create_folder(guest_folder_name, self.hotel.google_drive_folder_id)
            
            # Prepare file metadata
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            
            # Create media upload object
            file_obj.seek(0)  # Reset file pointer
            media = MediaIoBaseUpload(
                BytesIO(file_obj.read()),
                mimetype='image/jpeg',  # Adjust based on file type
                resumable=True
            )
            
            # Upload file
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink'
            ).execute()
            
            # Share with hotel email if provided
            if self.hotel.google_drive_share_email:
                self._share_file(file['id'], self.hotel.google_drive_share_email)
            
            return {
                'file_id': file['id'],
                'file_name': file['name'],
                'web_view_link': file['webViewLink']
            }
            
        except Exception as e:
            raise Exception(f"Failed to upload file to Google Drive: {str(e)}")
    
    def _get_or_create_folder(self, folder_name, parent_folder_id):
        """Get existing folder or create new one"""
        try:
            # Search for existing folder
            query = f"name='{folder_name}' and parents in '{parent_folder_id}' and mimeType='application/vnd.google-apps.folder'"
            results = self.service.files().list(q=query).execute()
            items = results.get('files', [])
            
            if items:
                return items[0]['id']
            
            # Create new folder
            folder_metadata = {
                'name': folder_name,
                'parents': [parent_folder_id],
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            folder = self.service.files().create(body=folder_metadata, fields='id').execute()
            return folder['id']
            
        except Exception as e:
            raise Exception(f"Failed to create folder: {str(e)}")
    
    def _share_file(self, file_id, email):
        """Share file with specified email"""
        try:
            permission = {
                'type': 'user',
                'role': 'reader',
                'emailAddress': email
            }
            
            self.service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()
            
        except Exception as e:
            # Don't fail the upload if sharing fails
            print(f"Warning: Failed to share file: {str(e)}")

def upload_to_google_drive(file_obj, filename, hotel, guest_name=None):
    """Helper function to upload file to Google Drive"""
    try:
        drive_service = GoogleDriveService(hotel)
        return drive_service.upload_file(file_obj, filename, guest_name)
    except Exception as e:
        raise Exception(f"Google Drive upload failed: {str(e)}")