from drf_yasg import openapi  # type: ignore
from drf_yasg.utils import swagger_auto_schema  # type: ignore
from portal_backend.models.model_serializers import OrganizationSerializer  # type: ignore


organization_create_schema = swagger_auto_schema(
    request_body=OrganizationSerializer,
    responses={
        201: "Created",
        400: "Bad Request",
        500: "Internal Server Error",
        403: "Forbidden",
    },
)

organization_update_schema = swagger_auto_schema(
    request_body=OrganizationSerializer,
    responses={
        200: "Success",
        400: "Bad Request",
        404: "Organization not found",
        403: "Forbidden",
        500: "Internal Server Error",
    },
)


organization_maintainer_create_schema = swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["email"],
        properties={
            "email": openapi.Schema(
                type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
            ),
        },
    ),
    responses={
        201: "Created",
        400: "Bad Request",
        403: "Forbidden",
        404: "Organization not found",
    },
)


organization_maintainer_delete_schema = swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
    ),
    responses={
        200: "Success",
        400: "Bad Request",
        403: "Forbidden",
        404: "Organization not found / Maintainer not found",
    },
)
