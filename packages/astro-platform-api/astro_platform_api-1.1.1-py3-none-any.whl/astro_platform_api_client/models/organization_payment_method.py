from enum import Enum


class OrganizationPaymentMethod(str, Enum):
    AWS_MARKETPLACE = "AWS_MARKETPLACE"
    AZURE_MARKETPLACE = "AZURE_MARKETPLACE"
    CREDIT_CARD = "CREDIT_CARD"
    GCP_MARKETPLACE = "GCP_MARKETPLACE"
    INVOICE = "INVOICE"
    SNOWFLAKE_MARKETPLACE = "SNOWFLAKE_MARKETPLACE"

    def __str__(self) -> str:
        return str(self.value)
