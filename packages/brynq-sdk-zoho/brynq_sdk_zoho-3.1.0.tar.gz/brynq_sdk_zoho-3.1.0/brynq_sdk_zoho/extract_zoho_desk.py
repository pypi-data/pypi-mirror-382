import os
import sys
import pandas as pd
from typing import Union, List, Optional, Literal
import requests
import json
from brynq_sdk_brynq import BrynQ

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(basedir)


class ExtractZohoDesk(BrynQ):

    def __init__(self, system_type: Optional[Literal['source', 'target']] = None, debug: bool = False):
        """
        For the full documentation, see: https://avisi-apps.gitbook.io/tracket/api/
        """
        super().__init__()
        self.headers = self._get_authentication(system_type)
        self.base_url = "https://desk.zoho.com/api/v1/"
        self.payload = {}
        self.timeout = 3600

    def _get_authentication(self, system_type):
        """
        Get the credentials for the Tracket API from BrynQ, with those credentials, get the access_token for Tracket.
        Return the headers with the access_token.
        """
        # Get credentials from BrynQ
        credentials = self.interfaces.credentials.get(system="zoho-desk", system_type=system_type)
        credentials = credentials.get('data')

        # With those credentials, get the access_token from Tracket
        headers = {
            'Authorization': f'Zoho-oauthtoken {credentials.get("access_token")}'
        }
        return headers

    def get_zoho_accounts(self, query_params=""):
        """
        This function gets all the accounts from zoho and saves them as df_zoho_accounts
        :return: df_zoho_accounts
        """
        base_url = f"{self.base_url}accounts"
        return self._multiple_calls(base_url, query_params)

    def get_zoho_agents(self, query_params=""):
        """
        This function gets the user data from zoho and saves the data to df_zoho_users
        :return:
        """
        base_url = f"{self.base_url}agents"
        return self._multiple_calls(base_url, query_params)

    def get_zoho_agent(self, agent_id, query_params=""):
        """
        This function gets the user data from zoho and saves the data to df_zoho_users
        :return:
        """
        url = f"{self.base_url}agents/{agent_id}?{query_params}"
        return self._single_call(url)

    def get_zoho_contacts(self, query_params=""):
        """
        This function gets the zoho contact information from zoho desk and saves the data to df_zoho_contacts
        :return:
        """
        base_url = f"{self.base_url}contacts"
        return self._multiple_calls(base_url, query_params)

    def get_recent_zoho_tickets(self, query_params=""):
        """
        This function gets the newest 100 tickets form Zoho-Desk
        :return:
        """
        url = f"{self.base_url}tickets?limit=100&from=0&{query_params}"
        return self._single_call(url)

    def get_all_zoho_tickets(self, query_params: str = "") -> pd.DataFrame:
        """
        This function gets the zoho contact information from zoho desk and saves the data to df_zoho_contacts
        :return:
        """
        base_url = f"{self.base_url}tickets"
        return self._multiple_calls(base_url, query_params)

    def get_archived_zoho_tickets(self, query_params: str = "") -> pd.DataFrame:
        """
        This function gets the zoho contact information from zoho desk and saves the data to df_zoho_contacts
        :return:
        """
        base_url = f"{self.base_url}tickets/archivedTickets"
        return self._multiple_calls(base_url, query_params)

    def get_active_ticket_timers(self, tickets: pd.DataFrame, query_params: str = "") -> pd.DataFrame:
        """=
        This function gets all the active ticket timers from the tickets given in the tickets dataframe.
        :param tickets: dataframe with the ticket_id's
        :param query_params: query parameters for the API call
        :return: pd.DataFrame with the ticket timers
        """
        df = pd.DataFrame()
        count = 0
        for index, ticket in tickets.iterrows():
            count = count + 1
            print(f"Checking for ticket number {ticket.ticket_id}. ticket {count} / " + str(
                len(tickets.index)))
            url = f"{self.base_url}tickets/{ticket.ticket_id}/activeTimer?{query_params}"
            df_temp = self._single_call(url)
            df_temp['ticket_id'] = ticket.ticket_id
            df_temp['link'] = ticket.link
            df_temp['ticket_number'] = ticket.ticket_number
            df = pd.concat([df, df_temp])
        df = df.reset_index(drop=True)
        return df

    def get_zoho_ticket_timers(self, tickets, query_params=""):
        """
        This function gets all the ticket timers from the recent tickets if there already exists a database. Otherwise,
        it will get all the ticket timers. the ticket timers are saved to df_zoho_ticket_timers
        :return:
        """
        df = pd.DataFrame()
        count = 0
        for ticket_id in tickets["ticket_id"]:
            count = count + 1
            print(f"Checking for ticket number {ticket_id}. ticket {count} / " + str(
                len(tickets.index)))
            url = f"{self.base_url}tickets/{ticket_id}/timeEntry?{query_params}"
            df_temp = self._single_call(url)
            df = pd.concat([df, df_temp])
        df = df.reset_index(drop=True)
        return df

    def _multiple_calls(self, base_url, query_params) -> pd.DataFrame:
        """
        This function helps the API calls to do multiple calls in one function
        :return:
        """
        df = pd.DataFrame()
        end_of_loop = False
        offset = 1
        while not end_of_loop:
            url = f"{base_url}?from={offset}&limit=90&{query_params}"
            df_temp = self._single_call(url)
            df = pd.concat([df_temp, df])
            if len(df_temp) != 90:
                end_of_loop = True
            else:
                offset += 90
        return df

    def _single_call(self, url: str) -> pd.DataFrame:
        """
        This function helps the API calls to do a single call in one function
        :return:
        """
        response = requests.request("GET", url, headers=self.headers, data=self.payload, timeout=self.timeout)
        if response.status_code == 401:
            response = requests.request("GET", url, headers=self.headers, data=self.payload, timeout=self.timeout)
        if response.status_code == 200:
            df = response.json()
            if 'data' in df:
                df = pd.json_normalize(df['data'])
            else:
                df = pd.json_normalize(df)
            return df
        elif response.status_code == 204:
            return pd.DataFrame()
        else:
            raise Exception(response.text)

    def get_zoho_articles(self, exclude_category_ids: list = []) -> list:
        """
        Retrieves all Zoho articles, excluding articles with specified category ID
        Category ID's can be easily found in your KB-Admin in the link of any article.
        """
        limit = 50
        offset = 1
        all_articles = []

        while True:
            url = f'{self.base_url}articles'
            params = {"status": "Draft,Published", "from": offset, "limit": limit}
            response = requests.get(url, headers=self.headers, params=params, timeout=120)
            if response.status_code == 200:
                articles = response.json().get('data', [])
                if not articles:
                    break

                # Filter out articles with the excluded category ID
                filtered_articles = []
                for article in articles:
                    article_category_id = article.get('categoryId')
                    locale = article.get('locale', "")
                    if article_category_id not in exclude_category_ids and locale == "nl":
                        filtered_articles.append(article)

                all_articles.extend(filtered_articles)

                if len(articles) < limit:
                    break
            else:
                error_text = response.text
                all_articles.insert("Failed to retrieve Zoho articles, status: {response.status_code}, body: {error_text}")
            offset += limit
        return all_articles

    def get_base_article_by_id(self, article_id: str) -> dict:
        """
        Retrieves the base (non-versioned) Zoho article by ID.
        """
        try:
            detail_url = f"{self.base_url}articles/{article_id}"
            response = requests.get(detail_url, headers=self.headers, timeout=60)
            if response.status_code == 200:
                return response.json()
            message = f"Failed to retrieve base article for article ID: {article_id}, status: {response.status_code}"
            return message
        except Exception as e:
            message = f"Error getting base article by id: {e}"
            return message

    def get_zoho_article_latest(self, zoho_article: dict) -> dict:
        """
        Retrieves detailed article data from Zoho Desk using the base article object.
        Uses the article's id and, if available, its latestVersion to fetch the right version.
        """
        try:
            article_id = zoho_article.get("id")
            if not article_id:
                message = "Error: No article id provided in base article object."
                return message

            latest_version = zoho_article.get("latestVersion")

            if latest_version:
                versioned_article_url = f"{self.base_url}articles/{article_id}?version={latest_version}"
                version_response = requests.get(versioned_article_url, headers=self.headers, timeout=60)
                if version_response.status_code == 200:
                    return version_response.json()
                message = f"Failed to retrieve versioned article data, status: {version_response.status_code}"
                return message

            detail_url = f"{self.base_url}articles/{article_id}"
            response = requests.get(detail_url, headers=self.headers, timeout=60)
            if response.status_code == 200:
                article_data = response.json()
                print(f"Retrieved detailed article data for article ID: {article_id}")
                return article_data
            else:
                message = f"Failed to retrieve versioned article data, status: {version_response.status_code}"
                return message
        except Exception as e:
            message = "Retrieving latest Zoho Article Failed."
            return message
