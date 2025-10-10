from sapiopycommons.ai.protoapi.externalcredentials.external_credentials_pb2 import ExternalCredentialsPbo


class ExternalCredentials:
    """
    A class representing external credentials.
    """
    id: str
    display_name: str
    description: str
    category: str
    url: str
    username: str
    password: str
    token: str
    custom_fields: dict[str, str]

    def __init__(self, pbo: ExternalCredentialsPbo):
        self.id = pbo.id
        self.display_name = pbo.display_name
        self.description = pbo.description
        self.category = pbo.category
        self.url = pbo.url
        self.username = pbo.username
        self.password = pbo.password
        self.token = pbo.token
        self.custom_fields = dict(pbo.custom_field)

    def get_custom_field(self, key: str, default: str = None) -> str | None:
        """
        Get a custom field by key.

        :param key: The key of the custom field to retrieve.
        :param default: The value to return if the key does not exist.
        :return: The value of the custom field, or None if the key does not exist.
        """
        return self.custom_fields.get(key, default)
