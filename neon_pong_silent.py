
"""
Neon Pong – Silent Edition (no sound, no extra deps).

Just run:  python neon_pong_silent.py
"""

import pygame, sys, random, math, time

WIDTH, HEIGHT = 800, 450
PADDLE_W, PADDLE_H = 12, 90
BALL_SIZE = 12
TRAIL_LEN = 15

COL_BG   = (10, 10, 20)
COL_NEON = {"cyan": (0, 255, 255), "magenta": (255, 0, 200),
            "green": (0, 255, 120), "yellow": (255, 255, 0)}

LEVELS = {
    "EASY":   {"ball_speed": 5, "ai_speed": 4},
    "NORMAL": {"ball_speed": 6, "ai_speed": 5},
    "HARD":   {"ball_speed": 7, "ai_speed": 6},
}

pygame.init()
FONT  = pygame.font.SysFont("Consolas", 28)
FONT2 = pygame.font.SysFont("Consolas", 48, bold=True)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock  = pygame.time.Clock()

def beep(*args, **kwargs):
    """No‑op placeholder to keep existing calls."""
    return

# ----- classes (identical to previous, but without pygame.mixer/beep changes) -----
class Paddle:
    def __init__(self, x, color):
        self.rect = pygame.Rect(x, HEIGHT//2-PADDLE_H//2, PADDLE_W, PADDLE_H)
        self.color = color
        self.speed = 7
    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=5)
    def move(self, dy):
        self.rect.y = max(0, min(HEIGHT-self.rect.height, self.rect.y+dy))

class Ball:
    def __init__(self, speed):
        self.speed = speed
        self.rect = pygame.Rect(WIDTH//2-BALL_SIZE//2, HEIGHT//2-BALL_SIZE//2,
                                BALL_SIZE, BALL_SIZE)
        self.vx = random.choice([-1,1])*speed
        self.vy = random.uniform(-0.6,0.6)*speed
        self.trail=[]
    def step(self):
        self.trail.append(self.rect.center)
        if len(self.trail)>TRAIL_LEN: self.trail.pop(0)
        self.rect.x+=self.vx
        self.rect.y+=self.vy
        if self.rect.top<=0 or self.rect.bottom>=HEIGHT:
            self.vy*=-1
    def draw(self):
        for i,pos in enumerate(self.trail):
            alpha=int(255*i/len(self.trail))
            surf=pygame.Surface((BALL_SIZE,BALL_SIZE),pygame.SRCALPHA)
            surf.fill((*COL_NEON["green"],alpha))
            screen.blit(surf,(pos[0]-BALL_SIZE//2,pos[1]-BALL_SIZE//2))
        pygame.draw.rect(screen, COL_NEON["green"], self.rect, border_radius=3)

def start_screen():
    pulse=0
    while True:
        screen.fill(COL_BG)
        pulse=(pulse+2)%360
        title_color=(int(155+100*math.sin(math.radians(pulse))),0,
                     int(155+100*math.cos(math.radians(pulse))))
        title=FONT2.render("NEON  PONG",True,title_color)
        screen.blit(title,title.get_rect(center=(WIDTH/2,HEIGHT/3)))
        btns=[]
        for i,lvl in enumerate(LEVELS):
            r=pygame.Rect(0,0,160,50); r.center=(WIDTH/2,HEIGHT/2+i*70)
            btns.append((r,lvl))
            pygame.draw.rect(screen,COL_NEON["cyan"],r,3,border_radius=8)
            txt=FONT.render(lvl,True,COL_NEON["magenta"])
            screen.blit(txt, txt.get_rect(center=r.center))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit();sys.exit()
            if e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
                for r,lvl in btns:
                    if r.collidepoint(e.pos): return lvl
        clock.tick(60)

def bounce(ball,paddle,left):
    next_left = ball.rect.left
    next_right= ball.rect.right
    prev_left = next_left - ball.vx
    prev_right= next_right - ball.vx
    if left:
        plane = paddle.rect.right
        crossed = prev_left >= plane and next_left <= plane
    else:
        plane = paddle.rect.left
        crossed = prev_right <= plane and next_right >= plane
    if not crossed: return
    y_at_plane = ball.rect.centery - ball.vy
    if paddle.rect.top-5 <= y_at_plane <= paddle.rect.bottom+5:
        offset = (ball.rect.centery - paddle.rect.centery)/(paddle.rect.height/2)
        ball.vx = abs(ball.vx) if left else -abs(ball.vx)
        ball.vy = ball.speed * offset

def game_loop(cfg):
    player=Paddle(40,COL_NEON["cyan"])
    ai    =Paddle(WIDTH-40-PADDLE_W,COL_NEON["magenta"])
    ball  =Ball(cfg["ball_speed"])
    score_p=score_ai=0
    paused=False
    while True:
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_ESCAPE: pygame.quit(); sys.exit()
                if e.key==pygame.K_p: paused=not paused
        if paused:
            pygame.display.set_caption("Neon Pong – Paused")
            clock.tick(20); continue
        keys=pygame.key.get_pressed()
        if keys[pygame.K_UP]: player.move(-player.speed)
        if keys[pygame.K_DOWN]: player.move(player.speed)
        if ball.rect.centery < ai.rect.centery-12: ai.move(-cfg["ai_speed"])
        elif ball.rect.centery > ai.rect.centery+12: ai.move(cfg["ai_speed"])
        ball.step()
        bounce(ball,player,left=True)
        bounce(ball,ai,left=False)
        if ball.rect.left<0:
            score_ai+=1; ball=Ball(cfg["ball_speed"])
        if ball.rect.right>WIDTH:
            score_p+=1; ball=Ball(cfg["ball_speed"])
        screen.fill(COL_BG)
        player.draw(); ai.draw(); ball.draw()
        hud=FONT.render(f"{score_p} : {score_ai}",True,COL_NEON["yellow"])
        screen.blit(hud,hud.get_rect(center=(WIDTH/2,35)))
        pygame.display.flip()
        clock.tick(60)

if __name__=="__main__":
    lvl=start_screen()
    game_loop(LEVELS[lvl])
