# dkany
Python package for accessing open data websites powered by dkan

# `uv` and package management
We're using [`uv`](https://docs.astral.sh/uv/), since pipenv was having a hard time building.  Install it with `pip install uv`, then it should work almost identically to `pipenv`

# Local Development

To install the package and it's dependences for development, run 
```
uv sync --dev
```
`uv` can manage your python versions for you.  Try out `uv python list` or `uv python install 3.13`


## Environment Variables
 The default behavior of this app can be changed with environment variables.
 The easiest way to set these is by adding them to a `.env` file in the base directory of this repo. This file is not commited to the repo, as it might change in different contexts, but you can see the `.env_example` to get a sense of how this might look.

Here are the environment variables the app is currently using:

# Running the Tests
There are many ways to run the tests associated with this app.

1. Probably the easiest is to run the tests in vscode's testing pannel

2. You can also run the tests from bash with `source scripts/test.sh` 


# Ideas for Improvement
TODO: Validate dataset file (All columns have column names)

# Deploying

See [our confluence doc on deploying to AWS CodeArtifact](https://mathematicampr.atlassian.net/wiki/spaces/WEB/pages/2514354711/Deploying+to+AWS+CodeArtifact)