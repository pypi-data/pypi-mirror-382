![Inspiring Image](https://repository-images.githubusercontent.com/1055704668/6835e004-16c3-4ffe-be59-b51e72a378c2)

# Data Grimorium
Data Grimorium is a collection of utilities for Data Scientists and Machine Learning 
Engineers, designed to streamline workflows and accelerate day-to-day coding tasks.

# Resources
For the developers, check the wiki [Package & Modules](https://github.com/Volscente/DataGrimorium/wiki/Packages-&-Modules) Section.

Please refer to this [Contributing Guidelines](https://github.com/users/Volscente/projects/16/views/1) in order to contribute to the repository.

# Setup
## Environment Variables
Add the project root directory as `DATA_GRIMORIUM_ROOT_PATH` environment variable.
``` bash
export DATA_GRIMORIUM_ROOT_PATH="/<absolute_path>/DataGrimorium"
```
Create a `.env` file in the root folder like
```
# Set the Root Path
DATA_GRIMORIUM_ROOT_PATH="/<absolute_path>/DataGrimorium"
```

## Setup gcloud CLI
Install `gcloud` on the local machine ([Guide](https://cloud.google.com/sdk/docs/install)).

Authenticate locally to GCP:
```bash
gcloud auth login
```

Set the project ID.
```bash
# List all the projects
gcloud projects list

# Set the project
gcloud config set project <project_id>
```

Create authentication keys.
```bash
gcloud auth application-default login
```

## Justfile
> `just` is a handy way to save and run project-specific commands
> 
> The main benefit it to keep all configuration and scripts in one place.
> 
> It uses the `.env` file for ingesting variables.

You can install it by following the [Documentation](https://just.systems/man/en/chapter_4.html).
Afterward, you can execute existing commands located in the `justfile`.

Type `just` to list all available commands.

## Pre-commit
```bash
# Install
pre-commit install

# Check locally
pre-commit run --all-files
```