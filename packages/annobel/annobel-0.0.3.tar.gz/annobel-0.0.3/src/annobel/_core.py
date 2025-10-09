"""
Core logic for the annobel package (AGPL-3.0-or-later).
Vendored from original standalone script so that the package provides the
same runtime behavior without needing the separate yolo_detect_and_save.py file.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Tuple

###############################################################################
# CONFIG
###############################################################################
CONFIG = {
    "mode": "",                           # auto | manual
    "model_path": "",
    "images_dir": "",
    "labels_dir": "",
    "classes_file": "",
    "conf": 0.25,
    "open_editor_after_detect": True,
    "write_empty_detection_files": True,  # 0.0.3: now True by default to ensure 1:1 image:label mapping
    "display_max_width": 1000,
    "display_max_height": 800,
    "force_mode_dialog": True,
    "classes_filter_ids": []              # for auto mode subset
}

MODEL_VARIANTS = ["yolov8n.pt", "yolov8s.pt", "yolov8m.pt", "yolov8l.pt", "yolov8x.pt"]

###############################################################################
# CLI OVERRIDE
###############################################################################
def parse_cli():
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        a = args[i]
        if a.startswith("--"):
            k = a[2:]
            if i + 1 < len(args) and not args[i+1].startswith("--"):
                CONFIG[k] = args[i+1]; i += 2
            else:
                CONFIG[k] = "1"; i += 1
        elif "=" in a:
            k, v = a.split("=", 1)
            CONFIG[k.lstrip("-")] = v
            i += 1
        else:
            i += 1
parse_cli()

###############################################################################
# TK SAFE IMPORT
###############################################################################
def _tk_safe_import():
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox
        return tk, filedialog, messagebox
    except Exception:
        return None, None, None

###############################################################################
# DATA & HELPERS
###############################################################################
SUPPORTED_IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
_YOLO_CLS = None

@dataclass
class Box:
    cls: int
    xc: float
    yc: float
    w: float
    h: float

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def collect_images(folder: Path) -> List[Path]:
    return [p for p in sorted(folder.rglob("*"))
            if p.is_file() and p.suffix.lower() in SUPPORTED_IMG_EXT]

def load_model(model_path: str):
    global _YOLO_CLS
    try:
        if _YOLO_CLS is None:
            from ultralytics import YOLO
            _YOLO_CLS = YOLO
    except ImportError:
        print("Install ultralytics: pip install ultralytics")
        sys.exit(1)
    return _YOLO_CLS(model_path)

def read_classes(f: Path) -> List[str]:
    return [l.strip() for l in f.read_text().splitlines() if l.strip()] if f.exists() else []

def write_classes(f: Path, names: List[str]):
    f.write_text("\n".join(names))

def load_yolo_label_file(label_path: Path) -> List[Box]:
    if not label_path.exists(): return []
    txt = label_path.read_text().strip()
    if not txt: return []
    out: List[Box] = []
    for ln in txt.splitlines():
        p = ln.split()
        if len(p) != 5: continue
        try:
            c = int(p[0]); xc = float(p[1]); yc = float(p[2]); w = float(p[3]); h = float(p[4])
            if not (0 <= xc <= 1 and 0 <= yc <= 1 and 0 < w <= 1 and 0 < h <= 1): continue
            out.append(Box(c, xc, yc, w, h))
        except:
            pass
    return out

def save_yolo_label_file(label_path: Path, boxes: List[Box]):
    if not boxes:
        label_path.write_text("")
        return
    label_path.write_text(
        "\n".join(f"{b.cls} {b.xc:.6f} {b.yc:.6f} {b.w:.6f} {b.h:.6f}" for b in boxes)
    )

###############################################################################
# GUI DIALOGS
###############################################################################
def gui_mode_selection() -> Optional[str]:
    tk, _, messagebox = _tk_safe_import()
    if tk is None:
        while True:
            print("Select mode:")
            print("  1. Automatic Annotation (YOLO)")
            print("  2. Manual Annotation / Editing")
            print("  Q. Quit")
            m = input("Choice: ").strip().lower()
            if m in ("1","auto","automatic"): return "auto"
            if m in ("2","manual","edit","editing"): return "manual"
            if m in ("q","quit"): return "quit"
    root = tk.Tk(); root.title("Select Mode"); root.geometry("360x200")
    var = tk.StringVar(value="manual")
    tk.Label(root, text="Select Annotation Mode", font=("Arial",12,"bold")).pack(pady=8)
    tk.Radiobutton(root, text="Automatic Annotation (YOLO detection)", variable=var, value="auto").pack(anchor="w", padx=20)
    tk.Radiobutton(root, text="Manual Annotation / Editing", variable=var, value="manual").pack(anchor="w", padx=20)
    result={"mode":None}
    def ok(): result["mode"]=var.get(); root.destroy()
    def quit_():
        if messagebox.askyesno("Confirm","Quit?"): result["mode"]="quit"; root.destroy()
    bar = tk.Frame(root); bar.pack(pady=12)
    tk.Button(bar,text="OK",width=12,command=ok).grid(row=0,column=0,padx=6)
    tk.Button(bar,text="Quit",width=12,command=quit_).grid(row=0,column=1,padx=6)
    root.mainloop()
    return result["mode"]

def gui_select_model() -> Optional[str]:
    tk, filedialog, messagebox = _tk_safe_import()
    if tk is None:
        have = input("Local YOLO model file? (y/N): ").strip().lower()=='y'
        if have:
            p = input("Model path: ").strip()
            return p or None
        print("Variants:", ", ".join(MODEL_VARIANTS))
        choice = input("Variant (blank=yolov8n.pt): ").strip() or "yolov8n.pt"
        return attempt_model_download(choice)
    root = tk.Tk(); root.title("Model Selection"); root.geometry("430x300")
    import tkinter.ttk as ttk
    mode_var=tk.StringVar(value="download")
    variant_var=tk.StringVar(value="yolov8n.pt")
    local_var=tk.StringVar(value="")
    def browse():
        f=filedialog.askopenfilename(title="Select YOLO .pt model",filetypes=[("Model","*.pt"),("All","*.*")])
        if f: local_var.set(f)
    tk.Label(root,text="Model Source",font=("Arial",11,"bold")).pack(anchor="w", padx=12, pady=(10,4))
    tk.Radiobutton(root,text="Download official model",variable=mode_var,value="download").pack(anchor="w", padx=24)
    tk.Radiobutton(root,text="Use local model file",variable=mode_var,value="local").pack(anchor="w", padx=24)
    lf1=tk.LabelFrame(root,text="Download Variant"); lf1.pack(fill="x", padx=12, pady=6)
    tk.Label(lf1,text="Variant:").grid(row=0,column=0,padx=4,pady=6,sticky="w")
    ttk.Combobox(lf1,textvariable=variant_var,values=MODEL_VARIANTS,width=22).grid(row=0,column=1,padx=4,pady=6,sticky="w")
    lf2=tk.LabelFrame(root,text="Local Model"); lf2.pack(fill="x", padx=12, pady=6)
    tk.Entry(lf2,textvariable=local_var,width=34).grid(row=0,column=0,padx=4,pady=6,sticky="w")
    tk.Button(lf2,text="Browse",command=browse).grid(row=0,column=1,padx=4,pady=6)
    result={"path":None}
    def proceed():
        if mode_var.get()=="local":
            lp=local_var.get().strip()
            if not lp:
                messagebox.showerror("Error","Select local file."); return
            if not Path(lp).exists():
                messagebox.showerror("Error","File not found."); return
            result["path"]=lp; root.destroy()
        else:
            p=attempt_model_download(variant_var.get())
            if p: result["path"]=p; root.destroy()
            else: messagebox.showwarning("Download Failed","Could not load model.")
    tk.Button(root,text="OK",width=16,command=proceed).pack(pady=12)
    root.mainloop()
    return result["path"]

def attempt_model_download(name: str) -> Optional[str]:
    try:
        print(f"[MODEL] Loading '{name}' ...")
        model=load_model(name)
        path=getattr(model,'ckpt_path',None) or name
        print(f"[MODEL] Ready: {path}")
        return path
    except Exception as e:
        print(f"[MODEL] Failed: {e}")
        return None

def gui_pick_folders(mode: str):
    tk, filedialog, messagebox = _tk_safe_import()
    if tk is None:
        CONFIG["images_dir"]=input("Images folder: ").strip()
        CONFIG["labels_dir"]=input("Labels folder (blank=images/labels): ").strip() or str(Path(CONFIG["images_dir"])/"labels")
        if mode=="auto" and not CONFIG["model_path"]:
            CONFIG["model_path"]=input("Model path (blank=yolov8n.pt): ").strip()
            if not CONFIG["model_path"]:
                mp=attempt_model_download("yolov8n.pt")
                if not mp:
                    print("Model required."); sys.exit(1)
                CONFIG["model_path"]=mp
        return
    root=tk.Tk(); root.withdraw()
    messagebox.showinfo("Images","Select the folder containing images.")
    d=filedialog.askdirectory(title="Select IMAGES folder")
    if not d: root.destroy(); sys.exit(0)
    CONFIG["images_dir"]=d
    messagebox.showinfo("Labels","Select labels folder. Cancel = images/labels will be created.")
    d2=filedialog.askdirectory(title="Select LABELS folder (Cancel = images/labels)")
    if not d2:
        d2=str(Path(CONFIG["images_dir"])/"labels")
    CONFIG["labels_dir"]=d2
    Path(d2).mkdir(parents=True, exist_ok=True)
    root.destroy()

def gui_initial_class_editor(classes_file: Path, mode: str, model_class_names: Optional[List[str]]=None):
    """
    Manual: ask if user wants to define classes now.
    If yes: open editor (blank if new). If no: leave (possibly empty).
    Auto: select subset of model classes.
    """
    tk, _, messagebox = _tk_safe_import()
    example_text = "Example:\ncar\nperson\ntraffic light"
    # Console path
    if tk is None:
        if mode=="manual":
            define = input("Define classes now? (y/N): ").strip().lower()=='y'
            if define:
                print("Enter class names one per line. Blank line to finish.")
                print(example_text)
                lines=[]
                while True:
                    ln=input()
                    if not ln.strip(): break
                    lines.append(ln.strip())
                if lines:
                    write_classes(classes_file, lines)
                else:
                    if not classes_file.exists():
                        classes_file.write_text("")
        elif mode=="auto" and model_class_names:
            print("Model classes:")
            for i,n in enumerate(model_class_names):
                print(f"{i}: {n}")
            sel=input("Class IDs to detect (comma separated) blank=all: ").strip()
            if sel:
                try:
                    CONFIG["classes_filter_ids"]= [int(s) for s in sel.split(",") if s.strip().isdigit()]
                except:
                    pass
        return
    # GUI path
    if mode=="manual":
        existing=read_classes(classes_file)
        # Ask first
        ask_root = tk.Tk(); ask_root.withdraw()
        if messagebox.askyesno("Classes","Define class names now?"):
            ask_root.destroy()
            root=tk.Tk(); root.title("Class List Editor"); root.geometry("430x420"); root.resizable(True, True)
            tk.Label(root,text="Provide class list (one per line):",font=("Arial",11,"bold"), justify="center").pack(anchor="center", pady=(8,4))
            tk.Label(root,text=example_text,font=("Arial",9,"italic"),fg="gray", justify="center").pack(anchor="center", pady=(0,4))
            txt=tk.Text(root,height=10,width=54, wrap="word")
            txt.pack(padx=8,pady=6, fill="both", expand=True)
            # Do NOT prefill with defaults if new; only show existing if user already had a file
            if existing:
                txt.insert("1.0","\n".join(existing))
            result={"ok":False}
            def save_close():
                lines=[l.strip() for l in txt.get("1.0","end").splitlines() if l.strip()]
                # Allow empty (user can add later)
                write_classes(classes_file, lines)
                result["ok"]=True
                root.destroy()
            tk.Button(root,text="Save & Continue",width=26, height=2, padx=6, pady=4, command=save_close).pack(padx=40, pady=12, fill="x")
            root.mainloop()
            if not result["ok"] and not classes_file.exists():
                classes_file.write_text("")
        else:
            ask_root.destroy()
            if not classes_file.exists():
                classes_file.write_text("")
    elif mode=="auto" and model_class_names:
        root=tk.Tk(); root.title("Select Classes to Detect"); root.geometry("360x500")
        tk.Label(root,text="Select classes for automatic annotation.\n(Ctrl/Shift multi-select; none=ALL)",wraplength=340).pack(padx=8,pady=6)
        lb=tk.Listbox(root,selectmode="extended",width=40,height=20)
        for i,n in enumerate(model_class_names):
            lb.insert("end", f"{i}: {n}")
        lb.pack(padx=8,pady=4,fill="both",expand=True)
        def accept():
            sel=lb.curselection()
            if sel:
                CONFIG["classes_filter_ids"]=list(sel)
            root.destroy()
        tk.Button(root,text="OK",command=accept).pack(pady=8)
        root.mainloop()

###############################################################################
# DETECTION
###############################################################################
def run_detection(model_path: str,
                  images_dir: Path,
                  labels_dir: Path,
                  classes_filter_ids: List[int],
                  conf: float):
    print("[AUTO] Starting automatic annotation")
    t0=time.time()
    model=load_model(model_path)
    names_raw=model.names
    if isinstance(names_raw, dict):
        class_names=[names_raw[i] for i in sorted(names_raw)]
        id_map={i:i for i in sorted(names_raw)}
    else:
        class_names=list(names_raw)
        id_map={i:i for i in range(len(class_names))}
    classes_file=Path(CONFIG["classes_file"])
    if not classes_file.exists():
        write_classes(classes_file, class_names)
    requested=set(classes_filter_ids) & set(id_map.keys()) if classes_filter_ids else set(id_map.keys())
    imgs=collect_images(images_dir)
    if not imgs:
        print("[AUTO] No images found.")
        return
    ensure_dir(labels_dir)
    write_empty=bool(CONFIG.get("write_empty_detection_files"))
    print(f"[AUTO] Images: {len(imgs)} | Classes: {sorted(requested) if classes_filter_ids else 'ALL'} | Empty label files: {'ON' if write_empty else 'OFF'}")
    for i,img_path in enumerate(imgs,1):
        res=model.predict(source=str(img_path), conf=conf, verbose=False)[0]
        lines=[]
        if getattr(res,"boxes",None) is not None and len(res.boxes):
            cls_list=res.boxes.cls.cpu().tolist()
            xywhn=res.boxes.xywhn.cpu().tolist()
            for cid,(xc,yc,w,h) in zip(cls_list,xywhn):
                if int(cid) in requested:
                    lines.append(f"{int(cid)} {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}")
        out=labels_dir / f"{img_path.stem}.txt"
        if lines: out.write_text("\n".join(lines))
        elif write_empty:  # 0.0.3 explicit creation path
            if not out.exists():
                out.write_text("")
        if i % 10 == 0 or i <= 5 or i == len(imgs):
            print(f"[AUTO] {i}/{len(imgs)} {img_path.name} -> {len(lines)} boxes")
    print(f"[AUTO] Done in {time.time()-t0:.2f}s")

###############################################################################
# EDITOR
###############################################################################
class TkLabelEditor:
    HANDLE_SIZE=8
    MIN_PIXELS=6

    def __init__(self, images_dir: Path, labels_dir: Path, classes_file: Path):
        self.images_dir=images_dir
        self.labels_dir=labels_dir
        self.classes_file=classes_file
        self.class_names=read_classes(classes_file)  # may be empty now
        self.images=collect_images(images_dir)
        if not self.images:
            print("[EDITOR] No images.")
            self.valid=False; return
        self.valid=True
        self.index=0
        self.boxes: List[Box]=[]
        self.selected: Optional[int]=None
        self.mode='add'
        self.orig_w=self.orig_h=0
        self.scale=1.0
        self.display_w=self.display_h=0
        self.off_x=self.off_y=0
        self.base_image=None
        self.img_tk=None
        self.drawing=False
        self.start_x=self.start_y=0
        self.curr_x=self.curr_y=0
        self.last_class=0
        self.dragging=False
        self.resizing=False
        self.resize_handle=None
        self.orig_box_disp: Optional[Tuple[float,float,float,float]]=None
        self.press_x=self.press_y=0
        self.return_to_menu=False
        tk, _, _ = _tk_safe_import()
        if tk is None:
            print("Tk not available.")
            self.valid=False; return
        self.tk=tk.Tk()
        self.tk.title("YOLO Manual Annotation / Editing")
        self.canvas=tk.Canvas(self.tk,bg="black",
                              width=CONFIG["display_max_width"],
                              height=CONFIG["display_max_height"],
                              cursor="tcross")
        self.canvas.pack(side="left")
        import tkinter.ttk as ttk
        right=ttk.Frame(self.tk); right.pack(side="right", fill="y")
        self.status_var=tk.StringVar()
        ttk.Label(right,textvariable=self.status_var).pack(anchor="w", padx=4, pady=(4,2))
        btn_frame=ttk.Frame(right); btn_frame.pack(fill="x", pady=4)
        ttk.Button(btn_frame,text="Add Mode (A)",command=self.set_add_mode).grid(row=0,column=0,padx=2,pady=2)
        ttk.Button(btn_frame,text="Edit Mode (E)",command=self.set_edit_mode).grid(row=0,column=1,padx=2,pady=2)
        ttk.Button(btn_frame,text="Change Class (C)",command=self.change_selected_class).grid(row=0,column=2,padx=2,pady=2)
        ttk.Button(btn_frame,text="Manage Classes (M)",command=self.manage_classes).grid(row=1,column=0,columnspan=3,sticky="ew",padx=2,pady=2)
        nav_frame=ttk.Frame(right); nav_frame.pack(fill="x", pady=4)
        ttk.Button(nav_frame,text="Prev (←)",command=self.prev_image).grid(row=0,column=0,padx=2,pady=2)
        ttk.Button(nav_frame,text="Next (→)",command=self.next_image).grid(row=0,column=1,padx=2,pady=2)
        act_frame=ttk.Frame(right); act_frame.pack(fill="x", pady=4)
        ttk.Button(act_frame,text="Info (I)",command=self.show_info).grid(row=0,column=0,padx=2,pady=2)
        ttk.Button(act_frame,text="Del Sel (Del)",command=self.delete_selected).grid(row=0,column=1,padx=2,pady=2)
        ttk.Button(act_frame,text="Del All",command=self.delete_all).grid(row=0,column=2,padx=2,pady=2)
        ttk.Button(right,text="Back to Menu (Q)",command=self.back_to_menu).pack(fill="x", padx=4, pady=(4,2))
        import tkinter as tk2
        self.listbox=tk2.Listbox(right,width=46,height=26,exportselection=False)
        self.listbox.pack(fill="y", padx=4, pady=4)
        self.listbox.bind("<<ListboxSelect>>", self.on_list_select)
        self.listbox.bind("<Delete>", lambda e: self.delete_selected())
        instructions=(
            "Keys:\n"
            "  A: Add  E: Edit  C: Change class\n"
            "  M: Manage classes  Del: Delete sel\n"
            "  ←/→: Prev/Next  Q: Menu  I: Info\n"
            "Mouse:\n"
            "  Add: drag to create box\n"
            "  Edit: drag inside=move, edges=resize,\n"
            "        right-click=delete\n"
            "If no classes yet, add them via M."
        )
        ttk.Label(right,text=instructions,justify="left",wraplength=270).pack(anchor="w", padx=4, pady=4)
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<ButtonPress-3>", self.on_right_click)
        self.tk.bind("<Key>", self.on_key)
        self._load_current_image()

    def image_path(self)->Path:
        return self.images[self.index]

    def label_path(self)->Path:
        return self.labels_dir / f"{self.image_path().stem}.txt"

    def _load_current_image(self):
        from PIL import Image
        p=self.image_path()
        try:
            img=Image.open(p).convert("RGB")
        except:
            print(f"[EDITOR] Failed opening {p}")
            return
        self.orig_w,self.orig_h=img.size
        sw=CONFIG["display_max_width"]/self.orig_w
        sh=CONFIG["display_max_height"]/self.orig_h
        self.scale=min(sw,sh,1.0)
        self.display_w=int(self.orig_w*self.scale)
        self.display_h=int(self.orig_h*self.scale)
        self.off_x=(CONFIG["display_max_width"]-self.display_w)//2
        self.off_y=(CONFIG["display_max_height"]-self.display_h)//2
        self.base_image=img
        self.boxes=load_yolo_label_file(self.label_path())
        self.selected=None
        self.refresh_canvas()
        self.refresh_list()
        self.update_status()

    def norm_to_disp(self,b:Box):
        x1=(b.xc-b.w/2)*self.orig_w*self.scale+self.off_x
        y1=(b.yc-b.h/2)*self.orig_h*self.scale+self.off_y
        x2=(b.xc+b.w/2)*self.orig_w*self.scale+self.off_x
        y2=(b.yc+b.h/2)*self.orig_h*self.scale+self.off_y
        return x1,y1,x2,y2

    def disp_rect_to_box(self,x1,y1,x2,y2):
        x1-=self.off_x; x2-=self.off_x
        y1-=self.off_y; y2-=self.off_y
        inv=1/self.scale
        ox1=max(0,min(self.orig_w,x1*inv))
        oy1=max(0,min(self.orig_h,y1*inv))
        ox2=max(0,min(self.orig_w,x2*inv))
        oy2=max(0,min(self.orig_h,y2*inv))
        if ox2-ox1<2 or oy2-oy1<2: return None
        bw=(ox2-ox1)/self.orig_w
        bh=(oy2-oy1)/self.orig_h
        xc=(ox1+ox2)/2/self.orig_w
        yc=(oy1+oy2)/2/self.orig_h
        return xc,yc,bw,bh

    def refresh_canvas(self):
        from PIL import ImageTk
        disp=self.base_image.resize((self.display_w,self.display_h))
        self.img_tk=ImageTk.PhotoImage(disp)
        c=self.canvas
        c.delete("all")
        c.create_rectangle(0,0,CONFIG["display_max_width"],CONFIG["display_max_height"],fill="gray20",outline="")
        c.create_image(self.off_x,self.off_y,anchor="nw",image=self.img_tk)
        for i,b in enumerate(self.boxes):
            if i==self.selected: continue
            x1,y1,x2,y2=self.norm_to_disp(b)
            c.create_rectangle(x1,y1,x2,y2,outline="cyan",width=1)
        if self.selected is not None and 0<=self.selected<len(self.boxes):
            b=self.boxes[self.selected]
            x1,y1,x2,y2=self.norm_to_disp(b)
            c.create_rectangle(x1,y1,x2,y2,outline="yellow",width=2)
            if self.mode=='edit':
                for hx,hy in self.handle_points(x1,y1,x2,y2):
                    c.create_rectangle(hx-self.HANDLE_SIZE/2,hy-self.HANDLE_SIZE/2,
                                       hx+self.HANDLE_SIZE/2,hy+self.HANDLE_SIZE/2,
                                       outline="orange",fill="black")
        if self.drawing:
            c.create_rectangle(self.start_x,self.start_y,self.curr_x,self.curr_y,
                               outline="lime",dash=(4,2),width=1)

    def refresh_list(self):
        self.listbox.delete(0,'end')
        for i,b in enumerate(self.boxes):
            cname = self.class_names[b.cls] if 0<=b.cls<len(self.class_names) else f"id_{b.cls}?"
            self.listbox.insert('end', f"{i:03d} | cls={b.cls}:{cname} | xc={b.xc:.3f} yc={b.yc:.3f} w={b.w:.3f} h={b.h:.3f}")
        if self.selected is not None:
            self.listbox.selection_clear(0,'end')
            self.listbox.selection_set(self.selected)
            self.listbox.see(self.selected)

    def update_status(self):
        clsinfo=f"{len(self.class_names)} cls" if self.class_names else "NO CLASSES"
        self.status_var.set(f"Image {self.index+1}/{len(self.images)} | Boxes {len(self.boxes)} | {clsinfo} | Mode {self.mode.upper()}")

    def handle_points(self,x1,y1,x2,y2):
        xm=(x1+x2)/2; ym=(y1+y2)/2
        return [(x1,y1),(xm,y1),(x2,y1),(x2,ym),(x2,y2),(xm,y2),(x1,y2),(x1,ym)]

    def which_handle(self,x,y,x1,y1,x2,y2):
        tags=['nw','n','ne','e','se','s','sw','w']
        hs=self.HANDLE_SIZE
        for name,(hx,hy) in zip(tags,self.handle_points(x1,y1,x2,y2)):
            if abs(x-hx)<=hs and abs(y-hy)<=hs: return name
        if x1<=x<=x2 and y1<=y<=y2: return 'move'
        return None

    def find_top_box(self,x,y)->Optional[int]:
        for i in reversed(range(len(self.boxes))):
            x1,y1,x2,y2=self.norm_to_disp(self.boxes[i])
            if x1<=x<=x2 and y1<=y<=y2: return i
        return None

    # Events
    def on_press(self,e):
        # If no classes yet, force manage dialog before drawing
        if self.mode=='add' and not self.class_names:
            self.manage_classes()
            if not self.class_names:
                return
        x,y=e.x,e.y
        if self.mode=='add':
            self.drawing=True
            self.start_x=self.curr_x=x
            self.start_y=self.curr_y=y
            self.refresh_canvas()
            return
        hit=self.find_top_box(x,y)
        if hit is not None:
            self.selected=hit
            x1,y1,x2,y2=self.norm_to_disp(self.boxes[hit])
            h=self.which_handle(x,y,x1,y1,x2,y2)
            if h=='move':
                self.dragging=True
                self.press_x=x; self.press_y=y
                self.orig_box_disp=(x1,y1,x2,y2)
            elif h:
                self.resizing=True
                self.resize_handle=h
                self.press_x=x; self.press_y=y
                self.orig_box_disp=(x1,y1,x2,y2)
        else:
            self.selected=None
        self.refresh_canvas()
        self.refresh_list()

    def on_motion(self,e):
        x,y=e.x,e.y
        if self.drawing:
            self.curr_x=x; self.curr_y=y
            self.refresh_canvas()
        elif self.dragging and self.selected is not None:
            ox1,oy1,ox2,oy2=self.orig_box_disp
            dx=x-self.press_x; dy=y-self.press_y
            nx1=ox1+dx; ny1=oy1+dy; nx2=ox2+dx; ny2=oy2+dy
            minx=self.off_x; maxx=self.off_x+self.display_w
            miny=self.off_y; maxy=self.off_y+self.display_h
            w=nx2-nx1; h=ny2-ny1
            if nx1<minx: nx1=minx; nx2=nx1+w
            if ny1<miny: ny1=miny; ny2=ny1+h
            if nx2>maxx: nx2=maxx; nx1=nx2-w
            if ny2>maxy: ny2=maxy; ny1=ny2-h
            upd=self.disp_rect_to_box(nx1,ny1,nx2,ny2)
            if upd:
                xc,yc,bw,bh=upd
                b=self.boxes[self.selected]; b.xc=xc; b.yc=yc; b.w=bw; b.h=bh
            self.refresh_canvas()
        elif self.resizing and self.selected is not None:
            ox1,oy1,ox2,oy2=self.orig_box_disp
            nx1,ny1,nx2,ny2=ox1,oy1,ox2,oy2
            h=self.resize_handle
            minx=self.off_x; maxx=self.off_x+self.display_w
            miny=self.off_y; maxy=self.off_y+self.display_h
            if 'n' in h: ny1=min(max(miny,y),ny2-self.MIN_PIXELS)
            if 's' in h: ny2=max(ny1+self.MIN_PIXELS,min(maxy,y))
            if 'w' in h: nx1=min(max(minx,x),nx2-self.MIN_PIXELS)
            if 'e' in h: nx2=max(nx1+self.MIN_PIXELS,min(maxx,x))
            upd=self.disp_rect_to_box(nx1,ny1,nx2,ny2)
            if upd:
                xc,yc,bw,bh=upd
                b=self.boxes[self.selected]; b.xc=xc; b.yc=yc; b.w=bw; b.h=bh
            self.refresh_canvas()

    def on_release(self,e):
        changed=False
        if self.drawing:
            x1,y1=self.start_x,self.start_y
            x2,y2=e.x,e.y
            if abs(x2-x1)>4 and abs(y2-y1)>4:
                if x1>x2: x1,x2=x2,x1
                if y1>y2: y1,y2=y2,y1
                upd=self.disp_rect_to_box(x1,y1,x2,y2)
                if upd:
                    xc,yc,bw,bh=upd
                    # If classes empty still, abort
                    if not self.class_names:
                        print("[WARN] No classes defined. Box discarded.")
                    else:
                        self.boxes.append(Box(self.last_class,xc,yc,bw,bh))
                        self.selected=len(self.boxes)-1
                        changed=True
            self.drawing=False
        if self.dragging or self.resizing:
            changed=True
        self.dragging=False
        self.resizing=False
        self.resize_handle=None
        self.orig_box_disp=None
        if changed:
            self.autosave()
        self.refresh_list()
        self.refresh_canvas()

    def on_right_click(self,e):
        if self.mode!='edit': return
        hit=self.find_top_box(e.x,e.y)
        if hit is not None:
            del self.boxes[hit]
            if self.selected==hit: self.selected=None
            elif self.selected and self.selected>hit: self.selected-=1
            self.autosave()
            self.refresh_list()
            self.refresh_canvas()

    # Commands
    def set_add_mode(self):
        self.mode='add'
        self.refresh_canvas()
        self.update_status()

    def set_edit_mode(self):
        self.mode='edit'
        self.refresh_canvas()
        self.update_status()

    def delete_selected(self):
        if self.selected is not None and 0<=self.selected<len(self.boxes):
            del self.boxes[self.selected]
            self.selected=None
            self.autosave()
            self.refresh_list()
            self.refresh_canvas()

    def delete_all(self):
        if self.boxes:
            self.boxes.clear()
            self.selected=None
            self.autosave()
            self.refresh_list()
            self.refresh_canvas()

    def on_list_select(self,e):
        sel=self.listbox.curselection()
        if sel:
            self.selected=sel[0]
            self.refresh_canvas()

    def change_selected_class(self):
        if self.selected is None:
            return
        if not self.class_names:
            self.manage_classes()
            if not self.class_names:
                return
        tk, _, _ = _tk_safe_import()
        if tk is None: return
        dlg=tk.Toplevel(self.tk); dlg.title("Select Class")
        import tkinter.ttk as ttk
        lb=tk.Listbox(dlg,height=min(20,len(self.class_names)),width=34)
        for i,c in enumerate(self.class_names):
            lb.insert("end", f"{i}: {c}")
        lb.pack(padx=6,pady=6)
        cur=self.boxes[self.selected].cls
        if 0<=cur<len(self.class_names):
            lb.selection_set(cur)
        def ok():
            s=lb.curselection()
            if s:
                self.boxes[self.selected].cls=s[0]
                self.last_class=s[0]
                self.autosave()
                self.refresh_list()
                self.refresh_canvas()
            dlg.destroy()
        import tkinter as tk2
        tk2.Button(dlg,text="OK",width=12,command=ok).pack(pady=4)
        dlg.grab_set(); dlg.wait_window()

    def manage_classes(self):
        tk, _, _ = _tk_safe_import()
        if tk is None: return
        dlg=tk.Toplevel(self.tk); dlg.title("Manage Classes"); dlg.geometry("340x420")
        import tkinter.ttk as ttk
        ttk.Label(dlg,text="Current Classes (index: name)",font=("Arial",10,"bold")).pack(anchor="w", padx=8, pady=(8,4))
        lb=tk.Listbox(dlg,height=14,width=34)
        lb.pack(padx=8,pady=4,fill="both",expand=True)
        def refresh_lb():
            lb.delete(0,'end')
            for i,c in enumerate(self.class_names):
                lb.insert('end', f"{i}: {c}")
        refresh_lb()
        frm=ttk.Frame(dlg); frm.pack(fill="x", padx=8, pady=6)
        new_var=tk.StringVar()
        ttk.Entry(frm,textvariable=new_var,width=28).grid(row=0,column=0,padx=2,pady=2)
        def add_class():
            name=new_var.get().strip()
            if not name: return
            self.class_names.append(name)
            self.last_class=len(self.class_names)-1
            write_classes(self.classes_file, self.class_names)
            refresh_lb()
            self.update_status()
            new_var.set("")
        def rename_class():
            sel=lb.curselection()
            if not sel: return
            idx=sel[0]
            name=new_var.get().strip()
            if not name: return
            self.class_names[idx]=name
            write_classes(self.classes_file, self.class_names)
            refresh_lb()
            self.update_status()
        ttk.Button(frm,text="Add",width=8,command=add_class).grid(row=0,column=1,padx=4)
        ttk.Button(frm,text="Rename Sel",width=12,command=rename_class).grid(row=0,column=2,padx=4)
        def close():
            self.refresh_list()
            self.refresh_canvas()
            dlg.destroy()
        ttk.Button(dlg,text="Close",command=close).pack(pady=8)
        dlg.grab_set(); dlg.wait_window()

    def show_info(self):
        print(f"[INFO] {self.image_path().name} ({self.index+1}/{len(self.images)})")
        for i,b in enumerate(self.boxes):
            cname=self.class_names[b.cls] if 0<=b.cls<len(self.class_names) else f"id_{b.cls}?"
            print(f"  {i}: {cname} ({b.cls}) xc={b.xc:.3f} yc={b.yc:.3f} w={b.w:.3f} h={b.h:.3f}")

    def next_image(self):
        if self.index < len(self.images)-1:
            self.index+=1
            self._load_current_image()

    def prev_image(self):
        if self.index > 0:
            self.index-=1
            self._load_current_image()

    def autosave(self):
        save_yolo_label_file(self.label_path(), self.boxes)

    def back_to_menu(self):
        self.return_to_menu=True
        self.tk.destroy()

    def on_key(self,e):
        k=e.keysym.lower()
        if k=='q': self.back_to_menu()
        elif k=='a': self.set_add_mode()
        elif k=='e': self.set_edit_mode()
        elif k=='c': self.change_selected_class()
        elif k=='m': self.manage_classes()
        elif k=='delete': self.delete_selected()
        elif k=='left': self.prev_image()
        elif k=='right': self.next_image()
        elif k=='i': self.show_info()
        elif k=='escape':
            self.drawing=False; self.dragging=False; self.resizing=False
            self.refresh_canvas()

    def loop(self):
        if not self.valid: return False
        self.tk.mainloop()
        return self.return_to_menu

###############################################################################
# WORKFLOW
###############################################################################
def validate_and_fill():
    if not CONFIG["images_dir"]:
        print("Images directory not set."); sys.exit(1)
    if not CONFIG["labels_dir"]:
        CONFIG["labels_dir"]=str(Path(CONFIG["images_dir"])/"labels")
    if not CONFIG["classes_file"]:
        CONFIG["classes_file"]=str(Path(CONFIG["labels_dir"])/"classes.txt")

def run_mode(mode: str):
    images_dir=Path(CONFIG["images_dir"])
    labels_dir=Path(CONFIG["labels_dir"])
    classes_file=Path(CONFIG["classes_file"])
    ensure_dir(labels_dir)
    if mode=="auto":
        run_detection(CONFIG["model_path"], images_dir, labels_dir,
                      CONFIG["classes_filter_ids"], float(CONFIG["conf"]))
        if CONFIG.get("open_editor_after_detect"):
            editor=TkLabelEditor(images_dir, labels_dir, classes_file)
            while editor.loop(): return True
        return True
    elif mode=="manual":
        editor=TkLabelEditor(images_dir, labels_dir, classes_file)
        while editor.loop(): return True
        return False
    return False

def main():
    while True:
        if CONFIG.get("force_mode_dialog",True) or not CONFIG["mode"]:
            m=gui_mode_selection()
            if not m or m=="quit": break
            CONFIG["mode"]=m
        gui_pick_folders(CONFIG["mode"])
        if CONFIG["mode"]=="auto":
            if not CONFIG["model_path"]:
                mp=gui_select_model()
                if not mp:
                    print("Model not selected. Exiting.")
                    return
                CONFIG["model_path"]=mp
            temp_model=load_model(CONFIG["model_path"])
            names_raw=temp_model.names
            if isinstance(names_raw, dict):
                model_names=[names_raw[i] for i in sorted(names_raw)]
            else:
                model_names=list(names_raw)
            if not CONFIG["classes_file"]:
                CONFIG["classes_file"]=str(Path(CONFIG["labels_dir"])/"classes.txt")
            gui_initial_class_editor(Path(CONFIG["classes_file"]), "auto", model_class_names=model_names)
        else:
            if not CONFIG["classes_file"]:
                CONFIG["classes_file"]=str(Path(CONFIG["labels_dir"])/"classes.txt")
            gui_initial_class_editor(Path(CONFIG["classes_file"]), "manual")
        validate_and_fill()
        run_mode(CONFIG["mode"])
        CONFIG["mode"]=""  # back to menu

if __name__ == "__main__":
    main()
