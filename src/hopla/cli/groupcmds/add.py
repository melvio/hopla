"""
The module with CLI code that handles the `hopla add` group command.
"""
import datetime
import logging
from typing import Dict, List

import click
import requests

from hopla.hoplalib.clickhelper import data_on_success_else_exit
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
        """return score for a difficulty
           throws KeyError in case of an invalid difficulty
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


# @see https://habitica.com/apidoc/#api-Task-CreateUserTasks
valid_difficulties = click.Choice(list(DIFFICULTIES_SCORE_MAPPING.keys()))

due_date_formats = click.DateTime(formats=[
    "%Y-%m-%d",  # 2022-10-29
    "%d-%m-%Y",  # 29-10-2022
])


@add.command()
@click.option("--difficulty", type=valid_difficulties, default="easy")
@click.option("--due-date", "--deadline", type=due_date_formats, metavar="<date_format>",
              help="due date of the todo in either YYYY-MM-DD or DD-MM-YYYY")
@click.option("--checklist", "checklist_file", type=click.File(),
              help="every line in FILENAME will be an item of the checklist")
@click.option("--editor", "checklist_editor", is_flag=True, default=False,
              help="Open up an editor to create a checklist interactively")
@click.argument("todo_name")
def todo(difficulty: str,
         due_date: datetime.datetime,
         checklist_file,
         checklist_editor: bool,
         todo_name: str):
    """Add a To-Do.

    TODO_NAME the name of the To-Do

    \b
    Examples:
    ---
    # Simplest way to create a To-Do
    hopla add todo "My todo"

    \b
    # override the default 'easy' difficulty using either
    # --difficulty hard|medium|trivial
    hopla add --difficulty=hard todo 'This is a hard todo'

    \b
    # --due-date and --deadline work as synonyms.
    hopla add todo --deadline 2042-01-21 "My Todo"
    hopla add todo --due-date 2042-01-21 "My Todo"

    \b
    # using GNU's date "$(date '+Y-%m-%d')" as the due date
    # you'll set the due-date to 'today':
    hopla add todo --due-date $(date '+%Y-%m-%d') "Feed pet"

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
    :param difficulty:
    :param due_date:
    :param checklist_file:
    :param todo_name:
    :return:

    """
    log.debug(f"habitica add todo name={todo_name}"
              f"   difficulty={difficulty} , due_date={due_date}"
              f"   checklist ={checklist_file}, editor={checklist_editor}")

    #   TODO: look into ---editor list out of range issue I encoutnered
    habitica_checklist = get_checklist(checklist_file=checklist_file,
                                       checklist_editor=checklist_editor)
    habitica_todo = HabiticaTodo(todo_name=todo_name, difficulty=difficulty,
                                 due_date=due_date, checklist=habitica_checklist)

    url: str = UrlBuilder(path_extension="/tasks/user").url
    headers: dict = RequestHeaders().get_default_request_headers()
    response = requests.post(url=url, headers=headers, json=habitica_todo.to_json_dict())
    todo_data = data_on_success_else_exit(response)

    click.echo(JsonFormatter(todo_data).format_with_double_quotes())


def get_checklist(checklist_file, checklist_editor: bool) -> HabiticaChecklist:
    """Get a habitica checklist from the user

     Returns an empty HabiticaChecklist if user did not want a checklist
    """
    if checklist_editor:
        comment = "# Every line below this comment represents an item on your checklist\n"
        original_checklist = "".join(checklist_file.readlines()) if checklist_file else ""
        message = click.edit(text=comment + original_checklist)
        if message is not None:
            checklist_str_with_comment: List[str] = message.split(comment, maxsplit=1)
            checklist_str = checklist_str_with_comment[1]
            return HabiticaChecklist(checklist=checklist_str.split("\n"))
    elif checklist_file:
        return HabiticaChecklist(checklist=checklist_file.readlines())

    return HabiticaChecklist(checklist=[])
