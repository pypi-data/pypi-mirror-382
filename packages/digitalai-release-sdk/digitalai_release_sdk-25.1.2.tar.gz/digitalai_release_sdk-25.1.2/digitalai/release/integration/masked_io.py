from io import TextIOWrapper


class MaskedIO(TextIOWrapper):
    """
    A wrapper for an I/O stream that masks specified secrets in the output.

    Attributes:
        secrets (List[str]): The list of secrets to mask in the output.
    """

    def __init__(self, buffer):
        """
        Initializes the MaskedIO wrapper with the given buffer.

        Args:
            buffer (IO[str]): The buffer to wrap.
        """
        super().__init__(buffer, line_buffering=True, write_through=False)
        self._secrets = []

    @property
    def secrets(self):
        """
        Gets the list of secrets to mask in the output.

        Returns:
            List[str]: The list of secrets.
        """
        return self._secrets

    @secrets.setter
    def secrets(self, secrets):
        """
        Sets the list of secrets to mask in the output.

        Args:
            secrets (List[str]): The list of secrets.
        """
        self._secrets = secrets

    def write(self, s):
        """
        Writes the given string to the buffer, masking any secrets in the process.

        Args:
            s (str): The string to write.
        """
        d = s
        for secret in self.secrets:
            if secret:
                d = d.replace(secret, '********')
        self.buffer.write(d)
