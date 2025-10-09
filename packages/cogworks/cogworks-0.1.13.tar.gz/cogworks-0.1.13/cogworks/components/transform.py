import math

import pygame

from cogworks.component import Component

class Transform(Component):
    """
    Transform component to track position, rotation, and scale of a GameObject.

    Supports both local (relative to parent) and world (absolute) transforms.

    Attributes:
        local_x (float): Local X position relative to parent.
        local_y (float): Local Y position relative to parent.
        local_rotation (float): Local rotation in degrees relative to parent.
        local_scale_x (float): Local scale along X axis.
        local_scale_y (float): Local scale along Y axis.
    """

    def __init__(self, x=0, y=0, rotation=0, scale_x=1, scale_y=1, debug=False, z_index=1):
        """
        Initialise a new Transform component.

        Args:
            x (float, optional): Initial local X position relative to parent. Defaults to 0.
            y (float, optional): Initial local Y position relative to parent. Defaults to 0.
            rotation (float, optional): Initial local rotation in degrees. Defaults to 0.
            scale_x (float, optional): Initial local scale along the X axis. Defaults to 1.
            scale_y (float, optional): Initial local scale along the Y axis. If not provided,
                it will match scale_x. Defaults to 1.
            debug (bool, optional): Whether to enable debug rendering for this Transform. Defaults to False.
            z_index (int, optional): Render order index (higher values render on top). Defaults to 1.
        """
        super().__init__()
        self.start_x = x
        self.start_y = y
        self.local_x = x
        self.local_y = y
        self.start_rotation = rotation
        self.local_rotation = rotation
        self.start_scale_x = scale_x
        self.local_scale_x = scale_x
        self.start_scale_y = scale_y
        self.local_scale_y = scale_y
        self.debug = debug
        self.z_index = z_index
        self.world_bound_x = math.inf
        self.world_bound_y = math.inf

    def start(self):
        self.local_x = self.start_x
        self.local_y = self.start_y
        self.local_rotation = self.start_rotation
        self.local_scale_x = self.start_scale_x
        self.local_scale_y = self.start_scale_y
        self.world_bound_x = self.game_object.scene.engine.world_bound_x
        self.world_bound_y = self.game_object.scene.engine.world_bound_y

    # --- Local setters ---
    def set_local_position(self, x, y):
        """
        Set the local position of the Transform relative to parent.

        Args:
            x (float): Local X position.
            y (float): Local Y position.
        """
        self.local_x = x
        self.local_y = y

    def get_local_position(self):
        """
        Get the local position of the Transform relative to parent.

        Returns:
            tuple: (x, y) local position.
        """
        return self.local_x, self.local_y

    def set_local_rotation(self, degrees):
        """
        Set the local rotation of the Transform relative to parent.

        Args:
            degrees (float): Rotation angle in degrees.
        """
        self.local_rotation = degrees % 360

    def get_local_rotation(self, radians=True):
        """
        Get the local rotation of the Transform.

        Args:
            radians (bool): If True, returns rotation in radians; else in degrees.

        Returns:
            float: Rotation angle.
        """
        return math.radians(self.local_rotation) if radians else self.local_rotation

    def set_local_scale(self, sx, sy=None):
        """
        Set the local scale of the Transform relative to parent.

        Args:
            sx (float): Scale along X axis.
            sy (float, optional): Scale along Y axis. If None, Y scale = X scale.
        """
        local_scale_x = sx
        local_scale_y = sy if sy is not None else sx
        self.local_scale_x = local_scale_x
        self.local_scale_y = local_scale_y

    def get_local_scale(self):
        """
        Get the local scale of the Transform.

        Returns:
            tuple: (scale_x, scale_y)
        """
        return self.local_scale_x, self.local_scale_y

    # --- World setters ---
    def set_world_position(self, x, y):
        """
        Set the world position of the Transform.

        Converts world coordinates to local if the GameObject has a parent.

        Args:
            x (float): World X position.
            y (float): World Y position.
        """
        if self.game_object and self.game_object.parent:
            px, py = self.game_object.parent.transform.get_world_position()
            self.local_x = x - px
            self.local_y = y - py
        else:
            self.local_x = x
            self.local_y = y

    def set_world_rotation(self, degrees):
        """
        Set the world rotation of the Transform.

        Converts world rotation to local rotation if the GameObject has a parent.

        Args:
            degrees (float): Rotation angle in degrees.
        """
        if self.game_object and self.game_object.parent:
            parent_rotation = self.game_object.parent.transform.get_world_rotation(radians=False)
            self.local_rotation = (degrees - parent_rotation) % 360
        else:
            self.local_rotation = degrees % 360

    def set_world_scale(self, sx, sy=None):
        """
        Set the world scale of the Transform.

        Converts world scale to local scale if the GameObject has a parent.

        Args:
            sx (float): Scale along X axis.
            sy (float, optional): Scale along Y axis. If None, Y scale = X scale.
        """
        if self.game_object and self.game_object.parent:
            psx, psy = self.game_object.parent.transform.get_world_scale()
            self.local_scale_x = sx / psx
            self.local_scale_y = (sy / psy) if sy is not None else (sx / psx)
        else:
            self.local_scale_x = sx
            self.local_scale_y = sy if sy is not None else sx

    def rotate(self, delta_degrees):
        """
        Increment the local rotation by delta_degrees.

        Args:
            delta_degrees (float): Amount to rotate in degrees.
        """
        self.local_rotation = (self.local_rotation + delta_degrees) % 360

    # --- World getters ---
    def get_world_position(self):
        """
        Get the world position of the Transform.

        Returns:
            tuple: (x, y) position in world space.
        """
        if self.game_object and self.game_object.parent:
            px, py = self.game_object.parent.transform.get_world_position()
            return px + self.local_x, py + self.local_y
        return self.local_x, self.local_y

    def get_world_rotation(self, radians=True):
        """
        Get the world rotation of the Transform.

        Returns:
            float: Rotation angle in radians or degrees.
        """
        angle = self.local_rotation
        if self.game_object and self.game_object.parent:
            angle += self.game_object.parent.transform.get_world_rotation(radians=False)
        return math.radians(angle) if radians else angle

    def get_world_scale(self):
        """
        Get the world scale of the Transform.

        Returns:
            tuple: (scale_x, scale_y)
        """
        sx, sy = self.local_scale_x, self.local_scale_y
        if self.game_object and self.game_object.parent:
            psx, psy = self.game_object.parent.transform.get_world_scale()
            return sx * psx, sy * psy
        return sx, sy

    # --- Direction getters ---
    def get_forward(self):
        """
        Get the forward direction vector based on world rotation.

        Returns:
            tuple: (x, y) unit vector pointing forward.
        """
        angle = self.get_world_rotation(radians=True)
        return math.cos(angle), math.sin(angle)

    def get_back(self):
        """
        Get the backward direction vector (opposite of forward).

        Returns:
            tuple: (x, y) unit vector pointing backward.
        """
        fx, fy = self.get_forward()
        return -fx, -fy

    def get_right(self):
        """
        Get the right direction vector based on world rotation.

        Returns:
            tuple: (x, y) unit vector pointing right.
        """
        angle = self.get_world_rotation(radians=True)
        # 90° clockwise from forward
        return math.cos(angle + math.pi / 2), math.sin(angle + math.pi / 2)

    def get_left(self):
        """
        Get the left direction vector (opposite of right).

        Returns:
            tuple: (x, y) unit vector pointing left.
        """
        rx, ry = self.get_right()
        return -rx, -ry

    def update(self, dt: float) -> None:
        self.in_start = False
        x, y = self.get_world_position()

        out_of_bounds = (
                x < -self.world_bound_x or x > self.world_bound_x or
                y < -self.world_bound_y or y > self.world_bound_y
        )

        if out_of_bounds:
            self.game_object.destroy()

    # --- Rendering ---
    def render(self, surface):
        """
        Render debug information if debug is enabled.
        """
        if not self.debug:
            return

        camera = self.game_object.scene.camera_component

        # Get world transform data
        x, y = camera.world_to_screen(*self.get_world_position())
        fx, fy = self.get_forward()
        rx, ry = self.get_right()

        # Scale vectors for visibility in debug drawing
        length = 30
        forward_end = (x + fx * length, y + fy * length)
        right_end = (x + rx * length, y + ry * length)

        # Draw position point
        pygame.draw.circle(surface, (255, 255, 0), (int(x), int(y)), 5)  # Yellow dot

        # Draw forward direction
        pygame.draw.line(surface, (0, 255, 0), (x, y), forward_end, 2)

        # Draw right direction
        pygame.draw.line(surface, (255, 0, 0), (x, y), right_end, 2)