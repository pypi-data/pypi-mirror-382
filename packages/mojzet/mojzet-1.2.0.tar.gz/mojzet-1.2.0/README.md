ZET CLI
=======

Access ZET trips and time tables from the comfort of your terminal.

* Code & issues: https://codeberg.org/ihabunek/zet
* Python package: https://pypi.org/project/mojzet/

## Installation

Install using [uv](https://docs.astral.sh/uv/)

```sh
uv tool install mojzet
```

To upgrade to latest version:

```sh
uv tool upgrade mojzet
```

## Usage

Then run `zet` to get a list of commands:

```
λ zet
Usage: zet [OPTIONS] COMMAND [ARGS]...

Options:
  --debug    Enable debug logging
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  news         Show news feed
  route-trips  List trips for a given route
  routes       List routes
  stops        List stops
  trips        List arrivals for a given stop
  vehicles     List vehicles
```

## License

Copyright Ivan Habunek & contributors.

Licensed under GPLv3, see [LICENSE](LICENSE).
