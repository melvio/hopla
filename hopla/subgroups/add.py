import logging
import click
import requests

from hopla.hoplalib.Http import UrlBuilder, RequestHeaders

log = logging.getLogger()


# TODO: add some kind of json filtering
@click.group()
def add():
    """Command group for adding things to habitica (e.g. To-Dos) """
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
@click.option("--due-date", "--deadline", type=due_date_formats, metavar="<date_format>", help="YYYY-MM-DD or DD-MM-YYYY")
@click.argument("todo_name")
def todo(difficulty, due_date, todo_name):
    """Add a To-Do.

    TODO_NAME the name of the To-DO

    [apidocs](https://habitica.com/apidoc/#api-Task-CreateUserTasks)

    \f
    :param todo_name:
    :param difficulty:
    :param due_date:
    :return:

    """
    log.debug(f"habitica add todo name={todo_name}"
              f"   difficulty={difficulty} , due_date={due_date}")

    todo_item = dict()
    todo_item["text"] = todo_name
    todo_item["priority"] = difficulty_to_score(difficulty)
    todo_item["type"] = "todo"  # task type key
    if due_date is not None:
        habitica_date_format = "%Y-%m-%d"
        todo_item["date"] = due_date.strftime(habitica_date_format)  # ISO 8601 date format

    url: str = UrlBuilder(path_extension="/tasks/user").url
    headers: dict = RequestHeaders().get_default_request_headers()

    response = requests.post(url=url, headers=headers, json=todo_item)

    click.echo(response.text)
