
import re
from typing import List, NamedTuple

class HwVersion(NamedTuple):
    """
    Represents a hardware version triplet.
    See also hw_version.hpp and hw_version.dart.
    """
    product_line: int
    version: int
    variant: int

    @staticmethod
    def from_string(arg: str):
        """
        Constructs a HwVersion from a string of the form "4.4.58".
        """
        return HwVersion(*(int(i) for i in re.match(r'^([0-9]+)\.([0-9]+).([0-9]+)$', arg).groups()))

    @staticmethod
    def from_tuple(arg: List):
        """
        Constructs a HwVersion from a tuple or list of the form (4, 4, 58).
        """
        assert len(arg) == 3
        assert all([type(a) == int for a in arg])
        return HwVersion(*arg)

    @staticmethod
    def from_json(json):
        return HwVersion.from_tuple(json)

    @property
    def display_name(self):
        """
        Returns a display name such as "ODrive Pro" or "unknown device"
        corresponding to this board version.
        See also hw_version.hpp.
        """
        if self.product_line == 3:
            return f"CyberBeast Leopard v3.{self.version}"
        elif self.product_line == 4:
            return {
                0: "CyberBeast Lion v4.0",
                1: "CyberBeast Lion v4.1",
                2: "CyberBeast Lion v4.2",
                3: "CyberBeast Lion v4.3",
                4: "CyberBeast Lion",
            }.get(self.version, "unknown CyberBeast Lion v4")
        elif self.product_line == 5:
            return {
                0: "CyberBeast Leopard v5.0",
                1: "CyberBeast Leopard v5.1",
                2: "CyberBeast Leopard v5.2",
            }.get(self.version, "unknown CyberBeast Leopard v5")
        elif self.product_line == 6:
            return {
                0: "CyberBeast Lion v6.0",
                1: "CyberBeast Lion v6.1",
            }.get(self.version, "unknown CyberBeast Lion v6")
        elif self.product_line == 8:
            return {
                1: "CyberBeast Tiger v8.1",
            }.get(self.version, "unknown CyberBeast Tiger v8")
        else:
            return "unknown device"

    def to_json(self):
        return [self.product_line, self.version, self.variant]
