# Adivinhas no Escuro

Jogo de aventura em Python e Pygame Zero, controlado por cliques.
Bilbo encontra um anel, disputa charadas com Gollum, sobrevive à perseguição
usando a espada e atravessa a caverna dos goblins invisível.
Os erros nas charadas aumentam o tempo de perseguição e o número de goblins.

## Instalar e executar

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
