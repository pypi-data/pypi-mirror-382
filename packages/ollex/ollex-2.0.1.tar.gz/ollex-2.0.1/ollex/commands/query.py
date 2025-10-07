"""Ollex "query" command."""

import json
import readline  # noqa
import sys
from argparse import Namespace
from collections.abc import Iterator
from contextlib import suppress
from functools import lru_cache
from importlib import resources
from itertools import product
from os import isatty
from pathlib import Path
from random import choice
from time import time
from typing import Any, TextIO

import chromadb
import ollama
import yaml
from rich.align import Align
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.status import Status

from ollex.commands import CliCommand
from ollex.exceptions import OllexError
from ollex.lib.argparse import StoreNameValuePair
from ollex.lib.misc import plural
from ollex.lib.model import LLM_OPTIONS
from ollex.repl import ReplCommandController

EMBEDDING_MODEL = 'nomic-embed-text'  # Last resort only
MIN_QUERY_LENGTH = 10  # Applies to repl only
REPL_CMD_ESCAPE = '\\'
HISTORY_FILE = Path('~/.ollex_history').expanduser()
HISTORY_LENGTH = 100

# Number of docuemnts to return when searching the database.
N_SEARCH_RESULTS = 10

Style = Namespace(
    prompt='green',
    info='italic yellow',
    status='italic #008800',
    banner='red on white',
    error='red',
)

LLM_PROMPT_FILE = resources.files('ollex') / 'resources' / 'prompts.yaml'

BANNERS = [
    line
    for line in (resources.files('ollex') / 'resources' / 'banners.txt').read_text().splitlines()
    if line.strip() and not line.startswith('#')
]


# ------------------------------------------------------------------------------
@CliCommand.register('query')
class Query(CliCommand):
    """Interact with Ollama in REPL or batch mode."""

    # --------------------------------------------------------------------------
    def add_arguments(self) -> None:
        """Add arguments to the command handler."""

        self.argp.add_argument(
            'db_directory',
            help='Directory containing the Chroma DB containing embeddings.',
        )

        self.argp.add_argument(
            '-c',
            '--collection',
            action='append',
            default=[],
            help=(
                'Database collection to use. Multiple collections can be active at'
                ' the same time by repeating this option. A response is provided for'
                ' each active collection. If not specified and the database has'
                ' only one collection, that will be used. In interactive mode, the'
                ' collection(s) can also be specified using an interactive command.'
                ' A collection must be specified for any queries to be run.'
            ),
        )
        self.argp.add_argument(
            '-l',
            '--llm',
            metavar='MODEL',
            default=[],
            action='append',
            help=(
                'Model to be used for the LLM. Multiple models can be active at the'
                ' same time by repeating this option. A response is provided for'
                ' each active model. At least one model must be specified, either'
                f' as a command argument or via the {REPL_CMD_ESCAPE}llm'
                ' interactive command in order to process any queries.'
            ),
        )

        self.argp.add_argument(
            '-e',
            '--embedding',
            default=EMBEDDING_MODEL,
            help=(
                'The embedding used when creating storing documents in the database.'
                ' This is determined (in order or precedence) by'
                ' (1) the value stored in config.yaml in the database directory;'
                ' (2) the value of this argument;'
                f' (3) the default ({EMBEDDING_MODEL}).'
            ),
        )

        self.argp.add_argument(
            '-o',
            '--option',
            metavar='NAME=VALUE',
            dest='llm_options',
            action=StoreNameValuePair,
            default={},
            help=(
                'Set the specified LLM control option(s). Available options are:'
                f' {", ".join(sorted(LLM_OPTIONS.keys()))}.'
            ),
        )

        self.argp.add_argument(
            '-p',
            '--prompts',
            metavar='FILE.yaml',
            dest='prompts_file',
            default=str(LLM_PROMPT_FILE),
            help=(
                'Read prompts from the specified YAML file. Keys are the prompt IDs'
                ' and values are the prompt text. Each prompt must contain "{data}"'
                ' and "{question}" somewhere. If not specified, a default prompt is'
                f' used. Use the {REPL_CMD_ESCAPE}prompt interactive command to see'
                f' its content.'
            ),
        )

        self.argp.add_argument(
            '-n',
            type=int,
            metavar='COUNT',
            default=1,
            help='(Batch mode only) Run each query the specified number of times. Default 1.',
        )

        self.argp.add_argument(
            '-r',
            '--search-results',
            action='store',
            type=int,
            metavar='COUNT',
            default=N_SEARCH_RESULTS,
            help=(
                'Number of documents to return when searching the database.'
                f' Default is {N_SEARCH_RESULTS}.'
            ),
        )

    # --------------------------------------------------------------------------
    @staticmethod  # noqa B027
    def check_arguments(args: Namespace) -> None:
        """Validate arguments."""

        if args.llm_options:
            options = {}
            for k, v in args.llm_options.items():
                try:
                    options[k] = LLM_OPTIONS[k](v)
                except KeyError:
                    raise ValueError(f'Unknown LLM option: {k}')
                except (TypeError, ValueError) as e:
                    raise ValueError(f'Option {k}: {e}')
            args.llm_options = options

        # Validate that we have the LLMs requested
        available_llms = {m.model.removesuffix(':latest') for m in ollama.list().models}
        requested_llms = {m.removesuffix(':latest') for m in args.llm}
        if unavailable_llms := requested_llms - available_llms:
            raise ValueError(f'Unavailable models: {", ".join(sorted(unavailable_llms))}')
        args.llm = sorted(requested_llms)

    # --------------------------------------------------------------------------
    @staticmethod
    def execute(args: Namespace) -> int:
        """Execute the command."""

        # Open vector DB
        db_dirpath = Path(args.db_directory)
        if not db_dirpath.is_dir():
            raise FileNotFoundError(f'{args.db_directory} doesn\'t exist or is not a directory.')
        db_client = chromadb.PersistentClient(path=args.db_directory)

        # Load config file stored in root of DB folder. This is not a chroma construct.
        # It was added by our utility that populates the database.
        try:
            config = yaml.safe_load((db_dirpath / 'config.yaml').read_text())
        except FileNotFoundError:
            config = {}

        # Validate collections requested on command line.
        requested_collections = set(args.collection)
        available_collections = {c.name for c in db_client.list_collections()}
        if unavailable_collections := requested_collections - available_collections:
            raise OllexError(
                f'Unavailable collections: {", ".join(sorted(unavailable_collections))}'
            )

        if isatty(sys.stdin.fileno()) and isatty(sys.stdout.fileno()):
            try:
                with suppress(FileNotFoundError):
                    readline.read_history_file(HISTORY_FILE)
                repl(config, db_client, args)
            finally:
                with suppress(Exception):
                    readline.set_history_length(HISTORY_LENGTH)
                    readline.write_history_file(HISTORY_FILE)
        else:
            batch_loop(config, db_client, args)

        return 0


# ------------------------------------------------------------------------------
def get_queries_from_console(console: Console) -> Iterator[str]:
    """Prompt for queries."""

    while True:
        try:
            query = console.input(f'\n[{Style.prompt}]Query: ')
        except EOFError:
            return
        finally:
            print()
        if query:
            yield query.strip()


# ------------------------------------------------------------------------------
def get_queries_from_file(fp: TextIO) -> Iterator[str]:
    """Read queries from a file."""

    lines = []
    for line in fp:
        if not line.strip():
            if lines:
                yield ''.join(lines)
                lines = []
            continue
        lines.append(line)

    if lines:
        yield ''.join(lines)


# ------------------------------------------------------------------------------
def refresh_yaml_dict(filename: str) -> dict[str, Any]:
    """Read a dict from a YAML file, cache results and reread if it has been modified."""

    path = Path(filename)

    try:
        mtime, content = refresh_yaml_dict.cache[filename]  # noqa
        if path.stat().st_mtime <= mtime:
            return content
    except AttributeError:
        refresh_yaml_dict.cache = {}
    except KeyError:
        pass

    # Content doesn't exist or is out of date
    content = yaml.safe_load(path.read_text())
    if not isinstance(content, dict):
        raise ValueError('Must be dict')
    refresh_yaml_dict.cache[filename] = (path.stat().st_mtime, content)  # noqa
    return content


# ------------------------------------------------------------------------------
def get_collection_info(
    db_client: chromadb.ClientAPI, config: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    """
    Merge information about collections from the config file with collections found in the DB.

    :param db_client:   Chroma DB client.
    :param config:      The meta config which may contain a "collections" key
                        which is a dict containing info on each collection.
    :return:            A dictionary with the collection info for each
                        collection actually present in the DB.
    """

    db_collections = db_client.list_collections()
    if not db_collections:
        raise OllexError('No collections found in database')

    available_collections = {c.name for c in db_client.list_collections()}
    return {c: config.get('collections', {}).get(c, {}) for c in available_collections}


# ------------------------------------------------------------------------------
@lru_cache(maxsize=50)
def search_collection(
    db_client: chromadb.ClientAPI,
    collection: str,
    embedding_model: str,
    query: str,
    n_results: int,
) -> list[str]:
    """
    Search a ChromaDB collection using the specified query and embedding model.

    :param db_client:       Chroma DB client.
    :param collection:      Collection name.
    :param embedding_model: Embedding model name.
    :param query:           The LLM query for which to search.
    :param n_results:       Number of results to return.
    :return:                A list of search result strings.
    """

    embedded_query = ollama.embed(model=embedding_model, input=query)
    return db_client.get_collection(collection).query(
        query_embeddings=embedded_query['embeddings'],
        n_results=n_results,
    )['documents'][0]


# ------------------------------------------------------------------------------
def repl(config: dict[str, Any], db_client: chromadb.ClientAPI, cli_args: Namespace) -> None:
    """
    Run an interactive REPL.

    :param config:      Configuration metadata read from the database directory.
    :param db_client:   Chroma DB client.
    :param cli_args:    CLI arguments namespace.
    """

    repl_context = Namespace(
        llm=cli_args.llm,
        llm_options=cli_args.llm_options,
        collection_info=get_collection_info(db_client, config),
        collections=sorted(cli_args.collection),
        search_results=cli_args.search_results,
        prompts=refresh_yaml_dict(cli_args.prompts_file),
    )
    # If the DB contains a single collection default to that.
    if not repl_context.collections and len(repl_context.collection_info) == 1:
        repl_context.collections = list(repl_context.collection_info)

    console = Console()
    repl_command_controller = ReplCommandController(repl_context, console, REPL_CMD_ESCAPE)

    if BANNERS:
        console.print()
        console.print(
            Align.center(
                Panel(choice(BANNERS), style=Style.banner, border_style=Style.banner)  # noqa S311
            )
        )
    console.print()
    selected_models = ', '.join(sorted(repl_context.llm)) or '(not set - use /l)'
    selected_collections = ', '.join(repl_context.collections) or '(not set - use /c)'
    console.print(
        f'[{Style.info}]'
        f'{plural("Model", len(repl_context.llm))} = {selected_models}'
        '    '
        f'{plural("Collections", len(repl_context.collections))} = {selected_collections}'
        '    '
        f'{plural("Prompt", len(repl_context.prompts))} = {", ".join(repl_context.prompts)}'
    )

    for query in get_queries_from_console(console):
        # Read prompts. This is reread for any changes.
        repl_context.prompts = refresh_yaml_dict(cli_args.prompts_file)
        if query.startswith(REPL_CMD_ESCAPE):
            try:
                if not repl_command_controller.do_cmd(query[1:]):
                    break
            except Exception as e:
                console.print(f'[{Style.error}]{e}')
            continue

        if not repl_context.llm:
            console.print(f'[{Style.error}]One or more LLMs must be set -- try {REPL_CMD_ESCAPE}l')
            continue

        if not repl_context.collections:
            console.print(f'[{Style.error}]A data collection must be set -- try {REPL_CMD_ESCAPE}c')
            continue

        if len(query) < MIN_QUERY_LENGTH:
            console.print(f'[{Style.error}]Query is too short')
            readline.remove_history_item(readline.get_current_history_length() - 1)
            continue

        # Important the LLM is first in the product to minimise model loading / unloading
        for llm, collection, (prompt_id, prompt_txt) in product(
            repl_context.llm, repl_context.collections, repl_context.prompts.items()
        ):
            status = Status(f'[{Style.status}]Searching {collection} ...')
            status.start()
            embedding_model = (
                config.get('collections', {}).get(collection, {}).get('embedding_model')
            ) or cli_args.embedding

            try:
                query_results = search_collection(
                    db_client,
                    collection,
                    embedding_model,
                    query,
                    n_results=repl_context.search_results,
                )
            except Exception as e:
                status.stop()
                console.print(f'[{Style.error}]Query failed: {e}')
                continue
            else:
                status.stop()

            status = Status(
                f'[{Style.status}]Model = {llm}   Collection = {collection}   Prompt = {prompt_id}'
            )
            status.start()
            ts = time()
            try:
                response = ollama.generate(
                    model=llm,
                    options=repl_context.llm_options,
                    prompt=prompt_txt.format(data=query_results, question=query),
                )
            except Exception as e:
                status.stop()
                console.print(f'[{Style.error}]{e}')
                continue
            else:
                status.stop()
            console.rule(
                f'[{Style.info}]Model = {llm}   Collection = {collection}   Prompt = {prompt_id}',
                style=Style.info,
            )

            answer = response['response']
            elapsed = round(time() - ts, 1)
            console.print(Markdown(answer))
            console.print(f'\n[{Style.info}]{elapsed} s')
            console.print()


# ------------------------------------------------------------------------------
def batch_loop(config: dict[str, Any], db_client: chromadb.ClientAPI, cli_args: Namespace) -> None:
    """
    Run a batch query loop.

    :param config:      Configuration metadata read from the database directory.
    :param db_client:   Chroma DB client.
    :param cli_args:    CLI arguments namespace.
    """

    if not cli_args.llm:
        raise OllexError('LLM(s) must be specified in batch mode')

    collection_names = cli_args.collection
    if not collection_names:
        db_collections = db_client.list_collections()
        if len(db_collections) == 1:
            collection_names = db_collections
        else:
            raise OllexError(
                'Collection must be specified in batch mode'
                ' if DB contains more than one collection'
            )
    collections = {name: db_client.get_collection(name=name) for name in collection_names}
    prompts = refresh_yaml_dict(cli_args.prompts_file)

    for query in get_queries_from_file(sys.stdin):
        for llm, collection, (prompt_id, prompt_txt) in product(
            cli_args.llm, collections, prompts.items()
        ):
            embedding_model = (
                config.get('collections', {}).get(collection, {}).get('embedding_model')
                or cli_args.embedding
            )
            query_results = search_collection(
                db_client,
                collection,
                embedding_model,
                query,
                n_results=cli_args.search_results,
            )
            for n in range(cli_args.n):
                ts = time()
                response = ollama.generate(
                    model=llm,
                    options=cli_args.llm_options,
                    prompt=prompt_txt.format(data=query_results, question=query),
                )
                answer = response['response']
                elapsed = round(time() - ts, 1)
                print(
                    json.dumps(
                        {
                            'query': query.strip(),
                            'sequence_no': n,
                            'prompt_id': prompt_id,
                            'answer': answer,
                            'elapsed': elapsed,
                            'collection': collection,
                            'embedding_model': embedding_model,
                            'search_results': cli_args.search_results,
                            'llm': llm,
                            'options': cli_args.llm_options,
                        }
                    )
                )
