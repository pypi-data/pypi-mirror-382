"""
Access to the Gravity Forms API.

Two required environment variables:
- CONSUMER_KEY
- CONSUMER_SECRET
"""

import json
import os
from typing import Optional, Union

import oauthlib
from requests.exceptions import RequestException
from requests_oauthlib import OAuth1Session

from sat.logs import SATLogger

logger = SATLogger(name=__name__)


class Form:
    """
    A form object from GravityForms.
    """

    id: Union[int, str]
    title: str
    description: str
    date_created: str
    is_active: bool
    is_trash: bool
    version: str
    details: dict = {}

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", "")
        self.title = kwargs.get("title", "")
        self.description = kwargs.get("description", "")
        self.date_created = kwargs.get("date_created", "")
        self.date_updated = kwargs.get("date_updated", "")
        self.is_active = kwargs.get("is_active", False)
        self.is_trash = kwargs.get("is_trash", False)
        self.version = kwargs.get("version", "")

        # Storing additional kwargs in a dictionary attribute called details
        self.details = {
            key: value
            for key, value in kwargs.items()
            if key
            not in [
                "id",
                "title",
                "description",
                "date_created",
                "is_active",
                "is_trash",
                "version",
            ]
        }


class Entry:
    """
    An entry object from GravityForms.
    """

    id: Union[int, str]
    form_id: str
    created_by: str
    date_created: str
    date_updated: str
    is_starred: bool
    is_read: bool
    ip: str
    source_url: str
    post_id: int
    user_agent: str
    status: str
    is_fulfilled: bool
    details: dict = {}

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", "")
        self.form_id = kwargs.get("form_id", "")
        self.created_by = kwargs.get("created_by", "")
        self.date_created = kwargs.get("date_created", "")
        self.date_updated = kwargs.get("date_updated", "")
        self.is_starred = kwargs.get("is_starred", False)
        self.is_read = kwargs.get("is_read", False)
        self.ip = kwargs.get("ip", "")
        self.source_url = kwargs.get("source_url", "")
        self.post_id = kwargs.get("post_id", 0)
        self.user_agent = kwargs.get("user_agent", "")
        self.status = kwargs.get("status", "")
        self.is_fulfilled = kwargs.get("is_fulfilled", False)

        # Storing additional kwargs in a dictionary attribute called details
        self.details = {
            key: value
            for key, value in kwargs.items()
            if key
            not in [
                "id",
                "form_id",
                "created_by",
                "date_created",
                "is_starred",
                "is_read",
                "ip",
                "source_url",
                "post_id",
                "user_agent",
                "status",
                "is_fulfilled",
            ]
        }


class GravityForms:
    """
    A helper class for connecting to and calling the Gravity Forms API.
    """

    session = None
    base_url = None
    page_size = 50

    def __init__(self, **settings) -> None:
        """
        Configure the connection to Gravity Forms.

        Optional Parameters:
        - consumer_key: Key for accessing the Gravity Forms API.
        - consumer_secret: Secret for authenticating with the Gravity Forms API.
        - base_url: An alternate base URL, if different than the default.
        """
        consumer_key = settings.get("consumer_key", os.getenv("GRAVITY_FORMS_CONSUMER_KEY"))
        consumer_secret = settings.get(
            "consumer_secret", os.getenv("GRAVITY_FORMS_CONSUMER_SECRET")
        )
        self.base_url = settings.get("base_url", os.getenv("GRAVITY_FORMS_BASE_URL"))
        self.page_size = settings.get("page_size", self.page_size)

        if not all([consumer_key, consumer_secret, self.base_url]):
            raise ValueError(
                "A consumer_key, consumer_secret, and base_url are required as either environment "
                "variables or parameters."
            )

        self.session = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            signature_type=oauthlib.oauth1.SIGNATURE_TYPE_QUERY,
        )

    @staticmethod
    def field_filters(keys: [tuple]) -> str:
        """
        Generates the appropriate JSON string for the field_filters parameter.

        keys: list of tuples (key, value, operator)
        'search={"field_filters":
            [
                {"key":2,"value":"squiffy","operator":"contains"},
                {"key":1.3,"value":"squiffy","operator":"contains"}
            ]
        }'
        """
        field_filters = []
        for key, value, operator in keys:
            field_filters.append({"key": key, "value": value, "operator": operator})
        return json.dumps({"field_filters": field_filters})

    def get(self, endpoint: str, params: Optional[dict] = None):
        """
        Submits a GET request to a specified endpoint.

        Parameters:
        - endpoint: The string representing the endpoint URL. (ex. "/forms")
        """

        param_string: str = "?"
        if params:
            for key, value in params.items():
                param_string += f"{key}={value}&"
        try:
            response = self.session.get(self.base_url + endpoint + param_string)
            return response.json()
        except RequestException as e:
            raise e

    def get_forms(self, page: int = 1, page_size: int = 20):
        """
        Gets and returns a list of forms.
        """
        response = self.get(
            "/forms", params={"paging[current_page]": page, "paging[page_size]": page_size}
        )
        forms = []
        for form_id in response:
            forms.append(Form(**response[form_id]))
        return forms

    def get_form(self, form_id: int):
        """
        Gets and returns a form.

        Parameters:
        - form_id: The ID of the form.
        """
        response = self.get(f"/forms/{form_id}")
        entry = Form(**response)
        return entry

    def get_entries(self, page: int = 1, page_size: int = 20, form_id: Optional[int] = None):
        """
        Gets and returns a list of entries.
        """
        url = "/entries"
        if form_id:
            url = f"/forms/{form_id}/entries"

        response = self.get(
            url, params={"paging[current_page]": page, "paging[page_size]": page_size}
        )
        entries = []
        for entry in response["entries"]:
            entries.append(Entry(**entry))
        return entries

    def get_entry(self, entry_id: int):
        """
        Gets and returns an entry.

        Parameters:
        - form_id: The ID of the entry.
        """
        response = self.get(f"/entries/{entry_id}")
        entry = Entry(**response)
        return entry

    def search_entry(self, field_filters: str, form_id: int, page: int = 1, page_size: int = 20):
        response = self.get(
            f"/forms/{form_id}/entries",
            params={
                "search": field_filters,
                "paging[current_page]": page,
                "paging[page_size]": page_size,
            },
        )
        entries = []
        for entry in response.get("entries"):
            entries.append(Entry(**entry))
        return entries
