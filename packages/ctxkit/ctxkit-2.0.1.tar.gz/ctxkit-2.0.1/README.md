# ctxkit

[![PyPI - Status](https://img.shields.io/pypi/status/ctxkit)](https://pypi.org/project/ctxkit/)
[![PyPI](https://img.shields.io/pypi/v/ctxkit)](https://pypi.org/project/ctxkit/)
[![GitHub](https://img.shields.io/github/license/craigahobbs/ctxkit)](https://github.com/craigahobbs/ctxkit/blob/main/LICENSE)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ctxkit)](https://pypi.org/project/ctxkit/)

ctxkit is a command-line tool for creating AI prompts to modify code. It works as follows:

- construct an AI prompt containing files, directories, and URL content

- calls an API to generate the prompt response

- extract modified or newly-created files in-place

In the following example, the project's Python source code is included (`-d src -x py`), then a
change request message (`-m`), then call the xAI API (`--api grok`), and finally extract the modified
project files (`--extract`):

```sh
ctxkit -d src -x py -m 'Please add -q argument' --api grok grok-4-fast-reasoning --extract
```


## Installation

To install ctxkit, enter the following commands in a terminal window:

**macOS and Linux**

```
python3 -m venv $HOME/venv --upgrade-deps
. $HOME/venv/bin/activate
pip install ctxkit
```

**Windows**

```
python3 -m venv %USERPROFILE%\venv --upgrade-deps
%USERPROFILE%\venv\Scripts\activate
pip install ctxkit
```


## Calling APIs

ctxkit supports the following APIs:

`claude` - [Claude (Anthropic) API](https://console.anthropic.com/dashboard/)

```sh
export ANTHROPIC_API_KEY=<key>
ctxkit -m 'Hello!' --api claude claude-3-5-haiku-latest
```

`gpt` - [ChatGPT (OpenAI) API](https://platform.openai.com/docs/api-reference/chat)

```sh
export OPENAI_API_KEY=<key>
ctxkit -m 'Hello!' --api gpt model-name
```

`grok` - [Grok (xAI) API](https://docs.x.ai/docs/tutorial)

```sh
export XAI_API_KEY=<key>
ctxkit -m 'Hello!' --api grok grok-3
```

`ollama` - [Ollama API](https://ollama.com/)

```sh
ctxkit -m 'Hello!' --api ollama gpt-oss:20b
```


### List Models

Use the `--list` argument to list an API's models. For example:

```sh
ctxkit --list claude
```


### Prompt from `stdin`

You can call an API with a prompt from `stdin` by passing no prompt items:

```sh
echo 'Hello!' | ctxkit --api ollama gpt-oss:20b
```


## Extract Response Files

When a prompt includes one or more files, the AI may respond with modified versions of the files.
You can extract the modified files using the `-e` (or `--extract`) argument:

```
ctxkit -d src -x py -m "Add a -q argument to silence output" --api grok grok-4-fast-reasoning --extract
```

In this example, ctxkit passes a prompt with all of the project source and a change request, to
which we expect the AI to respond with modified versions of some project files that satisfy the
requested change. Magic!


## Inline Instructions

The AI processes *inline instructions* within the included files. These are lines or comments that
begin with `ctxkit:` followed by instructions. For example:

```python
def calculate_total(items):
    # ctxkit: add a docstring
    return sum(total)
```

Files containing the inline instructions are modified per the instructions and the inline
instructions removed. Note that only instructions prefixed with `ctxkit:` are processed -
instructions intended for others (e.g. `user:`) are ignored.


## Variables

You can specify one or more variable references in a message's text, a file path, a directory path,
or a URL using the syntax, `{{var}}`. A variable's value is specified using the `-v` argument. For
example:

```sh
ctxkit -v package ctxkit -m 'Write brief overview of the Python package, "{{package}}"'
```


## Configuration Files

ctxkit JSON configuration files allow you to construct complex prompts in one or more JSON files.


### Example: Write Unit Tests

To generate a prompt to write unit tests for a function or method in a module, create a
configuration file similar to the following:

```json
{
    "items": [
        {"message": "Write the unit test methods to cover the code in the {{scope}}."},
        {"file": "src/my_package/{{base}}.py"},
        {"file": "src/tests/test_{{base}}.py"}
    ]
}
```

In this example, the "scope" variable allows you to specify what you want to write unit tests for.
The "base" variable specifies the base sub-module name. To generate the prompt, run ctxkit:

```sh
ctxkit -v base main -v scope "main function" -c unittest.json
```

This outputs:

```
<system>
...
</system>

Write the unit test methods to cover the code in the main function.

<src/my_package/main.py>
# main.py
</src/my_package/main.py>

<src/tests/test_main.py>
# test_main.py
</src/tests/test_main.py>
```


## Copy Output

To copy the output of ctxkit and paste it into your favorite AI chat application, pipe ctxkit's
output into the clipboard tool for your platform.

**macOS**

```sh
ctxkit -m 'Hello!' | pbcopy
```

**Windows**

```sh
ctxkit -m 'Hello!' | clip
```

**Linux**

```sh
ctxkit -m 'Hello!' | xsel -ib
```


## Usage

Using the `ctxkit` command line application, you can add any number of ordered *context items* of
the following types: configuration files (`-c`), messages (`-m`), file path or URL content (`-i` and
`-f`), and directories (`-d`).

The `CTXKIT_FLAGS` environment variable is used to define default arguments, such as `--api grok
grok-4-fast-reasoning` to set a default model. `CTXKIT_FLAGS` is prepended to the command-line arguments.

```
usage: ctxkit [-h] [-g] [-e] [-o PATH] [-b] [-c PATH] [-m TEXT] [-i PATH]
              [-t PATH] [-f PATH] [-d PATH] [-v VAR EXPR] [-s PATH] [-x EXT]
              [-l INT] [--api API MODEL] [--list API] [--temp NUM]
              [--topp NUM] [--maxtok NUM] [--noapi]

options:
  -h, --help           show this help message and exit
  -g, --config-help    display the JSON configuration file format

Output Options:
  -e, --extract        extract response files
  -o, --output PATH    output to the file path
  -b, --backup         backup output files with ".bak" extension

Prompt Items:
  -c, --config PATH    process the JSON configuration file path or URL
  -m, --message TEXT   add a prompt message
  -i, --include PATH   add the file path or URL text
  -t, --template PATH  add the file path or URL template text
  -f, --file PATH      add the file path or URL as a text file
  -d, --dir PATH       add a directory's text files
  -v, --var VAR EXPR   define a variable (reference with "{{var}}")
  -s, --system PATH    the system prompt file path or URL, "" for none

Directory Options:
  -x, --ext EXT        add a directory text file extension
  -l, --depth INT      the maximum directory depth, default is 0 (infinite)

API Calling:
  --api API MODEL      pass to an API provider (see "API Providers")
  --list API           list API provider models (see "API Providers")
  --temp NUM           set the model response temperature
  --topp NUM           set the model response top_p
  --maxtok NUM         set the model response max tokens
  --noapi              do not pass to an API provider

API Providers:
  claude - Claude (Anthropic) API
  gpt    - ChatGPT (OpenAI) API
  grok   - Grok (xAI) API
  ollama - Ollama API

Examples:
  ctxkit --api ollama gpt-oss:20b -m "How do I count code lines?"
  ctxkit --api grok grok-4-fast-reasoning -f README.md -f main.py -f test_main.py -m "Add a -q argument" -e
  ctxkit --api claude claude-opus-4-1 -f README.md -d src -x py -i spec.txt -e
  ctxkit --list grok
```


## Configuration File Format

The ctxkit `-g` argument outputs the JSON configuration file format defined using the
[Schema Markdown Language](https://craigahobbs.github.io/schema-markdown-js/language/).

```schema-markdown
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
```


## Development

This package is developed using [python-build](https://github.com/craigahobbs/python-build#readme).
It was started using [python-template](https://github.com/craigahobbs/python-template#readme) as follows:

```
template-specialize python-template/template/ ctxkit/ -k package ctxkit -k name 'Craig A. Hobbs' -k email 'craigahobbs@gmail.com' -k github 'craigahobbs' -k noapi 1
```
