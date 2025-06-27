from drf_yasg import openapi  # type: ignore
from drf_yasg.utils import swagger_auto_schema  # type: ignore

relying_party_create_schema = swagger_auto_schema(
    responses={
        201: "Created",
        404: "Not Found",
        400: "Bad Request",
        401: "Unauthorized",
    },
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=[
            "hostnames",
            "environment",
            "attributes",
            "context_description_en",
            "context_description_nl",
        ],
        properties={
            "hostnames": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"hostname": openapi.Schema(type=openapi.TYPE_STRING)},
                    required=["hostname"],
                ),
            ),
            "environment": openapi.Schema(type=openapi.TYPE_STRING),
            "context_description_en": openapi.Schema(type=openapi.TYPE_STRING),
            "context_description_nl": openapi.Schema(type=openapi.TYPE_STRING),
            "attributes": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "credential_attribute_tag": openapi.Schema(
                            type=openapi.TYPE_STRING
                        ),
                        "reason_en": openapi.Schema(type=openapi.TYPE_STRING),
                        "reason_nl": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
        },
    ),
)

relying_party_patch_schema = swagger_auto_schema(
    responses={
        200: "Success",
        404: "Not Found",
        400: "Bad Request",
        401: "Unauthorized",
    },
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "hostnames": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"hostname": openapi.Schema(type=openapi.TYPE_STRING)},
                    required=["hostname"],
                ),
            ),
            "environment": openapi.Schema(type=openapi.TYPE_STRING),
            "context_description_en": openapi.Schema(type=openapi.TYPE_STRING),
            "context_description_nl": openapi.Schema(type=openapi.TYPE_STRING),
            "attributes": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "credential_attribute_tag": openapi.Schema(
                            type=openapi.TYPE_STRING
                        ),
                        "reason_en": openapi.Schema(type=openapi.TYPE_STRING),
                        "reason_nl": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            "rp_slug": openapi.Schema(type=openapi.TYPE_STRING),
            "ready": openapi.Schema(type=openapi.TYPE_BOOLEAN),
        },
    ),
)

relying_party_delete_schema = swagger_auto_schema(
    responses={
        204: "No Content",
        404: "Not Found",
        403: "Forbidden",
    }
)

relying_party_dns_status_schema = swagger_auto_schema(
    responses={
        200: "Success",
        404: "Not Found",
    }
)

relying_party_list_schema = swagger_auto_schema(
    responses={
        200: openapi.Response(
            description="List of relying parties",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "relying_parties": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "rp_slug": openapi.Schema(type=openapi.TYPE_STRING),
                                "environment": openapi.Schema(type=openapi.TYPE_STRING),
                            },
                        ),
                    )
                },
            ),
        )
    }
)

relying_party_detail_schema = swagger_auto_schema(
    responses={
        200: openapi.Response(
            description="Detailed RP info",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "rp_slug": openapi.Schema(type=openapi.TYPE_STRING),
                    "hostnames": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Items(type=openapi.TYPE_OBJECT),
                    ),
                    "context_description_en": openapi.Schema(type=openapi.TYPE_STRING),
                    "context_description_nl": openapi.Schema(type=openapi.TYPE_STRING),
                    "attributes": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Items(type=openapi.TYPE_OBJECT),
                    ),
                    "environment": openapi.Schema(type=openapi.TYPE_STRING),
                    "published_at": openapi.Schema(
                        type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
                    ),
                },
            ),
        )
    }
)
