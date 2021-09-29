# Style Guide

## Code Quality

Code style is enforced by `pylint` and `flake8`.      
Run `make flake` and `make lint` to run flake8 and pylint over your code.

## Code Style
Add types to everything.

The only exceptions to this should be direct constructor calls and literals. So:
```python3
# good :
user = HabiticaUser(...)
# bad: 
user: HabiticaUser = HabiticaUser()
#     ^ Already clear what the type is here.


# good:
message = f"Quest {quest_name} completed."

# bad: 
message: str = f"Quest {quest_name} completed."
#        ^ already clear what the type is
```

## Unit testing

Code coverage is enforced by `pytest`. We aim for 100% coverage.       
Run `make unittest` to unit test your code.

## Writing Documentation

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



