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
