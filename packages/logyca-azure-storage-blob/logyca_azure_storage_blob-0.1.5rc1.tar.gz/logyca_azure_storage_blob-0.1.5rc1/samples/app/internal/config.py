from dotenv import load_dotenv
from app.utils.constants.environment import Environment
from logyca import parse_bool
from pathlib import Path
import os

env_path= Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

class Settings:
    def __init__(self) -> None:
        self.account_name: str = os.getenv(Environment.AzureStorageAccount.AccessKeys.ACCOUNT_NAME)
        self.account_key: str = os.getenv(Environment.AzureStorageAccount.AccessKeys.ACCOUNT_KEY)
        self.connection_string: str = os.getenv(Environment.AzureStorageAccount.AccessKeys.CONNECTION_STRING)

        self.mandatory_attribute_validation()

    def mandatory_attribute_validation(self):
        attributes = vars(self)
        none_attributes = [attr for attr, value in attributes.items() if value is None]
        if len(none_attributes)!=0:
            raise KeyError(f"The following environment variables have not been created: {none_attributes}")

settings = Settings()

