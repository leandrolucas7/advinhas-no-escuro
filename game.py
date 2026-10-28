from math import hypot
from random import choice, sample, uniform
from audio import Audio
from characters import Character
from level import (GOBLIN_SPAWNS, HEIGHT, RING_POSITION, WIDTH, can_stand,
                   draw_map)
from riddles import BILBO_RIDDLES, GOLLUM_RIDDLES, POCKET_RIDDLE
from ui import (MENU_BUTTONS, START_BUTTON, SWORD_BUTTON, draw_menu, draw_ui,
                option_rect)

TITLE = 'Adivinhas no Escuro'
PAUSED = ('tutorial', 'stealth_tutorial', 'won', 'lost')
audio = Audio()
menu_open, started, pointer = True, False, (0, 0)


class Game:
    def __init__(self):
        self.hero = Character('bilbo', 480, 264, 145)
        self.gollum = Character('gollum', 880, 264, 110)
        self.enemies = [self.gollum]
        self.state, self.round = 'explore', 0
        self.questions, self.remaining = (sample(GOLLUM_RIDDLES, 3),
                                          sample(BILBO_RIDDLES, 3))
        self.bilbo_results, self.gollum_results = [], []
        self.dialogue_lines, self.dialogue_index, self.next_state = [], 0, ''
        self.pending_result, self.correct = None, False
        self.doors_open = self.gollum_gone = False
        self.escape_remaining = self.cooldown = self.sword_flash = 0.0
        self.transition_time = self.reaction_time = self.spawn_time = 0.0
        self.approach_target, self.goblins_remaining = 0, 0
        self.goblin_count = 10

    def talking_poses(self):
        self.hero.pose('think')
        self.gollum.pose('idle_right')  # This source sequence faces left.

    def dialogue(self, lines, destination):
        self.state, self.dialogue_lines = 'dialogue', lines
        self.dialogue_index, self.next_state = 0, destination
        self.talking_poses()

    def enter(self, state):
        self.state = state
        if state == 'reaction':
            audio.play('correct' if self.correct else 'wrong')
            self.reaction_time = self.hero.elapsed = self.gollum.elapsed = 0
            self.hero.animation = 'jump' if self.correct else 'rest'
            self.gollum.animation = 'hurt' if self.correct else 'gesture'
        elif state == 'approach':
            self.hero.pose('think')
            self.gollum.pose('crouch')
        elif state in ('gollum_question', 'bilbo_question'):
            self.talking_poses()
        elif state == 'chase':
            self.escape_remaining = 10 + 5 * self.bilbo_results.count(False)
            self.hero.target = (self.hero.x, self.hero.y)
        elif state == 'sword_raise':
            audio.play('sword')
            self.hero.target = (self.hero.x, self.hero.y)
            self.hero.pose('idle_down')
            self.sword_flash, self.transition_time = 0.5, 1.2
            self.gollum.speed = 240
            self.gollum.target = (880 if self.hero.x < 480 else 112, 264)
        elif state == 'depart':
            audio.play('doors')
            self.doors_open = True
            self.hero.speed = self.gollum.speed = 230
            self.hero.target = (80, 264)
            self.cooldown = self.sword_flash = 0
        elif state == 'distribute':
            self.enemies = []
            self.hero.pose('idle_down')
            self.goblin_count = 10 + 3 * self.bilbo_results.count(False)
            self.goblins_remaining = self.goblin_count
        elif state == 'stealth':
            self.hero.speed = 145
            for index, enemy in enumerate(self.enemies):
                enemy.speed = 65 + index % 5 * 7
        elif state in ('won', 'lost'):
            audio.play('win' if state == 'won' else 'lose')

    def advance(self):
        if self.next_state == 'depart' and self.dialogue_index == 1:
            self.hero.invisible = True
            audio.play('invisible')
            audio.play('alarm')
        self.dialogue_index += 1
        if self.dialogue_index == len(self.dialogue_lines):
            self.enter(self.next_state)
        elif (self.dialogue_lines[self.dialogue_index][0] == 'gollum'
              and self.pending_result is not None):
            self.gollum_results.append(self.pending_result)
            self.pending_result = None

    def choices(self):
        return [POCKET_RIDDLE] if self.round == 2 else self.remaining

    def choose(self, index):
        if self.state == 'gollum_question':
            riddle = self.questions[self.round]
            self.correct = index == riddle['correct']
            self.bilbo_results.append(self.correct)
            self.approach_target = max(self.hero.x + 150, self.gollum.x - 160)
            self.dialogue([('bilbo', riddle['answers'][index][1])], 'reaction')
        else:
            riddle = self.choices()[index]
            lines = [('bilbo', riddle['question'])]
            self.pending_result = self.round < 2
            if self.pending_result:
                self.remaining.remove(riddle)
                self.round += 1
                self.dialogue(lines + [('gollum', riddle['answer'])],
                              'gollum_question')
            else:
                self.dialogue(lines + [
                    ('gollum', 'Não sabemos! Isso não é uma charada!'),
                    ('gollum', 'Vamos pegar você!')], 'tutorial')

    def sword(self):
        if self.state == 'chase' and self.cooldown == 0:
            self.cooldown, self.sword_flash = 5, 0.5
            audio.play('sword')
            if hypot(self.gollum.x - self.hero.x,
                     self.gollum.y - self.hero.y) <= 150:
                self.gollum.scare(self.hero)

    def update(self, dt):
        steps = max(1, int(dt / 0.02) + 1)
        for _ in range(steps):
            if self.state in PAUSED:
                break
            previous = (self.hero.x, self.hero.y)
            self.tick(dt / steps)
            moving = previous != (self.hero.x, self.hero.y)
            audio.steps(dt / steps, moving and self.state not in PAUSED,
                        self.state in ('chase', 'depart', 'entrance'))

    def tick(self, dt):
        for character in [self.hero] + self.enemies:
            character.elapsed += dt
        if self.state == 'explore':
            self.hero.move(self.hero.target, dt)
            if hypot(self.hero.x - RING_POSITION[0],
                     self.hero.y - RING_POSITION[1]) < 22:
                audio.play('ring')
                self.state, self.hero.target = 'entrance', (112, 264)
                self.gollum.pose('idle_right')
        elif self.state == 'entrance':
            if self.hero.move(self.hero.target, dt):
                self.dialogue([
                    ('bilbo', 'Quem está aí?'),
                    ('gollum', 'O que faz nas nossas cavernas?'),
                    ('bilbo', 'Quero encontrar a saída.'),
                    ('gollum', 'Primeiro, vamos brincar de charadas!')],
                    'gollum_question')
        elif self.state == 'reaction':
            self.reaction_time += dt
            if self.reaction_time >= (0.8 if self.correct else 0.96):
                self.enter('bilbo_question' if self.correct else 'approach')
        elif self.state == 'approach':
            self.gollum.x = max(self.approach_target, self.gollum.x - 100 * dt)
            if self.gollum.x == self.approach_target:
                self.enter('bilbo_question')
        elif self.state == 'chase':
            self.cooldown = max(0, self.cooldown - dt)
            self.sword_flash = max(0, self.sword_flash - dt)
            self.hero.move(self.hero.target, dt)
            self.gollum.pursue(self.hero, dt)
            self.escape_remaining = max(0, self.escape_remaining - dt)
            if self.gollum.touches(self.hero):
                self.enter('lost')
            elif self.escape_remaining == 0:
                self.enter('sword_raise')
        elif self.state == 'sword_raise':
            self.transition_time -= dt
            self.sword_flash = max(0, self.sword_flash - dt)
            self.gollum.move(self.gollum.target, dt)
            if self.transition_time <= 0:
                self.dialogue([
                    ('bilbo', 'Afinal, o que tenho no meu bolso?'),
                    ('bilbo', 'O que é esse anel? Vou colocar!'),
                    ('gollum', 'Precioso!!!! Invasor, invasor!')], 'depart')
        elif self.state == 'depart':
            ready = self.hero.move(self.hero.target, dt, True)
            if not self.gollum_gone:
                self.gollum_gone = self.gollum.move((944, 264), dt, True)
            if ready and self.gollum_gone:
                self.enter('distribute')
        elif self.state == 'distribute':
            self.spawn_time -= dt
            if self.goblins_remaining and self.spawn_time <= 0:
                index = self.goblin_count - self.goblins_remaining
                goblin = Character('goblin', *choice(GOBLIN_SPAWNS), 230)
                goblin.target = (170 + index % 5 * 165 + uniform(-20, 20),
                                 129 + index // 5 * 80 + uniform(-15, 15))
                self.enemies.append(goblin)
                self.goblins_remaining -= 1
                self.spawn_time = 0.15
            arrived = [enemy.move(enemy.target, dt, True)
                       for enemy in self.enemies]
            if not self.goblins_remaining and all(arrived):
                self.enter('stealth_tutorial')
        elif self.state == 'stealth':
            self.hero.move(self.hero.target, dt, True)
            for enemy in self.enemies:
                enemy.wander(dt)
            if any(enemy.touches(self.hero) for enemy in self.enemies):
                self.enter('lost')
            elif self.hero.x >= 936 and abs(self.hero.y - 264) < 20:
                self.enter('won')

    def draw(self, screen):
        draw_map(screen, self.doors_open)
        if self.state == 'explore':
            screen.blit('ring', (RING_POSITION[0] - 16, RING_POSITION[1] - 15))
        enemies = [] if self.state == 'explore' else self.enemies
        characters = [self.hero] + [e for e in enemies if not (
            self.gollum_gone and e is self.gollum)]
        for character in sorted(characters, key=lambda item: item.y):
            character.draw(screen, self.state == 'reaction')
        if self.sword_flash > 0:
            screen.draw.circle((self.hero.x, self.hero.y - 10),
                               150, (120, 215, 255))
            screen.blit('sword', (self.hero.x + 8, self.hero.y - 64))
        draw_ui(screen, self)

    def continue_tutorial(self):
        audio.play('click')
        self.enter('chase' if self.state == 'tutorial' else 'stealth')

    def click(self, pos):
        if self.state.endswith('tutorial') and START_BUTTON.collidepoint(pos):
            self.continue_tutorial()
        elif self.state == 'chase' and SWORD_BUTTON.collidepoint(pos):
            self.sword()
        elif self.state in ('gollum_question', 'bilbo_question'):
            count = (3 if self.state == 'gollum_question'
                     else len(self.choices()))
            for index in range(count):
                if option_rect(index).collidepoint(pos):
                    audio.play('click')
                    self.choose(index)
        elif self.state in ('explore', 'chase', 'stealth'):
            if can_stand(*pos, self.doors_open):
                self.hero.target = pos


game = Game()


def draw():
    if menu_open:
        draw_map(screen, False)
        draw_menu(screen, audio, pointer, started)
    else:
        game.draw(screen)


def update(dt):
    if menu_open:
        audio.steps(dt, False)
    else:
        game.update(dt)
    audio.update_theme('menu' if menu_open else game.state)


def on_key_down(key):
    global game, menu_open
    if key == keys.ESCAPE and started:
        menu_open = not menu_open
    elif not menu_open:
        if key == keys.R:
            game = Game()
        elif key == keys.E:
            game.sword()
        elif key == keys.SPACE:
            if game.state == 'dialogue':
                audio.play('click')
                game.advance()
            elif game.state.endswith('tutorial'):
                game.continue_tutorial()


def on_mouse_move(pos):
    global pointer
    pointer = pos


def on_mouse_down(pos, button):
    global game, menu_open, started
    if button != mouse.LEFT:
        return
    if not menu_open:
        game.click(pos)
        return
    for action, rect in MENU_BUTTONS.items():
        if rect.collidepoint(pos) and (action != 'resume' or started):
            if action == 'music':
                audio.toggle_music()
            elif action == 'effects':
                audio.toggle_effects()
            elif action == 'start':
                game, menu_open, started = Game(), False, True
            elif action == 'resume':
                menu_open = False
            audio.play('click')
            if action == 'exit':
                exit()
