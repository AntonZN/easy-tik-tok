import asyncio
import os

from app.core.config import get_settings
from app.helpers.cmds import encode_cmd

settings = get_settings()


async def run_command(cmd: str) -> dict:
    ret = {}

    process = await asyncio.subprocess.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        try:
            ret["out"] = stdout.decode("utf-8")
        except BaseException:
            ret["out"] = ""
    else:
        try:
            ret["error"] = stderr.decode("utf-8")
        except BaseException:
            ret["error"] = ""
    return ret


async def get_file_size(input_file: str) -> int:
    if not os.path.isfile(input_file):
        return 0

    cmd = f"stat -c %s {input_file}"
    stdout = await run_command(cmd)
    if stdout.get("error", None):
        try:
            return int(stdout.get("out").strip())
        except Exception:
            return 0


async def encode_file(input_file: str, output_file) -> tuple:
    if not os.path.isfile(input_file):
        return False, "Input file is not a file"

    cmd = encode_cmd(input_file, output_file)
    stdout = await run_command(cmd)

    if stdout.get("error", None):
        return False, stdout.get("error")

    return True, "Success"
