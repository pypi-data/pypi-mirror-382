from osbot_fast_api.api.schemas.Schema__Fast_API__Config import Schema__Fast_API__Config


class Serverless__Fast_API__Config(Schema__Fast_API__Config):
    enable_cors    : bool = True
    enable_api_key : bool = True
    default_routes : bool = False