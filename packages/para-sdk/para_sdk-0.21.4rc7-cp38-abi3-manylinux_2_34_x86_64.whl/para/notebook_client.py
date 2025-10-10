import os
import json
import base64
import builtins
from dataclasses import dataclass
from para import para;

if hasattr(builtins, "__IPYTHON__"):
  from .conversation_panel import ConversationPanel

if hasattr(builtins, "__IPYTHON__"):
  import panel as pn
  pn.extension()

class NotebookClient:
    _client: any

    def __init__(self, client: any):
        self._client = client

    def new_request(self, subject: str, action: str, target_actor_id=None, **kwargs):
        return self._client.pncp.skill_request(subject, action, target=target_actor_id, **kwargs)

    


async def from_env():
    paranet_endpoint = os.environ.get('PARANET_ENDPOINT')

    if not paranet_endpoint:
        raise ValueError("PARANET_ENDPOINT is not set")

    actor = os.environ.get('PARANET_ACTOR')
    version = os.environ.get('PARANET_ACTOR_VERSION') or '1.0.0'

    if not actor:
        raise ValueError("PARANET_ACTOR is required")

    actor_entity_id = f'{actor}@{version}'

    paranet_access_token = os.environ.get('PARANET_ACCESS_TOKEN')
    paranet_refresh_token = os.environ.get('PARANET_REFRESH_TOKEN')

    paranet_jwt = os.environ.get('PARANET_JWT')
    paranet_password = os.environ.get('PARANET_PASSWORD')
    paranet_cognito_password = os.environ.get('PARANET_COGNITO_PASSWORD')


    print(f"Paranet endpoint: {paranet_endpoint}")
    endpoint = para.web_endpoint(paranet_endpoint)
    
    if paranet_access_token and paranet_refresh_token:
        client = await endpoint.paranode(actor, access_token=paranet_access_token, refresh_token=paranet_refresh_token)
    elif paranet_password:
        client = await endpoint.paranode(actor, password=paranet_password)
    elif paranet_cognito_password:
        client = await endpoint.paranode(actor, cognito_password=paranet_cognito_password)
    elif paranet_jwt:
        client = await endpoint.paranode(actor, jwt=paranet_jwt)
    else:
        raise ValueError("No login method provided")

    print(f"Logged into {paranet_endpoint} as {actor_entity_id}")

    return client