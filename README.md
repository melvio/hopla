# hopla
[![stars - hopla](https://img.shields.io/github/stars/melvio/hopla?style=social)](https://github.com/melvio/hopla) 

hopla - a command line interface for [habitica.com](https://habitica.com)

Hopla is a XDG-compliant command line interface (CLI) that uses `bash` and `python3` to interact with the [habitica.com](https://habitica.com) API.
Hopla is under active development and in a beta phase.      

[![melvio - hopla](https://img.shields.io/static/v1?label=melvio&message=hopla&color=blue&logo=github)](https://github.com/melvio/hopla)
[![License](https://img.shields.io/badge/License-apache--2.0-blue)](#license)

## How to Use Hopla
### Installation
Clone this repository by running:
```bash
$ git clone "git@github.com:melvio/hopla.git"
# Or, by using HTTPS:
$ git clone "https://github.com/melvio/hopla.git"
# or (my favorite), by using gh:
$ gh repo clone melvio/hopla
```

Now `cd` into the repository and run the installation script.
```bash
$ cd ./hopla && ./install.sh
```
`install.sh` will create a symbolic link to make the `hopla` command available on your `$PATH`.


### First Time Usage
Hopla needs your `User Id` and `API Token` to connect to Habitica on your behalve.
You can find these over at `https://habitica.com/user/settings/api`.
Run the following command to configure this automatically:

```bash
$ hopla set-hopla credentials
Please enter your habitica 'User ID': ****-****-****-***-*********
Please enter your habitica 'API Token': ****-****-****-***-*********
```

This will create a credentials file at `~/.config/hopla/auth.conf` that
Hopla uses. If you want to use a different file, you can set the `${HOPLA_AUTH_FILE}`
environment variable to choose your own path.

##### Autocompletion
If you want bash autocompletion you add this to your `~/.bashrc`
```bash
source <(hopla complete bash)
```



### Everyday Usage
After installation , you can use `hopla`. 
The supported commands can be found by running:
```bash
$ hopla --help

syntax:
    hopla [GLOBAL_OPTIONS]... [SUB_COMMANDS|GROUPS]... [SUB_COMMAND_OPTIONS]... [PARAMETERS]...

For more help on SUB_COMMANDs use: `hopla --help {SUB_COMMAND}`
For more help on SUB_GROUPS use:   `hopla --help {SUB_GROUP}`


GLOBAL_OPTIONS:
    hopla [SUB_GROUPS|SUB_COMMANDS] --help

SUPPORTED SUB_COMMANDS:
    hopla version

SUPPORTED SUB_GROUPS
    hopla add [subcmd]
    hopla api [subcmd]
    hopla buy [subcmd]
    hopla complete [subcmd]
    hopla feed [subcmd]
    hopla set [subcmd]
    hopla set-hopla [subcmd]
```

More functionality is currently being implemented.
Hopla is open-source. Pull request, feature requests, and issues are welcomed at <https://github.com/melvio/hopla>.
If you want to contribute, but don't know where to start, you might want to look in the `./developers`. folder.




### Background
Hopla is a XDG-compliant bash-based command line interface (CLI).
It was created because no other CLI supported the creation of To-Dos with both a due date and a checklist.
Hopla provides the following command to create these with the following command:

```bash
$ hopla add todo --hard --due-date 2021-12-07 --checklist ~/abs_file.txt "my todo name here"
```

Every line in the specified file will be added as a task to a To-Do's checklist.

Caveat: Every task of a checklist requires a separate Habitica API call. This means that long checklists (29+) are subject to
the rate-limiting requirements of the Habitica API. This CLI provides this rate-limiting automatically,
however, be aware that long checklists may result in long waiting times.




