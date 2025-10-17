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

irma_server_update_schema = swagger_auto_schema(
    request_body=IrmaServerSerializer,
    responses={
        200: "Success",
        400: "Bad Request",
        404: "Irma Server not found",
        403: "Forbidden",
        500: "Internal Server Error",
    },
)

irma_server_delete_schema = swagger_auto_schema(
    responses={
        200: "Success",
        400: "Bad Request",
        403: "Forbidden",
        404: "Irma Server not found",
    },
)

