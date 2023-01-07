import logging

import numpy as np

from . import settings


class EndToEndController:
    """ End-to-end Controller: works over multiple switches """

    def __init__(self, switches=None):
        self.period = 0
        self.switches = switches

    def __repr__(self):
        return f"EndToEnd Controller: working on {self.switches} (period: {self.period})"

    def register_switch(self, switch):
        """ Add switch to control """
        self.switches.append(switch)

    def control(self):
        """ Control function called by the framework. """
        logging.log(logging.INFO, "Executing %s", self)

        # increase period counter
        self.period += 1
