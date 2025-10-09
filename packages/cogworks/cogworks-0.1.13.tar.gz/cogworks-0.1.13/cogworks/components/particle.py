import random

from cogworks import Component
from cogworks.components.sprite import Sprite


class Particle(Component):
    def __init__(
        self,
        sprite_path: str | None = None,
        min_x: float = 0,
        max_x: float = 50,
        min_y: float = 0,
        max_y: float = 50,
        min_rotation: float = -180,
        max_rotation: float = 180,
        min_scale: float = 0.4,
        max_scale: float = 0.8,
        move_speed: float = 500,
        gravity: float = 500,
        min_direction: tuple[float, float] = (-1, -1),
        max_direction: tuple[float, float] = (1, 1),
        lifetime: float = 1.5,
        end_scale: float | None = None,
        scale_with_lifetime: bool = False,
        rotate_over_lifetime: bool = False,
        fade_over_lifetime: bool = False,
    ):
        super().__init__()
        self.sprite_path = sprite_path
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.min_rotation = min_rotation
        self.max_rotation = max_rotation
        self.min_scale = min_scale
        self.max_scale = max_scale
        self.move_speed = move_speed
        self.gravity = gravity
        self.min_direction = min_direction
        self.max_direction = max_direction
        self.lifetime = lifetime
        self.end_scale = end_scale if end_scale is not None else max_scale
        self.scale_with_lifetime = scale_with_lifetime
        self.rotate_over_lifetime = rotate_over_lifetime
        self.fade_over_lifetime = fade_over_lifetime

        self.age = 0.0
        self.initial_scale = 1.0
        self.initial_rotation = 0.0
        self.initial_alpha = 255

        self.sprite = None

        # Movement state
        self.direction: list[float] = [0.0, 0.0]
        self.velocity: list[float] = [0.0, 0.0]

    def start(self) -> None:
        # Randomise initial position
        random_x = random.uniform(self.min_x, self.max_x)
        random_y = random.uniform(self.min_y, self.max_y)
        self.game_object.transform.set_local_position(random_x, random_y)

        # Randomise initial rotation
        random_rotation = random.uniform(self.min_rotation, self.max_rotation)
        self.initial_rotation = random_rotation
        self.game_object.transform.set_local_rotation(random_rotation)

        # Randomise initial scale
        random_scale = random.uniform(self.min_scale, self.max_scale)
        self.initial_scale = random_scale
        self.game_object.transform.set_local_scale(random_scale, random_scale)

        # Randomise initial direction and velocity
        random_x_dir = random.uniform(self.min_direction[0], self.max_direction[0])
        random_y_dir = random.uniform(self.min_direction[1], self.max_direction[1])
        self.direction = [random_x_dir, random_y_dir]
        self.velocity = [
            self.direction[0] * self.move_speed,
            self.direction[1] * self.move_speed,
        ]

        # Add sprite if provided
        if self.sprite_path:
            self.sprite = Sprite(self.sprite_path)
            self.initial_alpha = self.sprite.alpha
            self.game_object.add_component(self.sprite)

    def update(self, dt: float) -> None:
        self.age += dt
        t = min(self.age / self.lifetime, 1.0)  # progress ratio (0 → 1)

        # Destroy particle after lifetime
        if self.age >= self.lifetime:
            self.game_object.destroy()
            return

        # Apply gravity
        self.velocity[1] += self.gravity * dt

        # Update position
        pos_x, pos_y = self.game_object.transform.get_local_position()
        new_x = pos_x + self.velocity[0] * dt
        new_y = pos_y + self.velocity[1] * dt
        self.game_object.transform.set_local_position(new_x, new_y)

        # Update scale over lifetime
        if self.scale_with_lifetime:
            new_scale = self.initial_scale + (self.end_scale - self.initial_scale) * t
            self.game_object.transform.set_local_scale(new_scale, new_scale)

        # Rotate over lifetime
        if self.rotate_over_lifetime:
            new_rotation = self.initial_rotation + 360 * t  # full rotation over lifetime
            self.game_object.transform.set_local_rotation(new_rotation)

        # Fade over lifetime
        if self.fade_over_lifetime and self.sprite is not None:
            alpha = self.initial_alpha * max(1.0 - t, 0.0)
            self.sprite.set_alpha(alpha)
