# ASP Chef CLI

A simple CLI to run ASP Chef, in headed or headless mode.

## Install

The suggested way is via pip:

```bash
$ pip install asp-chef-cli
$ playwright install
```

Docker is another option (headed mode needs extra parameters):

```bash
$ sudo docker run -i malvi/asp-chef-cli
$ sudo docker run -i --net=host --env="DISPLAY" --volume="$HOME/.Xauthority:/root/.Xauthority:rw" malvi/asp-chef-cli
```

## Usage

Run with one of the following commands:

```bash
$ python -m asp_chef_cli --help
$ sudo docker run malvi/asp-chef-cli --help
```

Add the recipe (an ASP Chef sharable URL) with the option `--url` (quote the URL as it contains characters like # that breaks bash and other terminals).
The headless mode can be activated with the flag `--headless` (always active in the docker image).
Possibly change the default browser used by playwright with the option `--browser`.
Finally, give a command to execute:
- `run` simply runs the recipe as it is;
- `run-with` runs the recipe with the input replaced by the one specified either with the option `--input` or via the prompt.
- `server` starts a server for `@dumbo/*` operations.

The flag `--help` can be specified after a command to get a list of arguments for that command.

## Examples

Let us consider [this simple recipe](https://asp-chef.alviano.net/#eJxtkNuOgjAQhl+plNUsl4srUKIQEXu6s+Ch2CIJIpan33bdRC/2ajKnf/75DibtRBt69QLNiUGSbkfJyawRsFAUqqFKMEBNpxl5TNz1YvzXC7w6ee5xHfUV3PWoTRWDauRbq+X3ck82MpfpJf/ePXhZGS6Bn+mltyo3MGvYLS8Z5AsAGVzOuN5AppGtr+Vqkd6rGBtGi07AD6dRchIZBk+nkgQXbr0gOUrhh2BPgqEyaH4w6VTHwfjuldFwFMlF5m1hauL8ZVfhV69cn9We1Ff3w7r5Gu1dW38op4famy/8tOcJGH5vtfjGNDaouRo3x4iaOF2/aT1ZURhNFGZ30Wag0pFlW0z/8vNDw0nRMRgBxwup4Mh0NPGSAep9OgaW5flOIR4YdD8XRxuHOsbDizkOjtgLfgC4qpvc%21) with no input and guessing the atom `world`.
The recipe can be run headless by giving the following command:

```bash
$ python -m asp_chef_cli --headless --browser=chromium --url="https://asp-chef.alviano.net/#eJxtkNuOgjAQhl+plNUsl4srUKIQEXu6s+Ch2CIJIpan33bdRC/2ajKnf/75DibtRBt69QLNiUGSbkfJyawRsFAUqqFKMEBNpxl5TNz1YvzXC7w6ee5xHfUV3PWoTRWDauRbq+X3ck82MpfpJf/ePXhZGS6Bn+mltyo3MGvYLS8Z5AsAGVzOuN5AppGtr+Vqkd6rGBtGi07AD6dRchIZBk+nkgQXbr0gOUrhh2BPgqEyaH4w6VTHwfjuldFwFMlF5m1hauL8ZVfhV69cn9We1Ff3w7r5Gu1dW38op4famy/8tOcJGH5vtfjGNDaouRo3x4iaOF2/aT1ZURhNFGZ30Wag0pFlW0z/8vNDw0nRMRgBxwup4Mh0NPGSAep9OgaW5flOIR4YdD8XRxuHOsbDizkOjtgLfgC4qpvc%21" run
EMPTY MODEL
§
world.
```

It is possible to specify a different input as follows:

```bash
$ python -m asp_chef_cli --headless --browser=chromium --url="https://asp-chef.alviano.net/#eJxtkNuOgjAQhl+plNUsl4srUKIQEXu6s+Ch2CIJIpan33bdRC/2ajKnf/75DibtRBt69QLNiUGSbkfJyawRsFAUqqFKMEBNpxl5TNz1YvzXC7w6ee5xHfUV3PWoTRWDauRbq+X3ck82MpfpJf/ePXhZGS6Bn+mltyo3MGvYLS8Z5AsAGVzOuN5AppGtr+Vqkd6rGBtGi07AD6dRchIZBk+nkgQXbr0gOUrhh2BPgqEyaH4w6VTHwfjuldFwFMlF5m1hauL8ZVfhV69cn9We1Ff3w7r5Gu1dW38op4famy/8tOcJGH5vtfjGNDaouRo3x4iaOF2/aT1ZURhNFGZ30Wag0pFlW0z/8vNDw0nRMRgBxwup4Mh0NPGSAep9OgaW5flOIR4YdD8XRxuHOsbDizkOjtgLfgC4qpvc%21" run-with --input "hello."
hello.
§
hello.
world.
```


## Local Server for @dumbo/* Operations

The server for `@dumbo/*` operations can be executed with the command `server`.
By default, it uses port `8000` (a different port can be specified using `--port` or `-p`; in this case, the port must be changed also in the options of ASP Chef).

For development, add the `--reload` flag so that the server is updated when the Python code of the CLI is changed. 

The Docker version must specify port mapping, for example:
```bash
$ sudo docker run -p 8000:8000 malvi/asp-chef-cli server --host 0.0.0.0
```
