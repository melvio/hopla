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


@add.command()
@click.option("--difficulty", type=valid_difficulties, default="medium", show_default=True)
@click.argument("todo_name")
def todo(difficulty, todo_name):
    """Add a To-Do.

    TODO_NAME the name of the To-DO

    [apidocs](https://habitica.com/apidoc/#api-Task-CreateUserTasks)

    \f
    :param todo_name:
    :param difficulty:
    :return:

    """
    log.debug(f"habitica add todo difficulty={difficulty} name={todo_name}")

    todo_item = dict()
    todo_item["text"] = todo_name
    todo_item["priority"] = difficulty_to_score(difficulty)
    todo_item["type"] = "todo"  # task type key

    url: str = UrlBuilder(path_extension="/tasks/user").url
    headers: dict = RequestHeaders().get_default_request_headers()

    response = requests.post(url=url, headers=headers, json=todo_item)

    click.echo(response.text)
