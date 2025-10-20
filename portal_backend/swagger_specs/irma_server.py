from drf_yasg.utils import swagger_auto_schema  # type: ignore
from portal_backend.models.model_serializers import IrmaServerSerializer

irma_server_create_schema = swagger_auto_schema(
    request_body=IrmaServerSerializer,
    responses={
        201: "Created",
        400: "Bad Request",
        500: "Internal Server Error",
        403: "Forbidden",
    },
)   