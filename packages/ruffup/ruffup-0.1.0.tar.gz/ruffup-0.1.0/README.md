# ruffup

Very simple. You want to `ruff` format your code, including isort?

Just run

    uv tool install ruffup

And now you can run `ruffup` wherever you want to run this:

    ruff check --select I --fix .
    ruff format .

Hopefully `ruff` will get something like this included.
