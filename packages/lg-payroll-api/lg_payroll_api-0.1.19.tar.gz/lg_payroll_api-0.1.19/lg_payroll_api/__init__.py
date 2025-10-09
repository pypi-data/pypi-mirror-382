from lg_payroll_api.helpers import LgAuthentication
from lg_payroll_api.scripts import (
    LgApiCompanyClient,
    LgApiCostCenterClient,
    LgApiEmployee,
    LgApiEmploymentContract,
    LgApiOrganizationalUnitClient,
    LgReportServiceClient,
    ReportParameters,
    LgApiRoleClient,
    LgApiWorkScaleClient,
    LgApiAdditionalInformationValueClient,
    LgApiAdditionalInformationClient,
    LgApiPositionClient,
    LgApiMovementClient,
    LgApiOfficeLocalClient,
)


class LgPayrollApi:
    """Interface to access endpoints."""

    def __init__(self, auth: LgAuthentication) -> None:
        self.__auth: LgAuthentication = auth

    @property
    def cost_center_service(self) -> LgApiCostCenterClient:
        """Access cost centers service methods."""
        return LgApiCostCenterClient(self.__auth)

    @property
    def employment_contract_service(self) -> LgApiEmploymentContract:
        """Access employment contracts service methods."""
        return LgApiEmploymentContract(self.__auth)

    @property
    def organizational_unit_service(self) -> LgApiOrganizationalUnitClient:
        """Access organizational units service methods."""
        return LgApiOrganizationalUnitClient(self.__auth)

    @property
    def company_service(self) -> LgApiCompanyClient:
        """Access companies service methods."""
        return LgApiCompanyClient(self.__auth)

    @property
    def employee_service(self) -> LgApiEmployee:
        """Access employee service methods."""
        return LgApiEmployee(self.__auth)

    @property
    def report_service(self) -> LgReportServiceClient:
        """Access report generator service methods."""
        return LgReportServiceClient(self.__auth)

    @property
    def role_service(self) -> LgApiRoleClient:
        """Access role service methods."""
        return LgApiRoleClient(self.__auth)

    @property
    def work_scale_service(self) -> LgApiWorkScaleClient:
        """Access work scale service methods."""
        return LgApiWorkScaleClient(self.__auth)
    
    @property
    def additional_information_value(self) -> LgApiAdditionalInformationValueClient:
        return LgApiAdditionalInformationValueClient(self.__auth)

    @property
    def additional_information(self) -> LgApiAdditionalInformationClient:
        return LgApiAdditionalInformationClient(self.__auth)
    
    @property
    def position_service(self) -> LgApiPositionClient:
        return LgApiPositionClient(self.__auth)
    
    @property
    def office_local_service(self) -> LgApiOfficeLocalClient:
        return LgApiOfficeLocalClient(self.__auth)

    @property
    def movement_service(self) -> LgApiMovementClient:
        """Access movement service methods."""
        return LgApiMovementClient(self.__auth)
