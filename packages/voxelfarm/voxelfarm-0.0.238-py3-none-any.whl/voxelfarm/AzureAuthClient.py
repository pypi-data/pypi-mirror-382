import msal
import os
import atexit
import json
from pathlib import Path
import logging # Using logging for better feedback

# Configure basic logging
# You can adjust the level (e.g., logging.WARNING) to see less output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AzureAuthClient:
    """
    Handles Azure AD authentication using MSAL for public clients (e.g., desktop/scripts)
    utilizing the interactive browser flow with persistent token caching.
    """

    _instances_sharing_cache = {} # Class variable to manage cache saving per file path

    def __init__(self,
                 client_id: str,
                 tenant_id: str,
                 scopes: list[str] = ["User.Read"], 
                 cache_directory: str = ".vf",
                 cache_filename: str = "msal_token_cache.json"):
        """
        Initializes the Azure Authentication Client.

        Args:
            client_id (str): The Application (client) ID registered in Azure AD.
            tenant_id (str): The Directory (tenant) ID, or 'common', 'organizations', 'consumers'.
            scopes (list[str]): A list of permission scopes required for the target API
                                 (e.g., ["User.Read", "api://your-api-client-id/.default"]).
            cache_directory (str): The name of the directory within the user's home
                                   folder to store the cache file. Defaults to '.vf'.
            cache_filename (str): The name of the token cache file. Defaults to 'msal_token_cache.json'.
        """
        if not all([client_id, tenant_id]):
            raise ValueError("client_id, tenant_id, and scopes are required.")

        self.client_id = client_id
        self.tenant_id = tenant_id
        self.scopes = scopes
        self.authority_url = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.token_cache = None
        self.msal_app = None

        # --- Cache Setup ---
        home_dir = Path.home()
        self._cache_dir_path = home_dir / cache_directory
        self._cache_file_path = self._cache_dir_path / cache_filename

        # Ensure cache directory exists
        try:
            self._cache_dir_path.mkdir(parents=True, exist_ok=True)
            logging.info(f"Using token cache file: {self._cache_file_path}")
        except OSError as e:
            logging.error(f"Could not create cache directory {self._cache_dir_path}: {e}. Caching might be in-memory only.")
            # Proceed without file path if directory creation fails

        # --- Initialize Cache and MSAL App ---
        self._initialize_cache_and_app()

        # --- Register Cache Saving on Exit (only once per cache file) ---
        # Use the cache file path as a key to ensure atexit is registered only once
        # for this specific cache file, even if multiple instances use it.
        cache_file_str = str(self._cache_file_path)
        if cache_file_str not in AzureAuthClient._instances_sharing_cache:
            AzureAuthClient._instances_sharing_cache[cache_file_str] = self.token_cache
            atexit.register(self._save_cache, cache_file_str)
            logging.debug(f"Registered cache saving for {cache_file_str}")


    def _initialize_cache_and_app(self):
        """Loads the token cache and initializes the MSAL PublicClientApplication."""
        self.token_cache = msal.SerializableTokenCache()

        if self._cache_file_path.exists():
            try:
                with open(self._cache_file_path, "r") as cache_file:
                    self.token_cache.deserialize(cache_file.read())
                logging.info(f"Token cache loaded from {self._cache_file_path}.")
            except Exception as e:
                logging.warning(f"Failed to load token cache from {self._cache_file_path}: {e}. Starting with an empty cache.")
                # If loading fails, ensure we proceed with a clean cache object
                self.token_cache = msal.SerializableTokenCache()

        self.msal_app = msal.PublicClientApplication(
            self.client_id,
            authority=self.authority_url,
            token_cache=self.token_cache
        )

    # Note: _save_cache is now a static method or requires the cache object if called directly
    # but it's primarily intended for use with atexit, which captures the necessary context.
    # Here, we pass the file path to ensure the correct cache is saved if multiple exist.
    @staticmethod
    def _save_cache(cache_file_path_str: str):
        """Saves the token cache associated with the given file path if it has changed."""
        # Retrieve the correct cache object using the path
        cache_obj = AzureAuthClient._instances_sharing_cache.get(cache_file_path_str)

        if cache_obj and cache_obj.has_state_changed:
            cache_file_path = Path(cache_file_path_str)
            try:
                logging.info(f"Saving token cache to {cache_file_path}...")
                with open(cache_file_path, "w") as cache_file:
                    cache_file.write(cache_obj.serialize())
                # MSAL handles resetting has_state_changed internally after serialization
                logging.info(f"Token cache saved successfully to {cache_file_path}.")
            except Exception as e:
                logging.error(f"Failed to save token cache to {cache_file_path}: {e}")
        else:
             logging.debug(f"No changes detected in token cache for {cache_file_path_str}. No save needed.")


    def get_access_token(self) -> str:
        """
        Acquires an Azure AD access token for the configured scopes.

        It first attempts to get a token silently from the cache. If that fails
        (e.g., no token, expired token, needs interaction), it initiates the
        interactive browser-based login flow.

        Requires 'http://localhost' to be configured as a Redirect URI for
        'Mobile and desktop applications' in the Azure App Registration.

        Returns:
            str: The acquired access token if successful.
            None: If token acquisition fails.
        """
        if not self.msal_app:
            logging.error("MSAL application is not initialized.")
            return None

        result = None
        accounts = self.msal_app.get_accounts()

        if accounts:
            chosen_account = accounts[0] # Use the first account found
            logging.info(f"Account found in cache: {chosen_account.get('username')}. Attempting silent token acquisition...")
            result = self.msal_app.acquire_token_silent(self.scopes, account=chosen_account)

        if not result:
            logging.info("Silent token acquisition failed or no cached account available. Initiating interactive login...")
            try:
                # This will open the user's default web browser
                result = self.msal_app.acquire_token_interactive(scopes=self.scopes)
            except msal.AuthenticationError as e:
                 logging.error(f"MSAL Authentication error during interactive flow: {e}")
                 return None
            except Exception as e:
                # Catch other potential errors like browser issues, network timeouts
                logging.error(f"Unexpected error during interactive token acquisition: {e}")
                return None


        # --- Process Result ---
        if result and "access_token" in result:
            logging.info("Access token acquired successfully.")
            # Trigger saving check in case interactive flow updated cache
            # The atexit handler will perform the actual save later if needed.
            self._check_cache_state_after_acquire()
            return result['access_token']
        elif result and "error" in result:
            self._log_msal_error(result)
            return None
        else:
            # This case might occur if acquire_token_interactive was interrupted or failed unexpectedly
            logging.error("Could not acquire access token. The result was unexpected or empty.")
            return None

    def _check_cache_state_after_acquire(self):
        """Checks if the cache state changed and logs info. Actual saving is deferred to atexit."""
        if self.token_cache and self.token_cache.has_state_changed:
            logging.debug("Token cache state has changed after token acquisition.")
        else:
            logging.debug("Token cache state unchanged after token acquisition.")


    def _log_msal_error(self, error_result: dict):
        """Logs detailed error information from an MSAL result dictionary."""
        logging.error("MSAL token acquisition failed:")
        logging.error(f"  Error: {error_result.get('error')}")
        logging.error(f"  Description: {error_result.get('error_description')}")
        logging.error(f"  Error Codes: {error_result.get('error_codes')}")
        if "correlation_id" in error_result:
             logging.error(f"  Correlation ID: {error_result.get('correlation_id')} (Useful for support)")
        if "claims" in error_result:
             logging.warning(f"  Server requires claims: {error_result.get('claims')}") # Advanced scenario

