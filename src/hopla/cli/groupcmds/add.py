"""
The module with CLI code that handles the `hopla add` group command.
"""
import sys
import datetime
import logging
from typing import Dict, List, Optional

import click
import requests

from hopla.hoplalib.requests_helper import get_data_or_exit
from hopla.hoplalib.clickhelper import EnhancedDate
from hopla.hoplalib.http import HabiticaRequest, UrlBuilder
from hopla.hoplalib.outputformatter import JsonFormatter

log = logging.getLogger()


@click.group()
def add():
    """GROUP for adding things to Habitica."""


DIFFICULTIES_SCORE_MAPPING = {"hard": "2", "medium": "1.5", "easy": "1", "trivial": "0.1"}


class HabiticaChecklist:
    """ Habitica Checklist """

    def __init__(self, *, checklist: Optional[list] = None):
        self.checklist = checklist or []

    def __repr__(self) -> object:
        return self.__class__.__name__ + f"(checklist={self.checklist})"

    def is_empty(self) -> bool:
        """Return true if the checklist is empty.

        >>> HabiticaChecklist(checklist=[]).is_empty()
        True
        >>> HabiticaChecklist(checklist=["item 1"]).is_empty()
        False

        """
        return self.checklist is None or len(self.checklist) == 0

    def to_json_list(self) -> List[Dict[str, str]]:
        """Turn a checklist into a list that we can pass to the habitica API"""
        return [{"text": line} for line in self.checklist]


class HabiticaTodo:
    """ Habitica To-Do"""

    def __init__(self, *,
                 todo_name: str,
                 difficulty: str,
                 due_date: Optional[datetime.datetime] = None,
                 checklist: Optional[HabiticaChecklist] = None):
        self.todo_name = todo_name
        self._type = "todo"
        self.difficulty = difficulty
        self.due_date = due_date
        self.checklist: Optional[HabiticaChecklist] = checklist or HabiticaChecklist()

    def difficulty_to_score(self) -> str:
        """Return score for the To-Do's difficulty.

        >>> hab_todo = HabiticaTodo(todo_name="my-task", difficulty="easy")
        >>> hab_todo.difficulty_to_score()
        '1'
        >>> hab_todo.difficulty = "trivial"
        >>> hab_todo.difficulty_to_score()
        '0.1'

        :raise KeyError in case of an invalid difficulty
        """
        return DIFFICULTIES_SCORE_MAPPING[self.difficulty]

    def due_date_to_date_str(self) -> str:
        """Turn the due_date into a valid ISO 8601 date format

        >>> hab_todo = HabiticaTodo(todo_name="my-task", difficulty="easy",\
                                    due_date=datetime.datetime(day=31, month=1, year=2069))
        >>> hab_todo.due_date_to_date_str()
        '2069-01-31'
        """
        habitica_date_format = "%Y-%m-%d"
        return self.due_date.strftime(habitica_date_format)

    def to_json_dict(self) -> dict:
        """Turn an instance of this class into a dict that we can pass to the habitica API.

        >>> hab_todo = HabiticaTodo(todo_name="my-task", difficulty="medium",\
                                    checklist=HabiticaChecklist(checklist=["myitem"]))
        >>> hab_todo.to_json_dict()
        {'text': 'my-task', 'type': 'todo', 'priority': '1.5', 'checklist': [{'text': 'myitem'}]}
        """
        todo_dict = {
            "text": self.todo_name,
            "type": self._type,
            "priority": self.difficulty_to_score(),
            "checklist": self.checklist.to_json_list()
        }

        if self.due_date:
            todo_dict["date"] = self.due_date_to_date_str()

        return todo_dict


class AddTodoRequest(HabiticaRequest):
    """An object that can perform an add To-Do request"""

    def __init__(self, habitica_todo: HabiticaTodo):
        self.url: str = UrlBuilder(path_extension="/tasks/user").url
        self.habitica_todo = habitica_todo

    def post_add_todo_request(self):
        """Perform the add To-Do request and return the data in case of success"""
        response = requests.post(
            url=self.url,
            headers=self.default_headers,
            json=self.habitica_todo.to_json_dict()
        )
        return get_data_or_exit(response)


# @see https://habitica.com/apidoc/#api-Task-CreateUserTasks
valid_difficulties = click.Choice(list(DIFFICULTIES_SCORE_MAPPING.keys()))


@add.command()
@click.option("--difficulty", type=valid_difficulties,
              default="easy",
              show_default=True,
              help="the priority of the To-Do")
@click.option("--due-date", "--deadline", type=EnhancedDate(),
              help="due date of the To-Do in format YYYY-MM-DD or DD-MM-YYYY."
                   "The special keywords 'today' and 'tomorrow' specify the "
                   "current day, or tomorrow.")
@click.option("--checklist", "checklist_file", type=click.File(),
              help="Every line in FILENAME will be an item of the checklist.")
@click.option("--editor/--no-editor", "checklist_editor", default=False,
              help="Open up an editor to create a checklist interactively",
              show_default=True)
@click.argument("todo_name", required=False)
def todo(difficulty: str,
         due_date: datetime.datetime,
         checklist_file,
         checklist_editor: bool,
         todo_name: str):
    """Add a To-Do.

    TODO_NAME the name of the To-Do. When omitted, hopla will prompt the user to input
    a TODO_NAME interactively.

    \b
    Examples:
    ---
    # Simplest way to create a To-Do
    $ hopla add todo "My todo"

    \b
    # If you don't specify a To-Do name, hopla will prompt you for one.
    $ hopla add todo
    Please provide a name for your todo: My todo


    \b
    # override the default 'easy' difficulty using either
    # --difficulty hard|medium|trivial
    $ hopla add --difficulty=hard todo 'This is a hard todo'

    \b
    # --due-date and --deadline work as synonyms.
    $ hopla add todo --deadline 2042-01-21 "My Todo"
    $ hopla add todo --due-date 2042-01-21 "My Todo"


    \b
    # You can use the 'today' or 'tomorrow' special keywords instead
    # of a date format.
    $ hopla add todo --due-date today "Feed pet"

    \b
    # You can use cool shell tricks to provide checklists on the fly
    # e.g. sort a list in a file:
    $ hopla add todo --checklist <(sort ./tasks.txt) "Sorted Checklist"

    \b
    # open up an editor and type in your new checklist on the go
    $ hopla add todo --editor "My Long Checklist"

    \b
    # open up a file, edit it, and send it as a checklist.
    # note that this keeps the underlying file unchanged
    $ hopla add todo --checklist tasks.txt --editor "My editable checklist"


    \b
    # create a hard To-Do with due date on the 22nd of october in 2077, and
    # use every line in the `my_todo.md` FILE as an item of your checklist.
    $ hopla add todo --difficulty hard --due-date=2077-10-21 \\
                   --checklist-file ./my_todo.md 'Text for my todo'


    [apidocs](https://habitica.com/apidoc/#api-Task-CreateUserTasks)

    \f
    :param checklist_editor:
    :param difficulty: str
    :param due_date:
    :param checklist_file:
    :param todo_name:
    :return:

    """
    log.debug(f"habitica add todo name={todo_name}"
              f"   difficulty={difficulty} , due_date={due_date}"
              f"   checklist ={checklist_file}, editor={checklist_editor}")

    habitica_todo = create_habitica_todo(checklist_editor=checklist_editor,
                                         checklist_file=checklist_file,
                                         difficulty=difficulty,
                                         due_date=due_date,
                                         todo_name=todo_name)

    add_todo_response_data = AddTodoRequest(habitica_todo=habitica_todo).post_add_todo_request()

    click.echo(JsonFormatter(add_todo_response_data).format_with_double_quotes())


def create_habitica_todo(*,
                         checklist_editor: bool,
                         checklist_file,
                         difficulty: str,
                         due_date: datetime.datetime,
                         todo_name: str) -> HabiticaTodo:
    """Create a HabiticaTodo object from the provided parameters"""
    habitica_checklist = get_checklist(checklist_file=checklist_file,
                                       checklist_editor=checklist_editor)
    if todo_name is None:
        todo_name = click.prompt("Please provide a name for your todo")
    habitica_todo = HabiticaTodo(todo_name=todo_name, difficulty=difficulty,
                                 due_date=due_date, checklist=habitica_checklist)
    return habitica_todo


def get_checklist(checklist_file, checklist_editor: bool) -> HabiticaChecklist:
    """Get a habitica checklist from the user

     Returns an empty HabiticaChecklist if user did not want a checklist

     >>> get_checklist(None, False)
     HabiticaChecklist(checklist=[])
    """
    if checklist_editor:
        return get_checklist_with_editor(checklist_file)
    if checklist_file:
        return HabiticaChecklist(checklist=checklist_file.readlines())
    return HabiticaChecklist(checklist=[])


def get_checklist_with_editor(checklist_file) -> HabiticaChecklist:
    """
    Get the HabiticaUser for an user that requested the editor.
    """
    comment = "# Every line below this comment represents an item on your checklist\n"
    if checklist_file:
        text = comment + "".join(checklist_file.readlines())
    else:
        text = comment
    message = click.edit(text=text, extension=".md")
    if message is not None:
        try:
            checklist_str_with_comment: List[str] = message.split(comment, maxsplit=1)
        except IndexError as ex:
            sys.exit(f"could not find the checklist below the specified comment: {ex}")
        checklist_str = checklist_str_with_comment[1]
        return HabiticaChecklist(checklist=checklist_str.split("\n"))

    sys.exit("editor exited")
