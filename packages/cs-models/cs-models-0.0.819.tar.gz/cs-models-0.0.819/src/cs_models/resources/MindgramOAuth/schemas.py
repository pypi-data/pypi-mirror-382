from marshmallow import (
    Schema,
    fields,
)


class MindgramOAuthTokenResourceSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.String(required=True)
    provider = fields.String(required=True)
    access_token = fields.String(allow_none=True)
    refresh_token = fields.String(required=True)
    token_type = fields.String(allow_none=True)
    scope = fields.String(allow_none=True)
    expiry = fields.DateTime(allow_none=True)
    token_uri = fields.String(required=True)
    client_id = fields.String(required=True)
    client_secret = fields.String(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
