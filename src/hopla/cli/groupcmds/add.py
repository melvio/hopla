"""
The module with CLI code that handles the `hopla add` group command.
"""
import sys
import datetime
import logging
from typing import Dict, List

import click
import requests

from hopla.hoplalib.clickhelper import data_on_success_else_exit
from hopla.hoplalib.clickhelper import EnhancedDate
from hopla.hoplalib.http import RequestHeaders, UrlBuilder
from hopla.hoplalib.outputformatter import JsonFormatter

log = logging.getLogger()


@click.group()
def add():
    """GROUP for adding things to habitica"""


DIFFICULTIES_SCORE_MAPPING = {"hard": "2", "medium": "1.5", "easy": "1", "trivial": "0.1"}


class HabiticaChecklist:
    """ Habitica Checklist """

    def __init__(self, *, checklist=None):
        self.checklist = checklist

    def __repr__(self) -> object:
        return self.__class__.__name__ + f"(checklist={self.checklist})"

    def is_empty(self) -> bool:
        """Return true if checklist is none or empty"""
        return self.checklist is None or len(self.checklist) == 0

    def to_json_list(self) -> List[Dict[str, str]]:
        """Turn a checklist into a list that we can pass to the habitica API"""
        return [{"text": line} for line in self.checklist]


class HabiticaTodo:
    """ Habitica To-Do"""

    def __init__(self, *, todo_name, difficulty, due_date=None, checklist=None):
        self.todo_name = todo_name
        self._type = "todo"
        self.difficulty = difficulty
        self.due_date = due_date
        self.checklist: HabiticaChecklist = checklist

    def difficulty_to_score(self) -> str:
        """
        return score for a difficulty
        :raise KeyError in case of an invalid difficulty
        """
        return DIFFICULTIES_SCORE_MAPPING[self.difficulty]

    def str_due_date_to_date(self) -> str:
        """Turn the due_date into a valid ISO 8601 date format"""
        habitica_date_format = "%Y-%m-%d"
        return self.due_date.strftime(habitica_date_format)

    def to_json_dict(self) -> dict:
        """Turn an instance of this class into a dict that we can pass to the habitica API"""
        todo_dict = {
            "text": self.todo_name,
            "type": self._type,
            "priority": self.difficulty_to_score(),
            "checklist": self.checklist.to_json_list()
        }

        if self.due_date:
            todo_dict["date"] = self.str_due_date_to_date()

        return todo_dict


class AddTodoRequest:
    """An object that can perform an add To-Do request"""

    def __init__(self, habitica_todo: HabiticaTodo):
        self.url: str = UrlBuilder(path_extension="/tasks/user").url
        self.headers: dict = RequestHeaders().get_default_request_headers()
        self.habitica_todo = habitica_todo

    def post_add_todo_request(self):
        """Perform the add To-Do request and return the data in case of success"""
        response = requests.post(
            url=self.url,
            headers=self.headers,
            json=self.habitica_todo.to_json_dict()
        )
        return data_on_success_else_exit(response)


# @see https://habitica.com/apidoc/#api-Task-CreateUserTasks
valid_difficulties = click.Choice(list(DIFFICULTIES_SCORE_MAPPING.keys()))


@add.command()
@click.option("--difficulty", type=valid_difficulties, default="easy")
@click.option("--due-date", "--deadline", type=EnhancedDate(),
              help="due date of the To-Do in format YYYY-MM-DD or DD-MM-YYYY."
                   "The special keywords 'today' and 'tomorrow' specify the "
                   "current day, or tomorrow.")
@click.option("--checklist", "checklist_file", type=click.File(),
              help="every line in FILENAME will be an item of the checklist")
@click.option("--editor", "checklist_editor", is_flag=True, default=False,
              help="Open up an editor to create a checklist interactively")
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
    hopla add todo "My todo"

    \b
    # If you don't specify a To-Do name, hopla will prompt you for one.
    hopla add todo
    Please provide a name for your todo: My todo


    \b
    # override the default 'easy' difficulty using either
    # --difficulty hard|medium|trivial
    hopla add --difficulty=hard todo 'This is a hard todo'

    \b
    # --due-date and --deadline work as synonyms.
    hopla add todo --deadline 2042-01-21 "My Todo"
    hopla add todo --due-date 2042-01-21 "My Todo"


    \b
    # You can use the 'today' or 'tomorrow' special keywords instead
    # of a date format.
    hopla add todo --due-date today "Feed pet"

    \b
    # You can use cool shell tricks to provide checklists on the fly
    # e.g. sort a list in a file:
    hopla add todo --checklist <(sort ./tasks.txt) "Sorted Checklist"

    \b
    # open up an editor and type in your new checklist on the go
    hopla add todo --editor "My Long Checklist"

    \b
    # open up a file, edit it, and send it as a checklist.
    # note that this keeps the underlying file unchanged
    hopla add todo --checklist tasks.txt --editor "My editable checklist"


    \b
    # create a hard To-Do with due date on the 22nd of october in 2077, and
    # use every line in the `my_todo.md` FILE as an item of your checklist.
    hopla add todo --difficulty hard --due-date=2077-10-21 \\
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
    Get the HabiticaUser given that the user requested the use of an editor.
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


if __name__ == "__main__":
    import doctest

    doctest.testmod()
