#!/usr/bin/python3

# python controller/controller_circle.py
#   Insert P4 table entries to route traffic among hosts

from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI


class RoutingController:

    def __init__(self):
        self.topo = load_topo("topology.json")
        self.controllers = {}
        self.init()

    def init(self):
        self.connect_to_switches()
        self.reset_states()
        self.set_table_defaults()

    # Establishes a connection with the simple switch `thrift` server
    # using the `SimpleSwitchAPI` object
    # and saves those objects in the `self.controllers` dictionary.
    # This dictionary has the form of: `{'sw_name' : SimpleSwitchAPI()}`.
    def connect_to_switches(self):
        for p4switch in self.topo.get_p4switches():
            thrift_port = self.topo.get_thrift_port(p4switch)
            self.controllers[p4switch] = SimpleSwitchThriftAPI(thrift_port)

    # Iterates over the `self.controllers` object
    # and runs the `reset_state` function which empties the state
    # (registers, tables, etc) for every switch.
    def reset_states(self):
        [controller.reset_state() for controller in self.controllers.values()]

    # For each P4 switch, it sets the default action for `dmac` table
    def set_table_defaults(self):
        for controller in self.controllers.values():
            controller.table_set_default("dmac", "drop", [])

    # Create forwarding rules for the dmac table
    def route(self):
        # TODO: install routing rules for circle topology
        print("ERROR: routes not installed\n")

    def main(self):
        self.route()


if __name__ == "__main__":
    controller = RoutingController().main()
