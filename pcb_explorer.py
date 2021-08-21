#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from pcbnew import LoadBoard, wxPoint
from yaml import load, dump, Loader


def get_all_designators(pcb):
    """Returns a list of all designators"""
    return [module.GetReference() for module in pcb.GetModules()]


def _get_module_from_reference(pcb, reference):
    """Return the module of the given reference"""
    for module in pcb.GetModules():
        if module.GetReference() == reference:
            return module
    return None


def export_placement(pcb, designators=None):
    """Export placement (side, orientation, position) for given designators"""
    if designators is None:
        designators = get_all_designators(pcb)
    ret = {}
    for designator in designators:
        module = _get_module_from_reference(pcb, designator)
        pos = module.GetPosition()
        ret[designator] = {"flipped": module.IsFlipped(),
                           "orientation": module.GetOrientation(),
                           "position": [pos.x, pos.y]}
    return ret


def apply_placement(pcb, placement):
    """Apply placement"""
    if placement is None:
        return
    for designator, params in placement.items():
        module = _get_module_from_reference(pcb, designator)
        if params["flipped"] and not(module.IsFlipped()):
            module.Flip(module.GetCenter())
        module.SetOrientation(params["orientation"])
        pos = wxPoint(*params["position"])
        module.SetPosition(pos)


if __name__ == "__main__":
    main_parser = argparse.ArgumentParser("PCB Explorer")
    sub_parser = main_parser.add_subparsers(dest="command")

    # Dump command
    dump_parser = sub_parser.add_parser("dump")
    dump_parser.add_argument("pcb", help="The PCB")

    # Apply command
    apply_parser = sub_parser.add_parser("apply")
    apply_parser.add_argument("src_pcb", help="The initial PCB")
    apply_parser.add_argument("placement", help="The placement file")
    apply_parser.add_argument("dst_pcb", help="The final PCB")

    args = main_parser.parse_args()

    if args.command == "dump":
        the_pcb = LoadBoard(args.pcb)
        the_placement = export_placement(the_pcb)
        print(dump(the_placement))
    elif args.command == "apply":
        the_pcb = LoadBoard(args.src_pcb)
        the_placement = load(open(args.placement).read(), Loader=Loader)
        apply_placement(the_pcb, the_placement)
        the_pcb.Save(args.dst_pcb)
