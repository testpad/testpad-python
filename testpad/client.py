from http import HTTPMethod, HTTPStatus
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urljoin

from requests import Response, Session

from . import models
from ._const import DEFAULT_USER_AGENT, TESTPAD_API
from ._utils import parse_folder_contents
from .exceptions import (
    ActionNotAllowed,
    APIServerError,
    BadRequest,
    IncorrectMethod,
    NotFound,
    RateLimitExceeded,
    UnexpectedResponse,
)

JsonSerializable = Union[Dict[str, Any], List[Any]]


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

        if api_url is None:
            api_url = TESTPAD_API
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

    # ---
    # HTTP utility methods
    # ---

    def _request(
        self,
        method: str,
        path: str,
        *accepted_responses: HTTPStatus,
        data: Optional[JsonSerializable] = None,
        query_params: Optional[Dict[str, str]] = None,
    ) -> Response:
        url = urljoin(self._base_url, path)
        resp = self._session.request(
            str(method), url, params=query_params, json=data, allow_redirects=True
        )

        if resp.status_code in accepted_responses:
            return resp

        if resp.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN):
            raise ActionNotAllowed(resp)

        if resp.status_code == HTTPStatus.BAD_REQUEST:
            raise BadRequest(resp)

        if resp.status_code == HTTPStatus.NOT_FOUND:
            raise NotFound(resp)

        if resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED:
            raise IncorrectMethod(resp)

        if resp.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            raise RateLimitExceeded(resp)

        if resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
            raise APIServerError(resp)

        raise UnexpectedResponse(resp)

    def _get(self, path: str, params: Dict[str, str] = None) -> Dict[str, Any]:
        return self._request(
            HTTPMethod.GET, path, HTTPStatus.OK, query_params=params
        ).json()

    def _put(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request(
            HTTPMethod.PUT, path, HTTPStatus.CREATED, HTTPStatus.OK, data=data
        ).json()

    def _post(
        self, path: str, data: JsonSerializable, *, params: dict[str, str] = None
    ) -> Dict[str, Any]:
        return self._request(
            HTTPMethod.POST,
            path,
            HTTPStatus.OK,
            HTTPStatus.CREATED,
            query_params=params,
            data=data,
        ).json()

    def _patch(self, path: str, data: Dict[str, str]) -> Dict[str, Any]:
        return self._request(HTTPMethod.PATCH, path, HTTPStatus.OK, data=data).json()

    def _delete(self, path: str) -> Response:
        return self._request(HTTPMethod.DELETE, path, HTTPStatus.NO_CONTENT)

    # ---
    # Utilities
    # ---

    def whoami(self) -> Tuple[models.Company, models.ApiKey]:
        """
        Utility method to get information about authentication being used for requests.

        :return:
            An object containing the information of the company owning the API key, and information
            about the API key making the request.
        """
        data = self._get("whoami")
        company = models.Company(**data["company"])
        key = models.ApiKey(**data["apikey"])
        return company, key

    # ---
    # Projects
    # ---

    def get_project(self, project_id: int) -> models.Project:
        data = self._get(f"projects/{project_id}")
        proj = data["project"]
        return models.Project(**proj)

    def list_projects(self) -> List[models.Project]:
        data = self._get("projects")
        return [models.Project(**proj) for proj in data["projects"]]

    def get_project_contents(
        self, project_id: int
    ) -> list[Union[models.Folder, models.Script, models.Note]]:
        """
        :param project_id:
            The project to get the contents of
        :return:
            The list of contents of the project
        """
        data = self._get(f"projects/{project_id}/folders")
        if len(data["folders"]) > 0:
            return [parse_folder_contents(obj) for obj in data["folders"]]
        return []

    # ---
    # Project notes
    # ---

    def list_project_notes(self, project_id: int) -> List[models.Note]:
        data = self._get(f"projects/{project_id}/notes")
        return [models.Note(**note) for note in data["notes"]]

    def add_project_note(self, project_id: int, name: str) -> models.Note:
        data = self._post(f"projects/{project_id}/notes", {"name": name})
        return models.Note(**data)

    def update_project_note(
        self, project_id: int, note_id: str, name: str
    ) -> models.Note:
        """
        Replaces the text in a note with the new contents given - the "name" of the note is the text in the note.

        :param project_id:
            Which project this note belongs to
        :param note_id:
            The ID of the note
        :param name:
            The contents of the note
        :return:
            An updated Note object with the new contents
        """
        data = self._patch(f"projects/{project_id}/notes/{note_id}", {"name": name})
        return models.Note(**data)

    # def delete_project_note(self, project_id: int, note_id: str):
    #     self._delete(f"projects/{project_id}/notes/{note_id}")

    # ---
    # Folders
    # ---

    def get_folder(
        self, project_id: int, folder_id: str, subfolders: bool = True
    ) -> models.Folder:
        url = f"projects/{project_id}/folders/{folder_id}"
        if not subfolders:
            url = f"{url}?subfolders=none"
        data = self._get(url)
        return parse_folder_contents(data["folder"])

    def rename_folder(
        self, project_id: int, folder_id: str, name: str
    ) -> models.Folder:
        data = self._patch(
            f"projects/{project_id}/folders/{folder_id}",
            {"name": name},
        )

        return parse_folder_contents(data["folder"])

    def create_folder(
        self,
        project_id: int,
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
        data = self._post(endpoint, data={"name": name, "insert": insert})
        return parse_folder_contents(data["folder"])

    # ---
    # Folder notes
    # ---

    def list_folder_notes(self, project_id: int, folder_id: str) -> List[models.Note]:
        data = self._get(f"projects/{project_id}/folders/{folder_id}/notes")
        return [models.Note(**note) for note in data["notes"]]

    def add_folder_note(
        self, project_id: int, folder_id: str, name: str
    ) -> models.Note:
        data = self._post(
            f"projects/{project_id}/folders/{folder_id}/notes", {"name": name}
        )
        return models.Note(**data)

    def update_folder_note(
        self, project_id: int, folder_id: str, note_id: str, name: str
    ) -> models.Note:
        data = self._patch(
            f"projects/{project_id}/folders/{folder_id}/notes/{note_id}", {"name": name}
        )
        return models.Note(**data)

    # ---
    # Scripts
    # ---

    def create_script(
        self,
        project_id: int,
        name: str,
        *,
        description: str = None,
        in_folder: str = None,
        tests: List[models.Test] = None,
    ) -> models.Script:
        """

        :param project_id:
            required: The project in which to create this script
        :param name:
            required: The name of the script to create
        :param description:
            optional: A description of the script
        :param in_folder:
            optional: The folder to create the script in. If omitted, the script will be
            placed in the root of the project
        :param tests:

        :return:
        """
        if in_folder is None:
            endpoint = f"projects/{project_id}/scripts"
        else:
            endpoint = f"projects/{project_id}/folders/{in_folder}/scripts"

        payload = {"name": name}
        if description is not None:
            payload["description"] = description

        data = self._post(endpoint, payload)
        return parse_folder_contents(data["script"])

    def get_script(self, script_id: int) -> models.Script:
        data = self._get(f"scripts/{script_id}")
        return models.Script(**data["script"])

    def update_script(
        self, script_id: int, *, name: str = None, description: str = None
    ) -> models.Script:
        if name is None and description is None:
            raise ValueError("Must provide at least one of name or description")
        payload = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        data = self._patch(f"scripts/{script_id}", payload)
        return models.Script(**data["script"])

    # ---
    # Tests (also called "cases")
    # ---

    def append_test(
        self,
        script_id: int,
        test_text: str,
        indent: int = 0,
        tags: List[str] = None,
        notes: str = None,
    ) -> models.Test:
        """
        This will simply append the given test to the end of an existing script

        :param script_id:
            The ID of the script to append the test to
        :param test_text:
            The text of the test to add
        :param tags:
            Optionally, include tags for the test
        :param notes:
            Optionally, include notes for the test
        :param indent:
            Whether to indent the test or not. This must be the same, smaller, or one larger than
            the previous test in the script
        :return:
            An object containing the full details of the created test
        """
        # convert into the format expected by the API, from the more user-friendly version here
        tags = "" if tags is None else " ".join(tags)
        data = self._post(
            f"scripts/{script_id}/tests",
            data=[{"text": test_text, "indent": indent, "notes": notes, "tags": tags}],
        )
        return models.Test(**data["tests"][0])

    def get_test(self, script_id: int, test_id: int) -> models.Test:
        data = self._get(f"scripts/{script_id}/tests/{test_id}")
        return models.Test(**data["test"])

    def update_test(
        self,
        script_id: int,
        test_id: int,
        test_text: str = None,
        *,
        tags: List[str] = None,
        notes: str = None,
        indent: int = None,
    ) -> models.Test:
        new_data = {"text": test_text, "indent": indent, "tags": tags, "notes": notes}
        data = self._patch(f"scripts/{script_id}/tests/{test_id}", data=new_data)
        return models.Test(**data["test"])

    def list_tests(self, script_id: int) -> List[models.Test]:
        data = self._get(f"scripts/{script_id}/tests")
        return [models.Test(**test) for test in data["tests"]]

    # def delete_test(self, script_id: int, test_id: int):
    #     self._delete(f"scripts/{script_id}/tests/{test_id}")

    # ---
    # Runs
    # ---

    def get_run(self, script_id: int, run_id: int) -> models.Run:
        data = self._get(f"scripts/{script_id}/runs/{run_id}")
        return models.Run(**data["run"])

    def create_run(
        self,
        script_id: int,
        headers: dict[str, str] = None,
        results: dict[str, models.TestResult] = None,
    ) -> models.Run:
        return self._set_run(script_id, headers, results)

    def retest_run(
        self,
        script_id: int,
        retest_of_id: int,
        headers: dict[str, str] = None,
        results: dict[str, models.TestResult] = None,
    ) -> models.Run:
        return self._set_run(script_id, headers, results, retest_of_id)

    def _set_run(
        self,
        script_id: int,
        headers: dict[str, str] = None,
        results: dict[str, models.TestResult] = None,
        retest_id: int = None,
    ) -> models.Run:
        payload = {
            "headers": headers,
            "results": results,
        }
        params = {"retest": retest_id} if retest_id is not None else None
        data = self._post(f"scripts/{script_id}/runs", data=payload, params=params)
        return models.Run(**data["run"])
