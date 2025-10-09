import subprocess
import asyncio

START_VIRUAL_MACHINE = "common/shell_scripts/start-virtual-machine.sh"
START_ADB_APP = "common/shell_scripts/start-adb-app.sh"
START_NPM_AT_PATH = "common/shell_scripts/start-npm-at-path.sh"
START_FIREFOX_AT_URL = "common/shell_scripts/start-firefox-at-url.sh"
KILL_PROCESS_AT_PORT = "common/shell_scripts/kill-process-at-port.sh"


def start_virtual_machine(virtual_device_id: str) -> bool:
    process = subprocess.run(
        [START_VIRUAL_MACHINE, virtual_device_id], check=True)
    return proccess_end_handling(process.returncode)


def start_adb_app(package_name: str):
    process = subprocess.run([START_ADB_APP, package_name])
    return proccess_end_handling(process.returncode)


async def start_npm_at_path(path: str, search_message: str = ''):
    process = await asyncio.create_subprocess_exec(
        START_NPM_AT_PATH, path,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=False
    )

    try:
        while True:
            output_bytes = await process.stdout.readline()
            output = output_bytes.decode('utf-8')
            if output == '' and process.poll() is not None:
                break
            if search_message and search_message in output:
                break
            if output:
                print(output.strip())
            await asyncio.sleep(1)
    except Exception as e:
        print(f"Error in waiting for process to end {e}", flush=True)
        return proccess_end_handling(1)
    finally:
       print("Process ended")
       return proccess_end_handling(0)


def start_firefox_at_url(url: str):
    process = subprocess.run([START_FIREFOX_AT_URL, url])
    return proccess_end_handling(process.returncode)


def kill_process_at_port(port: int):
    process = subprocess.run(
        [KILL_PROCESS_AT_PORT, str(port)])
    return proccess_end_handling(process.returncode)


def kill_proccess(name: str):
    process = subprocess.run(["pkill", name])
    return proccess_end_handling(process.returncode)


def kill_adb_app(package_name: str):
    process = subprocess.run(
        ["adb", "shell", "am", "force-stop", package_name])
    return proccess_end_handling(process.returncode)


def proccess_end_handling(return_code: str) -> bool:
    success = False
    if return_code == 0:
        print("Script completed successfully")
        success = True
    else:
        print("Script failed with exit code", return_code)
    return success
