import os
import sys
import pandas as pd
from typing import Union, List, Optional, Literal
import requests
import json
import re
from brynq_sdk_brynq import BrynQ
basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(basedir)


class UploadZohoDesk(BrynQ):

    def __init__(self, system_type: Optional[Literal['source', 'target']] = None, debug: bool = False):
        """
        For the full documentation, see: https://avisi-apps.gitbook.io/tracket/api/
        """
        super().__init__()
        self.headers = self._get_authentication(system_type)
        self.base_url = "https://desk.zoho.com/api/v1/"
        self.timeout = 3600

    def _get_authentication(self, system_type):
        """
        Get the credentials for the Traket API from BrynQ, with those credentials, get the access_token for Tracket.
        Return the headers with the access_token.
        """
        # Get credentials from BrynQ
        credentials = self.interfaces.credentials.get(system="zoho-desk", system_type=system_type)
        credentials = credentials.get('data')

        headers = {
            'Authorization': f'Zoho-oauthtoken {credentials.get("access_token")}',
            'Content-Type': 'application/json'
        }
        return headers

    def update_ticket_time_entry(self, ticket_id, time_entry_id, payload):
        """
        This function updates the time entry of a ticket in zoho desk
        :param ticket_id: str
        :param time_entry_id: str
        :param payload: dict
        """
        url = f"{self.base_url}tickets/{ticket_id}/timeEntry/{time_entry_id}"
        response = requests.request("PATCH", url, headers=self.headers, data=json.dumps(payload), timeout=self.timeout)
        return response

    def update_article(self, article_id: str, updated_content: str, category_id: int, status="Draft") -> str:
        """
        Updates the Zoho article with the updated content as a draft.
        Returns the web URL where the draft can be reviewed, or an empty string if the update fails.

        Status can be:
        - Draft
        - Published
        - Review
        - Unpublished
        """
        try:

            payload = {
                "answer": updated_content,
                "status": status
            }
            if category_id is not None:
                payload["categoryId"] = category_id
            update_url = f"{self.base_url}articles/{article_id}"
            update_headers = self.headers

            update_response = requests.patch(update_url, headers=update_headers, data=json.dumps(payload), timeout=60)
            if update_response.status_code == 200:
                update_data = update_response.json()
                web_url = update_data.get("webUrl", "")
                return web_url
            else:
                message = f"Uploading Draft failed. Response: {update_response.status_code}"
                return message
        except Exception as e:
            message = "Uploading Draft failed."
            return message

    def upload_translation(self, translated, article_data, locale = "en-us"):
        try:
            article_id = article_data.get("id")
            title = article_data.get("title")

            url = f"{self.base_url}articles/{article_id}/translations"

            # Get authorId from the article data or use a default
            author_id = article_data.get("authorId") or article_data.get("createdBy", {}).get("id")
            payload = {
                "title" : title,
                "answer" : translated,
                "status" : "Draft",
                "locale" : locale,
                "authorId" : author_id
            }
            response = requests.post(url, headers=self.headers, data=json.dumps(payload), timeout=60)
            if response.status_code == 200:
                update_data = response.json()
                web_url = update_data.get("webUrl", "")
                return web_url
            else:
                url = f"{self.base_url}articles/{article_id}/translations/{locale}"
                payload = {
                "answer" : translated,
                "status" : "Draft"
            }
                response = requests.patch(url, headers=self.headers, data=json.dumps(payload), timeout=60)
                if response.status_code == 200:
                    update_data = response.json()
                    web_url = update_data.get("webUrl", "")
                    return web_url
                else:
                    message = "Uploading Translation failed."
                    return message
        except Exception as e:
                message = "Uploading Translation failed."
                return message
