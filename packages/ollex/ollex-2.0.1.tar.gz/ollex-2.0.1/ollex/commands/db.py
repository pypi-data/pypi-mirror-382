"""Ollex "db" command."""

from argparse import Namespace
from hashlib import sha256
from pathlib import Path

import chromadb
import yaml
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.documents import Document  # noqa
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter
from rich.progress import Progress

from ollex.commands import CliCommand
from ollex.exceptions import OllexError
from ollex.lib.argparse import StoreNameValuePair
from ollex.lib.misc import chunk_list
from ollex.lib.model import get_embedding_dimensions

DEFAULT_COLLECTION = 'ai-boondoggle'

HEADERS_TO_SPLIT_ON = [
    ('#', 'Header 1'),
    ('##', 'Header 2'),
    ('###', 'Header 3'),
    ('####', 'Header 4'),
]

# Default values for embedding documents into a database collection.
# These can be set when a collection is created and cannot then be changed.
FROZEN_CONFIG = {
    'embedding_model': 'nomic-embed-text',
    'chunk_size': 1000,
    'chunk_overlap': 100,
}


# ------------------------------------------------------------------------------
@CliCommand.register('db')
class Db(CliCommand):
    """Load Markdown documents into a Chroma vector DB."""

    # --------------------------------------------------------------------------
    def add_arguments(self) -> None:
        """Add arguments to the command handler."""

        self.argp.add_argument('db_directory', help='Directory containing the Chroma DB.')
        self.argp.add_argument(
            'files',
            metavar='FILE.md',
            nargs='+',
            help='Markdown documents to add.',
        )

        self.argp.add_argument(
            '-c',
            '--collection',
            action='store',
            default=DEFAULT_COLLECTION,
            help=(
                'Database collection to which documents will be added. This will be'
                f' created if it does not exist. Default is {DEFAULT_COLLECTION}.'
            ),
        )

        self.argp.add_argument(
            '-p',
            '--param',
            metavar='NAME=VALUE',
            default={},
            action=StoreNameValuePair,
            help=(
                'Set the specified embedding control parameter(s). Default values are:'
                f' {", ".join(f"{k}={v}" for k, v in sorted(FROZEN_CONFIG.items()))}.'
                f' These cannot be changed for an existing collection and it is an error'
                f' to attempt to do so.'
            ),
        )

    @staticmethod  # noqa B027
    def check_arguments(args: Namespace) -> None:
        """Validate arguments."""

        for k, v in args.param.items():
            # Coerce values to the same type as the default
            try:
                args.param[k] = type(FROZEN_CONFIG[k])(v)
            except KeyError:
                raise ValueError(f'Parameter {k}: Not valid')
            except (ValueError, TypeError) as e:
                raise ValueError(f'Parameter {k}: {e}')

    # --------------------------------------------------------------------------
    @staticmethod
    def execute(args: Namespace) -> int:
        """Execute the command."""

        # Read existing config from the DB directory if present otherwise set up a
        # config for the collection from defaults. We also backfill any defaults
        # that happen to be missing from the existing config.
        config_path = Path(args.db_directory) / 'config.yaml'
        if config_path.exists():
            config = yaml.safe_load(config_path.read_text())
            config.setdefault('collections', {})
        else:
            config = {'collections': {}}

        collection_config = config['collections'].setdefault(args.collection, {})

        # Command line params are not allowed to override the config file.
        for k, v in args.param.items():
            if k in collection_config and collection_config[k] != v:
                raise OllexError(
                    f'{k} has already been set to {collection_config[k]} - cannot change now'
                )
        # Backfill any missing config values from our defaults
        collection_config = {'files': []} | FROZEN_CONFIG | args.param | collection_config
        config['collections'][args.collection] = collection_config

        md_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=HEADERS_TO_SPLIT_ON, strip_headers=False
        )
        # Second splitter for large Markdown sections
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=collection_config['chunk_size'],
            chunk_overlap=collection_config['chunk_overlap'],
            length_function=len,
        )

        db_client = chromadb.PersistentClient(path=args.db_directory)
        db_client.get_or_create_collection(args.collection)
        embedding_fn = OllamaEmbeddings(model=collection_config['embedding_model'])
        vector_store = Chroma(
            client=db_client,
            collection_name=args.collection,
            embedding_function=embedding_fn,
        )
        collection_config['embedding_dimensions'] = get_embedding_dimensions(
            collection_config['embedding_model']
        )

        with Progress() as progress:
            if len(collection_config['files']) > 1:
                all_files_task = progress.add_task('Files', total=len(args.files))
            for filename in args.files:
                # We compare pre-loaded files with new files by hash to avoid duplication.
                file_content = Path(filename).read_text()
                file_hash = sha256(file_content.encode()).hexdigest()
                if file_hash in {f.get('sha256') for f in collection_config['files']}:
                    print(f'{filename}: Already added - skipping')
                    continue
                collection_config['files'].append({'name': filename, 'sha256': file_hash})

                md_split_docs = md_splitter.split_text(file_content)
                # Process each document - further split if needed
                split_docs = []
                for doc in md_split_docs:
                    if len(doc.page_content) > collection_config['chunk_size']:
                        for chunk in text_splitter.split_text(doc.page_content):
                            split_docs.append(
                                Document(page_content=chunk, metadata=doc.metadata.copy())
                            )
                    else:
                        split_docs.append(doc)
                # add meta data
                file_task = progress.add_task(filename, total=len(split_docs))
                for batch in chunk_list(split_docs, 10):
                    vector_store.add_documents(batch)
                    progress.update(file_task, advance=len(batch))
                progress.remove_task(file_task)

            # Update config file after each file in case of failure in a later file
            config_path.write_text(yaml.dump(config))
            if len(collection_config['files']) > 1:
                progress.update(all_files_task, advance=1)

        return 0
