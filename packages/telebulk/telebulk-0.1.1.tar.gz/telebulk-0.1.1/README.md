<div align="center">

![](.media/icon-128x128_round.png)

# Telebulk

Execute actions on multiple Telegram users or groups

</div>

> [!Warning]
>
> New actions are added to this tool as needed.
>
> Because of that, functionality is very limited at the moment.
>
> Feel free to request any new features though!

## Links

[![Available on PyPI](https://img.shields.io/pypi/v/telebulk)](https://pypi.org/project/telebulk/)

## Actions available

- Kick (and Unban)

## Usage examples

<details>
<summary>Kick a single user from a single group</summary>

```fish
telebulk --user='12345' --group='67890' --kick
```

</details>

<details>
<summary>Unban a user from all group IDs contained in a file</summary>

```fish
#!/usr/bin/env fish
telebulk --user='12345' --group=(cat unban_groups.txt) --kick
```

</details>
