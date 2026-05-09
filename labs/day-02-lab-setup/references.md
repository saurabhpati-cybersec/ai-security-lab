# Day 2 References

## SDKs and Client Libraries

- **Anthropic Python SDK**
  https://docs.anthropic.com/en/api/client-sdks
  Official Python library for the Anthropic API. Used by `starter/python/anthropic_client.py` and all agents.

- **OpenAI Python SDK**
  https://platform.openai.com/docs/libraries/python-library
  Official Python library for the OpenAI API. Used by `starter/python/openai_client.py` for optional GPT-4.1 adapter verification.

## Environment and Configuration

- **python-dotenv documentation**
  https://github.com/theskumar/python-dotenv
  Loads `.env` files into `os.environ`. Used by all entry points to inject API keys without hardcoding them.

## Output and Display

- **rich library — Progress and Console documentation**
  https://rich.readthedocs.io/en/stable/
  Used by the eval harness for live progress bars and formatted output. Required in `requirements.txt`.

## Python Runtime

- **Python 3.11 release notes**
  https://docs.python.org/3/whatsnew/3.11.html
  Python 3.11 is the minimum supported version. Key improvements used in this lab series: `tomllib` (built-in), better error messages, and `ExceptionGroup`.
