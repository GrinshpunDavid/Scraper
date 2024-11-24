from requests import Session
import requests
import logging


class SessionManagement:
    """
    A utility class for managing authenticated sessions.

    This class handles logging in to a given URL with HTTP Basic Auth
    and managing the session cookies for subsequent requests.
    """

    def __init__(self, username: str, password: str, login_url: str):
        """
        Initialize the SessionManagement instance.

        Args:
            username (str): The username for authentication.
            password (str): The password for authentication.
            login_url (str): The URL used for logging in.
        """
        self.username = username
        self.password = password
        self.login_url = login_url
        self.session = Session()
        self.is_login = False

    def _login(self) -> bool:
        """
        Perform login using HTTP Basic Authentication and set cookies.

        Returns:
            bool: True if login is successful, False otherwise.
        """
        if not self.username or not self.password:
            logging.error("Authentication credentials (username or password) are missing.")
            return False

        try:
            # Send a GET request with basic authentication
            response = self.session.get(self.login_url, auth=(self.username, self.password))

            # Check for successful response
            if response.status_code == 200:
                logging.info("Login successful.")
                logging.debug(f"Session cookies: {self.session.cookies.get_dict()}")
                self.is_login = True
                return True
            else:
                logging.error(f"Login failed. HTTP status code: {response.status_code}. Response: {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            logging.error(f"An error occurred during login: {e}")
            return False

    def get_session(self) -> Session:
        """
        Retrieve the authenticated session.

        If not already logged in, attempts to log in before returning the session.

        Returns:
            Session: The authenticated session object.
        """
        if not self.is_login:
            logging.info("Session not authenticated. Attempting to log in...")
            if not self._login():
                logging.error("Failed to authenticate session. Returning unauthenticated session.")
        return self.session
