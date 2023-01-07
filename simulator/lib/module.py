class Module:
    """ A software switch module. """

    def __init__(self, cost, module_id=-1):
        self.cost = cost
        self.module_id = module_id

    def __repr__(self):
        return f"Module{self.get_id()}: cost {self.cost}"

    def get_id(self):
        """ Get Module ID """
        return self.module_id
