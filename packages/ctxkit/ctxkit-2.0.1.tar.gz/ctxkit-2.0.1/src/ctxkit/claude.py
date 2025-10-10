# Licensed under the MIT License
# https://github.com/craigahobbs/ctxkit/blob/main/LICENSE

"""
Claude API utilities
"""

import itertools
import json
import os

import urllib3


# Load environment variables
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')


# API endpoint
ANTHROPIC_URL = 'https://api.anthropic.com/v1/messages'
ANTHROPIC_MODELS_URL = 'https://api.anthropic.com/v1/models'


# Anthropic API requires max_tokens
ANTHROPIC_MAX_TOKENS = 8000


# Call the Claude API and yield the response chunk strings
def claude_chat(pool_manager, model, system_prompt, prompt, temperature=None, top_p=None, max_tokens=None):
    # No API key?
    if ANTHROPIC_API_KEY is None:
        raise urllib3.exceptions.HTTPError('ANTHROPIC_API_KEY environment variable not set')

    # Make POST request with streaming
    messages = [{'role': 'user', 'content': prompt}]
    claude_json = {
        'model': model,
        'messages': messages,
        'max_tokens': max_tokens or ANTHROPIC_MAX_TOKENS,
        'stream': True
    }
    if system_prompt:
        claude_json['system'] = system_prompt
    if temperature is not None:
        claude_json['temperature'] = temperature
    if top_p is not None:
        claude_json['top_p'] = top_p
    response = pool_manager.request(
        method='POST',
        url=ANTHROPIC_URL,
        headers={
            'x-api-key': ANTHROPIC_API_KEY,
            'anthropic-version': '2023-06-01',
            'Content-Type': 'application/json'
        },
        json=claude_json,
        preload_content=False,
        retries=0
    )
    try:
        if response.status != 200:
            raise urllib3.exceptions.HTTPError(f'Claude API failed with status {response.status}')

        # Process the streaming response
        data_prefix = None
        for line in itertools.chain.from_iterable(line.decode('utf-8').splitlines() for line in response.read_chunked()):
            # Skip non-data lines
            if not line.startswith('data: '):
                continue
            data = line[6:]
            if data == '[DONE]':
                break

            # Combine with previous partial line
            if data_prefix:
                data = data_prefix + data
                data_prefix = None

            # Parse the event data
            try:
                event = json.loads(data)
            except json.JSONDecodeError:
                # If JSON parsing fails, save as prefix for next iteration
                data_prefix = data
                continue

            # Check for API errors in the event
            if event.get('type') == 'error':
                error_message = event.get('error', {}).get('message', 'Unknown API error')
                raise urllib3.exceptions.HTTPError(f'Claude API error: {error_message}')

            # Yield content from content_block_delta
            if event.get('type') == 'content_block_delta' and 'delta' in event:
                delta = event['delta']
                if 'text' in delta:
                    yield delta['text']

    finally:
        response.close()


# List available Claude models
def claude_list(pool_manager):
    # No API key?
    if ANTHROPIC_API_KEY is None:
        raise urllib3.exceptions.HTTPError('ANTHROPIC_API_KEY environment variable not set')

    response = pool_manager.request(
        method='GET',
        url=ANTHROPIC_MODELS_URL,
        headers={
            'x-api-key': ANTHROPIC_API_KEY,
            'anthropic-version': '2023-06-01',
            'Content-Type': 'application/json'
        },
        retries=0
    )
    try:
        if response.status != 200:
            raise urllib3.exceptions.HTTPError(f'Claude API failed with status {response.status}')
        data = response.json()
        return [model['id'] for model in data.get('data', [])]
    finally:
        response.close()
