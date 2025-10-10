# Licensed under the MIT License
# https://github.com/craigahobbs/ctxkit/blob/main/LICENSE

"""
OpenAI GPT API utilities
"""

import itertools
import json
import os

import urllib3


# Load environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


# API endpoint
OPENAI_URL = 'https://api.openai.com/v1/chat/completions'
OPENAI_MODELS_URL = 'https://api.openai.com/v1/models'


# Helper function to format OpenAI API errors
def _format_openai_error(base_message, error_data=None):
    error_message = base_message
    if error_data is not None:
        error_info = error_data.get('error')
        if isinstance(error_info, dict):
            if 'message' in error_info:
                error_message += f': {error_info["message"]}'
            if 'type' in error_info:
                error_message += f' (type: {error_info["type"]})'
            if 'code' in error_info:
                error_message += f' (code: {error_info["code"]})'
        else:
            error_message += f': {error_info}'

    return error_message


# Call the OpenAI API and yield the response chunk strings
def gpt_chat(pool_manager, model, system_prompt, prompt, temperature=None, top_p=None, max_tokens=None):
    # No API key?
    if not OPENAI_API_KEY:
        raise urllib3.exceptions.HTTPError('OPENAI_API_KEY environment variable not set')

    # Make POST request with streaming
    messages = []
    if system_prompt:
        messages.append({'role': 'system', 'content': system_prompt})
    messages.append({'role': 'user', 'content': prompt})
    gpt_json = {
        'model': model,
        'messages': messages,
        'stream': True
    }
    if temperature is not None:
        gpt_json['temperature'] = temperature
    if top_p is not None:
        gpt_json['top_p'] = top_p
    if max_tokens is not None:
        gpt_json['max_tokens'] = max_tokens
    response = pool_manager.request(
        method='POST',
        url=OPENAI_URL,
        headers={
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        },
        json=gpt_json,
        preload_content=False,
        retries=0
    )
    try:
        if response.status != 200:
            error_data = None
            try:
                error_data = json.loads(response.data.decode('utf-8'))
            except:
                pass
            error_message = _format_openai_error(f'OpenAI API failed with status {response.status}', error_data)
            raise urllib3.exceptions.HTTPError(error_message)

        # Process the streaming response
        data_prefix = None
        for line in itertools.chain.from_iterable(line.decode('utf-8').splitlines() for line in (response.read_chunked() or [])):
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

            # Parse the chunk
            try:
                chunk = json.loads(data)
            except json.JSONDecodeError:
                # If JSON parsing fails, save as prefix for next iteration
                data_prefix = data
                continue

            # Check for errors in the stream
            if 'error' in chunk:
                error_message = _format_openai_error('OpenAI API streaming error', chunk)
                raise urllib3.exceptions.HTTPError(error_message)

            # Yield the chunk content
            choices = chunk.get('choices', [])
            if choices:
                content = choices[0].get('delta', {}).get('content')
                if content:
                    yield content

    finally:
        response.close()


# List available GPT models
def gpt_list(pool_manager):
    # No API key?
    if not OPENAI_API_KEY:
        raise urllib3.exceptions.HTTPError('OPENAI_API_KEY environment variable not set')

    response = pool_manager.request(
        method='GET',
        url=OPENAI_MODELS_URL,
        headers={
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        },
        retries=0
    )
    try:
        if response.status != 200:
            error_data = None
            try:
                error_data = json.loads(response.data.decode('utf-8'))
            except:
                pass
            error_message = _format_openai_error(f'OpenAI API failed with status {response.status}', error_data)
            raise urllib3.exceptions.HTTPError(error_message)
        data = response.json()
        return [model['id'] for model in data.get('data', [])]
    finally:
        response.close()
