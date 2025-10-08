import json
from datetime import datetime
import pathlib
import re
import os
import requests
import shutil
import tempfile
from typing import Literal
from sensestreet.auth_header_builder import AuthHeaderBuilder


class SenseStreetClient:
    """
    A class to represent a client for the Sense Street API.
    Attributes
    ----------
    app_id: str
        Id of a client's app.
    api_url: str
        Url of the api to use with the client.
    priv_key_path: str, optional
        Path to the private key.
    pub_key_id: str, optional
        Id of the public key.
    server_id: str, optional,
        Id of the server
    req_timeout_sec: int, optional
        After how many seconds the request will time out.
    pub_key_path: str, optional
        Path to the public key.
    extra_headers: dict
        Extra headers to use when making requests.
    request_args: dict
        Extra arguments to use when making requests.


    Methods
    -------
    ping():
        Sends a ping. Useful for testing network connectivity.

    ping_auth():
        Sends an authorised ping.

    predict_rfqs(conversation, options):
        Predicts RFQs from input converstaion.

    chat_snippet_predict_rfqs(chat_snippet, options):
        Predicts RFQs from chat snippet.

    upload_files_with_conversations(files_paths):
        Uploads files with conversations for processing.

    upload_file_with_bond_ref_data(file_path):
        Uploads files with information about bonds.

    get_processed_conv_file(file_id, output_file_path):
        Download processed conversations.

    get_conv_file_status(file_id):
        Check if conversations sent in file with the file_id have already been processed.



    """

    __version__ = "1.0.16"

    def __init__(
        self,
        app_id,
        api_url,
        priv_key_path=None,
        pub_key_id="default.pub",
        server_id="default",
        req_timeout_sec=500,
        pub_key_path=None,
        extra_headers=None,
        request_args=None,
    ):
        self.api_url = self._prepare_api_url(api_url)
        self.header_builder = AuthHeaderBuilder(app_id=app_id, priv_key_path=priv_key_path, pub_key_id=pub_key_id,
                                                server_id=server_id, pub_key_path=pub_key_path, extra_headers=extra_headers)
        self.req_timeout_sec = req_timeout_sec

        if isinstance(request_args, dict):
            forbidded_keys = {"url", "timeout", "headers"}
            if forbidded_keys_found := forbidded_keys & set(request_args.keys()):
                raise ValueError(
                    f"Not allowed request arguments found {forbidded_keys_found}"
                )

            self.request_args = request_args
        else:
            self.request_args = {}

    def ping(self):
        """Sends a ping. Useful for testing network connectivity."""
        ping_url = f"{self.api_url}/ping"
        res = requests.get(
            url=ping_url,
            timeout=self.req_timeout_sec,
            headers=self._get_headers(),
            **self.request_args,
        )
        res.raise_for_status()
        res_json = json.loads(res.text)
        return res_json

    def ping_auth(self):
        """Sends an authorised ping.
        Once bare ping works, it's useful for testing authorisation.
        """
        ping_auth_url = f"{self.api_url}/ping_auth"
        res = requests.get(
            url=ping_auth_url,
            headers=self._get_headers(),
            timeout=self.req_timeout_sec,
            **self.request_args,
        )
        res.raise_for_status()
        res_json = json.loads(res.text)
        return res_json

    def predict_rfqs(self, conversation, options=None):
        """Predict RFQs from input converstaion.
        Input must be valid conversation dict.
        """
        predict_rfqs_url = f"{self.api_url}/predict_rfqs"
        flags = options or {}
        conversation_json = (
            conversation if isinstance(conversation, dict) else json.loads(conversation)
        )
        json_payload = {"conv": conversation_json, "flags": flags}
        res = requests.post(
            json=json_payload,
            url=predict_rfqs_url,
            headers=self._get_headers(),
            timeout=self.req_timeout_sec,
            **self.request_args,
        )
        res.raise_for_status()
        res_json = json.loads(res.text)
        return res_json

    def chat_snippet_predict_rfqs(self, chat_snippet, options=None):
        """Predict RFQs from chat snippet.
        Input must be valid conversation dict.
        """
        predict_rfqs_url = f"{self.api_url}/predict_chat_snippet_rfqs"
        flags = options or {}
        conversation_json = (
            chat_snippet if isinstance(chat_snippet, dict) else json.loads(chat_snippet)
        )
        json_payload = {"chat_snippet": conversation_json, "flags": flags}
        res = requests.post(
            json=json_payload,
            url=predict_rfqs_url,
            headers=self._get_headers(),
            timeout=self.req_timeout_sec,
            **self.request_args,
        )
        res.raise_for_status()
        res_json = json.loads(res.text)
        return res_json

    def upload_files_with_conversations(self, files_paths, compress=True):
        """Uploads list of files with conversations to be processed by the server."""
        conv_upload_url = f"{self.api_url}/conversations"
        if not isinstance(files_paths, list):
            raise RuntimeError(
                "Please provide list of filenames even if you're sending just one file"
            )
            
        try:
            if compress:
                tempdir = tempfile.mkdtemp()
                archive_dir = tempfile.mkdtemp()
                for file_path in files_paths:
                    shutil.copy(file_path, os.path.join(tempdir, os.path.basename(file_path)))

                tmp_archive = os.path.join(archive_dir, 'archive')
                shutil.make_archive(tmp_archive, 'zip', tempdir)
                tmp_archive += ".zip"
                files_paths = [tmp_archive]

            files = []
            auth_headers = self._get_headers(True)
            for file_path in files_paths:
                file = pathlib.Path(file_path)
                files.append(("files", file.open("rb")))

            resp = requests.post(
                url=conv_upload_url, files=files, headers=auth_headers, **self.request_args
            )
        finally:
            if compress:
                shutil.rmtree(archive_dir)
                shutil.rmtree(tempdir)

        return resp.json()

    def upload_file_with_bond_ref_data(self, file_path):
        """Uploads file with bond data to be added to the server."""
        bond_upload_url = f"{self.api_url}/bonds"
        file = pathlib.Path(file_path)
        resp = requests.post(
            url=bond_upload_url,
            files={"file": (file.name, file.open("rb"))},
            headers=self._get_headers(True),
            **self.request_args,
        )
        return resp.json()
    
    def _upload_file(self, file_path, file_type: Literal["ERFQ"], compress = True):
        upload_url = f"{self.api_url}/upload_file"
        try:
            if compress:
                tempdir = tempfile.mkdtemp()
                archive_dir = tempfile.mkdtemp()
                shutil.copy(file_path, os.path.join(tempdir, os.path.basename(file_path)))

                tmp_archive = os.path.join(archive_dir, os.path.basename(file_path))
                shutil.make_archive(tmp_archive, 'zip', tempdir)
                tmp_archive += ".zip"
                file_path = tmp_archive

            file = pathlib.Path(file_path)
            resp = requests.post(
                url=upload_url,
                files={"file": (file.name, file.open("rb")), "file_type": file_type},
                headers=self._get_headers(True),
                **self.request_args,
            )

        finally:
            if compress:
                shutil.rmtree(archive_dir)
                shutil.rmtree(tempdir)
        
        return resp.json()

    def upload_erfq(self, file_path, compress=True):
        return self._upload_file(file_path, "ERFQ", compress)
    
    def get_processed_conv_file(self, file_id, output_file_path, target="RFQ_CREDIT"):
        """Returns file with processed conversations."""
        url = f"{self.api_url}/conversations/file/{file_id}"
        get_response = requests.get(url=url, stream=True, headers=self._get_headers(), params={"target": target})
        if get_response.status_code != 200:
            return get_response.json()

        with open(output_file_path, "wb") as f:
            for chunk in get_response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        return True

    def get_conv_file_status(self, file_id, target="RFQ_CREDIT"):
        """Returns status of the conversations sent in a given file for the processing by the server."""
        url = f"{self.api_url}/conversations/status/{file_id}"
        resp = requests.get(url=url, headers=self._get_headers(), **self.request_args, params={"target": target})
        return resp.json()
    
    def get_conv_file_history(self, since, until):
        """Returns status of the conversations sent in a given file for the processing by the server."""
        url = f"{self.api_url}/conversations/history"
        resp = requests.get(url=url, headers=self._get_headers(), **self.request_args, params={"since": since, "until": until})
        return resp.json()


    def _get_headers(self, is_not_json=False):
        return self.header_builder.get_headers(is_not_json=is_not_json)

    def _prepare_api_url(self, url):
        if re.search("/api/v1$", url):
            return url
        elif re.search("/api/v1/", url):
            return url[:-1]
        else:
            if re.search("/$", url):
                suffix = "api/v1"
            else:
                suffix = "/api/v1"
            return url + suffix

    @staticmethod
    def dict2conv(messages):
        """A simple util function for generating a conversation dict from simple list of dicts."""
        tstamp = datetime.utcnow().isoformat()
        conv = {
            "chat_id": f"{tstamp}Z_auto",
            "participants": [
                {
                    "login_name": "CLIENT",
                    "role": "Client",
                    "company_name": "CLIENT FIRM",
                    "first_name": "Client",
                    "last_name": "One",
                },
                {
                    "login_name": "BANK",
                    "role": "Bank",
                    "company_name": "Bank Name",
                    "first_name": "Bank",
                    "last_name": "One",
                },
            ],
            "msgs": [
                {
                    "msg_id": str(idx),
                    "content": str(list(msg.values())[0]),
                    "message_time_utc": tstamp,
                    "login_name": "BANK"
                    if str(list(msg.keys())[0]).upper() == "BANK"
                    else "CLIENT",
                }
                for idx, msg in enumerate(messages)
            ],
        }
        return conv
