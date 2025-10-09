import pygame
from cogworks import Component

class TriggerCollider(Component):
    def __init__(self, shape="rect", width=0, height=0, radius=0, layer="Default", debug=False, layer_mask=None):
        """
        Initializes a trigger collider component.

        Args:
            shape (str): Type of collider, "rect" or "circle".
            width (int): Width of the rectangle collider (ignored for circle).
            height (int): Height of the rectangle collider (ignored for circle).
            radius (int): Radius of the circle collider (ignored for rect).
            layer (str): Layer name for collision filtering.
            debug (bool): If True, collider is drawn for debugging purposes.
            layer_mask (list[str] or None): List of layers this collider interacts with. None = all layers.
        """
        super().__init__()
        self.transform = None
        self.shape = shape
        self.width = width
        self.height = height
        self.radius = radius
        self.rect = None
        self.center = None
        self._colliding_with = set()
        self.layer = layer
        self.debug = debug
        self.layer_mask = layer_mask

    def start(self):
        self.transform = self.game_object.transform

        # Auto-size rectangle collider from Sprite if width/height not set
        if self.shape == "rect" and (self.width == 0 or self.height == 0):
            sprite = self.game_object.get_component("Sprite")
            if sprite:
                self.width = sprite.image.get_width()
                self.height = sprite.image.get_height()

        # Auto-size circle collider from Sprite if radius not set
        if self.shape == "circle" and self.radius == 0:
            sprite = self.game_object.get_component("Sprite")
            if sprite:
                self.radius = max(sprite.image.get_width(), sprite.image.get_height()) // 2

        self.update_shape()

        # Register with collision manager
        self.game_object.scene.trigger_collision_manager.register(self)

    def update_shape(self):
        x, y = self.transform.get_world_position()

        # Update rectangle or circle position
        if self.shape == "rect":
            self.rect = pygame.Rect(x - self.width // 2, y - self.height // 2, self.width, self.height)
            self.center = self.rect.center
        elif self.shape == "circle":
            self.center = (x, y)

    def update(self, dt):
        self.update_shape()


    def on_remove(self):
        self.game_object.scene.trigger_collision_manager.unregister(self)

    def intersects(self, other):
        """
        Checks if this collider intersects with another collider.

        Args:
            other (TriggerCollider): The other collider to check against.

        Returns:
            bool: True if colliders intersect, False otherwise.
        """
        # Layer mask filtering
        if self.layer_mask and other.layer not in self.layer_mask:
            return False
        if other.layer_mask and self.layer not in other.layer_mask:
            return False

        # Rectangle-rectangle collision
        if self.shape == "rect" and other.shape == "rect":
            return self.rect.colliderect(other.rect)
        # Circle-circle collision
        elif self.shape == "circle" and other.shape == "circle":
            dx = self.center[0] - other.center[0]
            dy = self.center[1] - other.center[1]
            return dx * dx + dy * dy < (self.radius + other.radius) ** 2
        # Circle-rectangle collision
        elif self.shape == "rect" and other.shape == "circle":
            return TriggerCollider._circle_rect_intersects(other, self)
        elif self.shape == "circle" and other.shape == "rect":
            return TriggerCollider._circle_rect_intersects(self, other)
        return False

    def render(self, surface):
        if not self.debug:
            return

        camera = self.game_object.scene.camera_component

        if self.shape == "rect":
            # Convert world coordinates to screen coordinates
            screen_x, screen_y = camera.world_to_screen(self.rect.x, self.rect.y)
            # Scale width and height by zoom
            screen_width = self.rect.width * camera.zoom
            screen_height = self.rect.height * camera.zoom
            screen_rect = pygame.Rect(screen_x, screen_y, screen_width, screen_height)
            pygame.draw.rect(surface, (255, 0, 0), screen_rect, 1)
        else:
            screen_center = camera.world_to_screen(*self.center)
            # Scale radius by zoom
            screen_radius = int(self.radius * camera.zoom)
            pygame.draw.circle(surface, (255, 0, 0), (int(screen_center[0]), int(screen_center[1])), screen_radius, 1)

    @staticmethod
    def _circle_rect_intersects(circle, rect_collider):
        """
        Checks collision between a circle and rectangle collider.

        Args:
            circle (TriggerCollider): Circle collider.
            rect_collider (TriggerCollider): Rectangle collider.

        Returns:
            bool: True if colliders intersect, False otherwise.
        """
        rect = rect_collider.rect
        cx, cy = circle.center
        closest_x = max(rect.left, min(cx, rect.right))
        closest_y = max(rect.top, min(cy, rect.bottom))
        dx = cx - closest_x
        dy = cy - closest_y
        return dx * dx + dy * dy < circle.radius * circle.radius
