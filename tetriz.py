import curses
import random
import time

# Configurações do tabuleiro
BOARD_WIDTH = 10
BOARD_HEIGHT = 20

# Definição dos tetrominós – cada peça é representada por uma matriz (lista de listas)
TETROMINOS = {
    'I': [[1, 1, 1, 1]],
    'J': [
        [1, 0, 0],
        [1, 1, 1]
    ],
    'L': [
        [0, 0, 1],
        [1, 1, 1]
    ],
    'O': [
        [1, 1],
        [1, 1]
    ],
    'S': [
        [0, 1, 1],
        [1, 1, 0]
    ],
    'T': [
        [0, 1, 0],
        [1, 1, 1]
    ],
    'Z': [
        [1, 1, 0],
        [0, 1, 1]
    ]
}

def rotate(piece):

    #Rotaciona a peça 90 graus no sentido horário.
    return [list(row) for row in zip(*piece[::-1])]

def create_board():
    #Cria o tabuleiro.
    return [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

def is_valid_position(board, piece, offset):
    #Verifica se a peça pode ser posicionada na posição dada (offset).
    #Retorna False se estiver fora dos limites ou se colidir com peças já posicionadas.
    off_x, off_y = offset
    for y, row in enumerate(piece):
        for x, cell in enumerate(row):
            if cell:
                new_x = off_x + x
                new_y = off_y + y
                # Checa se a peça está fora dos limites do tabuleiro.
                if new_x < 0 or new_x >= BOARD_WIDTH or new_y < 0 or new_y >= BOARD_HEIGHT:
                    return False
                # Checa as colisões com peças já posicionadas.
                if board[new_y][new_x]:
                    return False
    return True

def place_piece(board, piece, offset):
    #"Trava" a peça no tabuleiro –coloca seus blocos ao grid.
    off_x, off_y = offset
    for y, row in enumerate(piece):
        for x, cell in enumerate(row):
            if cell:
                board[off_y + y][off_x + x] = cell

def remove_complete_lines(board):

    #Verifica linhas completas, remove-as e retorna o novo tabuleiro,
    #junto com a quantidade de linhas removidas.
    new_board = [row for row in board if any(cell == 0 for cell in row)]
    num_removed = BOARD_HEIGHT - len(new_board)
    for _ in range(num_removed):
        new_board.insert(0, [0 for _ in range(BOARD_WIDTH)])
    return new_board, num_removed

def draw_board(stdscr, board, score):
    #Desenha o tabuleiro e exibe a pontuação, respeitando os limites da janela.
    #Cada célula preenchida é representada por "[]" para dar uma boa visualização.
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()
    header = "Terminal Tetris - Score: {}".format(score)
    try:
        stdscr.addstr(0, 0, header[:max_x-1])
    except curses.error:
        pass  # Ignora se a linha não couber na tela.

    # Desenha cada linha do tabuleiro.
    for y, row in enumerate(board):
        line = ""
        for cell in row:
            line += "[]" if cell else "  "
        # Garante que a linha não ultrapasse a largura da tela.
        line = line[:max_x-1]
        try:
            if y + 1 < max_y:
                stdscr.addstr(y+1, 0, line)
        except curses.error:
            pass
    stdscr.refresh()

def draw_piece(stdscr, piece, offset):
    #Desenha a peça que está em movimento no tabuleiro.
    off_x, off_y = offset
    for y, row in enumerate(piece):
        for x, cell in enumerate(row):
            if cell:
                try:
                    # Multiplica coordenada x por 2 para manter a proporção.
                    stdscr.addstr(off_y+y+1, (off_x+x)*2, "[]")
                except curses.error:
                    pass

def tetris(stdscr):
    #Função principal que gerencia o jogo.
    #Configura o terminal, lida com entradas e executa a lógica de queda,
    #rotação, movimentação e detecção de colisões.
    curses.curs_set(0)      # Oculta o cursor.
    stdscr.nodelay(True)    # Configura o getch para não bloquear.
    stdscr.timeout(100)     # Atualiza a cada 100ms.

    board = create_board()
    score = 0
    current_piece = random.choice(list(TETROMINOS.values()))
    current_piece = [row[:] for row in current_piece]  # Cria uma cópia da peça.
    piece_x = BOARD_WIDTH // 2 - len(current_piece[0]) // 2
    piece_y = 0

    last_move_time = time.time()
    fall_speed = 0.5  # Intervalo (em segundos) para a queda automática.

    while True:
        # Tratamento de entradas do teclado.
        try:
            key = stdscr.getch()
        except Exception:
            key = -1

        if key != -1:
            if key == curses.KEY_LEFT:
                if is_valid_position(board, current_piece, (piece_x - 1, piece_y)):
                    piece_x -= 1
            elif key == curses.KEY_RIGHT:
                if is_valid_position(board, current_piece, (piece_x + 1, piece_y)):
                    piece_x += 1
            elif key == curses.KEY_DOWN:
                if is_valid_position(board, current_piece, (piece_x, piece_y + 1)):
                    piece_y += 1
            elif key == curses.KEY_UP:
                rotated_piece = rotate(current_piece)
                if is_valid_position(board, rotated_piece, (piece_x, piece_y)):
                    current_piece = rotated_piece
            elif key == ord('q'):
                #'q' para sair.
                break

        # Queda automática da peça.
        if time.time() - last_move_time > fall_speed:
            if is_valid_position(board, current_piece, (piece_x, piece_y + 1)):
                piece_y += 1
            else:
                # "Trava" a peça no tabuleiro.
                place_piece(board, current_piece, (piece_x, piece_y))
                board, removed = remove_complete_lines(board)
                score += removed * 100
                # Seleciona uma nova peça aleatória.
                current_piece = [row[:] for row in random.choice(list(TETROMINOS.values()))]
                piece_x = BOARD_WIDTH // 2 - len(current_piece[0]) // 2
                piece_y = 0
                if not is_valid_position(board, current_piece, (piece_x, piece_y)):
                    try:
                        stdscr.addstr(BOARD_HEIGHT // 2, BOARD_WIDTH, "GAME OVER!")
                    except curses.error:
                        pass
                    stdscr.refresh()
                    time.sleep(2)
                    break
            last_move_time = time.time()

        # Desenha o tabuleiro e a peça em movimento.
        draw_board(stdscr, board, score)
        draw_piece(stdscr, current_piece, (piece_x, piece_y))
        stdscr.refresh()

def main():
    curses.wrapper(tetris)

if __name__ == '__main__':
    main( )
