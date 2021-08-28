# Hopla
[![hopla](https://img.shields.io/static/v1?label=melvio&message=hopla&color=blue&logo=github)](https://github.com/melvio/hopla) 
[![stars - hopla](https://img.shields.io/github/stars/melvio/hopla?style=social)](https://github.com/melvio/hopla)      

hopla - a command line interface (CLI) for [habitica.com](https://habitica.com)


Hopla is a XDG-compliant command CLI which uses `python3` to interact with 
the [Habitica API](https://habitica.com/apidoc/).

Hopla is currently under active development so buyer beware. 




## How to Use Hopla
### Installation
Clone this repository by running:
```bash
git clone "git@github.com:melvio/hopla.git"
# Or, by using HTTPS:
git clone "https://github.com/melvio/hopla.git"
# or (my favorite), by using gh:
gh repo clone melvio/hopla
```

Now `cd` into the repository and install hopla:
```bash
cd ./hopla && pip install --upgrade -e .
```


### First Time Usage
Hopla needs your `User Id` and `API Token` to connect to Habitica on your behalve.
You can find these over at `https://habitica.com/user/settings/api`.
Run the following command to configure this automatically:

```bash
$ hopla auth 
Please enter your credentials
You can find them over at <https://habitica.com/user/settings/api> 
The user id can be found under 'User ID' and you need to click 'Show API Token'
Please paste your user id here: 7c551d98-31e9-42b4-b7fa-9d89b0944320
Please paste your api token id here: *******-*******-*******-*******
```

This will create a credentials file at `~/.config/hopla/auth.conf` that
Hopla uses. If you want to use a different file, you can set the `${HOPLA_AUTH_FILE}`
environment variable to choose your own path.

##### Autocompletion
If you want bash autocompletion you can run the following command:
```bash
$ hopla complete bash --enable
enabled autocompletion
restart bash to make use of it
```

To print the autocomplete code for bash|zsh|fish so that you can install it yourself optionally run:
```bash
# optionally, install the autocomplete code yourself:
hopla complete bash
hopla complete zsh
hopla complete fish
```







### Everyday Usage
After installation, you can use `hopla`. 
The supported commands can be found by running:
```bash
$ hopla -h
Usage: hopla [OPTIONS] COMMAND [ARGS]...

  hopla - a command line interface (CLI) to interact with habitica.com

Options:
  -h, --help  Show this message and exit.

Commands:
  add       GROUP for adding things to habitica
  api       GROUP for requesting Habitica API metadata
  auth      Authorize yourself to access the Habitica.com API
  buy       GROUP to buy things
  complete  print or enable shell autocompletion
  config    get, set, or list config values
  feed      feed a pet
  get       GROUP for getting information from habitica
  set       GROUP to set things in Habitica
  version   print the hopla version string
```

More functionality is currently being implemented.
Hopla is open-source. Pull request, feature requests, and issues are welcomed at <https://github.com/melvio/hopla>.
If you want to contribute, but don't know where to start, you might want to look in the `./developers`. folder.

[![License](https://img.shields.io/badge/License-apache--2.0-blue)](#license)




### Background
Hopla is a XDG-compliant bash-based command line interface (CLI).
It was created because no other CLI supported the creation of To-Dos with both a due date and a checklist.
Hopla provides the following command to create these with the following command:

```bash
# add a hard todo with every line in the specified file being added as
#  an item of this To-Do's checklist.
hopla add todo --difficulty hard \
               --due-date 2027-12-07 \
               --checklist ./my_todo.txt \
               "my todo name here"
```






