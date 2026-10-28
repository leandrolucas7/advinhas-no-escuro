from math import hypot
from random import uniform
from level import can_stand

FRAMES = {
    'bilbo': {'idle_down': 6, 'think': 6, 'walk_left': 8,
              'walk_right': 8, 'jump': 5, 'rest': 8},
    'gollum': {'idle_right': 6, 'idle_down': 5, 'run_left': 6, 'run_right': 6,
               'gesture': 6, 'hurt': 4, 'crouch': 5},
    'goblin': {'idle_down': 3, 'walk_left': 6, 'walk_right': 6},
}


class Character:
    def __init__(self, kind, x, y, speed):
        self.kind, self.x, self.y, self.speed = kind, float(x), float(y), speed
        self.target, self.elapsed = (x, y), 0.0
        self.animation, self.flee_remaining = 'idle_down', 0.0
        self.invisible, self.wait = False, 0.0
        self.flee_direction = (1.0, 0.0)

    def pose(self, animation):
        if self.animation != animation:
            self.animation, self.elapsed = animation, 0.0

    def move(self, target, dt, doors_open=False):
        dx, dy = target[0] - self.x, target[1] - self.y
        distance = hypot(dx, dy)
        if distance < 0.5:
            self.pose('idle_down')
            return True
        prefix = 'run' if self.kind == 'gollum' else 'walk'
        self.pose(f'{prefix}_{"right" if dx >= 0 else "left"}')
        step = min(self.speed * dt, distance)
        x, y = self.x + dx / distance * step, self.y + dy / distance * step
        if can_stand(x, y, doors_open):
            self.x, self.y = x, y
        else:
            self.target = (self.x, self.y)
        return hypot(target[0] - self.x, target[1] - self.y) < 0.5

    def scare(self, hero):
        self.flee_remaining = 2.0
        dx, dy = self.x - hero.x, self.y - hero.y
        distance = hypot(dx, dy) or 1
        self.flee_direction = (dx / distance, dy / distance)
        if not (dx or dy):
            self.flee_direction = (1, 0)

    def pursue(self, hero, dt):
        target = (hero.x, hero.y)
        if self.flee_remaining > 0:
            self.flee_remaining = max(0, self.flee_remaining - dt)
            dx, dy = self.flee_direction
            target = (self.x + dx * 100, self.y + dy * 100)
        self.move(target, dt, doors_open=False)

    def wander(self, dt):
        if self.wait > 0:
            self.wait = max(0, self.wait - dt)
            self.pose('idle_down')
            return
        if self.move(self.target, dt, doors_open=True):
            self.wait = uniform(0.3, 1.1)
            self.target = (uniform(90, 870), uniform(109, 394))

    def touches(self, other):
        return abs(self.x - other.x) < 22 and abs(self.y - other.y) < 14

    def draw(self, screen, reaction=False):
        count = FRAMES[self.kind][self.animation]
        frame = int(self.elapsed / (0.16 if reaction else 0.12))
        if reaction:
            first = 1 if self.animation == 'gesture' else 0
            frame = min(first + frame, count - 1)
        else:
            frame %= count
        folder = 'bilbo_invisible' if self.invisible else self.kind
        screen.blit(f'{folder}/{self.animation}_{frame:02d}',
                    (round(self.x) - 48, round(self.y) - 88))
