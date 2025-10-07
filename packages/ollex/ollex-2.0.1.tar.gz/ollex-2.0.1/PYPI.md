# Ollex (Open LLM Experimental Workbench)

**Ollex** is a little desktop experiment built to get a bit of hands-on
experience fiddling with this AI caper. It's a very basic, naive implementation
but I knew nothing at the time. The uncharitable amongst you will suggest that
situation hasn't changed. So it goes.

[![PyPI version](https://img.shields.io/pypi/v/ollex)](https://pypi.org/project/ollex/)
[![Python versions](https://img.shields.io/pypi/pyversions/ollex)](https://pypi.org/project/ollex/)
![PyPI - Format](https://img.shields.io/pypi/format/ollex)
[![GitHub License](https://img.shields.io/github/license/jin-gizmo/ollex)](https://github.com/jin-gizmo/ollex/blob/master/LICENCE.txt)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Genesis

**Ollex** was developed at [Origin Energy](https://www.originenergy.com.au)
as part of the *Jindabyne* initiative. While not part of our core IP, it proved
valuable internally, and we're sharing it in the hope it's useful to others.

Kudos to Origin for fostering a culture that empowers its people
to build complex technology solutions in-house.

[![Jin Gizmo Home](https://img.shields.io/badge/Jin_Gizmo_Home-d30000?logo=GitHub&color=d30000)](https://jin-gizmo.github.io)

## Premise

The use case was simple ...

> Given a reasonable sized source document, load it up so we can ask
> questions about its contents. 

Turned out to be more fiddly than expected. The final result was a simple CLI tool with a couple of subcommands:

*   **olx db**:  Create / extend a ChromaDB vector database with
    embeddings from one or more Markdown formatted documents.
*   **olx query**: A simple tool to run queries using one or more LLM models against
    a ChromaDB database that has been created using **olx db**. This can be run,
    either in batch mode, or as an iterative REPL.

The intent behind the **olx query** tool is this ... given:

*   `n` different embeddings of a given source document
*   `m` LLM models
*   `p` system prompts

... process queries against the `n * m * p` possible combinations of these to
see how each performs.

> TL;DR Every one of them is a lottery.

## Installation and Usage

See [Ollex on GitHub](https://github.com/jin-gizmo/ollex).
