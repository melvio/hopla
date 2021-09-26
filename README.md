# Hopla

[![hopla](https://img.shields.io/static/v1?label=melvio&message=hopla&color=blue&logo=github)](https://github.com/melvio/hopla)
[![stars - hopla](https://img.shields.io/github/stars/melvio/hopla?style=social)](https://github.com/melvio/hopla)      
[![Continuous Integration](https://github.com/melvio/hopla/actions/workflows/ci-lint-and-test.yml/badge.svg)](https://github.com/melvio/hopla/actions/workflows/ci-lint-and-test.yml)

hopla - a command line interface (CLI) for [habitica.com](https://habitica.com)

Hopla is a XDG-compliant CLI which uses `python3` to interact with
the [Habitica API](https://habitica.com/apidoc/).

Hopla is currently under active development so new features are added rapidly.

## How to Use Hopla

### Installation

Hopla can be installed by running the following command:

```bash
python3 -m pip install --user hopla-cli
```


### First Time Usage

Hopla needs your `User Id` and `API Token` to connect to Habitica. 
You can find these over at `https://habitica.com/user/settings/api`. 

Run the following command to configure this automatically:

```bash
$ hopla authenticate 
Please enter your credentials.
You can find them over at <https://habitica.com/user/settings/api>.
They have the following format: 'c0ffee69-dada-feed-abb1-5ca1ab1ed004'.
The user id can be found under 'User ID'.
Please paste your user ID here (press Ctrl-C to abort): c0ffee69-dada-feed-abb1-5ca1ab1ed004
Please paste your user API Token here (input remains hidden):
```

This will create a credentials file at `~/.config/hopla/authenticate.conf` that Hopla uses. 
If you want to use a different file, you can set the `${HOPLA_AUTH_FILE}` environment 
variable to choose your own file.

##### Autocompletion

If you want bash autocompletion, you can run the following command:

```bash
$ hopla complete bash --enable
enabled autocompletion
restart bash to make use of it
```

To make use of the autocompletion you need to reload your bashrc.
You can do this by either opening up a new terminal window, or
running `bash` again, or running `source ~/.bashrc`.


To print the autocomplete code for bash|zsh|fish, so that you can install 
it yourself, optionally run:

```bash
# optionally, install the autocomplete code yourself:
hopla complete bash
hopla complete zsh
hopla complete fish
```

## Everyday Usage

After installation, you can use `hopla`. 
The supported commands can be found by running:

```bash
$ hopla --help
Usage: hopla [OPTIONS] COMMAND [ARGS]...

  hopla - a command line interface (CLI) to interact with habitica.com

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  add                  GROUP for adding things to Habitica.
  api                  GROUP for requesting Habitica API metadata.
  authenticate         Authorize yourself to access the Habitica.com API.
  buy                  GROUP to buy things.
  complete             Print or enable shell autocompletion.
  # etcetera
```

More functionality is currently being implemented. 
Hopla is open-source. 
Pull request, feature requests, and issues are welcomed at <https://github.com/melvio/hopla>. 
If you want to contribute, but don't know where to start, you might want to look at
`.github/CONTRIBUTING.md` and the `./developers` folder.

[![License](https://img.shields.io/badge/License-apache--2.0-blue)](#license)

### Environment Variables for Hopla's options

*Use case*: You can use environment variables to set default values for all Hopla options. 

Hopla automatically recognizes environment variables starting with `HOPLA_`. 
All option (such as `--difficulty` for `hopla add todo` and `--times` for `hopla feed`) can be 
set in this manner.

To get the right environment variable name, use this logic:

1. Define an environment variable starting with `HOPLA_`

2. Append the subcommand to the environment variable as follows:
    * `hopla add todo` -> `HOPLA_ADD_TODO_`
    * `hopla support-development` -> `HOPLA_SUPPORT_DEVELOPMENT_`
    * `hopla feed` -> `HOPLA_FEED_`
 
3. Append the option name that you want to set as follows:
    * `hopla add todo --difficulty` -> `HOPLA_ADD_TODO_DIFFICULTY`
    * `hopla support-development --gems` -> `HOPLA_SUPPORT_DEVELOPMENT_GEMS`
    * `hopla feed --times` -> `HOPLA_FEED_TIMES`


For example:

```bash
HOPLA_ADD_TODO_DIFFICULTY=hard    hopla add todo "Hello"
HOPLA_SUPPORT_DEVELOPMENT_GEMS=8  hopla support-development
HOPLA_FEED_AMOUNT=3               hopla feed Wolf-Shade Chocolate
````


Other examples:

```bash
# add a To-Do for today
HOPLA_ADD_TODO_DUE_DATE=today hopla add todo "Task with Deadline from today"

# automatically enable autocomplete for bash 
HOPLA_COMPLETE_ENABLE=true    hopla complete bash
HOPLA_COMPLETE_ENABLE=yes     hopla complete bash
HOPLA_COMPLETE_ENABLE=1       hopla complete bash

# only print autocomplete for bash
HOPLA_COMPLETE_ENABLE=0       hopla complete bash   
HOPLA_COMPLETE_ENABLE=false   hopla complete bash   
HOPLA_COMPLETE_ENABLE=no      hopla complete bash   
```

### Background

Hopla is a XDG-compliant bash-based command line interface (CLI). 
It was created because no other CLI supported the creation of To-Dos with both a 
due date and a checklist. 
Hopla provides the following command to create these with the following command:

```bash
# Add a hard To-Do. Every line in the specified file will being added as
#  an item of this To-Do's checklist.
hopla add todo --difficulty hard \
               --due-date 2027-12-07 \
               --checklist ./my_todo.txt \
               "my todo name here"
```

The most simple way to add a To-Do would be to run `hopla add todo` without arguments.
Hopla will then prompt you for a To-Do name:

```bash
$ hopla add todo
Please provide a name for your todo: Feed the dog
```







