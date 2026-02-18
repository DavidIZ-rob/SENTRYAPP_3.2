#this app used Ai only for the next details:
#1.to correct the early motion detection scaffolding
#2.help with debugging 
import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
import webbrowser
import time
import datetime

class VectorMap:
    def __init__(self):
        self.m = np.zeros((400, 400, 3), dtype=np.uint8)
        self.c = [200, 200]
        self.old_g = None
        self.p0 = None
        
        self.lk = dict(winSize=(15, 15), maxLevel=2, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
        self.ft = dict(maxCorners=50, qualityLevel=0.3, minDistance=7, blockSize=7)

    def wipe(self):
        self.m.fill(0)
        self.c = [200, 200]
        self.old_g = None

    def step(self, fr):
        g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
        
        if self.p0 is None or len(self.p0) < 5:
            self.p0 = cv2.goodFeaturesToTrack(g, mask=None, **self.ft)
            self.old_g = g
            return fr

        p1, st, _ = cv2.calcOpticalFlowPyrLK(self.old_g, g, self.p0, None, **self.lk)
        
        if p1 is not None:
            # vect delta calc
            good_new = p1[st==1]
            good_old = self.p0[st==1]
            
            if len(good_new) > 0:
                diff = np.mean(good_new - good_old, axis=0) * 2.5
                dx, dy = int(diff[0]), int(diff[1])
                
                self.c[0] += dx
                self.c[1] += dy
                
                #  visuals
                cent = np.mean(good_new, axis=0).astype(int)
                cv2.circle(fr, tuple(cent), 8, (0, 255, 0), 2)
                cv2.line(fr, tuple(cent), (cent[0] + dx*4, cent[1] + dy*4), (0, 0, 255), 2)
                
                # up internal map
                cv2.circle(self.m, tuple(self.c), 2, (0, 255, 255), -1)

            self.old_g = g.copy()
            self.p0 = good_new.reshape(-1, 1, 2)
            
        return fr

class Sentry:
    def __init__(self, root):
        self.root = root
        self.root.title("SENTRYAPP_3.2")
        self.root.geometry("1100x600")
        self.root.configure(bg="#1e1e1e")

        self.cap = cv2.VideoCapture(0)
        self.vec = VectorMap()
        self.qr = cv2.QRCodeDetector()
        
        self.mode = "MOTION"
        self.bg = None
        self.thresh = 600
        self.last_url = ""

        self.trk = None
        self.is_tracking = False

        self._ui()
        self._loop()

    def _ui(self):
        f = tk.Frame(self.root, bg="#1e1e1e")
        f.pack(fill="both", expand=True, padx=10, pady=10)

        # controls
        col = tk.Frame(f, bg="#2d2d2d", width=180)
        col.pack(side="left", fill="y", padx=5)
        
        tk.Label(col, text="MODE SELECT", bg="#2d2d2d", fg="white", font=("Arial", 10, "bold")).pack(pady=15)
        
        tk.Button(col, text="MOTION", bg="#c62828", fg="white", width=20, command=lambda: self.swap("MOTION")).pack(pady=2)
        tk.Button(col, text="QR SCAN", bg="#1565c0", fg="white", width=20, command=lambda: self.swap("QR")).pack(pady=2)
        tk.Button(col, text="VECTOR MAP", bg="#6a1b9a", fg="white", width=20, command=lambda: self.swap("VECT")).pack(pady=2)
        
        tk.Label(col, text="TOOLS", bg="#2d2d2d", fg="#aaa", font=("Arial", 8)).pack(pady=(20, 5))
        tk.Button(col, text="SET TRACKER", bg="#2e7d32", fg="white", width=20, command=self.set_track).pack(pady=2)

        self.st = tk.Label(col, text="Ready", bg="#2d2d2d", fg="#00e676", font=("Consolas", 8))
        self.st.pack(side="bottom", pady=10)

        # video
        self.cv = tk.Canvas(f, width=640, height=480, bg="black")
        self.cv.pack(side="left", padx=5)
        
        # map
        self.mp = tk.Canvas(f, width=400, height=400, bg="#111")
        self.mp.pack(side="left", padx=5)

    def swap(self, m):
        self.mode = m
        self.st.config(text=f"Mode: {m}")
        if m == "VECT": self.vec.wipe()
        if m == "MOTION": self.bg = None

    def set_track(self):
        self.mode = "TRACKING"
        ret, fr = self.cap.read()
        if ret:
            r = cv2.selectROI("Target", fr, False)
            cv2.destroyWindow("Target")
            if r[2] > 0:
                self.trk = cv2.TrackerKCF_create()
                self.trk.init(fr, r)
                self.is_tracking = True
            else:
                self.swap("MOTION")

    def _loop(self):
        ret, fr = self.cap.read()
        if not ret: return
        
        fr = cv2.flip(fr, 1)

        if self.mode == "MOTION":
            gray = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            if self.bg is None:
                self.bg = gray
            else:
                d = cv2.absdiff(self.bg, gray)
                _, t = cv2.threshold(d, 25, 255, cv2.THRESH_BINARY)
                t = cv2.dilate(t, None, iterations=2)
                
                c, _ = cv2.findContours(t, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                stat = "Clear"
                for cnt in c:
                    if cv2.contourArea(cnt) < self.thresh: continue
                    x,y,w,h = cv2.boundingRect(cnt)
                    cv2.rectangle(fr, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    stat = "Motion"
                
                cv2.putText(fr, stat, (10, 30), 1, 1.5, (0, 0, 255), 2)

        elif self.mode == "QR":
            val, pts, _ = self.qr.detectAndDecode(fr)
            if val:
                if pts is not None:
                    p = np.int32(pts).reshape(-1, 2)
                    cv2.polylines(fr, [p], True, (255, 0, 0), 2)
                
                cv2.putText(fr, val, (10, 50), 1, 1, (0, 255, 0), 2)
                if val != self.last_url:
                    if "http" in val: webbrowser.open(val)
                    self.last_url = val

        elif self.mode == "TRACKING" and self.is_tracking:
            ok, box = self.trk.update(fr)
            if ok:
                p1 = (int(box[0]), int(box[1]))
                p2 = (int(box[0] + box[2]), int(box[1] + box[3]))
                cv2.rectangle(fr, p1, p2, (0, 255, 0), 2, 1)
            else:
                cv2.putText(fr, "LOST", (10, 50), 1, 1, (0, 0, 255), 2)

        elif self.mode == "VECT":
            fr = self.vec.step(fr)
            rgb = cv2.cvtColor(self.vec.m, cv2.COLOR_BGR2RGB)
            im_map = ImageTk.PhotoImage(image=Image.fromarray(rgb))
            self.mp.create_image(0, 0, anchor="nw", image=im_map)
            self.mp.image = im_map

        # main render
        im_fr = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)))
        self.cv.create_image(0, 0, anchor="nw", image=im_fr)
        self.cv.image = im_fr
        
        self.root.after(10, self._loop)

if __name__ == "__main__":
    tk_root = tk.Tk()
    app = Sentry(tk_root)
    tk_root.mainloop()