import click


@click.group()
def slack_cli():
    pass


@click.command('slack-notify')
@click.option('--hook', help='Webhook hook1,hook2...', required=True)
@click.option('--title', help='Title', required=True)
@click.option('--icon', help='Icon unicode')
@click.option('--message', help='Body message', required=True)
@click.option('--origin', help='From', required=True)
def slack_notify(hook, title, icon, message, origin):
    from giscemultitools.slackutils.utils import SlackUtils
    data_to_send = SlackUtils.generic_notify_data(title, icon, message, origin)
    SlackUtils.notify(hook, data_to_send)


slack_cli.add_command(slack_notify)


if __name__ == "__main__":
    slack_cli()
