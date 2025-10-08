import os
import time
from datetime import datetime, timezone
from multiprocessing import Process
from pathlib import Path

import click
from django.core.management import call_command
from django.db.models import Q
from rich.console import Console
from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn
from rich.table import Table

from config import DB_PATH, GROUP_NAME, PASSWORD_FILE
from crypto import Crypto
from db.models import Account, Group, Tag

from .secret import Secret
from .totp import Totp


def count_down(start, code, time_step):
    with Progress(
        TextColumn(f"[bold green]{code}"),
        BarColumn(),
        TimeRemainingColumn(),
        transient=True,
    ) as progress:
        task = progress.add_task("", total=time_step, completed=start)

        while not progress.finished:
            progress.update(task, advance=1)
            time.sleep(1)


@click.group()
def cli():
    pass


@cli.command()
@click.pass_context
def init(ctx):
    click.secho(
        r"""
  ______     __         __     ______     ______   ______
 /\  ___\   /\ \       /\ \   /\  __ \   /\__  _\ /\  == \
 \ \ \____  \ \ \____  \ \ \  \ \ \/\ \  \/_/\ \/ \ \  _-/
  \ \_____\  \ \_____\  \ \_\  \ \_____\    \ \_\  \ \_\
   \/_____/   \/_____/   \/_/   \/_____/     \/_/   \/_/
        """,
        fg="magenta",
    )

    if Path(DB_PATH).is_file():
        click.secho(f"Already initialized: {DB_PATH}", fg="yellow")
        return

    call_command("migrate", "db", verbosity=0)
    Group.objects.get_or_create(name=GROUP_NAME, salt=os.urandom(16))

    ctx.invoke(create_password)


@cli.command()
def create_password():
    if Path(PASSWORD_FILE).is_file():
        click.secho(f"Password already saved: {PASSWORD_FILE}", fg="yellow")
        return

    password = click.prompt(
        "Enter a password", type=str, confirmation_prompt=True, hide_input=True
    )
    group = Group.objects.get(name=GROUP_NAME)

    t = Process(
        target=Crypto.save_master_password,
        kwargs={"password": password, "salt": group.salt},
    )
    t.start()

    console = Console()
    with console.status("Deriving master password", spinner="bouncingBar") as status:
        status.update(status="Deriving master password")
        t.join()


@cli.command()
@click.argument("service")
@click.argument("seed")
@click.option(
    "-n",
    "--name",
    default="",
    help="Name to differentiate accounts of the same service",
)
@click.option("-t", "--tag", default=[], help="Tags to apply", multiple=True)
def add(service, seed, name, tag):
    group, _ = Group.objects.get_or_create(name=GROUP_NAME)
    click.secho(f"Adding {service}:{name}", fg="green")

    account = Account.objects.create(
        service=service,
        seed=seed,
        name=name,
        group=group,
        initialization_vector=Crypto.random_bytes(),
    )

    if tag:
        for t in tag:
            tag_object, _ = Tag.objects.get_or_create(group=group, name=t)
            tag_object.account.add(account)


@cli.command()
@click.argument("id")
def remove(id):
    group, _ = Group.objects.get_or_create(name=GROUP_NAME)
    account = group.account_set.get(id=id)

    click.secho(f"Removing {account.service}:{account.name}", fg="red")

    account.delete()


@cli.command()
@click.argument("identifier")
def code(identifier):
    """Get TOTP code for given IDENTIFIER

    IDENTIFIER can be ID, service, or name of an account. The code
    for the first account will be generated in the case of multiple.
    """
    group, _ = Group.objects.get_or_create(name=GROUP_NAME)
    account_set = group.account_set
    account = (
        account_set.filter(id=identifier).first()
        if identifier.isdigit()
        else group.account_set.filter(service=identifier).first()
        or group.account_set.filter(name=identifier).first()
    )

    if not account:
        return click.secho(f"No matching account found for {identifier}", fg="yellow")

    time_step = account.period
    code_length = account.digits

    totp = Totp(
        Secret.from_base32(account.seed),
        code_digits=code_length,
        algorithm=account.get_algorithm(),
        time_step=time_step,
    )

    try:
        while 1:
            start = datetime.now(tz=timezone.utc).second % time_step
            code = str(totp.generate_code()).zfill(code_length)
            count_down(start, code, time_step)
    except KeyboardInterrupt:
        pass


@cli.command()
@click.option(
    "-t",
    "--term",
    default="",
    help="Searches service, name, and tags",
)
def list(term):
    table = Table(title="Accounts", show_lines=True)
    table.add_column("ID")
    table.add_column("Service", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Tags")

    group, _ = Group.objects.get_or_create(name=GROUP_NAME)

    accounts = (
        group.account_set.filter(
            Q(service__contains=term)
            | Q(name__contains=term)
            | Q(tag__name__contains=term)
        )
        if term
        else group.account_set.all()
    )

    for account in accounts:
        table.add_row(str(account.id), account.service, account.name, account.tags())

    console = Console()
    console.print(table)


if __name__ == "__main__":
    cli()
