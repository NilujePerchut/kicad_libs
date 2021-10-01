#!/usr/bin/env python3

import os
import csv
import argparse


class Component():
    """Just an abstract of a PCB component"""

    def __init__(self, designator):
        """Just init the brand new instance"""
        self.designator = designator

    def __str__(self):
        """Just export the component in a readable form"""
        ret = self.designator + "\n"
        ret += "\tRef: {0}\n".format(self.ref)
        ret += "\tJLCPCB_CC: {0}\n".format(self.jlcpcb_cc)
        attrs = ("val", "package", "position_x", "position_y", "rotation",
                 "pcb_side")
        for attr in attrs:
            if hasattr(self, attr):
                ret += "\t {0}: {1}\n".format(attr, getattr(self, attr))

        return ret

    def __repr__(self):
        return str(self)


def get_components_from_xml(xml_path):
    components = []
    inside_component = False
    current_component = None
    for line in open(xml_path).readlines():
        line = line.strip()
        if not inside_component:
            if "<comp ref" in line:
                inside_component = True
                designator = line.split('"')[1]
                current_component = Component(designator)
        else:
            if "</comp>" in line:
                if not hasattr(current_component, "jlcpcb_rotation_offset"):
                    current_component.jlcpcb_rotation_offset = 0
                if hasattr(current_component, "jlcpcb_cc"):
                    components.append(current_component)
                inside_component = False
            elif "field (name F1)" in line:
                current_component.ref = line.split()[-1][:-1]
            elif "field (name Ref)" in line:
                # Same (hopefully) than F1
                current_component.ref = line.split()[-1][:-1]
            elif "field (name JLCC)" in line:
                current_component.jlcpcb_cc = line.split()[-1][:-1]
            elif "field (name JLROT)" in line:
                offset = float(line.split()[-1][:-1])
                current_component.jlcpcb_rotation_offset = offset
    return components


def parse_board_pos(pos_content, sides):
    """Just parse the pos content"""
    kicad_positions = csv.reader(pos_content)
    return {els[0]: els[1:] for els in kicad_positions
            if els[0] != "Ref"
            if els[-1] in sides}


def create_cpl(components, out_dir, project_name):
    """Generates the JLCPCB CPL file"""
    csv_path = os.path.join(out_dir, project_name + "_CPL_" + ".csv")
    with open(csv_path, "w", newline='') as csvfile:
        header = ["Designator", "Mid X", "Mid Y", "Layer", "Rotation"]
        cpl_writer = csv.writer(csvfile, delimiter=",")
        cpl_writer.writerow(header)
        for component in components:
            cpl_writer.writerow([component.designator,
                                 component.position_x, component.position_y,
                                 component.pcb_side,
                                 float(component.rotation) +\
                                 component.jlcpcb_rotation_offset])

def create_bom(components, out_dir, project_name):
    """Generates the JLCPCB BOM file"""
    csv_path = os.path.join(out_dir, project_name + "_BOM_" + ".csv")
    header = ["Designator", "Comment", "Footprint", "LCSC part#"]
    with open(csv_path, "w", newline="") as csvfile:
        bom_writer = csv.writer(csvfile, delimiter=",")
        bom_writer.writerow(header)
        for component in components:
            bom_writer.writerow([component.designator,
                                 component.val,
                                 component.package,
                                 component.jlcpcb_cc])

def jlcpcb_build(xml_path, pos_file, project_name, out_dir, sides=None):
    """Generates JLCPCB BOM and CPL"""
    if sides is None:
        sides = ["top", "bottom"]
    components = get_components_from_xml(xml_path)
    positions = parse_board_pos(pos_file, sides)
    for component in components:
        attrs = ("val", "package", "position_x", "position_y", "rotation",
                 "pcb_side")
        for i, val in enumerate(positions[component.designator]):
            setattr(component, attrs[i], val)

    create_cpl(components, out_dir, project_name)
    create_bom(components, out_dir, project_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    side_group = parser.add_mutually_exclusive_group()
    side_group.add_argument("--top_only", action="store_true",
                            help="Process only top side")
    side_group.add_argument("--bottom_only", action="store_true",
                            help="Process only top side")
    parser.add_argument("-o", default=None, help="output directory")
    parser.add_argument("project_name", help="project name")
    parser.add_argument("xml", help="skidl generated board xml file")
    parser.add_argument("pos", type=argparse.FileType("r"),
                        help="kicad generated board pos file")

    args = parser.parse_args()

    # Layer choice
    if args.top_only:
        sides = ["top"]
    elif args.bottom_only:
        sides = ["bottom"]
    else:
        sides = ["top", "bottom"]

    # Output dir: if nothing given, use current directory
    if args.o is None:
        out_dir = os.path.dirname(os.path.realpath(__file__))
    else:
        out_dir = args.o

    jlcpcb_build(args.xml, args.pos, args.project_name, out_dir, sides)
