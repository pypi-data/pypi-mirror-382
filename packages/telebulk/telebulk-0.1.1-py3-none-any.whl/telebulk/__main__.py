import click
import telethon
import telethon.tl.types
import importlib.metadata
import asyncio

def telethon_version() -> str:
	return importlib.metadata.version("telethon")

def telebulk_version() -> str:
	return importlib.metadata.version("telebulk")

def print_version(ctx, param, value):
	if not value or ctx.resilient_parsing:
		return
	click.echo(f"telebulk v{telebulk_version()}, telethon v{telethon_version()}")
	ctx.exit()

def format_user_name(user: telethon.tl.types.User) -> str:
	if user.username:
		return f"@{user.username} ({user.id})"
	if user.last_name:
		return f"{user.first_name} {user.last_name} ({user.id})"
	if user.first_name:
		return f"{user.first_name} ({user.id})"
	return f"({user.id})"

def format_group_name(group: telethon.tl.types.Channel) -> str:
	if group.title:
		return f"{group.title} ({group.id})"
	return f"({group.id})"

@click.command()
@click.option(
	"--session-name",
	"session_name",
	envvar="TELEBULK_SESSION_NAME",
	default="anon",
	type=str,
	help="The session name to pass to Telethon. It will be used to store information about the session as a `.session` file with that name in the working directory."
)
@click.option(
	"--api-id",
	"api_id",
	envvar="TELEBULK_API_ID",
	type=int,
	required=True,
	help="The Telegram API ID to use. Get yours at: https://my.telegram.org/apps"
)
@click.option(
	"--api-secret",
	"api_secret",
	envvar="TELEBULK_API_SECRET",
	type=str,
	required=True,
	help="The Telegram API secret to use. Get yours at: https://my.telegram.org/apps"
)
@click.option(
	"-u", 
	"--user", 
	"users", 
	type=int,
	multiple=True,
	help="Specifies a user."
)
@click.option(
	"-g",
	"--group",
	"groups",
	type=int,
	multiple=True,
	help="Specifies a group."
)
@click.option(
	"--kick",
	"action_kick",
	is_flag=True,
	default=False,
	help="Kick or unban an user from a group."
)
@click.option(
	"--version",
	help="Show the version number and exit.",
	is_flag=True,
	callback=print_version,
	expose_value=False,
	is_eager=True,
)
def telebulk(**kwargs):
	"""
	Does Telegram operations on multiple things at once.
	"""
	asyncio.run(telebulk_async(**kwargs))

async def telebulk_async(
	session_name,
	api_id,
	api_secret,
	users,
	groups,
	action_kick,
):
	async with telethon.TelegramClient(
		session_name, 
		api_id, 
		api_secret,
		device_model="Console",
		system_version=f"telethon {telethon_version()}",
		app_version=f"telebulk {telebulk_version()}",
	) as client:
		# Get login info
		me = await client.get_me()
		click.echo(
			click.style("Logged in as: ", fg="black") + 
			click.style(format_user_name(me), fg="black", bold=True)
		)
		# Retrieve open chats for entity resolution
		dialogs = await client.get_dialogs()
		click.echo(
			click.style("Retrieved list of open chats.", fg="black")
		)
		# Get selected user info
		resolved_users = []
		for user in users:
			this = await client.get_entity(user)
			assert type(this) == telethon.tl.types.User
			click.echo(
				click.style("Selected user: ", fg="blue") + 
				click.style(format_user_name(this), fg="blue", bold=True)
			)
			resolved_users.append(this)
		# Get selected groups info
		resolved_groups = []
		for group in groups:
			this = await client.get_entity(group)
			assert type(this) == telethon.tl.types.Channel
			click.echo(
				click.style("Selected group: ", fg="cyan") + 
				click.style(format_group_name(this), fg="cyan", bold=True)
			)
			resolved_groups.append(this)
		# Get action info
		if action_kick:
			click.echo(
				click.style("Selected action: ", fg="magenta") + 
				click.style("Kick", fg="magenta", bold=True)
			)
		# Proceed?
		click.confirm("Proceed?", abort=True)
		# Perform action
		if action_kick:
			for group in resolved_groups:
				for user in resolved_users:
					try:
						await client.kick_participant(
							entity=group,
							user=user,
						)
					except Exception as exc:
						click.echo(
							click.style("Failure.", fg="red", bold=True) + 
							" Could not " +
							click.style("kick", fg="magenta") + 
							" " +
							click.style(format_user_name(user), fg="cyan") +
							" from " +
							click.style(format_group_name(group), fg="blue") + 
							": " +
							click.style(f"{exc!r}", fg="red")
						)
					else:
						click.echo(
							click.style("Success!", fg="green", bold=True) + 
							" " +
							click.style("Kicked", fg="magenta") + 
							" " +
							click.style(format_user_name(user), fg="cyan") +
							" from " +
							click.style(format_group_name(group), fg="blue")
						)


if __name__ == "__main__":
	telebulk()
