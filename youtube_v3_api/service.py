import os
import pickle
from typing import Any, Optional, Sequence, Union
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


class Service:
    
    def __init__(self, api_name: str, api_version: str) -> None:
        """This class can be used to create a google api service object
        
        Args:
            api_name (str): the name of the service.
            api_version (str): the version of the service.
        """    
        self.api_name = api_name
        self.api_version = api_version
    
    def create_service(self, developer_key: str) -> Any:
        """Construct a Resource for interacting with an API.

        Construct a Resource object for interacting with an API. The serviceName and version are the names from the Discovery service.

        Args:
            developer_key (str): key obtained from https://code.google.com/apis/console

        Returns:
            Any: a resource object with methods for interacting with the service.
        """
        return build(self.api_name, self.api_version, developerKey=developer_key)
    
    def create_oauth_service(self, client_secret_file: str, scopes: Sequence[str], token_file: Optional[Union[str, None]] = None, relogin: Optional[bool] = False) -> Any:
        """Construct a Resource for interacting with an API.
        
        Construct a Resource object for interacting with an API. The serviceName and version are the names from the Discovery service.

        Args:
            client_secret_file (str): the path to the client secrets.json file.
            scopes (Sequence[str]): the list of scopes to request during the flow.
            token_file (Optional[Union[str, None]], optional): [description]. Defaults to None.
            relogin (Optional[bool], optional): explicit call to login again. Defaults to False.

        Raises:
            e: googleapiclient.discovery.build exceptions

        Returns:
            Any: a resource object with methods for interacting with the service.
        """
        credentials = None
        pickle_file = f"token_{self.api_name}_{self.api_version}.pkl" if token_file is None else token_file

        if os.path.exists(pickle_file) and not relogin:
            with open(pickle_file, "rb") as token:
                credentials = pickle.load(token)

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scopes)
                credentials = flow.run_local_server()

            with open(pickle_file, "wb") as token:
                pickle.dump(credentials, token)

        try:
            return build(self.api_name, self.api_version, credentials=credentials)
        
        except Exception as e:
            os.remove(pickle_file)
            raise e

class YoutubeService(Service):
    def __init__(self) -> None:
        """Create a youtube v3 Service class
        """
        super().__init__("youtube", "v3")
