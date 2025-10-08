# Colorls

Pure Python implementation of ls command with colors and icons. Inspired from [colorls](https://github.com/athityakumar/colorls). 
Requires [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts/blob/master/readme.md) for icon/glyphs.

__Note__: This is not optimized and runs an order of magnitude slower than native `ls`.

## Installation

This is intended to run as an executable and not a library, it is preferable to use a tool such as [pipx](https://github.com/pypa/pipx) or [uv tool](https://docs.astral.sh/uv/guides/tools/)

`pipx install color-ls`

[!NOTE]
To customize the colors or add / change icons, copy `config/colorls.toml` to either `$XDG_CONFIG_HOME/colorls/colorls.toml` or `~/.colorls.toml` and update as required.
Alternatively, you can call `lx` with a (partial) config file using the `-c` flag.

## Usage

```
lx --help

usage: colorls.py [-h] [-1] [-a] [-B] [-d] [-f] [--sd] [--sf] [-F] [-i]
                  [-I PATTERN] [-l] [-n] [-R] [-t [DEPTH]] [--version] [--si]
                  [-r] [-U] [-H] [-x] [--report] [--dump-config]
                  [-c [CONFIG_FILE]]
                  ...

Pure Python implementation of `ls` command. Only a subset of available
arguments are implemented

positional arguments:
  FILE                  List information about the FILE(s).

options:
  -h, --help            show this help message and exit
  -1                    list items on individual lines
  -a, --all             do not ignore entries starting with .
  -B, --ignore-backups  do not list implied entries ending with ~
  -d, --directory       list directories themselves, not their contents
  -f, --file            list files only, not directories
  --sd, --sort-directories
                        list directories first
  --sf, --sort-files    list files first
  -F, --classify        append indicator (one of */=>@|) to entries
  -i, --inode           display inode number
  -I, --ignore PATTERN  do not list implied entries matching shell PATTERN
  -l, --long            use a long listing format
  -n, --numeric-uid-gid
                        like -l, but list numeric user and group IDs
  -R, --recursive       list subdirectories recursively
  -t, --tree [DEPTH]    max tree depth
  --version             display current version number and exit
  --si                  display file size in SI units
  -r, --reverse         reverse sorting order
  -U, --unsorted        do not sort; list entries in directory order.
                        --reverse supercedes this.
  -H, --header          do not display header
  -x                    do not display icons
  --report              print counts of dirs and files
  --dump-config         dump default config to file `colorls.toml`
  -c, --config [CONFIG_FILE]
                        custom config file

Feature Requests/Bugs should be reported at https://codeberg.org/compilation-
error/colorls/issues
```

## Screenshots

### Default view

![lx](screenshots/lx.png)

### No Icons

![lx -x](screenshots/x.png)

### List *__only__* files _or_ dirs

![lx -f](screenshots/f.png)
![lx -d](screenshots/d.png)

### List files _or_ dirs first

![ls --sf](screenshots/sf.png)
![lx --sd](screenshots/sd.png)

### Long Listing

![lx -l](screenshots/l.png)

### Tree View

![lx -t[=3]](screenshots/t.png)

### Globs should work as well

![lx -I](screenshots/-i.png)

### Current Version

![lx --version](screenshots/v.png)

## Requirements

- Python 3.10 or higher
- Nerd Fonts

## License

GPL-3.0-or-later

