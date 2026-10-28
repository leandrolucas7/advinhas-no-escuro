# Adivinhas no Escuro

Jogo de aventura em Python e Pygame Zero, controlado por cliques.
Bilbo encontra um anel, disputa charadas com Gollum, sobrevive à perseguição
usando a espada e atravessa a caverna dos goblins invisível.
Os erros nas charadas aumentam o tempo de perseguição e o número de goblins.

## Instalar e executar

Versões testadas: Python 3.13.7, Pygame Zero 1.2.1 e Pygame 2.6.1.
Instale o Python 3.13 e abra o terminal na pasta do projeto.

### macOS / Linux

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
pgzrun game.py
```

### Windows (PowerShell)

```powershell
py -3.13 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\pgzrun.exe game.py
```

Nas próximas execuções, basta ativar o ambiente e usar `pgzrun game.py`
(no Windows, use diretamente o executável mostrado acima).
O executor do Pygame Zero inicia a janela e chama as funções do jogo;
`python game.py` não inicia a partida.
Mantenha `images/`, `music/` e `sounds/` junto dos arquivos Python.
É necessário um ambiente gráfico; o áudio depende da saída de som do sistema.

## Controles

- **Clique esquerdo:** escolher opções e o destino de Bilbo.
- **Espaço:** avançar diálogos e começar cada etapa após o tutorial.
- **E** ou botão **Espada:** afastar Gollum próximo, com recarga de 5 segundos.
- **ESC:** abrir ou fechar o menu durante a partida.
- **R:** reiniciar a tentativa durante o jogo.

Na travessia final, a espada fica indisponível. Mesmo invisível, Bilbo não
pode encostar nos goblins. Alcance a saída à direita para vencer.
O menu permite ligar e desligar música e efeitos separadamente.

## Organização

| Arquivo / pasta | Responsabilidade |
| --- | --- |
| `game.py` | Entrada do PgZero, estados, charadas e sequência da partida. |
| `level.py` | Matriz do mapa, desenho dos tiles e colisão com paredes. |
| `characters.py` | Movimento, animações, perseguição e passeio dos goblins. |
| `riddles.py` | Bancos de perguntas e respostas. |
| `ui.py` | Menu, balões, placar, botões e tutoriais. |
| `audio.py` | Trilhas, efeitos, passos e preferências de som. |
| `images/` | Frames PNG e objetos já preparados para uso. |
| `music/` | Quatro trilhas de fundo WAV. |
| `sounds/` | Doze efeitos WAV. |

Não é preciso recortar sprites nem gerar arquivos antes de jogar.
A pasta `.venv/` é criada localmente e não deve ser enviada ao GitHub.

## Recursos visuais e áudio

O cenário usa tiles do conjunto **Kenney Tiny Dungeon**. As imagens de
personagens e objetos foram fornecidas durante o desenvolvimento e preparadas
em PNG; as animações usam arquivos individuais. A aparência invisível de Bilbo
é uma variação dos mesmos frames.

As músicas e os efeitos foram sintetizados para este projeto, sem amostras ou
gravações externas. O jogo é um projeto de estudo inspirado em *O Hobbit*.
