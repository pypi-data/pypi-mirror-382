from cogworks.component import Component
from cogworks.pygame_wrappers.window import Window


class Camera(Component):
    def __init__(self):
        super().__init__()
        self.offset_x = 0
        self.offset_y = 0
        self.zoom = 1.0  # 1.0 = normal, <1.0 = zoom out, >1.0 = zoom in

    def move(self, dx, dy):
        """Move the camera by a given delta."""
        self.offset_x += dx
        self.offset_y += dy

    def get_world_position_of_point(self, point: str = "center"):
        """
        Get the world position of a point on the camera view.

        Args:
            point (str): The point on the camera view. Options:
                'center', 'topleft', 'topright', 'topcenter',
                'bottomleft', 'bottomright', 'bottomcenter',
                'leftcenter', 'rightcenter'

        Returns:
            tuple: (world_x, world_y)
        """
        # Screen positions
        sw, sh = Window.get_instance().get_size()
        points = {
            "center": (sw / 2, sh / 2),
            "topleft": (0, 0),
            "topright": (sw, 0),
            "topcenter": (sw / 2, 0),
            "bottomleft": (0, sh),
            "bottomright": (sw, sh),
            "bottomcenter": (sw / 2, sh),
            "leftcenter": (0, sh / 2),
            "rightcenter": (sw, sh / 2),
        }

        if point not in points:
            raise ValueError(f"Invalid point '{point}' for camera. Valid options: {list(points.keys())}")

        screen_x, screen_y = points[point]
        # Convert screen coordinates to world coordinates
        world_x, world_y = self.screen_to_world(screen_x, screen_y)

        return world_x, world_y

    def set_zoom(self, zoom: float):
        """Set the camera zoom level."""
        if zoom <= 0:
            raise ValueError("Zoom must be greater than 0")
        self.zoom = zoom

    def world_to_screen(self, x, y):
        """Convert world coordinates to screen coordinates based on offset and zoom."""
        screen_x = (x - self.offset_x) * self.zoom
        screen_y = (y - self.offset_y) * self.zoom
        return screen_x, screen_y

    def screen_to_world(self, screen_x, screen_y):
        """Convert screen coordinates back to world coordinates considering zoom and offset."""
        world_x = screen_x / self.zoom + self.offset_x
        world_y = screen_y / self.zoom + self.offset_y
        return world_x, world_y

    def scale_length(self, length: float) -> float:
        """Scale a size/length according to the zoom level."""
        return length * self.zoom

    def center_on(self, x, y, screen_width, screen_height):
        """
        Center the camera on a world position, taking zoom into account.
        """
        self.offset_x = x - (screen_width / 2) / self.zoom
        self.offset_y = y - (screen_height / 2) / self.zoom

    def is_visible(self, x: float, y: float, width: float, height: float) -> bool:
        """
        Determine if a rectangle (sprite) is visible on the camera surface.

        Args:
            x (float): World X position of the sprite center.
            y (float): World Y position of the sprite center.
            width (float): Width of the sprite after scaling/zoom.
            height (float): Height of the sprite after scaling/zoom.
        Returns:
            bool: True if the sprite is (partially) visible on camera, False if completely outside.
        """
        top, bottom, left, right = self.get_bounds()

        tolerance = right

        obj_left = x - width / 2
        obj_right = x + width / 2
        obj_top = y - height / 2
        obj_bottom = y + height / 2

        return not (obj_right < left - tolerance or obj_left > right + tolerance or
                    obj_bottom < top - tolerance or obj_top > bottom + tolerance)


    def get_bounds(self):
        """
        Returns the current camera bounds in world coordinates as (left, top, right, bottom).
        """
        w, h = Window.get_instance().get_size()
        left = self.offset_x
        top = self.offset_y
        right = self.offset_x + w / self.zoom
        bottom = self.offset_y + h/ self.zoom
        return top, bottom, left, right
