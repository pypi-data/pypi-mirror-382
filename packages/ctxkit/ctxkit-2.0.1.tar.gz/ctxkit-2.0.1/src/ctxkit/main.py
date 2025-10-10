# Licensed under the MIT License
# https://github.com/craigahobbs/ctxkit/blob/main/LICENSE

"""
ctxkit command-line script main module
"""

import argparse
from functools import partial
import json
import os
import re
import shutil
import sys

import schema_markdown
import urllib3

from .claude import claude_chat, claude_list
from .gpt import gpt_chat, gpt_list
from .grok import grok_chat, grok_list
from .ollama import ollama_chat, ollama_list


def main(argv=None):
    """
    ctxkit command-line script main entry point
    """

    # Combine the command-line and environment arguments
    argv_env = os.getenv('CTXKIT_FLAGS', '').split()
    argv_combined = argv_env + (sys.argv[1:] if argv is None else argv)

    # Compute the API provider documentation
    api_doc_lines = []
    api_desc_indent = max(len(api) for api in API_PROVIDERS) + 1
    for api in sorted(API_PROVIDERS.keys()):
        api_doc_lines.append(f'  {api}{" " * (api_desc_indent - len(api))}- {API_PROVIDERS[api]["description"]}')
    api_doc = '\n'.join(api_doc_lines)

    # Command line arguments
    parser = argparse.ArgumentParser(prog='ctxkit')
    parser.add_argument('-g', '--config-help', action='store_true', help='display the JSON configuration file format')
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument('-e', '--extract', action='store_true', help='extract response files')
    output_group.add_argument('-o', '--output', metavar='PATH', help='output to the file path')
    output_group.add_argument('-b', '--backup', action='store_true', help='backup output files with ".bak" extension')
    items_group = parser.add_argument_group('Prompt Items')
    items_group.add_argument('-c', '--config', metavar='PATH', dest='items', action=TypedItemAction, item_type='config',
                             help='process the JSON configuration file path or URL')
    items_group.add_argument('-m', '--message', metavar='TEXT', dest='items', action=TypedItemAction, item_type='message',
                             help='add a prompt message')
    items_group.add_argument('-i', '--include', metavar='PATH', dest='items', action=TypedItemAction, item_type='include',
                             help='add the file path or URL text')
    items_group.add_argument('-t', '--template', metavar='PATH', dest='items', action=TypedItemAction, item_type='template',
                             help='add the file path or URL template text')
    items_group.add_argument('-f', '--file', metavar='PATH', dest='items', action=TypedItemAction, item_type='file',
                             help='add the file path or URL as a text file')
    items_group.add_argument('-d', '--dir', metavar='PATH', dest='items', action=TypedItemAction, item_type='dir',
                             help="add a directory's text files")
    items_group.add_argument('-v', '--var', nargs=2, metavar=('VAR', 'EXPR'), dest='items', action=TypedItemAction, item_type='var',
                             help='define a variable (reference with "{{var}}")')
    items_group.add_argument('-s', '--system', metavar='PATH', help='the system prompt file path or URL, "" for none')
    dir_group = parser.add_argument_group('Directory Options')
    dir_group.add_argument('-x', '--ext', action='append', default=[], help='add a directory text file extension')
    dir_group.add_argument('-l', '--depth', metavar='INT', type=int, default=0, help='the maximum directory depth, default is 0 (infinite)')
    api_group = parser.add_argument_group('API Calling')
    api_group.add_argument('--api', nargs=2, metavar=('API', 'MODEL'), action=APIAction,
                           help='pass to an API provider (see "API Providers")')
    api_group.add_argument('--list', metavar='API', action=APIAction,
                           help='list API provider models (see "API Providers")')
    api_group.add_argument('--temp', metavar='NUM', type=float, help='set the model response temperature')
    api_group.add_argument('--topp', metavar='NUM', type=float, help='set the model response top_p')
    api_group.add_argument('--maxtok', metavar='NUM', type=int, help='set the model response max tokens')
    api_group.add_argument('--noapi', dest='api', action='store_false', help='do not pass to an API provider')
    parser.epilog = f'''\
API Providers:
{api_doc}

Examples:
  ctxkit --api ollama gpt-oss:20b -m "How do I count code lines?"
  ctxkit --api grok grok-4-fast-reasoning -f README.md -f main.py -f test_main.py -m "Add a -q argument" -e
  ctxkit --api claude claude-opus-4-1-20250805 -f README.md -d src -x py -i spec.txt -e
  ctxkit --list grok
'''
    parser.formatter_class = argparse.RawDescriptionHelpFormatter
    args = parser.parse_args(args=argv_combined)

    # Show configuration file format?
    if args.config_help:
        print(CTXKIT_SMD.strip())
        return

    # Initialize urllib3 PoolManager
    pool_manager = urllib3.PoolManager()

    try:
        # List models?
        if args.list:
            models = API_PROVIDERS[args.list]['list'](pool_manager)
            print('\n'.join(sorted(models)))
            return

        # Load the config file
        config = {'items': []}
        for item_type, item_value in (args.items or []):
            if item_type == 'config':
                config['items'].append({'config': item_value})
            elif item_type == 'include':
                config['items'].append({'include': item_value})
            elif item_type == 'template':
                config['items'].append({'template': item_value})
            elif item_type == 'file':
                config['items'].append({'file': item_value})
            elif item_type == 'dir':
                config['items'].append({'dir': {'path': item_value, 'exts': args.ext, 'depth': args.depth}})
            elif item_type == 'var':
                config['items'].append({'var': {'name': item_value[0], 'value': item_value[1]}})
            else: # item_type == 'message':
                config['items'].append({'message': item_value})

        # Get the system prompt
        system_prompt = DEFAULT_SYSTEM
        if args.system is not None:
            system_prompt = _fetch_text(pool_manager, args.system) if args.system else None

        # Output file?
        if args.output:
            # Backup the output file, if requested
            if args.backup and os.path.isfile(args.output):
                shutil.copy(args.output, f'{args.output}.bak')

            # Create the output directory
            output_dir = os.path.dirname(args.output)
            if output_dir: # pragma: no branch
                os.makedirs(output_dir, exist_ok=True)

        # Pass stdin to an AI?
        if args.api and not config['items']:
            prompt = sys.stdin.read()
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as output:
                    _output_api_call(args, pool_manager, output, system_prompt, prompt)
            else:
                _output_api_call(args, pool_manager, sys.stdout, system_prompt, prompt)
            return

        # No items specified
        if not config['items']:
            parser.error('no prompt items specified')

        # Process the configuration
        if args.api:
            # Pass prompt to an AI
            prompt = process_config(pool_manager, config, {})
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as output:
                    _output_api_call(args, pool_manager, output, system_prompt, prompt)
            else:
                _output_api_call(args, pool_manager, sys.stdout, system_prompt, prompt)
        else:
            # Output to file?
            if args.output:
                prompt = process_config(pool_manager, config, {})
                with open(args.output, 'w', encoding='utf-8') as output:
                    print(prompt, file=output)
            else:
                # Output to stdout
                items = []
                if system_prompt:
                    items.append(f'<system>\n{system_prompt}\n</system>')
                items.extend(process_config_items(pool_manager, config, {}))
                for ix_item, item_text in enumerate(items):
                    if ix_item != 0:
                        print()
                    print(item_text)

    except Exception as exc:
        print(f'\nError: {exc}', file=sys.stderr)
        sys.exit(2)


# API providers
API_PROVIDERS = {
    'claude': {
        'description': 'Claude (Anthropic) API',
        'chat': claude_chat,
        'list': claude_list
        },
    'gpt': {
        'description': 'ChatGPT (OpenAI) API',
        'chat': gpt_chat,
        'list': gpt_list
    },
    'grok': {
        'description': 'Grok (xAI) API',
        'chat': grok_chat,
        'list': grok_list
    },
    'ollama': {
        'description': 'Ollama API',
        'chat': ollama_chat,
        'list': ollama_list
    }
}


# argparse action to validate API provider
class APIAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        provider = values[0] if isinstance(values, list) else values
        if provider not in API_PROVIDERS:
            parser.error(f'Invalid API provider "{provider}". Valid options are: {", ".join(sorted(API_PROVIDERS.keys()))}')
        setattr(namespace, self.dest, values)


# argparse action typed-value items
class TypedItemAction(argparse.Action):

    def __init__(self, *args, **kwargs):
        self.item_type = kwargs.pop('item_type')
        super().__init__(*args, **kwargs)


    def __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest)
        if items is None:
            items = []
            setattr(namespace, self.dest, items)
        items.append((self.item_type, values))


DEFAULT_SYSTEM = '''\
You are a helpful assistant that can read and modify files provided in the prompt.

You can read and modify files provided in the prompt. When outputting modified or new files, always
provide the complete, updated content of the entire file, not just the modified parts. Use this
format:

<filename>
<complete content of the file>
</filename>

To delete a file, use:

<filename>
ctxkit: delete
</filename>

Files containing the inline instructions, lines or code comments that begin with "ctxkit:" followed
by instructions, are modified per the instructions and the inline instructions removed. Only process
instructions specifically prefixed with "ctxkit:" and ignore instructions intended for others (e.g.
"user:").

<filename>
    # ctxkit: Add a docstring
    def foo():
        pass
</filename>

Do not output files that have not changed.
You can include explanatory text outside of these file tags.'''


# Helper to output the response from stdin to passed to an API
def _output_api_call(args, pool_manager, output, system_prompt, prompt):
    provider, model = args.api
    api_func = API_PROVIDERS[provider]['chat']

    # Write the response to the output
    chunks = []
    for chunk in api_func(pool_manager, model, system_prompt, prompt, args.temp, args.topp, args.maxtok):
        chunks.append(chunk)
        output.write(chunk)
        output.flush()
    if chunks:
        output.write('\n')

    # Extract files, if requested
    if args.extract:
        _extract_files(''.join(chunks), args.backup)


# Helper to extract files from a response
def _extract_files(response, backup):
    search_pos = 0
    while True:
        match = _R_FILENAME_TAG.search(response, search_pos)
        if not match:
            break
        file_path = os.path.normpath(match.group(1))
        content = match.group(2).strip()
        search_pos = match.end()

        # Ignore URLs
        if _is_url(file_path):
            continue

        # Delete?
        if content == 'ctxkit: delete':
            if os.path.exists(file_path):
                os.remove(file_path)
            continue

        # Backup the existing file
        if backup and os.path.exists(file_path):
            shutil.copy(file_path, f'{file_path}.bak')

        # Create the file's parent directory
        file_dir = os.path.dirname(file_path)
        if file_dir: # pragma: no branch
            os.makedirs(file_dir, exist_ok=True)

        # Write the file
        with open(file_path, 'w', encoding='utf-8') as file_:
            file_.write(content.strip())
            file_.write('\n')


_R_FILENAME_TAG = re.compile(r'^<([^<>]+)>\n(.*)\n</\1>', re.DOTALL | re.MULTILINE)


# Process a configuration model and return the prompt string
def process_config(pool_manager, config, variables, root_dir='.'):
    return '\n\n'.join(process_config_items(pool_manager, config, variables, root_dir))


# Process a configuration model and yield the prompt item strings
def process_config_items(pool_manager, config, variables, root_dir='.'):
    # Output the prompt items
    for item in config['items']:
        item_key = list(item.keys())[0]

        # Get the item path, if any
        item_path = None
        if item_key in ('config', 'include', 'template', 'file'):
            item_path = _replace_variables(item[item_key], variables)
        elif item_key == 'dir':
            item_path = _replace_variables(item[item_key]['path'], variables)

        # Normalize the item path
        if item_path is not None and not _is_url(item_path) and not os.path.isabs(item_path):
            item_path = os.path.normpath(os.path.join(root_dir, item_path))

        # Config item
        if item_key == 'config':
            config = schema_markdown.validate_type(CTXKIT_TYPES, 'CtxKitConfig', json.loads(_fetch_text(pool_manager, item_path)))
            yield from process_config_items(pool_manager, config, variables, os.path.dirname(item_path))

        # File include item
        elif item_key == 'include':
            yield _fetch_text(pool_manager, item_path)

        # File include with variables item
        elif item_key == 'template':
            yield _replace_variables(_fetch_text(pool_manager, item_path), variables)

        # File item
        elif item_key == 'file':
            file_text = _fetch_text(pool_manager, item_path)
            newline = '\n'
            yield f'<{item_path}>{newline}{file_text}{newline if file_text else ""}</{item_path}>'

        # Directory item
        elif item_key == 'dir':
            # Recursively find the files of the requested extensions
            dir_exts = [f'.{ext.lstrip(".")}' for ext in item['dir'].get('exts') or []]
            dir_depth = item['dir'].get('depth', 0)
            dir_files = list(_get_directory_files(item_path, dir_exts, dir_depth))
            if not dir_files:
                raise Exception(f'No files found, "{item_path}"')

            # Output the file text
            newline = '\n'
            for file_path in dir_files:
                file_text = _fetch_text(pool_manager, file_path)
                yield f'<{file_path}>{newline}{file_text}{newline if file_text else ""}</{file_path}>'

        # Variable definition item
        elif item_key == 'var':
            variables[item['var']['name']] = item['var']['value']

        # Long message item
        elif item_key == 'long':
            yield _replace_variables('\n'.join(item['long']), variables)

        # Message item
        else: # if item_key == 'message'
            yield _replace_variables(item['message'], variables)


# Helper to fetch a file or URL text
def _fetch_text(pool_manager, path):
    if _is_url(path):
        response = pool_manager.request(method='GET', url=path, retries=0)
        try:
            if response.status != 200:
                raise urllib3.exceptions.HTTPError(f'POST {path} failed with status {response.status}')
            return response.data.decode('utf-8').strip()
        finally:
            response.close()
    else:
        with open(path, 'r', encoding='utf-8') as file:
            return file.read().strip()


# Helper to determine if a path is a URL
def _is_url(path):
    return re.match(_R_URL, path)

_R_URL = re.compile(r'^[a-z]+:')


# Helper to replace variable references
def _replace_variables(text, variables):
    return _R_VARIABLE.sub(partial(_replace_variables_match, variables), text)

def _replace_variables_match(variables, match):
    var_name = match.group(1)
    return str(variables.get(var_name, ''))

_R_VARIABLE = re.compile(r'\{\{\s*([_a-zA-Z]\w*)\s*\}\}')


# Helper enumerator to recursively get a directory's files
def _get_directory_files(dir_name, file_exts, max_depth=0, current_depth=0):
    yield from (file_path for _, file_path in sorted(_get_directory_files_helper(dir_name, file_exts, max_depth, current_depth)))

def _get_directory_files_helper(dir_name, file_exts, max_depth, current_depth):
    # Recursion too deep?
    if max_depth > 0 and current_depth >= max_depth:
        return

    # Scan the directory for files
    for entry in os.scandir(dir_name):
        if entry.is_file():
            if os.path.splitext(entry.name)[1] in file_exts:
                file_path = os.path.normpath(os.path.join(dir_name, entry.name))
                yield (os.path.split(file_path), file_path)
        elif entry.is_dir(): # pragma: no branch
            dir_path = os.path.join(dir_name, entry.name)
            yield from _get_directory_files_helper(dir_path, file_exts, max_depth, current_depth + 1)


# The ctxkit configuration file format
CTXKIT_SMD = '''\
# The ctxkit configuration file format
struct CtxKitConfig

    # The list of prompt items
    CtxKitItem[len > 0] items


# A prompt item
union CtxKitItem

    # Config file path or URL
    string config

    # A prompt message
    string message

    # A long prompt message
    string[len > 0] long

    # File path or URL text
    string include

    # File path or URL template text
    string template

    # File path or URL as a text file
    string file

    # Add a directory's text files
    CtxKitDir dir

    # Set a variable (reference with "{{var}}")
    CtxKitVariable var


# A directory item
struct CtxKitDir

    # The directory file path or URL
    string path

    # The file extensions to include (e.g. ".py")
    string[] exts

    # The directory traversal depth (default is 0, infinite)
    optional int(>= 0) depth


# A variable definition item
struct CtxKitVariable

    # The variable's name
    string name

    # The variable's value
    string value
'''
CTXKIT_TYPES = schema_markdown.parse_schema_markdown(CTXKIT_SMD)
