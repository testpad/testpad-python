import sys
from http import HTTPStatus
from importlib.metadata import version
from typing import Dict, List, Optional, Tuple, Union
from urllib.parse import urljoin

from requests import Response, Session

from . import models
from .exceptions import ActionNotAllowed, BadRequest, NotFound, UnexpectedResponse

VERSION = str(version("testpad"))
_python_version = ".".join(str(v) for v in sys.version_info[:2])
_requests_version = str(version("requests"))

# versioning is collected for anonymous usage statistics
DEFAULT_USER_AGENT = (
    f"testpad-python [t{VERSION}::p{_python_version}::r{_requests_version}]"
)

TESTPAD_API = "https://api.testpad.com/api/v1/"


class Testpad:

    def __init__(
        self,
        token: str,
        *,
        api_url: str = TESTPAD_API,
        user_agent: str = DEFAULT_USER_AGENT,
        session: Session = None,
    ):
        """
        Required parameters:

        :param token:
            The API token made at https://testpad.com/ to access the API

        Optional parameters:

        :param api_url:
            The base API URL. The default is for live testpad.com, but you can switch this for testing and development
        :param user_agent:
            Override the default user agent used to send in requests
        :param session:
            Use this to override the default requests Session object
        """
        self._token = token

        if not api_url.endswith("/"):
            api_url += "/"
        self._base_url = api_url

        self._session = session or Session()

        # set default headers including auth
        self._session.headers.update(
            {
                "User-Agent": user_agent,
                "Authorization": f"apikey {self._token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    def _request(
        self,
        method: str,
        path: str,
        *accepted_responses: HTTPStatus,
        data: Optional[Dict[str, str]] = None,
        query_params: Optional[Dict[str, str]] = None,
    ) -> Response:
        url = urljoin(self._base_url, path)
        resp = self._session.request(
            method, url, params=query_params, json=data, allow_redirects=True
        )

        if resp.status_code in accepted_responses:
            return resp

        if resp.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN):
            raise ActionNotAllowed(resp)

        if resp.status_code == HTTPStatus.BAD_REQUEST:
            raise BadRequest(resp)

        if resp.status_code == HTTPStatus.NOT_FOUND:
            raise NotFound(resp)

        raise UnexpectedResponse(resp)

    def _get(self, path: str, params: dict[str, str] = None) -> Response:
        return self._request("GET", path, HTTPStatus.OK, query_params=params)

    def _put(self, path: str, data: dict[str, str]) -> Response:
        return self._request("PUT", path, HTTPStatus.CREATED, data=data)

    def _post(self, path: str, data: dict[str, str]) -> Response:
        return self._request("POST", path, HTTPStatus.OK, data=data)

    def _delete(self, path: str) -> Response:
        return self._request("DELETE", path, HTTPStatus.NO_CONTENT)

    # ---
    # Utilities
    # ---

    def whoami(self) -> Tuple[models.Company, models.ApiKey]:
        data = self._get("whoami").json()
        company = models.Company(**data["company"])
        key = models.ApiKey(**data["apikey"])
        return company, key

    # ---
    # Projects
    # ---

    def get_project(self, project_id: str) -> models.Project:
        data = self._get(f"projects/{project_id}").json()
        return models.Project(**data)

    def list_projects(self) -> List[models.Project]:
        data = self._get("projects").json()
        return [models.Project(**proj) for proj in data["projects"]]

    def get_project_folders(self, project_id: str) -> models.Folder:
        """
        Note: this actually lists all contents, including folders, scripts and notes

        :param project_id:
            The project to get the contents of
        :return:
            The root folder of the project, and all of its contents
        """
        data = self._get(f"projects/{project_id}/folders").json()
        return models.parse_data(data["folders"])

    # ---
    # Project notes
    # ---

    def list_project_notes(self, project_id: str) -> List[models.Note]:
        data = self._get(f"projects/{project_id}/notes").json()
        return [models.Note(**note) for note in data["notes"]]

    def add_project_note(self, project_id: str, name: str) -> models.Note:
        data = self._put(f"projects/{project_id}/notes", {"name": name}).json()
        return models.Note(**data)

    def update_project_note(
        self, project_id: str, note_id: str, name: str
    ) -> models.Note:
        data = self._post(
            f"projects/{project_id}/notes/{note_id}", {"name": name}
        ).json()
        return models.Note(**data)

    def delete_project_note(self, project_id: str, note_id: str):
        self._delete(f"projects/{project_id}/notes/{note_id}")

    # ---
    # Folders
    # ---

    def get_folder(self, project_id: str, folder_id: str) -> models.Folder:
        data = self._get(f"projects/{project_id}/folders/{folder_id}").json()
        return models.parse_data(data["folder"])

    def rename_folder(
        self, project_id: str, folder_id: str, name: str
    ) -> models.Folder:
        resp = self._post(
            f"projects/{project_id}/folders/{folder_id}",
            {"name": name},
        )

        data = resp.json()
        return models.parse_data(data["folder"])

    def create_folder(
        self,
        project_id: str,
        name: str,
        in_folder: str = None,
        insert: Union[int, str] = 0,
    ) -> models.Folder:
        """

        :param project_id:
            required: The project in which to create this folder
        :param name:
            required: The name of the folder
        :param in_folder:
            optional: The parent folder for the new folder, or if none, will be placed in the root of the project
        :param insert:
            optional Where to place this folder - can be a numerical index, or one of 'first', 'last'
        :return:
        """
        endpoint = f"projects/{project_id}/folders"
        if in_folder is not None:
            endpoint = f"{endpoint}/{in_folder}/folders"
        data = self._put(endpoint, data={"name": name, "insert": insert}).json()
        return models.parse_data(data["folder"])

    # ---
    # Scripts
    # ---

    def create_script(
        self, project_id: str, name: str, in_folder: str = None
    ) -> models.Script:
        pass
