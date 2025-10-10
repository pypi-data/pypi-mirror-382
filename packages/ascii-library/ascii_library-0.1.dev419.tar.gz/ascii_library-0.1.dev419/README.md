# ASCII Research space

A single monorepo to store all our research.
Every person has a folder


## development infrastructure (local setup)

- a computer with internet access to install python packages
- an installed pixi [https://pixi.sh/latest/](https://pixi.sh/latest/) for your operating system
    - ensure the `pixi`command is in your path and working correctly
- an installation of `make` command in your path
- git
- docker
- an SSH key readily set up to connect to github
- permissions to view this (https://github.com/ascii-supply-networks/research-space) repository
- available infrastructure
    - server 
    - openAI API key

```bash
git clone git@github.com:ascii-supply-networks/research-space.git
cd research-space   

# Activate environment. If the environment is not installed it will be installed automaticially. 

# Default env:
pixi shell -e research-cpu 
# If you need gpu acceleration use:
pixi shell -e research-cuda
# For the pipeline:
pixi run create_environment_pipeline 

# To start a jupyter notebook session
make notebook

# Set up pre-commit hook for automatic formatting. Execute this in reasearch-space
pixi global install pre-commit
export PATH="$HOME/.pixi/bin:$PATH" # If you are on the server execute this and reload terminal
pre-commit install

```

### notes

#### adding new reference data

Ensure to set `DEV_REFERENCE_DATA_OVERRIDE` to the location where the reference data repository is checked out.

Ideally, you download the reference data from https://github.com/ascii-supply-networks/reference-data relative to/next to the research space; however, only by setting a softlink to make it appear there.

### using R

- talk to georg
    - enable renv   
    - integrate Rstudio
- in a shell: `conda activate ascii_rs`
- then start an `R` shell by typing `R` in the command line window
    - then inside R execute: `renv::restore()`
    - instally any additionally required packages
    - use them in your scripts. Only the used ones are recorded
    - commit these to version control by `renv::snapshot()` and then commiting the renv

- when you use the commandline you can use the new environment straight away

### updating the main deployment

Ensure the quality is high by testing the code beforehand.

Execute the following linting and testing procedures and fix any issues:

```bash
make fmt
make lint
make test

make fmt-sql
make lint-sql
```

prepare secrets.
Decrypt the secrets - you must have a valid key file to perform this step

```bash
make secrets-decrypt
```

Ensure `ROOT_DOMAIN` is pointing to the right setting.

Test one more time with the containerized pipeline:

```bash
make start-pipeline-staging
```

Run and build the containers and expose via proxy:

```bash
make start-pipeline-production
```

Open the URL to see the dashboard: https://orchestration.ascii.ac.at/

> WARNING a click will trigger the pipeline - some pipelines (for commoncrawl) cost 1k€/execution - know what you do.
