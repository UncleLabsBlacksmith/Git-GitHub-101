"""
Hello, World! — animated with tkinter (single file, no dependencies)

  • ตัวอักษรตกลงมาทีละตัวแบบเด้ง (ease-out-back) แล้วลอยเป็นคลื่น
  • สีไล่เฉดรุ้งต่อเนื่อง + เงาและแสงเรือง (glow)
  • ดาวกระพริบลอยเคลื่อนช้าๆ บนพื้นหลังไล่สี
  • พลุจุดอัตโนมัติ / คลิกเมาส์เพื่อจุดพลุเอง

Controls:  คลิก = จุดพลุ   |   Space = เล่นใหม่   |   Esc = ออก

by uncle engineer
"""

import colorsys
import math
import random
import time
import tkinter as tk
import tkinter.font as tkfont

W, H = 960, 540
FPS_MS = 16
TEXT = "Hello, World!"
SUBTITLE = "สวัสดีชาวโลก  ·  made with tkinter"
BG_TOP = (8, 6, 28)
BG_BOT = (46, 12, 66)


# ---------- helpers ----------
def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    return tuple(lerp(a, b, t) for a, b in zip(c1, c2))


def hexc(c):
    return "#%02x%02x%02x" % tuple(int(clamp(v, 0, 255)) for v in c)


def hsv(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
    return (r * 255, g * 255, b * 255)


def bg_at(y):
    return mix(BG_TOP, BG_BOT, clamp(y / H))


def ease_out_back(t):
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def ease_out_cubic(t):
    return 1 - (1 - t) ** 3


# ---------- app ----------
class HelloWorld:
    def __init__(self, root):
        self.root = root
        root.title("Hello, World! ✨")
        # root.state('zoomed')
        root.resizable(False, False)

        self.c = tk.Canvas(root, width=W, height=H, highlightthickness=0,
                           bg=hexc(BG_TOP))
        self.c.pack()

        self._draw_background()
        self._make_stars(150)
        self._make_title()
        self._make_subtitle()

        self.particles = []
        self.c.bind("<Button-1>", lambda e: self.burst(e.x, e.y, 70))
        root.bind("<space>", lambda e: self.restart())
        root.bind("<Escape>", lambda e: root.destroy())

        self.restart()
        self._tick()

    # --- scene setup ---
    def _draw_background(self):
        for y in range(0, H, 2):
            self.c.create_line(0, y, W, y, width=2, fill=hexc(bg_at(y)))

    def _make_stars(self, n):
        self.stars = []
        for _ in range(n):
            x, y = random.uniform(0, W), random.uniform(0, H)
            r = random.choice((0.8, 1.0, 1.2, 1.6, 2.2))
            item = self.c.create_oval(x - r, y - r, x + r, y + r, width=0)
            self.stars.append({
                "id": item, "x": x, "y": y, "r": r,
                "phase": random.uniform(0, math.tau),
                "speed": random.uniform(1.0, 3.5),
                "drift": random.uniform(0.05, 0.25) * r,
            })

    def _make_title(self):
        main_font = tkfont.Font(family="Helvetica", size=78, weight="bold")
        glow1 = tkfont.Font(family="Helvetica", size=84, weight="bold")
        glow2 = tkfont.Font(family="Helvetica", size=92, weight="bold")

        widths = [main_font.measure(ch) for ch in TEXT]
        x = (W - sum(widths)) / 2
        self.target_y = H * 0.44
        self.letters = []
        idx = 0
        for ch, w in zip(TEXT, widths):
            cx = x + w / 2
            x += w
            if ch == " ":
                continue
            kw = dict(text=ch, anchor="center", tags=("letter",))
            self.letters.append({
                "i": idx, "x": cx,
                "glow2": self.c.create_text(cx, -200, font=glow2, **kw),
                "glow1": self.c.create_text(cx, -200, font=glow1, **kw),
                "shadow": self.c.create_text(cx, -200, font=main_font, fill="#05030f", **kw),
                "main": self.c.create_text(cx, -200, font=main_font, **kw),
            })
            idx += 1

    def _make_subtitle(self):
        y = H * 0.62
        self.bar = self.c.create_line(W / 2, y, W / 2, y, width=3,
                                      capstyle="round", fill=hexc(bg_at(y)))
        self.sub = self.c.create_text(W / 2, y + 34, text=SUBTITLE,
                                      font=("Helvetica", 18), fill=hexc(bg_at(y + 34)))
        self.hint = self.c.create_text(W - 16, H - 14, anchor="se",
                                       text="คลิก = จุดพลุ   ·   Space = เล่นใหม่   ·   Esc = ออก",
                                       font=("Helvetica", 11), fill=hexc(bg_at(H)))

    def restart(self):
        for p in self.particles:
            self.c.delete(p["id"])
        self.particles.clear()
        self.t0 = self.last = time.perf_counter()
        self.next_firework = 2.6

    # --- per-frame updates ---
    def _update_stars(self, t, k):
        for s in self.stars:
            s["x"] -= s["drift"] * k
            if s["x"] < -3:
                s["x"] = W + 3
                s["y"] = random.uniform(0, H)
            tw = 0.5 + 0.5 * math.sin(t * s["speed"] + s["phase"])
            col = mix(bg_at(s["y"]), (235, 235, 255), 0.25 + 0.75 * tw)
            r = s["r"] * (0.8 + 0.4 * tw)
            self.c.coords(s["id"], s["x"] - r, s["y"] - r, s["x"] + r, s["y"] + r)
            self.c.itemconfig(s["id"], fill=hexc(col))

    def _update_title(self, t):
        for L in self.letters:
            i = L["i"]
            start = 0.25 + i * 0.09
            p = clamp((t - start) / 0.9)
            y = lerp(-120, self.target_y, ease_out_back(p))
            # float on a wave once landed (fade the wave in smoothly)
            wave_in = clamp((t - start - 0.9) / 0.8)
            y += math.sin(t * 2.6 - i * 0.55) * 10 * wave_in

            hue = t * 0.12 + i * 0.055
            bg = bg_at(y)
            appear = ease_out_cubic(p)
            main = mix(bg, hsv(hue, 0.45, 1.0), appear)
            g1 = mix(bg, hsv(hue, 0.9, 1.0), 0.35 * appear)
            g2 = mix(bg, hsv(hue + 0.05, 0.9, 1.0), 0.15 * appear)

            x = L["x"]
            self.c.coords(L["glow2"], x, y)
            self.c.coords(L["glow1"], x, y)
            self.c.coords(L["shadow"], x + 4, y + 6)
            self.c.coords(L["main"], x, y)
            self.c.itemconfig(L["glow2"], fill=hexc(g2))
            self.c.itemconfig(L["glow1"], fill=hexc(g1))
            self.c.itemconfig(L["main"], fill=hexc(main))

    def _update_subtitle(self, t):
        y = H * 0.62
        bp = ease_out_cubic(clamp((t - 1.9) / 0.8))
        half = 230 * bp
        self.c.coords(self.bar, W / 2 - half, y, W / 2 + half, y)
        self.c.itemconfig(self.bar, fill=hexc(mix(bg_at(y), hsv(t * 0.12, 0.6, 1.0), bp)))

        sp = clamp((t - 2.3) / 1.0)
        self.c.itemconfig(self.sub, fill=hexc(mix(bg_at(y + 34), (210, 205, 240), sp)))
        hp = clamp((t - 3.5) / 1.0)
        self.c.itemconfig(self.hint, fill=hexc(mix(bg_at(H), (120, 110, 160), hp)))

    def _update_particles(self, k):
        alive = []
        for p in self.particles:
            p["vy"] += 0.06 * k
            p["vx"] *= 0.985 ** k
            p["vy"] *= 0.985 ** k
            p["x"] += p["vx"] * k
            p["y"] += p["vy"] * k
            p["life"] -= k / 60
            if p["life"] <= 0:
                self.c.delete(p["id"])
                continue
            a = p["life"] / p["max"]
            r = p["r"] * (0.4 + 0.6 * a)
            self.c.coords(p["id"], p["x"] - r, p["y"] - r, p["x"] + r, p["y"] + r)
            self.c.itemconfig(p["id"], fill=hexc(mix(bg_at(p["y"]), p["col"], a)))
            alive.append(p)
        self.particles = alive

    def burst(self, x, y, n=55):
        base = random.random()
        for _ in range(n):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(1.5, 6.5)
            life = random.uniform(0.9, 1.7)
            r = random.uniform(1.6, 3.2)
            item = self.c.create_oval(x, y, x, y, width=0)
            self.c.tag_lower(item, "letter")  # keep sparks behind the title
            self.particles.append({
                "id": item, "x": x, "y": y,
                "vx": math.cos(ang) * spd, "vy": math.sin(ang) * spd,
                "life": life, "max": life, "r": r,
                "col": hsv(base + random.uniform(-0.06, 0.06), 0.7, 1.0),
            })

    def _tick(self):
        now = time.perf_counter()
        t = now - self.t0
        k = min(now - self.last, 0.05) * 60  # frame-rate independent step
        self.last = now

        self._update_stars(t, k)
        self._update_particles(k)
        self._update_title(t)
        self._update_subtitle(t)

        if t > self.next_firework:
            self.burst(random.uniform(W * 0.12, W * 0.88),
                       random.uniform(H * 0.10, H * 0.32))
            self.next_firework = t + random.uniform(0.9, 2.0)

        self.root.after(FPS_MS, self._tick)


if __name__ == "__main__":
    root = tk.Tk()
    HelloWorld(root)
    root.mainloop()