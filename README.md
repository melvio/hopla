# hopla

hopla - a command line interface for `habitica.com`


### background
Hopla is a XDG-compliant bash-based command line interface (CLI).
It was created because no other CLI supported the creation of To-Does with both a due date and a checklist.
Hopla provides the following command to create these with the following command:

```bash
$ hopla add todo --hard --due-date 2021-12-07 --checklist ~/abs_file.txt "my todo name here"
```

Every line in the specified file will be added as a task to a To-Do's checklist.

Caveat: Every task of a checklist requires a separate Habitica API call. This means that long checklists (29+) are subject to 
the rate-limiting requirements of the Habitica API. This CLI provides this rate-limiting automatically, 
however, be aware that long checklists may result in long waiting times.

### How to Use
#### Installation
Clone this repository by running:
```
git clone git@github.com:melvio/hopla.git
```

Now `cd` into the repository and run the installation script.
```
cd ./hopla
./install.sh
```
`install.sh` will create a symbolic link such that 
the `hopla` command becomes available on your `$PATH`.


#### First Time Usage
Hopla needs your `User Id` and `API Token` to connect to Habitica on your behalve.
You can find these over at `https://habitica.com/user/settings/api`.
Run the following command to configure this automatically:

```bash
$ hopla set credentials
Please enter your habitica 'User ID': ****-****-****-***-*********
Please enter your habitica 'API Token': ****-****-****-***-*********
```


This will create a credentials file at `~/.local/share/hopla/auth.conf` that
for Hopla to use. If you want to use a different file, you can set the `${HOPLA_AUTH_FILE}`
environment variable to choose your own path.

#### Everyday Usage
After this, you can use hopla. The supported commands can be found by running:
```bash
$ hopla --help
hopla - another Habitica cli

usage:
    hopla --help
    hopla version
    hopla set credentials
    hopla add todo [--trivial|--easy|--medium|--hard] [{--due-date|--deadline} yyyy-mm-dd] [--checklist absolute_file_path] "the name of your todo"
    hopla api version
    hopla api status
```

More advanced features and functionality may be implemented later.
Hopla is open-source. Pull request and issues are welcome over at <https://github.com/melvio/hopla>.
If you want to contribute, but don't know where to start, you might want to look in the `./developers`. folder.






