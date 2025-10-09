# Common Utils

A collection of common utility functions and scripts for various tasks including:
- File operations
- HTTP requests handling
- Image downloading
- Shell script execution
- Task completion management
- Machine wake functionality
- WebSocket listening

## Installation

```bash
pip install thetemani-common-utils
```

## Usage

```python
from common_utils import file_utils, http_wrapper, image_downloader

# File operations
result = file_utils.read_file("path/to/file.txt")
file_utils.write_file("path/to/output.txt", "content")

# HTTP requests
response = http_wrapper.make_request("https://api.example.com/data")

# Image downloading
image_downloader.download_image("https://example.com/image.jpg", "local_image.jpg")

# Shell script execution
from common_utils import shell_scripts_handler
shell_scripts_handler.execute_script("kill-process-at-port.sh", ["8080"])

# WebSocket listening
from common_utils import web_socket_listener
listener = web_socket_listener.WebSocketListener("ws://example.com")
await listener.connect()
```

## Features

- **File Utils**: Easy file reading, writing, and manipulation
- **HTTP Wrapper**: Simplified HTTP request handling
- **Image Downloader**: Efficient image downloading with retry logic
- **Shell Scripts Handler**: Execute shell scripts with parameters
- **Task Completion**: Async task completion management
- **Wake Machine**: Remote machine wake functionality
- **WebSocket Listener**: Async WebSocket communication

## Requirements

See `requirements.txt` for a list of dependencies.

## License

MIT License