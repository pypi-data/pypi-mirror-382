"""Kubernetes client helpers."""

from kubernetes_asyncio import client, config
from kubernetes_asyncio.dynamic import DynamicClient


async def get_dynamic_client(in_cluster: bool = False) -> DynamicClient:
    if in_cluster:
        await config.load_incluster_config()
    else:
        await config.load_kube_config()

    api_client = client.ApiClient()
    return DynamicClient(api_client)
