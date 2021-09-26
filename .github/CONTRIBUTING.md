# Contributing to Hopla

👍 First off, thank you! we appreciate that you are taking the time to contribute! 👍
Besides the things mentioned below in this file, there are no hard rules on how to contribute.
So feel free to contribute as you see fit.


## Installing Hopla locally

Clone this repository by running:

```bash
git clone "git@github.com:melvio/hopla.git"
# Or, by using HTTPS:
git clone "https://github.com/melvio/hopla.git"
# Or (my favorite), by using gh:
gh repo clone melvio/hopla
```

Now `cd` into the repository with:

```bash
cd ./hopla 
```

And install Hopla in development mode by running:

```bash
pip install --upgrade --editable .
```


## Style Guide
### Writing Documentation

Style Guide Rules for User-facing Documentation:
* Every option, argument, command, and group is documented.
* Use full sentences.
* Sentences start with uppercase letter and end with a dot.
* Use `hopla` (lowercase) when you mean the command.
* Use 'Hopla' (uppercase) when you mean to name the CLI by its name.
* Use 'Habitica' (uppercase) unless it is factually incorrect (e.g. <https://habitica.com>)
* Use 'CLI' and 'API' uppercase unless it is factually incorrect (e.g. `hopla api ...`)

Style Guide Suggestions for Developer-facing Documentation:
* Same as above

### Code Style
Code style is enforced by `pylint`. 
Run `make lint` in the root of the repository to see what `pylint` opinion is of your code changes.

