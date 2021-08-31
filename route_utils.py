#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import pcbnew
from pcbnew import wxPoint


def get_layer_table(pcb):
    """Returns the layer table"""
    layertable = {}

    # Workaround for oldies
    if hasattr(pcbnew, "LAYER_ID_COUNT"):
        pcbnew.PCB_LAYER_ID_COUNT = pcbnew.LAYER_ID_COUNT

    numlayers = pcbnew.PCB_LAYER_ID_COUNT
    for i in range(numlayers):
        layertable[pcb.GetLayerName(i)] = i

    return layertable


def get_pad_by_name(module, name):
    """Get a pad from the given module according to the given name"""
    for pad in module.Pads():
        if pad.GetPadName() == name:
            return pad
    return None


def route_direct_points(pcb, p1, p2, net, layer):
    """Route 2 pads"""
    track = pcbnew.TRACK(pcb)
    pcb.Add(track)
    track.SetLayer(layer)
    track.SetNet(net)
    track.SetStart(p1)
    track.SetEnd(p2)


def route_2_pads(pcb, pad1, pad2, layer):
    """Simple route between 2 pads. If one ou two pads is SMD, use its side.
    The route goes from pad1 to pad2 in the direction."""
    locs = [pad.GetPosition() for pad in [pad1, pad2]]

    if pad1.GetNet().GetNetname() != pad2.GetNet().GetNetname():
        assert False, "NetName is different for both pads"

    middle_point = wxPoint((locs[0].x + locs[1].x)/2, locs[0].y)
    route_direct_points(pcb, locs[0], middle_point, pad1.GetNet(), layer)
    route_direct_points(pcb, middle_point, locs[1], pad2.GetNet(), layer)
