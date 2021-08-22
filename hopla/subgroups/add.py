import datetime
import logging
from typing import Dict, List

import click
import requests

from hopla.hoplalib.Http import UrlBuilder, RequestHeaders

log = logging.getLogger()


# TODO: add some kind of json filtering
@click.group()
def add():
    """GROUP for adding things to habitica"""
    pass


difficulties_scores = {"hard": "2", "medium": "1.5", "easy": "1",
                       "trivial": "0.1"}  # @see https://habitica.com/apidoc/#api-Task-CreateUserTasks
valid_difficulties = click.Choice(list(difficulties_scores.keys()))


def difficulty_to_score(difficulty: str) -> str:
    """return score for given difficulty
       throws KeyError in case of an invalid difficulty
    :param difficulty: habitica difficulty
    :return: corresponding score
    """
    return difficulties_scores[difficulty]


# TODO: turn a ToDo in a @dataclass
# from dataclasses import dataclass
#
#
# @dataclass
# class HabiticaTodo:
#     difficulty: str
#     todo_name: str
#
# def score(self) -> str:
#     """return score for given difficulty
#        throws KeyError in case of an invalid difficulty
#     :param difficulty: habitica difficulty
#     :return: corresponding score
#     """
#     return difficulties_scores[self.difficulty]


due_date_formats = click.DateTime(formats=["%Y-%m-%d",  # 2022-10-29
                                           "%d-%m-%Y",  # 29-10-2022
                                           ])


@add.command()
@click.option("--difficulty", type=valid_difficulties, default="easy", show_default=True)
@click.option("--due-date", "--deadline", type=due_date_formats, metavar="<date_format>",
              help="due date of the todo in either YYYY-MM-DD or DD-MM-YYYY")
@click.option("--checklist-file", type=click.File(), help="every line in FILENAME will be an item of the checklist")
@click.argument("todo_name")
def todo(difficulty: str,
         due_date: datetime.datetime,
         checklist_file,
         todo_name: str):
    """Add a To-Do.

    TODO_NAME the name of the To-DO

    \b
    Examples:
    ---
    # create a To-Do without any hoopla:
    hopla add todo 'Text for my todo'

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
    # create a hard To-Do with due date on the 22nd of october in 2077, and
    # use every line in the `my_todo.md` FILE as an item of your checklist.
    hopla add todo --difficulty hard --due-date=2077-10-21 \\
                   --checklist-file ./my_todo.md 'Text for my todo'


    [apidocs](https://habitica.com/apidoc/#api-Task-CreateUserTasks)

    \f
    :param difficulty:
    :param due_date:
    :param checklist_file:
    :param todo_name:
    :return:

    """
    log.debug(f"habitica add todo name={todo_name}"
              f"   difficulty={difficulty} , due_date={due_date}")

    todo_item = dict()
    todo_item["text"] = todo_name
    todo_item["priority"] = difficulty_to_score(difficulty)
    todo_item["type"] = "todo"  # task type key
    if due_date is not None:
        habitica_date_format = "%Y-%m-%d"  # ISO 8601 date format
        todo_item["date"] = due_date.strftime(habitica_date_format)

    if checklist_file is not None:
        # TODO: Make an object for this, not dicts of list of dicts
        checklist_list: List[Dict[str, str]] = [{"text": line} for line in checklist_file.readlines()]
        todo_item["checklist"] = checklist_list

    url: str = UrlBuilder(path_extension="/tasks/user").url
    headers: dict = RequestHeaders().get_default_request_headers()

    response = requests.post(url=url, headers=headers, json=todo_item)

    click.echo(response.text)
