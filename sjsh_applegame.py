import pygame, time,ast

# -----------------------------
# 게임 초기화
# -----------------------------
def init_game(r=10, c=17, cell_sz=50, t_lim=120):
    pygame.init()
    if not pygame.mixer.get_init():
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    scr = pygame.display.set_mode((c * cell_sz, r * cell_sz + 50))
    pygame.display.set_caption("Apple Game")

    fnt = pygame.font.Font(None, 28)
    big_fnt = pygame.font.Font(None, 50)

    remove_sound = pygame.mixer.Sound("assets/remove_sound.mp3")
    remove_sound.set_volume(0.6)

    return scr, fnt, big_fnt, r, c, cell_sz, t_lim, remove_sound


# -----------------------------
# 타일 이미지 로딩
# -----------------------------
def load_tile_images(cell_sz):
    tiles = {}
    for n in range(1, 10):
        img = pygame.image.load(f"assets/sjsh_apple_{n}.png").convert_alpha()
        img = pygame.transform.smoothscale(img, (cell_sz, cell_sz))
        tiles[n] = img
    return tiles


# -----------------------------
# 서버에서 보드(2차원 리스트) 받기: 여기만 채우세요
# -----------------------------
def fetch_board_from_server():
    
 
    return None


def validate_board(brd, r=10, c=17):
    if not isinstance(brd, list) or len(brd) != r or any(not isinstance(row, list) or len(row) != c for row in brd):
        raise ValueError(f"보드 크기/형식 오류: {r}x{c} 2차원 리스트가 필요합니다.")
    for i in range(r):
        for j in range(c):
            v = brd[i][j]
            if not isinstance(v, int) or not (0 <= v <= 9):
                raise ValueError(f"보드 값 오류: brd[{i}][{j}]={v!r} (0~9 int만 허용)")


# -----------------------------
# 게임 실행
# -----------------------------
def play_game(scr, fnt, big_fnt, tile_imgs, r, c, cell_sz, t_lim, remove_sound, brd):
    validate_board(brd, r, c)

    sel_cells, s_cell, e_cell = [], None, None
    score, drag_rect = 0, None

    st_time = time.time()
    top_h = 50
    is_running = True

    def get_cell(pos):
        x, y = pos
        if y < top_h:
            return None
        col = x // cell_sz
        row = (y - top_h) // cell_sz
        if 0 <= row < r and 0 <= col < c:
            return row, col
        return None

    def select_range(s, e):
        sel_cells.clear()
        if not s or not e:
            return
        sr, sc = s
        er, ec = e
        for i in range(min(sr, er), max(sr, er) + 1):
            for j in range(min(sc, ec), max(sc, ec) + 1):
                if brd[i][j] != 0:
                    sel_cells.append((i, j))

    def calc_sum():
        return sum(brd[i][j] for i, j in sel_cells if brd[i][j] != 0)

    def remove_cells():
        nonlocal score
        removed_any = False
        for i, j in sel_cells:
            if brd[i][j] != 0:
                brd[i][j] = 0
                score += 1
                removed_any = True
        if removed_any:
            remove_sound.play()

    def draw_top(remaining):
        pygame.draw.rect(scr, (245, 245, 245), (0, 0, c * cell_sz, top_h))
        scr.blit(fnt.render(f"Score: {score}", True, (0, 0, 0)), (10, 12))
        scr.blit(fnt.render(f"Time: {remaining}s", True, (0, 0, 0)), (c * cell_sz - 180, 12))

    def draw_board():
        for i in range(r):
            for j in range(c):
                x = j * cell_sz
                y = i * cell_sz + top_h
                pygame.draw.rect(scr, (200, 200, 200), (x, y, cell_sz, cell_sz), 1)
                num = brd[i][j]
                if num != 0:
                    scr.blit(tile_imgs[num], (x, y))

    while is_running:
        elapsed = time.time() - st_time
        remaining = max(0, t_lim - int(elapsed))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                s_cell = get_cell(event.pos)
                sel_cells.clear()
                drag_rect = None

            elif event.type == pygame.MOUSEMOTION and s_cell:
                e_cell = get_cell(event.pos)
                select_range(s_cell, e_cell)

                if e_cell and sel_cells:
                    sr, sc = s_cell
                    er, ec = e_cell
                    left = min(sc, ec) * cell_sz
                    top = min(sr, er) * cell_sz + top_h
                    width = (abs(sc - ec) + 1) * cell_sz
                    height = (abs(sr - er) + 1) * cell_sz
                    drag_rect = (left, top, width, height)
                else:
                    drag_rect = None

            elif event.type == pygame.MOUSEBUTTONUP:
                if s_cell and e_cell and calc_sum() == 10:
                    remove_cells()
                s_cell = None
                drag_rect = None

        if remaining == 0:
            is_running = False

        scr.fill((255, 255, 255))
        draw_top(remaining)
        draw_board()

        if drag_rect:
            overlay = pygame.Surface((drag_rect[2], drag_rect[3]), pygame.SRCALPHA)
            overlay.fill((100, 160, 255, 80))
            scr.blit(overlay, (drag_rect[0], drag_rect[1]))

        pygame.display.flip()

    return score


# -----------------------------
# 종료 화면
# -----------------------------
def show_end(scr, score):
    scr.fill((255, 255, 255))
    font = pygame.font.Font(None, 48)
    txt = font.render(f"Game Over! Score: {score}", True, (0, 0, 0))
    scr.blit(
        txt,
        (scr.get_width() // 2 - txt.get_width() // 2,
         scr.get_height() // 2 - txt.get_height() // 2)
    )
    pygame.display.flip()
    pygame.time.wait(3000)
    pygame.quit()


# -----------------------------
# main
# -----------------------------
if __name__ == "__main__":
    #먼저 서버에서 2차원 리스트 보드 받기
    board = ast.literal_eval(input().strip())  #fetch_board_from_server()
    if board is None:
        raise RuntimeError("fetch_board_from_server()가 보드를 반환하지 않았습니다. 서버 수신 코드를 채우세요.")

    # pygame 초기화 및 게임 실행
    scr, fnt, big_fnt, r, c, cell_sz, t_lim, remove_sound = init_game()
    tile_imgs = load_tile_images(cell_sz)
    final_score = play_game(scr, fnt, big_fnt, tile_imgs, r, c, cell_sz, t_lim, remove_sound, board)
    show_end(scr, final_score)
