# Licensed under the MIT License
# https://github.com/craigahobbs/ctxkit/blob/main/LICENSE

"""
Grok API utilities
"""

import itertools
import json
import os

import urllib3


# Load environment variables
XAI_API_KEY = os.getenv('XAI_API_KEY')


# API endpoint
XAI_URL = 'https://api.x.ai/v1/chat/completions'
XAI_MODELS_URL = 'https://api.x.ai/v1/models'


# Call the xAI API and yield the response chunk strings
def grok_chat(pool_manager, model, system_prompt, prompt, temperature=None, top_p=None, max_tokens=None):
    # No API key?
    if XAI_API_KEY is None:
        raise urllib3.exceptions.HTTPError('XAI_API_KEY environment variable not set')

    # Make POST request with streaming
    messages = []
    if system_prompt:
        messages.append({'role': 'system', 'content': system_prompt})
    messages.append({'role': 'user', 'content': prompt})
    xai_json = {
        'model': model,
        'messages': messages,
        'stream': True
    }
    if temperature is not None:
        xai_json['temperature'] = temperature
    if top_p is not None:
        xai_json['top_p'] = top_p
    if max_tokens is not None:
        xai_json['max_tokens'] = max_tokens
    response = pool_manager.request(
        method='POST',
        url=XAI_URL,
        headers={
            'Authorization': f'Bearer {XAI_API_KEY}',
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream'
        },
        json=xai_json,
        preload_content=False,
        retries=0
    )
    try:
        if response.status != 200:
            raise urllib3.exceptions.HTTPError(f'xAI API failed with status {response.status}')

        # Process the streaming response
        data_prefix = None
        for line in itertools.chain.from_iterable(line.decode('utf-8').splitlines() for line in response.read_chunked()):
            # Parse the data chunk
            if not line.startswith('data: '):
                continue
            data = line[6:]
            if data == '[DONE]':
                break

            # Combine with previous partial line
            if data_prefix:
                data = data_prefix + data
                data_prefix = None

            # Parse the chunk
            try:
                chunk = json.loads(data)
            except json.JSONDecodeError:
                # If JSON parsing fails, save as prefix for next iteration
                data_prefix = data
                continue

            # Yield the chunk content
            content = chunk['choices'][0]['delta'].get('content')
            if content:
                yield content

    finally:
        response.close()


# List available Grok models
def grok_list(pool_manager):
    # No API key?
    if XAI_API_KEY is None:
        raise urllib3.exceptions.HTTPError('XAI_API_KEY environment variable not set')

    response = pool_manager.request(
        method='GET',
        url=XAI_MODELS_URL,
        headers={
            'Authorization': f'Bearer {XAI_API_KEY}',
            'Content-Type': 'application/json'
        },
        retries=0
    )
    try:
        if response.status != 200:
            raise urllib3.exceptions.HTTPError(f'xAI API failed with status {response.status}')
        data = response.json()
        return [model['id'] for model in data.get('data', [])]
    finally:
        response.close()
