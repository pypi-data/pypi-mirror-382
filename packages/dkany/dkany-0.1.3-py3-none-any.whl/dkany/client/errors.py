class Error(Exception):
    """Base class for exceptions in this module."""
    message: str

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.message


class BadResponse(Error):
    def __init__(self, response, acceptable_status_codes):
        status_code = response.status_code
        message = []
        message.append(
            "Status code returned not in acceptable status codes for this response"
        )
        message.append(
            f"Returned: {status_code}:{response.reason}, Acceptable Codes {acceptable_status_codes}"
        )
        message.append(response.text)

        self.response = response
        self.message = "\n".join(message)
