from math import ceil
from pygame import Rect

SWORD_BUTTON = Rect(730, 8, 210, 48)
START_BUTTON = Rect(330, 410, 300, 48)
MENU_BUTTONS = {
    name: Rect(300, 122 + index * 54, 360, 46)
    for index, name in enumerate(
        ('resume', 'start', 'music', 'effects', 'exit'))
}


def text(screen, label, pos, size=21, color='white', center=False, **options):
    """Use the same text defaults without repeating them at every call."""
    anchor = {'center': pos} if center else {'topleft': pos}
    screen.draw.text(label, fontsize=size, color=color, **anchor, **options)


def button(screen, rect, label, color=(54, 94, 103)):
    screen.draw.filled_rect(rect, color)
    text(screen, label, rect.center, 24, center=True)


def option_rect(index):
    return Rect(100, 358 + index * 54, 760, 46)


def panel(screen, title, rows, label, kicker, subtitle, accent):
    box = Rect(160, 54, 640, 430)
    screen.draw.filled_rect(box.move(7, 7), (12, 15, 21))
    screen.draw.filled_rect(box, (25, 31, 41))
    screen.draw.rect(box, accent)
    screen.draw.filled_rect(Rect(160, 54, 640, 5), accent)
    text(screen, kicker, (190, 76), 16, accent)
    text(screen, title, (190, 102), 35, (249, 244, 230))
    text(screen, subtitle, (190, 145), color=(183, 195, 209))
    for index, (heading, detail) in enumerate(rows):
        y = 198 + index * 62
        screen.draw.filled_circle((203, y + 10), 13, (43, 56, 68))
        text(screen, str(index + 1), (203, y + 10), 19, accent, True)
        text(screen, heading, (230, y - 3), 23)
        text(screen, detail, (230, y + 22), 19, (183, 195, 209), width=535)
    if label:
        button(screen, START_BUTTON, label)
    text(screen, 'ESC: menu', (190, 463), 15, (143, 159, 178))


def notice(screen, game):
    """Only the text differs between tutorials and end screens."""
    if game.state in ('tutorial', 'stealth_tutorial'):
        first = game.state == 'tutorial'
        title = 'Fuja de Gollum' if first else 'Atravesse os goblins'
        rows = [
            ('Clique para correr', 'Escolha um ponto e mantenha distância.'),
            ('Afaste-o com a espada', 'Use E ou Espada. Recarga: 5 segundos.'),
            ('Sobreviva ao tempo', 'Ao terminar, Bilbo poderá usar o anel.'),
        ] if first else [
            ('Você está invisível', 'Os goblins não o perseguem.'),
            ('Desvie sem a espada', 'Encostar em um goblin revela Bilbo.'),
            ('Alcance a saída', 'Procure uma brecha e siga para a direita.'),
        ]
        label = 'Começar fuga' if first else 'Começar travessia'
        kicker = 'ETAPA 1 / PERSEGUIÇÃO' if first else 'ETAPA 2 / INFILTRAÇÃO'
        subtitle = 'Não deixe os inimigos encostarem em Bilbo.'
        accent = (225, 192, 119) if first else (135, 204, 216)
        label += '  [ESPAÇO]'
    else:
        won = game.state == 'won'
        title = 'Bilbo escapou!' if won else 'Você foi pego!'
        rows = [
            ('Você alcançou a saída' if won else 'Cuidado com o contato',
             'O anel esconde Bilbo, mas não evita esbarrões.'
             if game.hero.invisible else 'Use a espada para afastar Gollum.'),
            ('Uma nova tentativa?', 'Pressione R para jogar novamente.'),
        ]
        label = None
        kicker = 'JORNADA CONCLUÍDA' if won else 'FIM DE JOGO'
        subtitle = 'A aventura continua.' if won else 'Tente outro caminho.'
        accent = (134, 202, 157) if won else (219, 143, 128)
    panel(screen, title, rows, label, kicker, subtitle, accent)


def speech_box(character, others=()):
    x, y = round(character.x), round(character.y)
    bodies = [Rect(round(c.x) - 48, round(c.y) - 88, 96, 96)
              for c in (character,) + tuple(others)]
    positions = [(left, top) for top in (y - 220, y + 24)
                 for left in (x - 175, x + 60, x - 410)]
    positions += [(left, top) for left in (24, 586, 305)
                  for top in (8, 410)]
    for left, top in positions:
        box = Rect(max(24, min(586, left)), max(8, min(410, top)), 350, 118)
        if not any(box.inflate(12, 20).colliderect(body) for body in bodies):
            return box
    return box


def speech(screen, character, label, prompt=False, others=()):
    box = speech_box(character, others)
    cream = (246, 240, 218)
    screen.draw.filled_rect(box, cream)
    screen.draw.rect(box, (76, 67, 57))
    tip = max(box.left + 12, min(box.right - 12, round(character.x)))
    for offset in range(14):
        width = 10 * (1 - offset / 14)
        y = box.bottom + offset if box.bottom <= character.y - 70 else (
            box.top - 1 - offset)
        screen.draw.line((tip - width, y), (tip + width, y), cream)
    text(screen, character.kind.title(), (box.x + 12, box.y + 9),
         19, (118, 73, 38))
    text(screen, label, (box.x + 12, box.y + 32),
         color=(32, 32, 36), width=326)
    if prompt:
        text(screen, 'ESPAÇO: continuar', (box.x + 12, box.bottom - 19),
             15, (95, 89, 80))


def score(screen, game):
    screen.draw.filled_rect(Rect(350, 12, 260, 65), (25, 29, 37))
    for name, results, x in (('Bilbo', game.bilbo_results, 410),
                             ('Gollum', game.gollum_results, 550)):
        text(screen, name, (x, 28), 20, center=True)
        for index in range(3):
            color = (85, 91, 104)
            if index < len(results):
                color = (74, 202, 114) if results[index] else (226, 86, 83)
            screen.draw.filled_circle((x - 26 + index * 26, 56), 9, color)


def draw_ui(screen, game):
    state = game.state
    if state in ('tutorial', 'stealth_tutorial', 'won', 'lost'):
        notice(screen, game)
    elif state == 'explore':
        text(screen, 'Clique na tela para andar', (480, 14), 22, center=True)
    elif state == 'chase':
        screen.draw.filled_rect(Rect(350, 12, 260, 65), (25, 29, 37))
        text(screen, 'FUJA!', (480, 29), 27, (255, 202, 90), True)
        text(screen, f'{ceil(game.escape_remaining)} s', (480, 60),
             25, center=True)
        label = f'Recarga: {ceil(game.cooldown)} s' if game.cooldown else (
            'Espada [E]')
        button(screen, SWORD_BUTTON, label)
    elif state in ('dialogue', 'approach', 'reaction',
                   'gollum_question', 'bilbo_question'):
        if not (state == 'dialogue' and game.next_state == 'depart'):
            score(screen, game)
        speaker, label = game.gollum, 'Errou... estamos chegando mais perto!'
        if state == 'dialogue':
            name, label = game.dialogue_lines[game.dialogue_index]
            speaker = game.hero if name == 'bilbo' else game.gollum
        elif state in ('gollum_question', 'bilbo_question'):
            answering = state == 'gollum_question'
            speaker = game.gollum if answering else game.hero
            label = game.questions[game.round]['question'] if answering else (
                'Agora é a minha vez de perguntar.')
            title = 'Escolha a Resposta' if answering else 'Escolha a Charada'
            labels = [a[0] for a in game.questions[game.round]['answers']] if (
                answering) else [r['question'] for r in game.choices()]
            text(screen, title, (100, 326), 23, (30, 29, 32))
            for index, choice in enumerate(labels):
                button(screen, option_rect(index), choice, (36, 56, 64))
        if state != 'reaction':
            speech(screen, speaker, label, state == 'dialogue',
                   (game.hero, game.gollum))


def draw_menu(screen, audio, pointer, started):
    screen.draw.filled_rect(Rect(250, 34, 460, 430), (20, 23, 31))
    text(screen, 'Adivinhas no Escuro', (480, 70),
         38, (245, 225, 170), True)
    labels = {'resume': 'Continuar', 'start': 'Começar o jogo', 'exit': 'Sair',
              'music': 'Música: ' + (
                  'ligada' if audio.music_enabled else 'desligada'),
              'effects': 'Efeitos: ' + (
                  'ligados' if audio.effects_enabled else 'desligados')}
    for action, rect in MENU_BUTTONS.items():
        if action != 'resume' or started:
            color = (65, 106, 115) if rect.collidepoint(pointer) else (
                39, 65, 73)
            button(screen, rect, labels[action], color)
    text(screen, 'ESC abre o menu durante o jogo.', (480, 425),
         18, (180, 189, 205), True)
