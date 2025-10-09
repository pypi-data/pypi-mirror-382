from norman_objects.shared.security.sensitive import Sensitive

from norman_core.clients.http_client import HttpClient, ResponseEncoding


class Retrieve:
    @staticmethod
    async def get_model_asset(http_client: HttpClient, token: Sensitive[str], account_id: str, model_id: str, asset_id: str):
        endpoint = f"retrieve/asset/{account_id}/{model_id}/{asset_id}"
        return await http_client.get(endpoint, token, response_encoding=ResponseEncoding.Iterator)

    @staticmethod
    async def get_invocation_input(http_client: HttpClient, token: Sensitive[str], account_id: str, model_id: str, invocation_id: str, input_id: str):
        endpoint = f"retrieve/input/{account_id}/{model_id}/{invocation_id}/{input_id}"
        return await http_client.get(endpoint, token, response_encoding=ResponseEncoding.Iterator)

    @staticmethod
    async def get_invocation_output(http_client: HttpClient, token: Sensitive[str], account_id: str, model_id: str, invocation_id: str, output_id: str):
        endpoint = f"retrieve/output/{account_id}/{model_id}/{invocation_id}/{output_id}"
        return await http_client.get(endpoint, token, response_encoding=ResponseEncoding.Iterator)