# -*- coding: utf-8 -*-

import hashlib
import uuid

from pydantic import BaseModel


class Key(BaseModel):
    """Utility class for creating keys."""

    prefix: str
    rand_uuid: str

    def __init__(self, prefix: str = ""):
        """Constructor.

        Args:
            prefix (str): Prefix of the token. Default empty.
        """
        rand_uuid = uuid.uuid4()

        super().__init__(prefix=prefix, rand_uuid=str(rand_uuid))

    def get_value(self) -> str:
        """Get the token as a string.

        Returns:
            str: The token string.
        """
        if len(self.prefix) > 0:
            value = self.prefix + "-" + self.rand_uuid
        else:
            value = self.rand_uuid

        return value

    def get_hash(self) -> str:
        """Get the token as a hashed SHA-256 string.

        Returns:
            str: The hashed token string.
        """
        value = self.get_value()

        hash_object = hashlib.sha256()
        value_encoded = value.encode("utf-8")
        hash_object.update(value_encoded)

        return hash_object.hexdigest()
