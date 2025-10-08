#!/usr/bin/env python
# -*- coding: utf-8 - *-

# Copyright (c) 2020 Romeet Chhabra

__author__ = "Romeet Chhabra"
__copyright__ = "Copyright 2020, Romeet Chhabra"
__license__ = "GPL-3.0-or-later"

from sys import exit, platform, stderr
from time import localtime, strftime
from importlib.resources import files
from os import environ
from pathlib import Path
from stat import filemode
from shutil import get_terminal_size
from configparser import ConfigParser
from argparse import REMAINDER, ArgumentParser


def get_human_readable_size(size, base=1024.0):
    """
    Convert a size in bytes to a human-readable string.

    Args:
        size (float): The size in bytes.
        base (int, optional): The base of the unit system (default is 1024).

    Returns:
        str: A human-readable representation of the size.

    Notes:
        This function uses a list of units with their corresponding values,
        and iteratively divides the size by the base until it reaches
        the first unit that results in a value greater than or equal to 1.
    """
    units = ["b", "K", "M", "G", "T", "P", "E", "Z", "Y"]
    for unit in units:
        if size < base:
            return f"{size:4.0f}{unit}"
        size /= base


def _get_config(fp=""):
    config = ConfigParser()
    # Read config file from (in order) bundled config,
    # XDG_CONFIG_HOME, HOME, or parent folder.
    if __name__ != "__main__":
        conf = files("colorls.config").joinpath("colorls.toml")
    else:
        conf = Path(__file__).parent.absolute() / "config/colorls.toml"
    config.read(
        [
            conf,
            Path(environ.get("XDG_CONFIG_HOME", "~/.config")).expanduser()
            / "colorls/colorls.toml",
            Path("~/.colorls.toml").expanduser(),
            fp,
        ],
        encoding="utf8",
    )
    return config


def get_config(fp=""):
    config = _get_config(fp)
    return (
        dict(config["COLOR"]),
        dict(config["ICONS"]),
        dict(config["ALIASES"]),
        dict(config["SUFFIXES"]),
    )


def get_keys(fp):
    n, ext = fp.stem.lower(), fp.suffix.lower()
    if ext == "":
        ext = n  # Replace ext with n if ext empty
    if ext.startswith("."):
        ext = ext[1:]  # Remove leading period

    if fp.is_symlink():
        fmtkey = "link"
        icokey = "link"
    elif fp.is_mount():
        fmtkey = "mount"
        icokey = "mount"
    elif fp.is_socket():
        fmtkey = "socket"
        icokey = "socket"
    elif fp.is_block_device():
        fmtkey = "block_device"
        icokey = "block_device"
    elif fp.is_char_device():
        fmtkey = "char_device"
        icokey = "char_device"
    elif fp.is_dir():
        fmtkey = "dir"
        icokey = "dir"
    elif fp.is_file():
        fmtkey = "file"
        icokey = "file"
        if filemode(fp.stat().st_mode)[3] == "x":
            fmtkey = "exec"
            icokey = "exec"
    else:
        fmtkey = "none"
        icokey = "none"

    if ext.endswith("~"):
        fmtkey = "backup"
        ext = ext[:-1]  # Remove trailing tilde
    if n.startswith("."):
        fmtkey = f"hidden_{fmtkey}"
    elif ALIAS.get(ext, "") in COLOR:
        fmtkey = ALIAS[ext]

    if icokey == "dir" and f"dir_{ALIAS.get(ext, '')}" in ICONS:
        icokey = f"dir_{ALIAS[ext]}"
    elif ALIAS.get(ext, "") in ICONS:
        icokey = ALIAS[ext]

    return fmtkey.lower(), icokey.lower()


def get_tree_listing_prefix(
    positions=None,
):
    tree_prefix_str = "".join(
        [(" │   " if pos > 0 else "     ") for pos in positions[:-1]]
    ) + (" ├───" if positions[-1] > 0 else " └───")  #  └┌  ┃━┗┣┏
    return tree_prefix_str


def get_long_listing_prefix(
    fp,
    is_numeric=False,
    use_si=False,
    inode=False,
    timefmt=None,
):
    try:
        st = fp.stat(follow_symlinks=False)
        hln = st.st_nlink
        ino = f"{fp.stat(follow_symlinks=False).st_ino: 10d} " if inode else ""
        mode = filemode(st.st_mode)

        size = st.st_size
        sz = get_human_readable_size(size, 1000.0 if use_si else 1024.0)

        mtime = localtime(st.st_mtime)
        if timefmt:
            mtime = strftime(timefmt, mtime)
        else:
            mtime = strftime(
                f"%b %d {'%H:%M' if strftime('%Y') == strftime('%Y', mtime) else ' %Y'}",
                mtime,
            )

        ug_str = ""
        if platform.startswith("linux") or platform.startswith("darwin"):
            from grp import getgrgid
            from pwd import getpwuid

            uid = (
                getpwuid(st.st_uid).pw_name
                if not is_numeric
                else str(st.st_uid)
            )
            gid = (
                getgrgid(st.st_gid).gr_name
                if not is_numeric
                else str(st.st_gid)
            )
            ug_str = f"{uid:4} {gid:4}"

        long_prefix_str = f"{ino}{mode} {hln:3} {ug_str} {sz} {mtime} "
        return long_prefix_str
    except FileNotFoundError as err:
        return err


def print_short_listing(
    fp,
    inode=False,
    expand_link=False,
    suff=False,
    format_override=None,
    sep_len=None,
    display_icons=True,
    expand_path=False,
    end="",
):
    ino = f"{fp.stat(follow_symlinks=False).st_ino: 10d}" if inode else ""
    fmt, ico = format_override if format_override else get_keys(fp)
    name = (
        str(fp)
        if expand_path
        else fp.name.strip() + (SUFFIX.get(fmt, "") if suff else "")
    )
    sep_len = sep_len if sep_len else len(name)
    icon_str = f" {ICONS.get(ico, '')}  " if display_icons else ""
    if expand_link and fp.is_symlink():
        name += " ➞ " + str(fp.resolve())
    print(
        f"{ino}\x1b[{COLOR[fmt]}m{icon_str}{name:<{sep_len}}\x1b[0m",
        end=end,
    )


def _get_entries(directory, args):
    contents = list()
    try:
        p = Path(directory)
        if not p.exists():
            print(f"lx: {p}: No such file or directory")
            exit(1)
        if p.is_dir():
            contents = list(p.iterdir())
        elif p.is_file():
            contents = [p]
    except Exception as e:
        print(e, file=stderr)
        exit(1)

    remove_list = list()
    if args.ignore:
        remove_list += list(p.glob(args.ignore))
    if not args.all:
        remove_list += list(p.glob(".*"))
    if args.ignore_backups:
        remove_list += list(p.glob("*~"))
    contents = [c for c in contents if c not in remove_list]

    entries = contents
    if args.reverse:
        entries = sorted(contents, reverse=True)
    elif not args.unsorted:
        entries = sorted(contents, reverse=False)

    if args.directory:
        entries = [x for x in contents if x.is_dir()]
    elif args.file:
        entries = [x for x in contents if x.is_file()]
    elif args.sd:
        entries = [x for x in contents if x.is_dir()]
        entries += [x for x in contents if x.is_file()]
    elif args.sf:
        entries = [x for x in contents if x.is_file()]
        entries += [x for x in contents if x.is_dir()]

    return entries


def process_entry(fp, args, positions=None, size=None):
    num_dirs, num_files = 0, 0
    positions = [] if not positions else positions

    # get entries for directory. If empty exit
    entries = _get_entries(fp, args)
    if not entries:
        return 0, 0

    num_entries = len(entries)

    if args.header and len(positions) == 0:
        p = Path(fp)
        # We know p exists since _get_entries would have failed if it did not
        print_short_listing(
            p,
            inode=args.inode,
            format_override=("this", "this"),
            display_icons=args.x,
            expand_path=True,
            end="\n",
        )

    # to ensure no overlap Additional padding of 3 added to length for better
    # differentiation between entries (aesthetic choice)
    longest = max([len(str(x.name)) for x in entries]) + 3
    # Additional padding when calculating number of entries
    # Padding of 4 to account for icons as used in print_short_listing
    # (<space><icon><space><space>) Padding of 11 to account for inode
    # printing (<inode aligned to 10 units><space>)
    # If size of terminal or size of file list can not determined, default
    # to one item per line
    max_items = (
        0
        if not size
        else size[0]
        // (longest + (4 if args.x else 0) + (11 if args.inode else 0))
    )

    run = 0
    subdirs = []
    for i, entry in enumerate(entries):
        prefix_str = ""

        if entry.is_dir():
            subdirs.append(entry)
            num_dirs += 1
        else:
            num_files += 1

        if args.long or args.numeric_uid_gid:
            prefix_str = get_long_listing_prefix(
                entry,
                is_numeric=args.numeric_uid_gid,
                use_si=args.si,
                inode=args.inode,
            )
            print(prefix_str, end="")
            print_short_listing(
                entry,
                expand_link=True,
                sep_len=longest,
                suff=args.classify,
                display_icons=args.x,
                end="\n",
            )
        elif args.tree and args.tree > 0:
            prefix_str = get_tree_listing_prefix(
                positions=positions + [num_entries - i - 1],
            )
            print(prefix_str, end="")
            print_short_listing(
                entry,
                inode=args.inode,
                expand_link=True,
                sep_len=longest,
                suff=args.classify,
                display_icons=args.x,
                end="\n",
            )
            if entry.is_dir() and len(positions) < args.tree - 1:
                d, f = process_entry(
                    entry,
                    args,
                    positions=positions + [num_entries - i - 1],
                    size=size,
                )
                num_dirs += d
                num_files += f
        elif vars(args)["1"]:
            print_short_listing(
                entry,
                inode=args.inode,
                sep_len=longest,
                suff=args.classify,
                display_icons=args.x,
                end="\n",
            )
        else:
            print_short_listing(
                entry,
                inode=args.inode,
                sep_len=longest,
                suff=args.classify,
                display_icons=args.x,
                end="",
            )
            run += 1
            if run >= max_items or i == num_entries - 1:
                run = 0
                print()

    if args.recursive and not args.tree:
        for sub in subdirs:
            print()
            if not args.header:
                print_short_listing(
                    sub,
                    inode=args.inode,
                    format_override=("this", "this"),
                    display_icons=args.x,
                    expand_path=True,
                    end="\n",
                )
            d, f = process_entry(sub, args, size=size)
            num_dirs += d
            num_files += f

    return num_dirs, num_files


def main():
    parser = ArgumentParser(
        description=(
            "Pure Python implementation of `ls` command. "
            "Only a subset of available arguments are implemented"
        ),
        epilog=(
            "Feature Requests/Bugs should be reported at "
            "https://codeberg.org/compilation-error/colorls/issues"
        ),
    )

    parser.add_argument(
        "-1",
        action="store_true",
        default=False,
        help="list items on individual lines",
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        default=False,
        help="do not ignore entries starting with .",
    )
    parser.add_argument(
        "-B",
        "--ignore-backups",
        action="store_true",
        default=False,
        help="do not list implied entries ending with ~",
    )
    parser.add_argument(
        "-d",
        "--directory",
        action="store_true",
        default=False,
        help="list directories themselves, not their contents",
    )
    parser.add_argument(
        "-f",
        "--file",
        action="store_true",
        default=False,
        help="list files only, not directories",
    )
    parser.add_argument(
        "--sd",
        "--sort-directories",
        action="store_true",
        default=False,
        help="list directories first",
    )
    parser.add_argument(
        "--sf",
        "--sort-files",
        action="store_true",
        default=False,
        help="list files first",
    )
    parser.add_argument(
        "-F",
        "--classify",
        action="store_true",
        default=False,
        help="append indicator (one of */=>@|) to entries",
    )
    parser.add_argument(
        "-i",
        "--inode",
        action="store_true",
        default=False,
        help="display inode number",
    )
    parser.add_argument(
        "-I",
        "--ignore",
        metavar="PATTERN",
        help="do not list implied entries matching shell PATTERN",
    )
    parser.add_argument(
        "-l",
        "--long",
        action="store_true",
        default=False,
        help="use a long listing format",
    )
    parser.add_argument(
        "-n",
        "--numeric-uid-gid",
        action="store_true",
        default=False,
        help="like -l, but list numeric user and group IDs",
    )
    parser.add_argument(
        "-R",
        "--recursive",
        action="store_true",
        default=False,
        help="list subdirectories recursively",
    )
    parser.add_argument(
        "-t",
        "--tree",
        metavar="DEPTH",
        type=int,
        nargs="?",
        const=3,
        help="max tree depth",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        default=False,
        help="display current version number and exit",
    )
    parser.add_argument(
        "--si",
        action="store_true",
        default=False,
        help="display file size in SI units",
    )
    parser.add_argument(
        "-r",
        "--reverse",
        action="store_true",
        default=False,
        help="reverse sorting order",
    )
    parser.add_argument(
        "-U",
        "--unsorted",
        action="store_true",
        default=False,
        help="do not sort; list entries in directory order. --reverse supercedes this.",
    )
    parser.add_argument(
        "-H",
        "--header",
        action="store_true",
        default=False,
        help="do not display header",
    )
    parser.add_argument(
        "-x", action="store_false", default=True, help="do not display icons"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        default=False,
        help="print counts of dirs and files",
    )
    parser.add_argument(
        "--dump-config",
        action="store_true",
        default=False,
        help="dump default config to file `colorls.toml`",
    )
    parser.add_argument(
        "-c",
        "--config",
        metavar="CONFIG_FILE",
        type=str,
        nargs="?",
        const="",
        help="custom config file",
    )
    parser.add_argument(
        "FILE",
        default=".",
        nargs=REMAINDER,
        help="List information about the FILE(s).",
    )
    args = parser.parse_args()

    if args is None:
        exit(2)

    if args.version:
        from . import __version__

        print("color-ls version " + __version__)
        exit(0)

    global COLOR
    global ICONS
    global ALIAS
    global SUFFIX
    COLOR, ICONS, ALIAS, SUFFIX = get_config(args.config if args.config else "")

    if args.dump_config:
        try:
            with open("./colorls.toml", "w", encoding="utf-8") as f:
                _get_config().write(f)
            print(
                "Default config written to `./colorls.toml`. \n"
                "Copy to `~/.colorls.toml` or `~/.config/colorls/colorls.toml`"
            )
            exit(0)
        except IOError:
            exit(1)

    if not args.FILE:
        args.FILE = ["."]

    if len(args.FILE) > 1:
        args.header = True

    term_size = get_terminal_size()
    for FILE in args.FILE:
        d, f = process_entry(FILE, args, size=term_size)
        print()
        if args.report:
            print(f" {d} directories, {f} files")
            print()

    return 0


if __name__ == "__main__":
    exit(main())


# vim: ts=4 sts=4 sw=4 et syntax=python:
