from cogworks import GameObject, Component
from cogworks.components.particle import Particle


class ParticleEffect(Component):
    def __init__(self,
                 sprite_path: str,
                 particle_amount: int = 3,
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
                 fade_over_lifetime: bool = False):
        super().__init__()
        self.sprite_path = sprite_path
        self.particle_amount = particle_amount
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
        self.end_scale = end_scale
        self.scale_with_lifetime = scale_with_lifetime
        self.rotate_over_lifetime = rotate_over_lifetime
        self.fade_over_lifetime = fade_over_lifetime

    def start(self) -> None:
        self.spawn_particles()

    def spawn_particles(self):
        x, y = self.game_object.transform.get_local_position()

        for i in range(self.particle_amount):
            particle = GameObject(f"Particle{i}", z_index=5)

            particle_component = Particle(
                sprite_path=self.sprite_path,
                min_x=x + self.min_x,
                max_x=x + self.max_x,
                min_y=y + self.min_y,
                max_y=y + self.max_y,
                min_rotation=self.min_rotation,
                max_rotation=self.max_rotation,
                min_scale=self.min_scale,
                max_scale=self.max_scale,
                move_speed=self.move_speed,
                gravity=self.gravity,
                min_direction=self.min_direction,
                max_direction=self.max_direction,
                lifetime=self.lifetime,
                end_scale=self.end_scale,
                scale_with_lifetime=self.scale_with_lifetime,
                rotate_over_lifetime=self.rotate_over_lifetime,
                fade_over_lifetime=self.fade_over_lifetime
            )

            particle.add_component(particle_component)
            self.game_object.scene.instantiate_game_object(particle)
