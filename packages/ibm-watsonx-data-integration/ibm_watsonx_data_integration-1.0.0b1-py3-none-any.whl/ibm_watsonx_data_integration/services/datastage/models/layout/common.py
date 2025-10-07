from abc import ABC, abstractmethod
from ibm_watsonx_data_integration.services.datastage.models.flow.dag import Node


class BoundingBox(ABC):
    def __init__(self, *, width: float = 0, height: float = 0, x: float = 0, y: float = 0):
        # POSITIONING IS ALWAYS RELATIVE TO PARENT
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.x_velocity = 0.0
        self.y_velocity = 0.0
        self.x_force = 0.0
        self.y_force = 0.0

    @abstractmethod
    def update_absolute_positions(self, parent_x: float, parent_y: float):
        pass

    def center_x(self):
        return self.x + self.width / 2

    def center_y(self):
        return self.y + self.height / 2

    def y_boundary_distance(self, other: "BoundingBox"):
        return min(
            abs(self.y - (other.y + other.height)),
            abs(other.y - (self.y + self.height)),
        )

    def get_x_from_center(self, center_x: float):
        return center_x - self.width / 2

    def get_y_from_center(self, center_y: float):
        return center_y - self.height / 2

    def add_force(self, x_force: float, y_force: float):
        self.x_force += x_force
        self.y_force += y_force

    def apply_forces(self):
        self.x_velocity += self.__clamp_magnitude(self.x_force, 60)
        self.y_velocity += self.__clamp_magnitude(self.y_force, 60)
        self.x_velocity *= 0.5
        self.y_velocity *= 0.5
        self.x_force = 0
        self.y_force = 0
        self.x += self.x_velocity
        self.y += self.y_velocity

    @staticmethod
    def __clamp_magnitude(val: float, magnitude: float):
        if val > 0:
            return min(val, magnitude)
        return max(val, -magnitude)


class NodeBoundingBox(BoundingBox):
    def __init__(self, node: Node, width: float = 0, height: float = 0):
        super().__init__(width=width, height=height)
        self.node = node

    def update_absolute_positions(self, parent_x: float, parent_y: float):
        self.node.metadata["x"] = round(parent_x + self.x)
        self.node.metadata["y"] = round(parent_y + self.y)
        self.node.metadata["width"] = round(self.width)
        self.node.metadata["height"] = round(self.height)


class GroupBoundingBox(BoundingBox):
    def __init__(self, *, width: float = 0, height: float = 0, x: float = 0, y: float = 0):
        super().__init__(width=width, height=height, x=x, y=y)
        self.children: list[BoundingBox] = []

    def center_within(self, other: BoundingBox):
        self.x = other.center_x() - self.width / 2
        self.y = other.center_y() - self.height / 2

    def update_absolute_positions(self, parent_x: float, parent_y: float):
        for child in self.children:
            child.update_absolute_positions(parent_x + self.x, parent_y + self.y)

    def arrange_children_vertically(self, spacing: float = 0):
        """Arrange children vertically with the specified spacing."""
        y = self.y
        for child in self.children:
            child.y = y
            y += child.height + spacing
        self.height = y - self.y

    def arrange_children_horizontally(self, spacing: float = 0):
        """Arrange children horizontally with the specified spacing."""
        x = self.x
        for child in self.children:
            child.x = x
            x += child.width + spacing
        self.width = x - self.x

    def round(self):
        self.x = round(self.x)
        self.y = round(self.y)
        self.width = round(self.width)
        self.height = round(self.height)
