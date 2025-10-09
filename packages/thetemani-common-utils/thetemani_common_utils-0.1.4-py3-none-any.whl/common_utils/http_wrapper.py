import aiohttp
import urllib.parse
import json
from typing import Any


class ApiResponse:
    def __init__(self, status_code, body):
        self.status = status_code
        self.body = body

    def __str__(self):
        return json.dumps({"status": self.status, "body": self.body})


async def send_request(url: str, request_type: str, headers: dict, query: dict = None, post_data: Any = '') -> ApiResponse:
    if query:
        query_string = urllib.parse.urlencode(query)
        url += '?' + query_string

    response_body = ''
    async with aiohttp.ClientSession() as session:
        if request_type == "GET":
            async with session.get(url, headers=headers) as response:
                response_body = await response.text()
                response_code = response.status
        elif request_type in ["POST", "PUT"]:  # Handle both POST and PUT
            post_data_dict = get_post_data_dict(post_data)
            post_data_json = json.dumps(post_data_dict)
            if request_type == "POST":
                async with session.post(url, data=post_data_json, headers=headers) as response:
                    response_body = await response.text()
                    response_code = response.status
            if request_type == "PUT":
                async with session.put(url, data=post_data_json, headers=headers) as response:
                    response_body = await response.text()
                    response_code = response.status

    try:
        response_body_json = json.loads(response_body)
    except json.JSONDecodeError:
        response_body_json = None

    return ApiResponse(status_code=response_code, body=response_body_json)


def get_post_data_dict(post_data: Any) -> dict:
    if type(post_data) == dict:
        return post_data
    return post_data.__dict__
