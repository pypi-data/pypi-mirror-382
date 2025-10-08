import os
import pygame
import importlib.resources as res

def load_engine_image(relative_path: str) -> pygame.Surface:
    """
    Load an image bundled inside the cogworks package.
    Example: load_engine_image("images/default.png")
    """
    with res.files("cogworks.engine_assets").joinpath(relative_path).open("rb") as f:
        img = pygame.image.load(f).convert_alpha()
    _ensure_pygame_display()
    return img


def load_user_image(relative_path: str) -> pygame.Surface:
    """
    Load an image from the user's project 'assets' folder.
    Example: load_user_image("images/player.png")
    """
    project_root = os.getcwd()
    assets_dir = os.path.join(project_root, "assets")
    abs_path = os.path.join(assets_dir, relative_path)

    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"User asset not found: {abs_path}")

    img = pygame.image.load(abs_path).convert_alpha()
    _ensure_pygame_display()
    return img


def _ensure_pygame_display():
    if not pygame.get_init():
        pygame.init()
    if not pygame.display.get_init():
        pygame.display.set_mode((1, 1))
