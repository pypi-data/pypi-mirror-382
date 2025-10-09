import math
import pymunk
from cogworks.component import Component
from cogworks.components.transform import Transform


class Rigidbody2D(Component):
    def __init__(
        self,
        shape_type="box",
        width=0,
        height=0,
        radius=0,
        mass=1.0,
        static=False,
        debug=False,
        freeze_rotation=False,
        friction=0.7,
        elasticity=0.0,
        velocity_controlled=False,
    ):
        """
        2D Rigidbody component supporting box and circle colliders with optional
        velocity-controlled movement.

        Args:
            shape_type (str): "box" or "circle"
            width (float): Box width
            height (float): Box height
            radius (float): Circle radius
            mass (float): Mass of the body
            static (bool): If True, body is immovable
            debug (bool): If True, render debug visuals
            freeze_rotation (bool): If True, prevents rotation
            friction (float): Shape friction coefficient
            elasticity (float): Shape elasticity coefficient
            velocity_controlled (bool): If True, Rigidbody velocity is manually controlled
        """
        super().__init__()
        self.shape_type = shape_type
        self.width = width
        self.height = height
        self.radius = radius
        self.mass = mass
        self.static = static
        self.debug = debug
        self.freeze_rotation = freeze_rotation
        self.friction = friction
        self.elasticity = elasticity
        self.velocity_controlled = velocity_controlled

        self.transform: Transform = None
        self.body: pymunk.Body = None
        self.shape: pymunk.Shape = None
        self.is_grounded = False
        self.desired_velocity = 0, 0

    def start(self):
        """Initialises the Rigidbody2D component by linking it to the Transform and creating the physics body."""
        self.transform = self.game_object.get_component(Transform)
        self._create_body()

    def on_disabled(self):
        """Removes the body/shape from the physics space but keeps them for later re-enable."""
        if self.body and self.shape:
            space = self.game_object.scene.physics_space
            if self.body in space.bodies:
                space.remove(self.body, self.shape)

    def on_remove(self) -> None:
        """Completely removes the body/shape from the space and clears references."""
        if self.body and self.shape:
            space = self.game_object.scene.physics_space
            if self.body in space.bodies:
                space.remove(self.body, self.shape)
        self.body = None
        self.shape = None
        self.transform._rb_body = None

    def _create_body(self):
        """Internal method to create the pymunk physics body and collider based on the component settings."""
        scale_x, scale_y = self.transform.local_scale_x, self.transform.local_scale_y

        if self.shape_type == "box":
            width = max(self.width * scale_x, 1)
            height = max(self.height * scale_y, 1)
        elif self.shape_type == "circle":
            radius = max(self.radius * max(scale_x, scale_y), 1)
        else:
            raise ValueError(f"Unknown shape_type: {self.shape_type}")

        if self.static:
            self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        else:
            safe_mass = max(self.mass, 0.0001)
            if self.shape_type == "box":
                moment = float("inf") if self.freeze_rotation else pymunk.moment_for_box(safe_mass, (width, height))
            else:
                moment = float("inf") if self.freeze_rotation else pymunk.moment_for_circle(safe_mass, 0, radius)
            self.body = pymunk.Body(safe_mass, moment)
            self.body.velocity_func = self._limit_velocity

        self.body.position = self.transform.get_local_position()
        self.body.angle = -math.radians(self.transform.local_rotation)
        self.transform._rb_body = self.body

        if self.shape_type == "box":
            if self.static:
                self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
                self.body.position = self.transform.get_local_position()

                hw, hh = width / 2, height / 2
                angle = -math.radians(self.transform.local_rotation)

                # Rotate vertices around origin
                verts = [
                    pymunk.Vec2d(x, y).rotated(angle)
                    for x, y in [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
                ]

                # Create poly relative to body
                self.shape = pymunk.Poly(self.body, verts)
            else:
                self.shape = pymunk.Poly.create_box(self.body, (width, height))
        else:
            self.shape = pymunk.Circle(self.body, radius)

        self.shape.friction = self.friction
        self.shape.elasticity = self.elasticity

        self.game_object.scene.physics_space.add(self.body, self.shape)

    def apply_force(self, fx, fy):
        """
        Applies a force to the Rigidbody2D at its centre of mass.

        Args:
            fx (float): Force along the x-axis
            fy (float): Force along the y-axis
        """
        self.body.apply_force_at_world_point((fx, fy), self.body.position)

    def render(self, surface):
        """
        Renders debug visuals for the Rigidbody2D, including shape, centre of mass, local axes,
        and collision rays if velocity-controlled.

        Args:
            surface (pygame.Surface): Surface to render onto
        """
        if not self.debug:
            return
        import pygame

        camera = getattr(self.game_object.scene, "camera_component", None)
        pos = camera.world_to_screen(*self.body.position) if camera else self.body.position
        pos = (int(pos[0]), int(pos[1]))

        # Draw shape
        if self.shape_type == "box":
            vertices = [v.rotated(self.body.angle) + self.body.position for v in self.shape.get_vertices()]
            points = [camera.world_to_screen(*v) if camera else v for v in vertices]
            for i in range(len(points)):
                pygame.draw.line(surface, (255, 0, 0), points[i], points[(i + 1) % len(points)], 2)
        else:  # circle
            zoom = camera.zoom

            scaled_radius = int(self.shape.radius * zoom)

            pygame.draw.circle(surface, (255, 0, 0), pos, scaled_radius, 2)

        # Draw center of mass
        pygame.draw.circle(surface, (0, 255, 0), pos, 3)

        # Draw local axes
        axis_length = 20
        angle = self.body.angle
        x_axis_end = (pos[0] + axis_length * math.cos(angle), pos[1] + axis_length * math.sin(angle))
        y_axis_end = (pos[0] - axis_length * math.sin(angle), pos[1] + axis_length * math.cos(angle))
        pygame.draw.line(surface, (0, 0, 255), pos, x_axis_end, 2)
        pygame.draw.line(surface, (255, 255, 0), pos, y_axis_end, 2)

        if not self.velocity_controlled:
            return

        # ------------------------
        # Draw collision rays
        # ------------------------
        ray_color = (0, 255, 255)
        # Horizontal rays
        for direction in [-1, 1]:
            start = self._get_ray_start(direction)
            end = start + pymunk.Vec2d(direction * (self.width / 2 + 20), 0)
            if camera:
                start = camera.world_to_screen(*start)
                end = camera.world_to_screen(*end)
            pygame.draw.line(surface, ray_color, start, end, 1)

        # Ground ray
        start = pymunk.Vec2d(self.body.position.x, self.body.position.y + self.height)
        end = start + pymunk.Vec2d(0, 10)
        if camera:
            start = camera.world_to_screen(*start)
            end = camera.world_to_screen(*end)
        pygame.draw.line(surface, ray_color, start, end, 1)

        # Ceiling ray
        start = pymunk.Vec2d(self.body.position.x, self.body.position.y - self.height)
        end = start + pymunk.Vec2d(0, -10)
        if camera:
            start = camera.world_to_screen(*start)
            end = camera.world_to_screen(*end)
        pygame.draw.line(surface, ray_color, start, end, 1)

    # ------------------------
    # Fixed Update / Collisions
    # ------------------------
    def fixed_update(self, dt):
        """
        Updates the Rigidbody2D physics state each fixed timestep.
        Handles velocity-controlled movement and synchronises Transform with physics body.

        Args:
            dt (float): Fixed delta time in seconds
        """
        if self.velocity_controlled and not self.static:
            vx_input, vy_input = self.desired_velocity

            # Preserve vertical velocity from physics (gravity)
            current_vx, current_vy = self.body.velocity
            vx = vx_input
            vy = current_vy

            # Apply collision checks
            vx = self.check_horizontal_collision(vx, dt)
            vy = self.check_vertical_collision(vy, dt)
            self.body.velocity = vx, vy

        if not self.static:
            self.transform.set_world_position(*self.body.position)
            self.transform.set_local_rotation(-math.degrees(self.body.angle))

    # ------------------------
    # Collision / Raycasting
    # ------------------------
    def check_horizontal_collision(self, vx, dt):
        """
        Checks for collisions horizontally and prevents movement if a collision occurs.

        Args:
            vx (float): Desired horizontal velocity
            dt (float): Fixed delta time

        Returns:
            float: Adjusted horizontal velocity (0 if collision detected)
        """
        if vx == 0:
            return 0
        direction = 1 if vx > 0 else -1
        ray_length = (self.width / 2 + abs(vx) * dt + 1)
        start = self._get_ray_start(direction)
        end = start + pymunk.Vec2d(direction * ray_length, 0)
        hit = self.game_object.scene.physics_space.segment_query_first(
            start, end, radius=0.3, shape_filter=pymunk.ShapeFilter()
        )
        if hit and hit.shape != self.shape:
            return 0
        return vx

    def check_vertical_collision(self, vy, dt):
        """
        Checks for collisions vertically and prevents movement through ceilings.

        Args:
            vy (float): Desired vertical velocity
            dt (float): Fixed delta time

        Returns:
            float: Adjusted vertical velocity (0 if collision detected)
        """
        if vy < 0 and self._check_ceiling(self.height + abs(vy) * dt + 1):
            return 0
        return vy

    def check_grounded(self):
        """
        Determines if the Rigidbody2D is currently grounded.

        Returns:
            bool: True if grounded, False otherwise
        """
        space = self.game_object.scene.physics_space
        start = pymunk.Vec2d(self.body.position.x, self.body.position.y + self.height)
        end = start + pymunk.Vec2d(0, 2)
        hit = space.segment_query_first(start, end, radius=0.1, shape_filter=pymunk.ShapeFilter())
        return hit and hit.shape != self.shape

    def _check_ceiling(self, ray_length):
        """
        Internal helper to check if there is a collision above the Rigidbody2D.

        Args:
            ray_length (float): Length of the upward ray

        Returns:
            bool: True if ceiling collision detected
        """
        space = self.game_object.scene.physics_space
        start = pymunk.Vec2d(self.body.position.x, self.body.position.y - self.height)
        end = start + pymunk.Vec2d(0, -ray_length)
        hit = space.segment_query_first(start, end, radius=0.1, shape_filter=pymunk.ShapeFilter())
        return hit and hit.shape != self.shape

    def _get_ray_start(self, direction):
        """
        Computes the starting point of a horizontal raycast for collision detection.

        Args:
            direction (int): 1 for right, -1 for left

        Returns:
            pymunk.Vec2d: Start position of the ray
        """
        bb = self.shape.bb
        x = bb.right if direction > 0 else bb.left
        y = self.body.position.y
        return pymunk.Vec2d(x, y)

    def _limit_velocity(self, body, gravity, damping, dt):
        """
        Limits the Rigidbody2D velocity to a maximum value to help prevent tunnelling.

        Args:
            body (pymunk.Body): The physics body
            gravity (pymunk.Vec2d): Gravity vector
            damping (float): Damping factor
            dt (float): Delta time
        """
        max_speed = 1000
        body.velocity = pymunk.Vec2d(
            max(-max_speed, min(body.velocity.x, max_speed)),
            max(-max_speed, min(body.velocity.y, max_speed))
        )
        pymunk.Body.update_velocity(body, gravity, damping, dt)
