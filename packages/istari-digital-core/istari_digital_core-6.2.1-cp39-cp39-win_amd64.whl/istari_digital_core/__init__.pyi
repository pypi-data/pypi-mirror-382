class Configuration:
    def __init__(
        self,
        registry_url: str | None = None,
        registry_auth_token: str | None = None,
        registry_timeout_seconds: int | None = None,
        retry_enabled: bool | None = None,
        retry_max_attempts: int | None = None,
        retry_min_interval_millis: int | None = None,
        retry_max_interval_millis: int | None = None,
        retry_jitter_enabled: bool | None = None,
        multipart_threshold: int | None = None,
        multipart_chunksize: int | None = None,
    ) -> None: ...
    @property
    def registry_url(self) -> str | None: ...
    @property
    def registry_auth_token(self) -> str | None: ...
    @property
    def registry_timeout_seconds(self) -> int | None: ...
    @property
    def retry_enabled(self) -> bool | None: ...
    @property
    def retry_max_attempts(self) -> int | None: ...
    @property
    def retry_min_interval_millis(self) -> int | None: ...
    @property
    def retry_max_interval_millis(self) -> int | None: ...
    @property
    def retry_jitter_enabled(self) -> bool | None: ...
    @property
    def multipart_threshold(self) -> int | None: ...
    @property
    def multipart_chunksize(self) -> int | None: ...

class Revision:
    @property
    def content_token(self) -> Token: ...
    @property
    def properties_token(self) -> Token: ...
    @property
    def properties(self) -> Properties: ...

class Token:
    @property
    def sha(self) -> str: ...
    @property
    def salt(self) -> str: ...
    @staticmethod
    def from_bytes(data: bytes, salt: str | None = None) -> Token: ...
    @staticmethod
    def compare_token(sha: str, salt: str, data: bytes) -> None: ...

class Properties:
    def __init__(
        self,
        file_name: str,
        extension: str,
        size: int,
        description: str | None = None,
        mime: str | None = None,
        version_name: str | None = None,
        external_identifier: str | None = None,
        display_name: str | None = None,
    ) -> None: ...
    @property
    def file_name(self) -> str: ...
    @property
    def mime(self) -> str | None: ...
    @property
    def extension(self) -> str: ...
    @property
    def size(self) -> int: ...
    @property
    def description(self) -> str | None: ...
    @property
    def version_name(self) -> str | None: ...
    @property
    def external_identifier(self) -> str | None: ...
    @property
    def display_name(self) -> str | None: ...

class Client:
    def __init__(
        self,
        configuration: Configuration,
    ) -> None: ...
    @property
    def configuration(self) -> Configuration: ...
    def create_revision(
        self,
        file_path: str,
        description: str | None = None,
        version_name: str | None = None,
        external_identifier: str | None = None,
        display_name: str | None = None,
    ) -> Revision: ...
    def create_secret_revision(
        self,
        file_path: str,
        description: str | None = None,
        version_name: str | None = None,
        external_identifier: str | None = None,
        display_name: str | None = None,
    ) -> Revision: ...
    def update_content(
        self,
        file_path: str,
        salt: str,
        description: str | None = None,
        version_name: str | None = None,
        external_identifier: str | None = None,
        display_name: str | None = None,
    ) -> Revision: ...
    def update_properties(
        self,
        properties: Properties,
        salt: str,
    ) -> Token: ...
    def read_contents(self, sha: str, salt: str) -> bytes: ...
    def read_properties(self, sha: str, salt: str) -> Properties: ...
