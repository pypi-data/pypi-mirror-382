from .constraint import Constraint


class FlagState:
    def __init__(self, raw_data: dict):
        self.is_on = raw_data.get("isOn", False)
        constraints = raw_data.get("constraints", [])
        self.constraints = [Constraint(c)
                            for c in constraints] if constraints else []
