import aiohttp
import os


async def download_image(url: str, save_path: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                with open(save_path, 'wb') as file:
                    while True:
                        chunk = await response.content.read(8192)
                        if not chunk:
                            break
                        file.write(chunk)

    except aiohttp.ClientError as e:
        print(f"An error occurred: {e}")


async def download_images(urls: list[str], images_directory: str):
    for url in urls:
        filename = url.split('/')[-1]
        save_path = os.path.join(images_directory, filename)
        await download_image(url, save_path)
