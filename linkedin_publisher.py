import os
import requests
from dotenv import load_dotenv

load_dotenv()

class LinkedInPublisher:
    def __init__(self, access_token=None):
        self.access_token = access_token or os.getenv("linkedin_access_token")
        if not self.access_token:
            raise ValueError("LinkedIn access token not found in environment variables.")
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json"
        }

    def get_user_info(self):
        """Fetch LinkedIn user profile and return user URN (urn:li:person:ID)."""
        url = "https://api.linkedin.com/v2/userinfo"
        response = requests.get(url, headers={"Authorization": f"Bearer {self.access_token}"})
        if response.status_code == 200:
            data = response.json()
            sub_id = data.get("sub")
            if sub_id:
                return f"urn:li:person:{sub_id}", data
        
        # Fallback to /v2/me if /userinfo doesn't return sub
        url_me = "https://api.linkedin.com/v2/me"
        response_me = requests.get(url_me, headers=self.headers)
        if response_me.status_code == 200:
            data_me = response_me.json()
            user_id = data_me.get("id")
            return f"urn:li:person:{user_id}", data_me
            
        raise Exception(f"Failed to fetch LinkedIn user info: {response.status_code} - {response.text}")

    def register_image_upload(self, owner_urn):
        """Register image upload request with LinkedIn Digital Media API."""
        url = "https://api.linkedin.com/v2/assets?action=registerUpload"
        body = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": owner_urn,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }
        response = requests.post(url, headers=self.headers, json=body)
        if response.status_code == 200:
            data = response.json()
            upload_url = data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
            asset_urn = data["value"]["asset"]
            return upload_url, asset_urn
        else:
            raise Exception(f"Failed to register image upload: {response.status_code} - {response.text}")

    def upload_image_file(self, upload_url, image_path):
        """Upload image binary data to LinkedIn upload URL."""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        with open(image_path, "rb") as image_file:
            response = requests.put(upload_url, headers=headers, data=image_file)
        
        if response.status_code in [200, 201]:
            return True
        else:
            raise Exception(f"Failed to upload image binary: {response.status_code} - {response.text}")

    def publish_feed_post(self, author_urn, text_content, asset_urn=None):
        """Publish a UGC feed post to LinkedIn with optional attached image asset."""
        url = "https://api.linkedin.com/v2/ugcPosts"
        
        share_content = {
            "shareCommentary": {
                "text": text_content
            },
            "shareMediaCategory": "IMAGE" if asset_urn else "NONE"
        }
        
        if asset_urn:
            share_content["media"] = [
                {
                    "status": "READY",
                    "description": {"text": "Cover Image"},
                    "media": asset_urn,
                    "title": {"text": "Tech & Business Pulse"}
                }
            ]

        body = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": share_content
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        response = requests.post(url, headers=self.headers, json=body)
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to create UGC post: {response.status_code} - {response.text}")


if __name__ == "__main__":
    # Quick connectivity test
    publisher = LinkedInPublisher()
    urn, profile = publisher.get_user_info()
    print(f"Authenticated LinkedIn User URN: {urn}")
    print(f"User Name: {profile.get('name') or profile.get('localizedFirstName')}")
