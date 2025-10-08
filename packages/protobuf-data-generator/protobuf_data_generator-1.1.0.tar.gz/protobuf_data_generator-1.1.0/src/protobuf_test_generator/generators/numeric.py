from random import randint, choice


class NumericGenerator:
    def __init__(self, constraints=None):
        self.constraints = constraints or {}

    def generate_valid(self, field_name):
        if field_name in self.constraints:
            constraints = self.constraints[field_name]
            return self._generate_valid_value(constraints)
        return self._generate_default_value()

    def generate_invalid(self, field_name):
        if field_name in self.constraints:
            constraints = self.constraints[field_name]
            return self._generate_invalid_value(constraints)
        return self._generate_default_value()

    def _generate_valid_value(self, constraints):
        if "min" in constraints and "max" in constraints:
            return randint(constraints["min"], constraints["max"])
        elif "min" in constraints:
            return randint(constraints["min"], constraints["min"] + 10)
        elif "max" in constraints:
            return randint(constraints["max"] - 10, constraints["max"])
        return randint(0, 100)

    def _generate_invalid_value(self, constraints):
        if "min" in constraints:
            return randint(constraints["min"] + 1, constraints["min"] + 10)
        elif "max" in constraints:
            return randint(constraints["max"] - 10, constraints["max"] - 1)
        return choice([-1, -100, 1000])  # Arbitrary invalid values

    def _generate_default_value(self):
        return 0  # Default value if no constraints are provided
