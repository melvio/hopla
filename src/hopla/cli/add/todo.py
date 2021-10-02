#!/usr/bin/env python3
"""
Module with the command for the `hopla add todo` command.
"""
import logging
import sys
from datetime import datetime, timedelta
from typing import Final, List

import click

from hopla.hoplalib.outputformatter import JsonFormatter
from hopla.hoplalib.tasks.taskcontroller import AddTodoRequest
from hopla.hoplalib.tasks.taskmodel import HabiticaChecklist, HabiticaTodo, TaskDifficultyData

log = logging.getLogger()


def create_habitica_todo(*,
                         checklist_editor: bool,
                         checklist_file,
                         difficulty: str,
                         due_date: datetime,
                         todo_name: str) -> HabiticaTodo:
    """Create a HabiticaTodo object from the provided parameters"""
    habitica_checklist: HabiticaChecklist = get_checklist(
        checklist_file=checklist_file, checklist_editor=checklist_editor
    )
    if todo_name is None:
        todo_name: str = click.prompt("Please provide a name for your todo")
    return HabiticaTodo(
        todo_name=todo_name,
        difficulty=difficulty,
        due_date=due_date,
        checklist=habitica_checklist
    )


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
        text: str = comment + "".join(checklist_file.readlines())
    else:
        text: str = comment
    message = click.edit(text=text, extension=".md")
    if message is not None:
        try:
            checklist_str_with_comment: List[str] = message.split(comment, maxsplit=1)
        except IndexError as ex:
            sys.exit(f"could not find the checklist below the specified comment: {ex}")
        checklist_str = checklist_str_with_comment[1]
        return HabiticaChecklist(checklist=checklist_str.split("\n"))

    sys.exit("editor exited")


_DUE_DATE_OPTION_NAME: Final[str] = "--due-date"
_DUE_DATE_TODAY_FLAG: Final[str] = "--today"
_DUE_DATE_TOMORROW_FLAG: Final[str] = "--tomorrow"
__DUE_DATE_FEATURE_FLAG_PARAM: Final[str] = "due_date"

date_formats = ["%Y-%m-%d", "%d-%m-%Y"]
TODAY = datetime.today()
TOMORROW = TODAY + timedelta(days=1)


@click.command()
@click.option(
    "--difficulty",
    type=click.Choice(TaskDifficultyData.VALID_DIFFICULTIES),
    default="easy",
    show_default=True,
    help="the priority of the To-Do"
)
@click.option(
    _DUE_DATE_OPTION_NAME, "--deadline", __DUE_DATE_FEATURE_FLAG_PARAM,
    type=click.DateTime(formats=date_formats),
    help="Due date of the To-Do in format YYYY-MM-DD or DD-MM-YYYY."
)
@click.option(
    _DUE_DATE_TODAY_FLAG, __DUE_DATE_FEATURE_FLAG_PARAM, flag_value=TODAY,
    type=click.DateTime(formats=date_formats),
    help="Use today as the due date."
)
@click.option(
    _DUE_DATE_TOMORROW_FLAG, __DUE_DATE_FEATURE_FLAG_PARAM, flag_value=TOMORROW,
    type=click.DateTime(formats=date_formats),
    help="Use tomorrow as the due date.")
@click.option(
    "--checklist", "checklist_file",
    type=click.File(),
    help="Every line in FILENAME will be an item of the checklist."
)
@click.option(
    "--editor", "checklist_editor", is_flag=True,
    default=False,
    help="Open up an editor to create a checklist interactively",
    show_default=True
)
@click.argument("todo_name", required=False)
def todo(difficulty: str,
         due_date: datetime,
         checklist_file,
         checklist_editor: bool,
         todo_name: str):
    """Add a To-Do.

    TODO_NAME the name of the To-Do. When omitted, hopla will prompt the user to input
    a TODO_NAME interactively.

    \b
    Examples:
    ---
    # Simplest way to create a To-Do:
    $ hopla add todo "My todo"

    \b
    # If you don't specify a To-Do name, hopla will prompt you for one.
    $ hopla add todo
    > Please provide a name for your todo: My todo

    \b
    # Override the default 'easy' difficulty using either hard|medium|trivial.
    $ hopla add --difficulty=hard todo 'This is a hard todo'

    \b
    # --due-date and --deadline work as synonyms.
    $ hopla add todo --deadline 2042-01-21 "My Todo"
    $ hopla add todo --due-date 2042-01-21 "My Todo"

    \b
    # --due-date and --deadline support YYYY-MM-DD and DD-MM-YYYY, so the
    # following commands are the same:
    $ hopla add todo --deadline 12-31-2101 "My Todo"
    $ hopla add todo --deadline 2101-12-31 "My Todo"


    \b
    # Use the 'today' or 'tomorrow' to set the due date to today/tomorrow.
    $ hopla add todo --today "Feed pet"
    $ hopla add todo --tomorrow "Feed pet Again"

    \b
    # You can use cool shell tricks to provide checklists on the fly.
    # e.g. sort a list in a file:
    $ hopla add todo --checklist <(sort ./tasks.txt) "Sorted Checklist"

    \b
    # Open up an editor and type in your new checklist on the go.
    $ hopla add todo --editor "My Long Checklist"
    > editor opens

    \b
    # Open up a file as a template for your checklist, edit it, and send
    # it as a checklist.
    # The underlying file remains unchanged.
    $ hopla add todo --checklist tasks.txt --editor "My editable checklist"
    > editor opens tasks.txt


    \b
    # Create a hard To-Do with due date on the 22nd of october in 2077, and
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
    log.debug(f"habitica add todo name={todo_name}\n"
              f"   difficulty={difficulty}, "
              f"   due_date={due_date},"
              f"   checklist ={checklist_file}, editor={checklist_editor}")

    habitica_todo: HabiticaTodo = create_habitica_todo(
        checklist_editor=checklist_editor,
        checklist_file=checklist_file,
        difficulty=difficulty,
        due_date=due_date,
        todo_name=todo_name
    )

    add_todo_response_data = AddTodoRequest(habitica_todo=habitica_todo).post_add_todo_request()

    click.echo(JsonFormatter(add_todo_response_data).format_with_double_quotes())
