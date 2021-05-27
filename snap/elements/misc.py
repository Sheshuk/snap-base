"""
Misc processing steps
=====================
"""
import asyncio
def run_shell(cmd):
    """
    A processing :term:`step`.
    Run shell command every time the `data` arrives.

    Args:
        cmd (str):
            A command to run. 
            If cmd is a template, like ``echo {foo} {bar}``, data should contain keys "foo" and "bar"

    :Input:
        data(dict) will be used to define the command:
        :code:`run_cmd = cmd.format(**data)`

    :Output: 
        (str) stdout of the executed command
    """
    async def _run(data):
        print(f"Run!")
        run_cmd = cmd.format(**data)
        print(f"Command to run: {run_cmd}")
        proc = await asyncio.create_subprocess_shell(run_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
                )
        stdout, stderr = await proc.communicate()
        if stdout:
            print(f'[stdout]\n{stdout.decode()}')
        if stderr:
            print(f'[stderr]\n{stderr.decode()}')
        await proc.wait()
        return stdout.decode()
    return _run

