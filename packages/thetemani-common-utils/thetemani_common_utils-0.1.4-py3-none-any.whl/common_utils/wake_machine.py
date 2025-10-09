import http_wrapper


async def wake_machine(mac_address, ip_address, wake_on_lan_api_url) -> bool:
    post_data = {
        "mac_address": mac_address,
        "ip_address": ip_address
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "/",
        "Connection": "keep-alive",
    }
    request_url = wake_on_lan_api_url + "/wake"
    response = await http_wrapper.send_request(request_url, "POST", headers, None, post_data)
    if (response.status != 200):
        print(f"Failed to wake machine: {response.status} trying again")
        response = await http_wrapper.send_request(request_url, "POST", headers, None, post_data)
        print(f"Second attempt response: {response}")

    return response.status == 200 and response.body["exit_code"] == 0
