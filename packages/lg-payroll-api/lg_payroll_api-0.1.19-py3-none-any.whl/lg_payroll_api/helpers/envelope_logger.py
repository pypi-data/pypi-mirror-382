from lxml import etree
import re
from typing import Literal

class EnvelopeLogger:
    """
    A class to log the XML envelope sent to the LG API.
    """
    def __init__(self, requests_history):
        self.requests_history = requests_history

    def log_envelope(self, envelope=Literal["request", "response"]):
        """
        Logs the last sent XML envelope.
        """
        if envelope == "response":
            if not self.requests_history.last_response:
                raise ValueError("No request has been sent yet.")
            envelope_data = self.requests_history.last_response
        else:
            if not self.requests_history.last_sent:
                raise ValueError("No request has been sent yet.")
            envelope_data = self.requests_history.last_sent
        envelope_data = etree.tostring(envelope_data["envelope"], pretty_print=True).decode()
        print(self.__clean_sensitive_fields(envelope_data))

    def __clean_sensitive_fields(self, body):
        """
        Cleans sensitive fields from the request envelope.
        """
        sensitive_fields = ["Senha", "GuidTenant", "LGContextoAmbiente", "Usuario", "Ambiente"]
        for field in sensitive_fields:
            pattern = fr"<(?P<prefix>\w+:)?(?P<tag>{field})(?P<attrs>[^>]*)>(.*?)</(?P=prefix)?(?P=tag)>"
            body = re.sub(pattern, self.apply_mask, body)
        return body
    
    def apply_mask(self, match):
        prefixo = match.group("prefix") or ""
        tag = match.group("tag")
        attrs = match.group("attrs")
        return f"<{prefixo}{tag}{attrs}>XXXXXX</{prefixo}{tag}>"
