#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import math
from skidl import Part, Net, lib_search_paths, generate_netlist, ERC, KICAD


PACKAGES_LIB = {"0603": "0603_1608Metric_Pad1.05x0.95mm_HandSolder"}
RSERIES = {3: [1.00, 2.20, 4.70],
           6: [1.00, 1.50, 2.20, 3.30, 4.70, 6.80],
          12: [1.00, 1.20, 1.50, 1.80, 2.20, 2.70, 3.30, 3.90, 4.70, 5.60,
               6.80, 8.20],
          24: [1.00, 1.10, 1.20, 1.30, 1.50, 1.60, 1.80, 2.00, 2.20, 2.40,
               2.70, 3.00, 3.30, 3.60, 3.90, 4.30, 4.70, 5.10, 5.60, 6.20,
               6.80, 7.50, 8.20, 9.10],
          48: [1.00, 1.05, 1.10, 1.15, 1.21, 1.27, 1.33, 1.40, 1.47, 1.54,
               1.62, 1.69, 1.78, 1.87, 1.96, 2.05, 2.15, 2.26, 2.37, 2.49,
               2.61, 2.74, 2.87, 3.01, 3.16, 3.32, 3.48, 3.65, 3.83, 4.02,
               4.22, 4.42, 4.64, 4.87, 5.11, 5.36, 5.62, 5.90, 6.19, 6.49,
               6.81, 7.15, 7.50, 7.87, 8.25, 8.66, 9.09, 9.53],
          96: [1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24,
               1.27, 1.30, 1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54, 1.58,
               1.62, 1.65, 1.69, 1.74, 1.78, 1.82, 1.87, 1.91, 1.96, 2.00,
               2.05, 2.10, 2.15, 2.21, 2.26, 2.32, 2.37, 2.43, 2.49, 2.55,
               2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09, 3.16, 3.24,
               3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12,
               4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23,
               5.36, 5.49, 5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65,
               6.81, 6.98, 7.15, 7.32, 7.50, 7.68, 7.87, 8.06, 8.25, 8.45,
               8.66, 8.87, 9.09, 9.31, 9.53, 9.76],
         192: [1.00, 1.01, 1.02, 1.04, 1.05, 1.06, 1.07, 1.09, 1.10, 1.11,
               1.13, 1.14, 1.15, 1.17, 1.18, 1.20, 1.21, 1.23, 1.24, 1.26,
               1.27, 1.29, 1.30, 1.32, 1.33, 1.35, 1.37, 1.38, 1.40, 1.42,
               1.43, 1.45, 1.47, 1.49, 1.50, 1.52, 1.54, 1.56, 1.58, 1.60,
               1.62, 1.64, 1.65, 1.67, 1.69, 1.72, 1.74, 1.76, 1.78, 1.80,
               1.82, 1.84, 1.87, 1.89, 1.91, 1.93, 1.96, 1.98, 2.00, 2.03,
               2.05, 2.08, 2.10, 2.13, 2.15, 2.18, 2.21, 2.23, 2.26, 2.29,
               2.32, 2.34, 2.37, 2.40, 2.43, 2.46, 2.49, 2.52, 2.55, 2.58,
               2.61, 2.64, 2.67, 2.71, 2.74, 2.77, 2.80, 2.84, 2.87, 2.91,
               2.94, 2.98, 3.01, 3.05, 3.09, 3.12, 3.16, 3.20, 3.24, 3.28,
               3.32, 3.36, 3.40, 3.44, 3.48, 3.52, 3.57, 3.61, 3.65, 3.70,
               3.74, 3.79, 3.83, 3.88, 3.92, 3.97, 4.02, 4.07, 4.12, 4.17,
               4.22, 4.27, 4.32, 4.37, 4.42, 4.48, 4.53, 4.59, 4.64, 4.70,
               4.75, 4.81, 4.87, 4.93, 4.99, 5.05, 5.11, 5.17, 5.23, 5.30,
               5.36, 5.42, 5.49, 5.56, 5.62, 5.69, 5.76, 5.83, 5.90, 5.97,
               6.04, 6.12, 6.19, 6.26, 6.34, 6.42, 6.49, 6.57, 6.65, 6.73,
               6.81, 6.90, 6.98, 7.06, 7.15, 7.23, 7.32, 7.41, 7.50, 7.59,
               7.68, 7.77, 7.87, 7.96, 8.06, 8.16, 8.25, 8.35, 8.45, 8.56,
               8.66, 8.76, 8.87, 8.98, 9.09, 9.20, 9.31, 9.42, 9.53, 9.65,
               9.76, 9.88]}


def dop_part(symbol, module, fields=None):
    """Returns a part from the Doppelganger library"""
    if fields is None:
        fields = {}
    p = Part(lib="Doppelganger.lib", name=symbol,
             footprint=F"Doppelganger:{module}")

    # Merges the fields part
    tmp = {**fields, **p.fields}
    p.fields = tmp
    return p


def get_res_from_std(r, serie=12):
    """Retreives the nearest value of the given resistor series"""
    decade = 10**(int(math.log10(r)))
    r_d = r/decade
    above = decade*min(s for s in RSERIES[serie] if s >= r_d)
    below = decade*max(s for s in RSERIES[serie] if s <= r_d)
    if (above-r)/r <= (r-below)/r:
        return above
    return below


# Resistor, Capacitor & Inductor Basics

def get_res(value, package, fields=None):
    """Returns a resistor with default package"""
    if fields is None:
        fields = {}
    fields["value"] = str(value)
    return dop_part("R", package+"R", fields=fields)


def get_capa(value, package, fields=None):
    """Returns a capacitor with default package"""
    if fields is None:
        fields = {}
    package_str = package + "C"
    fields["value"] = str(value)
    return dop_part("C", package+"C", fields=fields)

def get_inductance(value, package, fields=None):
    """Returns an inductance with default package"""
    if fields is None:
        fields = {}
    package_str = package + "L"
    fields["value"] = str(value)
    return dop_part("L", package+"L", fields=fields)

def pull_updown(power, signals, value, package="0603", fields=None):
    """Insert a PullUp or PullDown on the given signal"""
    if fields is None:
        fields = {}
    if not isinstance(signals, list):
        signals = [signals]
    for signal in signals:
        r = get_res(value, package, fields=fields)
        power & r & signal


def bypass_cap(net1, net2, values, package="0603", fields=None, descr=None):
    """Adds one or more bypass capacitors"""
    if fields is None:
        fields = {}
    if not isinstance(values, list):
        values = [values]
    if descr is not None:
        fields["bypass_dscr"] = descr
    for v in values:
        c = get_capa(v, package, fields=fields)
        net1 += c[1]
        net2 += c[2]


def power_indicator(nets, voltage=5, res_pkg="0603", color="green",
                    led_vf=2.4, led_if=20E-3):
    """Insert a resistor and an LED in serie between nets.
    nets[0] --> diode Anode side
    nets[1] --> diode Cathode side
    Resistor is computed in E12 serie"""
    ideal_resistor_value = float(voltage-led_vf)/led_if
    res_value = get_res_from_std(ideal_resistor_value)
    res = get_res(str(res_value), "0603")
    led = dop_part("LED", "0805LED")
    nets[0] & res & led["A,K"] & nets[1]


class NotEnoughGate(Exception):
    """Just a specific Exception class to help with multigate chips"""


class ICHelper():
    """Just an abstract class to simplify ic helper"""

    NAME = "UNKNOWN"

    def __init__(self, vcc, gnd, bypass_capacitor, c_fields=None):
        """Init the brand new instance
        If bypass is not None, bypass_cap must be a tuple as follows:
        (value, package)"""
        self.vcc, self.gnd = vcc, gnd
        self.part["Vcc"] += vcc
        self.part["GND"] += gnd

        # Adds bypass if needed
        if c_fields is None:
            c_fields = {}
        if bypass_capacitor is not None:
            bypass_cap(vcc, gnd, *bypass_capacitor, fields=c_fields,
                       descr=self.NAME)

        self.used_index = [False] * self.CELL_COUNT
        self.auto_inc_current = 0

    def get_next_index(self, req_index):
        """If index is None Returns the next index in the chip"""
        if req_index is None:
            if self.auto_inc_current == self.CELL_COUNT:
                raise NotEnoughGate("Not any gate left")
            req_index = self.auto_inc_current
            self.auto_inc_current += 1
        return req_index


# LVC32 helper
class LVC32(ICHelper):
    """LVC32 helper"""

    CELL_COUNT = 4
    MAPPING = [(1, 2, 3), (4, 5, 6), (9, 10, 8), (12, 13, 11)]
    NAME = "LVC32"

    def __init__(self, vcc, gnd, bypass_cap=None, c_fields=None):
        """Init the brand new instance."""
        if c_fields is None:
            c_fields = {}
        self.part = dop_part("74LVC32", "TSSOP14",
                         fields={"Reference": "74LVC32APW,118",
                                 "Descr": "Quad 2-input OR",
                                 "CC": "2438891",
                                 "JLCC": "C6087",
                                 "JLROT": "270"})
        super().__init__(vcc, gnd, bypass_cap, c_fields=c_fields)

    def add(self, in1, in2, out=None, index=None):
        """Sets one of the xor cell. If index is None, autoincrement is used"""
        index = self.get_next_index(index)
        self.used_index[index] = True
        m = self.MAPPING[index]
        self.part[m[0]] += in1
        self.part[m[1]] += in2

        if out is None:
            out = Net("{0}_or_{1}".format(in1.name, in2.name))
        self.part[m[2]] += out
        return out

    def fill_unused(self):
        """Sets GND on unused inputs and NC on used outputs"""
        for i in range(self.CELL_COUNT):
            if not self.used_index[i]:
                m = self.MAPPING[i]
                self.part[m[0]] += self.gnd
                self.part[m[1]] += self.gnd
                self.part[m[2]] += NC


# LVC07 Helper
class LVC07(ICHelper):
    """LVC07 helper"""

    CELL_COUNT = 6
    NAME = "LVC07"

    def __init__(self, vcc, gnd, bypass_cap=None, c_fields=None):
        """Init the brand new instance.
        If bypass is not None, bypass_cap must be a tuple as follows:
        (value, package)"""
        if c_fields is None:
            c_fields = {}
        self.part = dop_part("74LVC07", "TSSOP14",
                             fields={"Reference": "74LVC07APW,118",
                                     "Descr": "Hex Open Collector buffer",
                                     "CC": "2438795",
                                     "JLCC": "C6051",
                                     "JLROT": "270"})
        super().__init__(vcc, gnd, bypass_cap, c_fields=c_fields)

    def add(self, inp, out=None, index=None):
        """Sets one of the open collector buffer."""
        index = self.get_next_index(index)
        self.used_index[index] = True
        try:
            self.part[F"A{index}"] += inp
        except:
            print("Oups: index = {0}".format(index))
            assert False

        if out is None:
            out = Net("Buff_OC_{0}".format(inp.name))
        self.part[F"O{index}"] += out
        return out

    def fill_unused(self, net=None):
        """Sets GND on unused inputs and NC on used outputs"""
        for i in range(self.CELL_COUNT):
            if not self.used_index[i]:
                if net is None:
                    self.part[F"A{i}"] += self.gnd
                else:
                    self.part[F"A{i}"] += net
                self.part[F"O{i}"] += NC


# HC07 Helper
class HC4066(ICHelper):
    """HC4066 helper"""

    CELL_COUNT = 4
    NAME = "HC4066"

    def __init__(self, vcc, gnd, bypass_cap=None, c_fields=None):
        """Init the brand new instance.
        If bypass is not None, bypass_cap must be a tuple as follows:
        (value, package)"""
        if c_fields is None:
            c_fields = {}
        self.part = dop_part("74HC4066", "TSSOP14",
                             fields={"Ref": "74HC4066PW,118",
                                     "Descr": "Quad bilateral switches ",
                                     "CC": "2463675",
                                     "JLCC": "C5350",
                                     "JLROT": "270"})
        super().__init__(vcc, gnd, bypass_cap, c_fields=c_fields)

    def add(self, e, y, z, index=None):
        """Sets one of the open collector buffer."""
        index = self.get_next_index(index)
        self.used_index[index] = True
        real_index = index + 1
        try:
            self.part[F"{real_index}E"] += e
        except:
            print(F"Oups: index = {real_index}")
            assert False

        self.part[F"{real_index}Y"] += y
        self.part[F"{real_index}Z"] += z

    def fill_unused(self, net=None):
        """Sets GND on unused inputs and NC on used outputs"""
        for i in range(self.CELL_COUNT):
            if not self.used_index[i]:
                real_index = i + 1
                if net is None:
                    self.part[F"{real_index}E"] += self.gnd
                else:
                    self.part[F"{real_index}E"] += net
                self.part[F"{real_index}Y"] += NC
                self.part[F"{real_index}Z"] += NC


class ICSpan():
    """Span single gate over multi gate chips"""
    def __init__(self, chip_class, vcc, gnd, bypass_cap=None):
        """Init the brand new instance"""
        self.vcc, self.gnd = vcc, gnd
        self.bypass_capacitor = bypass_cap

        self.chip_class = chip_class
        self.parts = []
        self.add_chip()

    def add_chip(self):
        """Adds a new chip"""
        part = self.chip_class(self.vcc, self.gnd, self.bypass_capacitor)
        self.parts.append(part)
        self.current_part = part

    def get_constructor(self):
        """Return a function that executes the __add_gate from a pseudo
        static way)"""

        def constructor(*args, **kargs):
            """Just a pseudo static function"""
            return self.__add_gate(*args, **kargs)

        return constructor

    def __add_gate(self, *args, **kwargs):
        """Adds an individual gate to the set of chips"""
        try:
            return self.current_part.add(*args, **kwargs)
        except NotEnoughGate as e:
            # Adds a new chip and retry
            self.add_chip()
            return self.current_part.add(*args, **kwargs)

    def fill_unused(self):
        """Fills the unused gates of the last chip"""
        self.current_part.fill_unused()


def unit_map_on_he10(sigs):
    """Maps all the given sigs on a HE10_24"""
    conn = dop_part("HE10-12X2", "HE-10_2x12_2.54")
    for i, sig in enumerate(sigs):
        conn[i+1] += sig
    for i in range(len(sigs), 24):
        conn[i+1] += NC
    return conn


def run_unit(unit_to_test):
    """Just a simple helper for launching unit tests"""
    lib_search_paths[KICAD].append(os.environ["KIPRJLIB"])
    unit_to_test()
    ERC()
    generate_netlist()
