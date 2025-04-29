import logging

import numpy as np

from . import settings
from . import controller_switch
from . import switch

class EndToEndController:
    """ End-to-end Controller: works over multiple switches """

    def __init__(self, switches=[switch]):
        self.period = 0
        self.switches = switches
        self.controllers = [controller_switch.SwitchController(_switch) for _switch in switches]

    def __repr__(self):
        return f"EndToEnd Controller: working on {self.switches} (period: {self.period})"

    def register_switch(self, switch):
        """ Add switch to control """
        self.switches.append(switch)
        self.controllers.append(controller_switch.SwitchController(switch))

    def control(self):
        """ Control function called by the framework. """
        logging.log(logging.INFO, "Executing %s", self)
        for controller in self.controllers:
            controller.control()
        self.period += 1
