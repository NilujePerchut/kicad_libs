# -*- coding: utf-8 -*-


import argparse
import logging
import os
import os.path
import re
import shutil
import sys

import kinparse

import pcbnew

from six import string_types
from pckg_info import __version__


def rmv_quotes(s):
    """Remove starting and ending quotes from a string."""
    if not isinstance(s, string_types):
        return s

    mtch = re.match(r'^\s*"(.*)"\s*$', s)
    if mtch:
        try:
            s = s.decode(mtch.group(1))
        except (AttributeError, LookupError):
            s = mtch.group(1)

    return s


def get_global_fp_lib_table_dir():
    """Get the path to where the global fp-lib-table file is found."""

    paths = (
        "$HOME/.config/kicad",
        "~/.config/kicad",
        "%APPDATA%/kicad",
        "$HOME/Library/Preferences/kicad",
        "~/Library/Preferences/kicad",
    )
    for path in paths:
        path = os.path.normpath(os.path.expanduser(os.path.expandvars(path)))
        if os.path.lexists(path):
            return path
    return ""


class LibURIs(dict):
    """Dict for storing library URIs from all directories in fp-lib-table file."""

    def __init__(self, *args):
        super(self.__class__, self).__init__()
        for fp_lib_table_dir in args:
            self.load(fp_lib_table_dir)

    def load(self, fp_lib_table_dir):
        """Load cache with URIs for libraries in fp-lib-table file."""
        # Read contents of footprint library file into a single string.
        try:
            with open(os.path.join(fp_lib_table_dir, "fp-lib-table")) as fp:
                tbl = fp.read()
        except IOError:
            return

        # Get individual "(lib ...)" entries from the string.
        libs = re.findall(
            r"\(\s*lib\s* .*? \)\)", tbl, flags=re.IGNORECASE | re.VERBOSE | re.DOTALL
        )

        # Add the footprint modules found in each enabled KiCad libray.
        for lib in libs:

            # Skip disabled libraries.
            disabled = re.findall(
                r"\(\s*disabled\s*\)", lib, flags=re.IGNORECASE | re.VERBOSE
            )
            if disabled:
                continue

            # Skip non-KiCad libraries (primarily git repos).
            type_ = re.findall(
                r'(?:\(\s*type\s*) ("[^"]*?"|[^)]*?) (?:\s*\))',
                lib,
                flags=re.IGNORECASE | re.VERBOSE,
            )[0]
            if type_.lower() != "kicad":
                continue

            # Get the library directory and nickname.
            uri = re.findall(
                r'(?:\(\s*uri\s*) ("[^"]*?"|[^)]*?) (?:\s*\))',
                lib,
                flags=re.IGNORECASE | re.VERBOSE,
            )[0]
            nickname = re.findall(
                r'(?:\(\s*name\s*) ("[^"]*?"|[^)]*?) (?:\s*\))',
                lib,
                flags=re.IGNORECASE | re.VERBOSE,
            )[0]

            # Remove any quotes around the URI or nickname.
            uri = rmv_quotes(uri)
            nickname = rmv_quotes(nickname)

            # Expand variables and ~ in the URI.
            uri = os.path.expandvars(os.path.expanduser(uri))

            self[nickname] = uri


def kinet2pcb(netlist_filename, brd_filename=None):
    """Create a .kicad_pcb from a KiCad netlist file."""

    # Get the global and local fp-lib-table file URIs.
    paths = [get_global_fp_lib_table_dir(), "."]
    if "KIPRJMOD" in os.environ:
        paths.append(os.environ["KIPRJMOD"])
    fp_libs = LibURIs(*paths)

    # Create a blank KiCad PCB file based on the name of the netlist file.
    if brd_filename is None:
        base_filename = os.path.splitext(netlist_filename)[0]
        brd_filename = base_filename + ".kicad_pcb"
    brd = pcbnew.BOARD()

    # Parse the netlist.
    netlist = kinparse.parse_netlist(netlist_filename)

    # Add the components in the netlist to the PCB.
    for part in netlist.parts:
        # Get the library and footprint name for the part.
        fp_lib, fp_name = part.footprint.split(":")

        # Get the URI of the library directory.
        lib_uri = fp_libs[fp_lib]

        # Create a module from the footprint file.
        fp = pcbnew.FootprintLoad(lib_uri, fp_name)

        # Set the module parameters based on the part data.
        fp.SetParent(brd)
        fp.SetReference(part.ref)
        fp.SetValue(part.value)
        # fp.SetTimeStamp(part.sheetpath.tstamps)
        fp.SetPath(part.sheetpath.names)

        # Add the module to the PCB.
        brd.Add(fp)

    # Add the nets in the netlist to the PCB.
    cnct = brd.GetConnectivity()
    for net in netlist.nets:

        # Create a net with the current net name.
        pcb_net = pcbnew.NETINFO_ITEM(brd, net.name)

        # Add the net to the PCB.
        brd.Add(pcb_net)

        # Connect the part pins on the netlist net to the PCB net.
        for pin in net.pins:

            # Find the PCB module pad for the current part pin.
            module = brd.FindModuleByReference(pin.ref)
            pad = module.FindPadByName(pin.num)

            # Connect the pad to the PCB net.
            cnct.Add(pad)
            pad.SetNet(pcb_net)

    # Recalculate the PCB part and net data.
    brd.BuildListOfNets()
    cnct.RecalculateRatsnest()
    pcbnew.Refresh()

    # Save the PCB into the KiCad PCB file.
    pcbnew.SaveBoard(brd_filename, brd)


###############################################################################
# Command-line interface.
###############################################################################


def main():
    parser = argparse.ArgumentParser(
        description="""Convert KiCad netlist into a PCBNEW .kicad_pcb file."""
    )
    parser.add_argument(
        "--version", "-v", action="version", version="kinet2pcb " + __version__
    )
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        metavar="file",
        help="""Input file containing KiCad netlist.""",
    )
    parser.add_argument(
        "--output",
        "-o",
        nargs="?",
        type=str,
        metavar="file",
        help="""Output file for storing KiCad board.""",
    )
    parser.add_argument(
        "--overwrite",
        "-w",
        action="store_true",
        help="Allow overwriting of an existing board file.",
    )
    parser.add_argument(
        "--nobackup",
        "-nb",
        action="store_true",
        help="""Do *not* create backups before modifying files.
            (Default is to make backup files.)""",
    )
    parser.add_argument(
        "--debug",
        "-d",
        nargs="?",
        type=int,
        default=0,
        metavar="LEVEL",
        help="Print debugging info. (Larger LEVEL means more info.)",
    )

    args = parser.parse_args()

    logger = logging.getLogger("kinet2pcb")
    if args.debug is not None:
        log_level = logging.DEBUG + 1 - args.debug
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        logger.addHandler(handler)
        logger.setLevel(log_level)

    if args.output is None:
        args.output = os.path.splitext(args.input)[0] + ".kicad_pcb"

    if os.path.isfile(args.output):
        if not args.overwrite and args.nobackup:
            logger.critical(
                """File {} already exists! Use the --overwrite option to
                allow modifications to it or allow backups.""".format(
                    args.output
                )
            )
            sys.exit(1)
        if not args.nobackup:
            # Create a backup file.
            index = 1  # Start with this backup file suffix.
            while True:
                backup_file = args.output + ".{}.bak".format(index)
                if not os.path.isfile(backup_file):
                    # Found an unused backup file name, so make backup.
                    shutil.copy(args.output, backup_file)
                    break  # Backup done, so break out of loop.
                index += 1  # Else keep looking for an unused backup file name.

    kinet2pcb(args.input, args.output)


###############################################################################
# Main entrypoint.
###############################################################################
if __name__ == "__main__":
    main()
