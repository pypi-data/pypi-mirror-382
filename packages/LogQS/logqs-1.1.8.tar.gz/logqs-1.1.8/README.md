<p align="center">
  <br/>
  <img src="misc/images/logqs_logo.png?raw=true" alt="LogQS Logo" width="250"/>
</p>

# LogQS


## Setup

The LogQS module source is located in `lqs` and it's Python requirements are listed in the `requirements.txt` file.  You can install it locally with `pip install .`.  You can then run the module with `lqs`.  You can also run the API with `lqs.api` and the client with `lqs.client`.

## Development

### Python Installation

The project uses Python 3.11, which may require some dependencies to be required.  In one go,

    sudo apt install python3.11 python3.11-dev python3.11-distutils python3.11-venv

Note that you may need to add the deadsnakes PPA to your system before being able to install Python 3.11:

    sudo add-apt-repository ppa:deadsnakes/ppa

You may also need to install liblz4-dev:

    sudo apt install liblz4-dev

### Environment Setup

To run the application from this directory (i.e., for development):

1. Create a virtual environment:

        python3.11 -m venv venv

2. Source the environment:

        source venv/bin/activate

3. Install the dev requirements:
    
        pip install -r requirements-dev.txt

4. Install LogQS in develop mode:
    
        pip install -e .

5. Run the module:
    
        lqs

6. Run the API (in dev mode):

        lqs.api run dev

#### PJM Dependencies

The PJM module requires additional dependencies to run. These are listed in `requirements-pjm.txt` and can be installed with:

    pip install -r requirements-pjm.txt

Currently, we use the CPU version of PyTorch for inference. In order to install this version, you must first install the CPU version of PyTorch *then* install the other requirements:

    pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
    pip install -r requirements-pjm.txt

### Docker Installation

If you haven't already, [install Docker Engine](https://docs.docker.com/engine/install/ubuntu/) (here's using the convenience script):

    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh

You'll probably also want to be able to [manage Docker as a non-root user](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user):

    sudo groupadd docker
    sudo usermod -aG docker $USER
    newgrp docker

### LogQS Auxiliary Services

LogQS requires a Postgres database and an object store.  We use MinIO for the object store, which is an S3-compatible object store.  LogQS can also, optionally, use Redis for caching.  We use Docker to run these services:

    docker compose -f docker/compose.dev.yaml up -d

After getting these containers running, invoking the module (`lqs`) should return the CLI help menu.

We can create a database named `lqs_test` with the following:

    lqs database create_database lqs_test

A fresh database needs to have migrations ran against it.  You can do this via LogQS with:

    lqs database migrate

We'll also create a bucket named `lqs-bucket`:

    lqs storage create_bucket lqs-bucket

### Testing

You can confirm everything is working properly by running the tests (note: this will delete the data in the `lqs_test` database and `lqs-bucket` bucket).  Use the `-x` flag to stop on the first failure:

    pytest -x

Use the `-s` flag to print to stdout (easier for debugging):

    pytest -xs


### Formatting

[Read this first.](https://gist.github.com/nathanmargaglio/d9386920b64b358f3028ff93d7e946f4)

- Use Black
- Pre-Commit Hooks: https://pre-commit.com/#install 

```
npm i git-conventional-commits
```

It's easiest to install `black` locally and just run it against `lqs` after saving files.

We follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) for Git messages, i.e.,

    <type>(<optional scope>): <subject>

For branch naming conventions, we follow [a typical "grouping" scheme](https://stackoverflow.com/a/6065944), i.e.,

    <group>/<detail>

For example, if you're working on a feature for issue 100, then your branch name may be

    feat/issue-100

### ANTLR

Our `transcode` module uses [ANTLR](https://www.antlr.org/) to parse message definitions for deserialization. Currently, we use version v4.13 and pre-generate the necessary files. However, if you're using a different version of the ANTLR runtime for Python, then you may need to re-generate these files. We'll assume you're using v4.9 of the ANTLR runtime for Python (i.e., `antlr4-python3-runtime==4.9.3`).

First, install the ANTLR tools:

    pip install antlr4-tools

Next, change into the `lqs/transcode/ros1` directory:

    cd lqs/transcode/ros1
    
And make a copy of the `RosMessageParserVisitor.py` file:
    
    cp RosMessageParserVisitor.py RosMessageParserVisitor.py.bak

Then, generate the files from the same directory:

    antlr4 -v 4.9.3 -Dlanguage=Python3 RosMessageParser.g4 RosMessageLexer.g4 -visitor

Finally, replace the `RosMessageParserVisitor.py` file with the one you just generated:

    mv RosMessageParserVisitor.py.bak RosMessageParserVisitor.py

The resulting code should now work with the ANTLR runtime for Python v4.9.3.
