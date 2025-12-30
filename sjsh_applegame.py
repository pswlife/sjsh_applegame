import pygame
import random
import time

# -----------------------------
# 게임 초기화
# -----------------------------
def init_game(r=9, c=18, cell_sz=50, t_lim=120):
    pygame.init()

    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    scr_width = c * cell_sz
    scr_height = r * cell_sz + 50
    scr = pygame.display.set_mode((scr_width, scr_height))
    pygame.display.set_caption("Apple Game")

    fnt = pygame.font.Font(None, 28)
    big_fnt = pygame.font.Font(None, 50)

    # 🔑 제거 사운드 로딩
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
# 보드 생성
# -----------------------------
def make_board(r, c):
    return [[random.randint(1, 9) for _ in range(c)] for _ in range(r)]


# -----------------------------
# 게임 실행
# -----------------------------
def play_game(scr, fnt, big_fnt, tile_imgs, r, c, cell_sz, t_lim, remove_sound):
    brd = make_board(r, c)
    sel_cells = []
    s_cell = None
    e_cell = None
    score = 0
    drag_rect = None   # (x, y, w, h) 형태의 드래그 사각형


    st_time = time.time()
    top_h = 50
    is_running = True

    # -------------------------
    # 좌표 → 셀 변환
    # -------------------------
    def get_cell(pos):
        x, y = pos
        if y < top_h:
            return None
        col = x // cell_sz
        row = (y - top_h) // cell_sz
        if 0 <= row < r and 0 <= col < c:
            return row, col
        return None

    # -------------------------
    # 선택 범위 계산 (직사각형)
    # -------------------------
    def select_range(s, e):
        sel_cells.clear()
        if not s or not e:
            return

        sr, sc = s
        er, ec = e

        for i in range(min(sr, er), max(sr, er) + 1):
            for j in range(min(sc, ec), max(sc, ec) + 1):
                # 🔑 이미 사라진 사과(0)는 선택하지 않음
                if brd[i][j] != 0:
                    sel_cells.append((i, j))



    # -------------------------
    # 선택 합계
    # -------------------------
    def calc_sum():
        return sum(brd[i][j] for i, j in sel_cells if brd[i][j] != 0)

    # -------------------------
    # 셀 제거
    # -------------------------
    def remove_cells():
        nonlocal score

        removed_any = False   # 🔑 실제 제거 여부 추적

        for i, j in sel_cells:
            if brd[i][j] != 0:
                brd[i][j] = 0
                score += 1
                removed_any = True

        # 🔑 사과가 하나라도 제거됐을 때만 사운드 재생
        if removed_any:
            remove_sound.play()


    # -------------------------
    # 상단 HUD
    # -------------------------
    def draw_top(remaining):
        pygame.draw.rect(scr, (245, 245, 245), (0, 0, c * cell_sz, top_h))

        score_txt = fnt.render(f"Score: {score}", True, (0, 0, 0))
        time_txt = fnt.render(f"Time: {remaining}s", True, (0, 0, 0))

        scr.blit(score_txt, (10, 12))
        scr.blit(time_txt, (c * cell_sz - 180, 12))

    # -------------------------
    # 보드 렌더링
    # -------------------------
    def draw_board():
        for i in range(r):
            for j in range(c):
                x = j * cell_sz
                y = i * cell_sz + top_h

                pygame.draw.rect(
                    scr, (200, 200, 200),
                    (x, y, cell_sz, cell_sz), 1
                )

                num = brd[i][j]
                if num != 0:
                    scr.blit(tile_imgs[num], (x, y))


    # -------------------------
    # 메인 루프
    # -------------------------
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

                if e_cell and sel_cells:   # 🔑 선택된 유효 셀이 있을 때만
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
                if s_cell and e_cell:
                    if calc_sum() == 10:
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
    scr, fnt, big_fnt, r, c, cell_sz, t_lim, remove_sound = init_game()
    tile_imgs = load_tile_images(cell_sz)
    final_score = play_game(scr, fnt, big_fnt, tile_imgs, r, c, cell_sz, t_lim, remove_sound)
    show_end(scr, final_score)
