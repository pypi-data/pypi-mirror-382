class Constraint:
    def __init__(self, raw_data: dict):
        self.key = raw_data.get("key", "")
        self.values = raw_data.get("values", [])
