# This module contais a authentication class


class LgAuthentication:
    base_url: str = None
    retry_time_request: int = None

    def __init__(
        self,
        base_url: str,
        user: str,
        password: str,
        guild_tenant: str,
        environment_context: int,
    ) -> None:
        """Authentication class used to generate a auth header dictionary

        Args:
            base_url (str, mandatory): Your LG Environment Url, for example "https://your-domain-api.lgcloud.com.br"
            user (str, mandatory): An user able to use LG API, for example "your_user@domain.com"
            password (str, mandatory): Password of user
            guid_tenant (str, mandatory): This is a client identification guid. You can get this code by accessing the portal Gent.te. See more about this in https://portalgentedesucesso.lg.com.br/documentacao.api.suitegente/Autenticacao
            environment_context: (int, mandatory): This is a client identification environment code. You can get this code in the same way of guid_tenant
        """
        self.base_url = base_url
        self.user = user
        self.password = password
        self.guild_tenant = guild_tenant
        self.environment_context = environment_context

    @property
    def auth_header(self) -> dict:
        """Return a auth header to xml body in json format."""

        environment: dict = {"Ambiente": self.environment_context}

        header_authentication = {
            "TokenUsuario": {
                "Senha": self.password,
                "Usuario": self.user,
                "GuidTenant": self.guild_tenant,
            }
        }

        return {
            "LGContextoAmbiente": environment,
            "LGAutenticacao": header_authentication,
        }
