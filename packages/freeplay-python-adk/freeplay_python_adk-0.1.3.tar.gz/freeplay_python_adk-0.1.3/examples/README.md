The code in the examples directory is a set of scripts that you can run to
trigger Freeplay functionality. We use it internally to validate our service and
make sure the instrumentation is working as expected. The examples may be
helpful if you are are trying to understand how to set up your agent or how to
get your traces to show up in Freeplay as expected.

You can run it like so: `uv run pytest examples/test_research_agent.py`.

Most tests require environment variables to be set via an .env file in the root
repository.

In the default setup, requests to LLMs are captured via VCR so our tests do not
cost a fortune, but requests to localhost are allowed through, so we can test
against a locally running Freeplay server.
