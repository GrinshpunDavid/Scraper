from requests import Session
import requests
import logging


class SessionManagement:
    def __init__(self, username: str, password: str, login_url: str):
        """
        Initializes the session management instance.

        Args:
            username (str): Username for authentication.
            password (str): Password for authentication.
            login_url (str): URL to perform login.
        """
        self.username = username
        self.password = password
        self.login_url = login_url
        self.session = Session()
        self.is_login = False

    def _login(self) -> bool:
        """
        Logs into the session and manages cookies.

        Returns:
            bool: True if login is successful, False otherwise.
        """
        if not self.username or not self.password:
            logging.error("Username or password is not set.")
            return False

        try:
            response = self.session.get(self.login_url, auth=(self.username, self.password))
            if response.status_code == 200:
                logging.info("Login successful")
                self.is_login = True
                logging.info(f"Cookies retrieved: {self.session.cookies.get_dict()}")
                return True
            else:
                logging.error(f"Login failed with status code {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logging.error(f"Login request failed: {e}")
            return False

    def get_session(self) -> Session:
        """
        Returns the session object, logging in if not already logged in.

        Returns:
            Session: A session object with cookies managed.
        """
        if not self.is_login:
            self._login()
        return self.session
