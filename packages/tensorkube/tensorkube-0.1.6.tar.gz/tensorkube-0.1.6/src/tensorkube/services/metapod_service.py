import socket

import click
import metapod_python
import asyncio




def list_instances_in_cloud(cloud_name: str = None):
    async def run_async():
        return await metapod_python.list_instances_in_cloud(cloud_name)

    loop = asyncio.get_event_loop()
    if loop.is_running():
        # If we're already in an event loop, use create_task
        return asyncio.create_task(run_async())
    else:
        # If no event loop is running, use run_until_complete
        return loop.run_until_complete(run_async())

def is_port_available(port: int) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('127.0.0.1', port))
        return True
    except OSError:
        return False
    finally:
        s.close()


def start_devcontainer(cloud_name:str, gpu_type:str, port:int):
    if not is_port_available(port):
        # Port is not available. print in red and return
        click.echo(click.style(f"Port {port} is not available. Please choose a different port.", fg='red'))
        return
    async def run_async():
        return await metapod_python.start_devcontainer(cloud_name, port, gpu_type)

    loop = asyncio.get_event_loop()
    if loop.is_running():
        # If we're already in an event loop, use create_task
        return asyncio.create_task(run_async())
    else:
        # If no event loop is running, use run_until_complete
        return loop.run_until_complete(run_async())

def pause_devcontainer(cloud_name:str):
    async def run_async():
        return await metapod_python.pause_devcontainer(cloud_name)

    loop = asyncio.get_event_loop()
    if loop.is_running():
        # If we're already in an event loop, use create_task
        return asyncio.create_task(run_async())
    else:
        # If no event loop is running, use run_until_complete
        return loop.run_until_complete(run_async())

def purge_devcontainer(cloud_name:str):
    async def run_async():
        return await metapod_python.purge_devcontainer(cloud_name)

    loop = asyncio.get_event_loop()
    if loop.is_running():
        # If we're already in an event loop, use create_task
        return asyncio.create_task(run_async())
    else:
        # If no event loop is running, use run_until_complete
        return loop.run_until_complete(run_async())

def reset_cloud(cloud_name:str):
    async def run_async():
        return await metapod_python.reset_cloud(cloud_name)

    loop = asyncio.get_event_loop()
    if loop.is_running():
        # If we're already in an event loop, use create_task
        return asyncio.create_task(run_async())
    else:
        # If no event loop is running, use run_until_complete
        return loop.run_until_complete(run_async())