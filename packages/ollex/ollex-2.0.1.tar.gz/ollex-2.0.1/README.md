# Ollex (Open LLM Experimental Workbench)

<div align="center">
<img src="./doc/img/ollex.png" alt="Ollex Logo" width="120px" height="auto">
</div>

**Ollex** is a little desktop experiment built to get a bit of hands-on
experience fiddling with this AI caper. It's a very basic, naive implementation
but I knew nothing at the time. The uncharitable amongst you will suggest that
situation hasn't changed. So it goes.

[![PyPI version](https://img.shields.io/pypi/v/ollex)](https://pypi.org/project/ollex/)
[![Python versions](https://img.shields.io/pypi/pyversions/ollex)](https://pypi.org/project/ollex/)
[![GitHub Licence](https://img.shields.io/github/license/jin-gizmo/ollex)](https://github.com/jin-gizmo/ollex/blob/master/LICENCE.txt)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Genesis

**Ollex** was developed at [Origin Energy](https://www.originenergy.com.au)
as part of the *Jindabyne* initiative. While not part of our core IP, it proved
valuable internally, and we're sharing it in the hope it's useful to others.

Kudos to Origin for fostering a culture that empowers its people to build
complex technology solutions in-house.

[![Jin Gizmo Home](https://img.shields.io/badge/Jin_Gizmo_Home-d30000?logo=GitHub&color=d30000)](https://jin-gizmo.github.io)

## Premise

The use case was simple ...

> Given a reasonable sized source document, load it up so we can ask
> questions about its contents. 

Turned out to be more fiddly than expected. The final result was a simple CLI tool with a couple of subcommands:

*   **[olx db](#olx-db)**:  Create / extend a ChromaDB vector database with
    embeddings from one or more Markdown formatted documents.

*   **[olx query](#olx-query)**: Run queries using one or more LLM models against
    a ChromaDB database that has been created using **olx db**. This can be run,
    either in batch mode, or as an iterative REPL.

The intent behind the **olx query** tool is this ... given:

*   `n` different embeddings of a given source document
*   `m` LLM models
*   `p` system prompts

... process queries against the `n * m * p` possible combinations of these to
see how each performs.

> TL;DR Every one of them is a lottery.

## Quick Start

First, install [Ollama](https://ollama.com) and download an embedding model and
a generating (LLM) model to get started:

```bash
ollama pull nomic-embed-text
allama pull llama3.2
```

Then prepare a virtual environment and install ollex:
```bash
mkdir ollex
cd ollex
python3 -m venv venv
source venv/bin/activate

pip install ollex

# Quick check
olx --help
olx db --help
olx query --help
```

To take it for a spin, first create a DB with a markdown formatted source
document.

```bash
# Create a DB with a markdown document
# Default embedding model is nomic-embed-text 
olx db --collection sample sample.db sample-source-doc.md
```

You can add multiple collections to the database with different embedding models,
parameters and/or source content. For example, let's add a new collection using
the same source document but with a different chunk size:

```bash
olx db --collection sample-500 --param chunk_size=500 sample.db \
    sample-source-doc.md
```

Now we can run some queries against our DB. This is interactive mode.
Once the REPL starts, type a question or `\h` for help. This will describe the
commands to do things such as change LLMs, data collections and system prompts
being used.

```bash
olx query --llm llama3.2 --collection sample sample.db
```

## Usage

### olx db

```bare
usage: olx db [-h] [-c COLLECTION] [-p NAME=VALUE] [-v]
              db_directory FILE.md [FILE.md ...]

Load Markdown documents into a Chroma vector DB.

positional arguments:
  db_directory          Directory containing the Chroma DB.
  FILE.md               Markdown documents to add.

options:
  -h, --help            show this help message and exit
  -c COLLECTION, --collection COLLECTION
                        Database collection to which documents will be added.
                        This will be created if it does not exist. Default is
                        ai-boondoggle.
  -p NAME=VALUE, --param NAME=VALUE
                        Set the specified embedding control parameter(s).
                        Default values are: chunk_overlap=100,
                        chunk_size=1000, embedding_model=nomic-embed-text.
                        These cannot be changed for an existing collection and
                        it is an error to attempt to do so.
  -v, --version         Show version and exit.
```

### olx query

**Olx query** has a batch mode and an interactive REPL (read, evaluate and print
loop) mode. If stdin and stdout are connected to a tty, **olx query** uses the
REPL. 

In batch mode, queries are read from stdin. Each query can span multiple lines,
with a blank line between queries. Output from batch mode goes to stdout and
consists of one line of JSON per query containing the query, response and the
configuration details that lead to the response. The intent was to produce a
format that could be used to rate responses.

```bare
usage: olx query [-h] [-c COLLECTION] [-l MODEL] [-e EMBEDDING]
                 [-o NAME=VALUE] [-p FILE.yaml] [-n COUNT] [-r COUNT] [-v]
                 db_directory

Interact with Ollama in REPL or batch mode.

positional arguments:
  db_directory          Directory containing the Chroma DB containing
                        embeddings.

options:
  -h, --help            show this help message and exit
  -c COLLECTION, --collection COLLECTION
                        Database collection to use. Multiple collections can
                        be active at the same time by repeating this option. A
                        response is provided for each active collection. If
                        not specified and the database has only one
                        collection, that will be used. In interactive mode,
                        the collection(s) can also be specified using an
                        interactive command. A collection must be specified
                        for any queries to be run.
  -l MODEL, --llm MODEL
                        Model to be used for the LLM. Multiple models can be
                        active at the same time by repeating this option. A
                        response is provided for each active model. At least
                        one model must be specified, either as a command
                        argument or via the \llm interactive command in order
                        to process any queries.
  -e EMBEDDING, --embedding EMBEDDING
                        The embedding used when creating storing documents in
                        the database. This is determined (in order or
                        precedence) by (1) the value stored in config.yaml in
                        the database directory; (2) the value of this
                        argument; (3) the default (nomic-embed-text).
  -o NAME=VALUE, --option NAME=VALUE
                        Set the specified LLM control option(s). Available
                        options are: mirostat, mirostat_eta, mirostat_tau,
                        num_ctx, num_predict, repeat_last_n, repeat_penalty,
                        seed, stop, temperature, tfs_z, top_k, top_p.
  -p FILE.yaml, --prompts FILE.yaml
                        Read prompts from the specified YAML file. Keys are
                        the prompt IDs and values are the prompt text. Each
                        prompt must contain "{data}" and "{question}"
                        somewhere. If not specified, a default prompt is used.
                        Use the \prompt interactive command to see its content.
  -n COUNT              (Batch mode only) Run each query the specified number
                        of times. Default 1.
  -r COUNT, --search-results COUNT
                        Number of documents to return when searching the
                        database. Default is 10.
  -v, --version         Show version and exit.
```

## Editorial

1.  Langchain is a mixed blessing. It's byzantine and documentation could be better.

2.  This whole process takes a machine with significant grunt. Even then, some
    of the better models will take a while to produce an answer.

3.  Do not expect answers on a par with ChatGPT, Claude etc. It's still
    interesting though.

4.  Be careful not to add the same content to a given collection more than once.

## Release Notes

#### v2.0.1

*   Updated CLI install process.

*   Updated for ChromaDB API changes.

*   Minor packaging changes for PyPI.

#### v1.0.0

*   Open source base release.
