
"""GUI Pong (Tkinter) — paddles now always bounce the ball.

Usage:
  python pong_window_fix.py --level hard
"""

import tkinter as tk
import random, argparse, sys

WIDTH, HEIGHT = 500, 300
PADDLE_W, PADDLE_H = 10, 70
BALL_SIZE = 10

DIFF = {
    "easy":   {"ball_speed": 4, "ai_delay": 12},
    "normal": {"ball_speed": 5, "ai_delay": 8},
    "hard":   {"ball_speed": 6, "ai_delay": 4},
}

class Pong:
    def __init__(self, root, level):
        self.root = root
        self.cfg = DIFF[level]
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="black")
        self.canvas.pack()
        root.title(f"Pong – {level.upper()}")

        # game objects
        self.player = self.canvas.create_rectangle(20, 0, 20+PADDLE_W, PADDLE_H, fill="white")
        self.ai     = self.canvas.create_rectangle(WIDTH-20-PADDLE_W, 0, WIDTH-20, PADDLE_H, fill="white")
        self.ball   = self.canvas.create_oval(0,0,BALL_SIZE,BALL_SIZE, fill="white")
        self.score_p = self.score_ai = 0
        self.score_text = self.canvas.create_text(WIDTH/2, 20, fill="white",
                                                  font=("Courier", 16), text=self.score_str())

        # initial positions
        self.canvas.move(self.player, 0, HEIGHT/2-PADDLE_H/2)
        self.canvas.move(self.ai, 0, HEIGHT/2-PADDLE_H/2)
        self.reset_ball(direction=random.choice([-1,1]))

        # bindings
        root.bind("<Up>", lambda e: self.move_paddle(self.player, -25))
        root.bind("<Down>", lambda e: self.move_paddle(self.player, 25))
        root.bind("<Escape>", lambda e: root.destroy())

        self.frame = 0
        self.loop()

    def score_str(self):
        return f"{self.score_p}  :  {self.score_ai}"

    def move_paddle(self, paddle, dy):
        x1,y1,x2,y2 = self.canvas.coords(paddle)
        if y1+dy < 0: dy = -y1
        if y2+dy > HEIGHT: dy = HEIGHT - y2
        self.canvas.move(paddle,0,dy)

    def reset_ball(self, direction):
        self.canvas.coords(self.ball,
                           WIDTH/2-BALL_SIZE/2, HEIGHT/2-BALL_SIZE/2,
                           WIDTH/2+BALL_SIZE/2, HEIGHT/2+BALL_SIZE/2)
        speed = self.cfg["ball_speed"]
        self.vx = direction * speed
        self.vy = random.choice([-speed/2, -speed/3, 0, speed/3, speed/2])

    def loop(self):
        self.update_ai()
        self.move_ball()
        self.frame += 1
        self.root.after(16, self.loop)

    def update_ai(self):
        if self.frame % self.cfg["ai_delay"] != 0:
            return
        bx1,by1,bx2,by2 = self.canvas.coords(self.ball)
        ball_mid = (by1+by2)/2
        x1,y1,x2,y2 = self.canvas.coords(self.ai)
        paddle_mid = (y1+y2)/2
        if ball_mid < paddle_mid-10:
            self.move_paddle(self.ai, -15)
        elif ball_mid > paddle_mid+10:
            self.move_paddle(self.ai, 15)

    def move_ball(self):
        self.canvas.move(self.ball, self.vx, self.vy)
        bx1,by1,bx2,by2 = self.canvas.coords(self.ball)

        # top/bottom walls
        if by1<=0 or by2>=HEIGHT:
            self.vy = -self.vy
            self.canvas.move(self.ball, 0, -2 if by1<=0 else 2)

        # paddle collisions
        self.check_collision(self.player, left_side=True)
        self.check_collision(self.ai, left_side=False)

        # scoring
        if bx2 < 0:
            self.score_ai += 1
            self.canvas.itemconfig(self.score_text, text=self.score_str())
            self.reset_ball(direction=1)
        elif bx1 > WIDTH:
            self.score_p += 1
            self.canvas.itemconfig(self.score_text, text=self.score_str())
            self.reset_ball(direction=-1)

    def check_collision(self, paddle, left_side):
        px1,py1,px2,py2 = self.canvas.coords(paddle)
        bx1,by1,bx2,by2 = self.canvas.coords(self.ball)

        overlap = not (bx2 < px1 or bx1 > px2 or by2 < py1 or by1 > py2)
        if overlap:
            # bounce only if ball moving toward paddle
            if (left_side and self.vx < 0) or (not left_side and self.vx > 0):
                # reposition ball just outside paddle to avoid sticking
                if left_side:
                    self.canvas.move(self.ball, (px2-bx1)+1, 0)
                else:
                    self.canvas.move(self.ball, -(bx2-px1)+1, 0)

                # compute new velocities
                speed = self.cfg["ball_speed"]
                paddle_mid = (py1+py2)/2
                ball_mid   = (by1+by2)/2
                offset = (ball_mid - paddle_mid)/(PADDLE_H/2)  # -1..1
                self.vy = offset * speed
                self.vx = speed if left_side else -speed

def main():
    argp = argparse.ArgumentParser()
    argp.add_argument("--level", choices=DIFF.keys(), default="normal")
    args = argp.parse_args()

    root = tk.Tk()
    Pong(root, args.level)
    root.mainloop()

if __name__ == "__main__":
    main()
