#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import pcbnew
from pcbnew import wxPoint


def get_net_by_name(pcb, netname):
    """Returns the net of given netname"""
    nets = pcb.GetNetsByName()
    return nets.find(netname).value()[1]


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


def create_via(pcb, net, pos, toplayer="F.Cu", bottomlayer="B.Cu"):
    """Create a via"""
    layer_table = get_layer_table(pcb)

    via = pcbnew.VIA(pcb)
    pcb.Add(via)
    toplayer = layer_table[toplayer]
    bottomlayer = layer_table[bottomlayer]
    via.SetNet(net)
    nc = net.GetNetClass()
    via.SetWidth(nc.GetViaDiameter())
    via.SetLayerPair(toplayer, bottomlayer)
    via.SetViaType(pcbnew.VIA_THROUGH)
    via.SetPosition(pos)
    return via


def _get_width_from_net_class(pcb, net):
    """Returns track width form net's class"""
    net_classes = pcb.GetDesignSettings().m_NetClasses
    net_class = net_classes.Find(net.GetClassName())
    return net_class.GetTrackWidth()


def route_direct_points(pcb, p1, p2, net, layer):
    """Route 2 pads"""
    track = pcbnew.TRACK(pcb)
    pcb.Add(track)
    track.SetLayer(layer)
    track.SetNet(net)
    track.SetStart(p1)
    track.SetEnd(p2)
    track.SetWidth(_get_width_from_net_class(pcb, net))


def route_2_pads(pcb, pad1, pad2, layer):
    """Simple route between 2 pads. If one ou two pads is SMD, use its side.
    The route goes from pad1 to pad2 in the direction."""
    locs = [pad.GetPosition() for pad in [pad1, pad2]]

    if pad1.GetNet().GetNetname() != pad2.GetNet().GetNetname():
        assert False, "NetName is different for both pads"

    middle_point = wxPoint((locs[0].x + locs[1].x)/2, locs[0].y)
    route_direct_points(pcb, locs[0], middle_point, pad1.GetNet(), layer)
    route_direct_points(pcb, middle_point, locs[1], pad2.GetNet(), layer)
