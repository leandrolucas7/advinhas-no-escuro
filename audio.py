from pgzero import music
from pgzero.loaders import sounds

EFFECTS = ('click', 'ring', 'correct', 'wrong', 'alarm', 'doors',
           'invisible', 'win', 'lose', 'sword', 'step', 'step_alt')


def theme_for(state):
    if state in ('menu', 'explore', 'won'):
        return 'fantasy'
    if state in ('tutorial', 'chase', 'sword_raise', 'lost'):
        return 'danger'
    if state in ('depart', 'distribute', 'stealth_tutorial', 'stealth'):
        return 'stealth'
    return 'riddles'


class Audio:
    def __init__(self):
        self.music_enabled = self.effects_enabled = self.left_foot = True
        self.theme, self.current_theme, self.step_timer = 'fantasy', None, 0

    def start(self):
        if self.music_enabled and self.current_theme != self.theme:
            music.set_volume(0.28)
            music.play(f'{self.theme}.wav')
            self.current_theme = self.theme

    def update_theme(self, state):
        self.theme = theme_for(state)
        self.start()

    def play(self, name):
        if self.effects_enabled:
            sound = getattr(sounds, name)
            volume = 0.55 if name in ('lose', 'sword') else 0.4
            sound.set_volume(0.28 if name.startswith('step') else volume)
            sound.play()

    def steps(self, dt, moving, fast=False):
        self.step_timer = self.step_timer - dt if moving else 0
        if moving and self.step_timer <= 0:
            self.play('step' if self.left_foot else 'step_alt')
            self.left_foot = not self.left_foot
            self.step_timer = 0.20 if fast else 0.26

    def toggle_music(self):
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            self.start()
            music.unpause()
        else:
            music.pause()

    def toggle_effects(self):
        self.effects_enabled = not self.effects_enabled
        if not self.effects_enabled:
            for name in EFFECTS:
                getattr(sounds, name).stop()
