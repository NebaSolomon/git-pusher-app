import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess, os, sys, shlex, shutil
from tkinterdnd2 import DND_FILES, TkinterDnD

# ---------- paths & helpers ----------
def resource_path(*parts):
    base = getattr(sys, "_MEIPASS", os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    return os.path.normpath(os.path.join(base, *parts))

def find_git_bash():
    candidates = [
        r"C:\Program Files\Git\git-bash.exe",
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files (x86)\Git\git-bash.exe",
        r"C:\Program Files (x86)\Git\bin\bash.exe",
        shutil.which("git-bash.exe") or "",
        shutil.which("bash.exe") or "",
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None

def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        set_project_folder(folder)

def set_project_folder(folder_path):
    """Set the project folder and validate it"""
    if folder_path and os.path.isdir(folder_path):
        project_var.set(folder_path)
        clear_error("project")
        set_status(f"Project folder set: {os.path.basename(folder_path)}", "ok")
    else:
        show_error("project", "Invalid folder path")
        set_status("Invalid folder - please select a valid directory", "error")

def handle_drag_enter(event):
    """Handle drag enter events - visual feedback"""
    entry_project.configure(style="DragOver.TEntry")
    drag_hint.configure(text="📁 Drop folder here!")

def handle_drag_leave(event):
    """Handle drag leave events - reset visual feedback"""
    entry_project.configure(style="TEntry")
    drag_hint.configure(text="💡 Tip: Drag and drop a folder here!")

def handle_drop(event):
    """Handle drag and drop events"""
    # Reset visual feedback
    entry_project.configure(style="TEntry")
    drag_hint.configure(text="💡 Tip: Drag and drop a folder here!")
    
    files = root.tk.splitlist(event.data)
    if files:
        # Take the first dropped item
        dropped_path = files[0]
        # Remove quotes if present
        dropped_path = dropped_path.strip('"\'')
        
        if os.path.isdir(dropped_path):
            set_project_folder(dropped_path)
        elif os.path.isfile(dropped_path):
            # If a file is dropped, use its parent directory
            parent_dir = os.path.dirname(dropped_path)
            set_project_folder(parent_dir)
        else:
            show_error("project", "Invalid path - please drop a folder")
            set_status("Please drop a valid folder, not a file", "error")

def push_to_git(event=None):
    project = project_var.get().strip()
    version = version_var.get().strip() or "v1.0"
    repo    = repo_var.get().strip()
    branch  = branch_var.get().strip() or "main"
    commit  = commit_var.get().strip()
    whats_new = whats_new_box.get("1.0", "end").strip()

    ok_all = True
    if not project:
        show_error("project", "Required")
        ok_all = False
    if not repo:
        show_error("repo", "Required")
        ok_all = False
    if not ok_all:
        set_status("Please fill the required fields.", "warn")
        return

    bash_exe = find_git_bash()
    if not bash_exe:
        messagebox.showerror("Error", "Git Bash not found. Install Git for Windows.")
        set_status("Git Bash not found.", "error")
        return

    sh_script = resource_path("base", "push_it.sh")
    if not os.path.exists(sh_script):
        messagebox.showerror("Error", f"push_it.sh not found at:\n{sh_script}")
        set_status("push_it.sh not found.", "error")
        return

    # Build command (commit is arg5). What's-new sent via ENV (supports multiline)
    cmd = [
        bash_exe, "-c",
        f"bash {shlex.quote(sh_script)} "
        f"{shlex.quote(project)} {shlex.quote(version)} "
        f"{shlex.quote(repo)} {shlex.quote(branch)} "
        f"{shlex.quote(commit)}"
    ]
    env = os.environ.copy()
    if whats_new:
        env["WHATS_NEW"] = whats_new

    # Disable push button during run
    push_btn.config(state="disabled")
    set_status("Pushing… please wait.", "info")
    root.update_idletasks()

    try:
        subprocess.run(cmd, check=True, env=env)
        human_commit = commit if commit else f"Git Pusher {version}"
        msg = f"Commit:\n{human_commit}\n\nPushed to:\n{repo}\nBranch: {branch}\nTag: {version}"
        if whats_new:
            msg += "\n\nWhat's new saved to WHATS_NEW.txt"
        messagebox.showinfo("Success", msg)
        set_status("Push completed successfully.", "ok")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Failed", f"Push failed.\n\n{e}")
        set_status("Push failed. See error.", "error")
    finally:
        push_btn.config(state="normal")

# ---------- UI (Dark theme) ----------
BG      = "#0f1115"  # window
PANEL   = "#151821"  # card panels
ENTRYBG = "#1c2130"
TEXTBG  = "#121520"
FG      = "#e6e6e6"
FG_DIM  = "#b9c0cb"
ACCENT  = "#4c8bf5"  # blue
WARN    = "#ffb454"
ERR     = "#ff6b6b"
OK      = "#49c774"

root = TkinterDnD.Tk()
root.title("Git Pusher App")
root.geometry("860x620")
root.configure(bg=BG)
root.resizable(False, False)

# Enable drag and drop for the entire window
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', handle_drop)

# icon
try:
    icon_path = resource_path("pusher.ico")
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
except Exception:
    pass

# ttk style
style = ttk.Style()
try:
    style.theme_use("clam")
except Exception:
    pass

style.configure(".", background=BG, foreground=FG)
style.configure("TLabel", background=PANEL, foreground=FG, font=("Segoe UI", 10))
style.configure("Header.TLabel", background=BG, foreground=FG, font=("Segoe UI Semibold", 14))
style.configure("Hint.TLabel", background=PANEL, foreground=FG_DIM, font=("Segoe UI", 9))

style.configure("Card.TFrame", background=PANEL, relief="flat")
style.configure("TEntry", fieldbackground=ENTRYBG, foreground=FG)
style.map("TEntry", fieldbackground=[("focus", ENTRYBG)], bordercolor=[("focus", ACCENT)])
style.configure("TButton", background=ACCENT, foreground="white", font=("Segoe UI Semibold", 10), relief="flat")
style.map("TButton",
          background=[("active", "#5b95f6"), ("disabled", "#3a4461")],
          foreground=[("disabled", "#d0d0d0")])

# containers
outer = ttk.Frame(root, style="Card.TFrame")
outer.place(relx=0.5, rely=0.02, anchor="n", width=820, height=540)

title = ttk.Label(root, text="Git Pusher App", style="Header.TLabel")
title.place(x=20, y=12)

# sections (cards)
card1 = ttk.Frame(outer, style="Card.TFrame")
card2 = ttk.Frame(outer, style="Card.TFrame")
card3 = ttk.Frame(outer, style="Card.TFrame")

for c in (card1, card2, card3):
    c.pack(fill="x", padx=16, pady=12, ipady=8)

# --- Card 1: Project & Repo ---
ttk.Label(card1, text="Project & Repository", style="Header.TLabel").grid(row=0, column=0, columnspan=3, sticky="w", padx=12, pady=(10, 6))

# Add drag and drop hint
drag_hint = ttk.Label(card1, text="💡 Tip: Drag and drop a folder here!", style="Hint.TLabel")
drag_hint.grid(row=0, column=3, sticky="e", padx=12, pady=(10, 6))

def labeled_entry(frame, label, var, width=64, col=0, row=0, placeholder=""):
    ttk.Label(frame, text=label).grid(row=row, column=col, sticky="w", padx=12, pady=6)
    e = ttk.Entry(frame, textvariable=var, width=width)
    e.grid(row=row, column=col+1, sticky="we", padx=12, pady=6)
    if placeholder and not var.get():
        var.set(placeholder)
        e.icursor(0)
        e.select_range(0, tk.END)
    return e

project_var = tk.StringVar()
entry_project = labeled_entry(card1, "Project Folder *", project_var, width=68, row=1)

# Enable drag and drop for the project entry field
entry_project.drop_target_register(DND_FILES)
entry_project.dnd_bind('<<Drop>>', handle_drop)
entry_project.dnd_bind('<<DragEnter>>', handle_drag_enter)
entry_project.dnd_bind('<<DragLeave>>', handle_drag_leave)

def set_project_from_dialog():
    folder = filedialog.askdirectory()
    if folder:
        set_project_folder(folder)

ttk.Button(card1, text="Browse…", command=set_project_from_dialog).grid(row=1, column=2, padx=6, pady=6)

repo_var = tk.StringVar()
entry_repo = labeled_entry(card1, "Repository URL *", repo_var, width=68, row=2, placeholder="https://github.com/USER/REPO.git")

branch_var = tk.StringVar(value="main")
entry_branch = labeled_entry(card1, "Branch", branch_var, width=30, row=3)

# --- Card 2: Version & Commit ---
ttk.Label(card2, text="Version & Commit", style="Header.TLabel").grid(row=0, column=0, columnspan=3, sticky="w", padx=12, pady=(10, 6))

version_var = tk.StringVar(value="v1.0")
entry_version = labeled_entry(card2, "Version (tag)", version_var, width=24, row=1)

commit_var = tk.StringVar()
entry_commit = labeled_entry(card2, "Commit message", commit_var, width=68, row=2)

# --- Card 3: What's New (multiline) ---
ttk.Label(card3, text="What's New (optional)", style="Header.TLabel").grid(row=0, column=0, sticky="w", padx=12, pady=(10, 6))
whats_new_box = tk.Text(card3, height=10, width=90, bg=TEXTBG, fg=FG, insertbackground=FG, relief="flat", wrap="word")
whats_new_box.grid(row=1, column=0, columnspan=3, sticky="we", padx=12, pady=(4, 10))

# push button
push_btn = ttk.Button(root, text="🚀  Push Now", command=push_to_git)
push_btn.place(relx=0.5, rely=0.90, anchor="center", width=220, height=38)

# status bar
status_var = tk.StringVar(value="Ready.")
status = tk.Label(root, textvariable=status_var, bg=PANEL, fg=FG_DIM, anchor="w")
status.place(relx=0, rely=1.0, anchor="sw", relwidth=1.0, height=26)

def set_status(text, kind="info"):
    status_var.set(text)
    if kind == "ok":
        status.config(fg=OK)
    elif kind == "warn":
        status.config(fg=WARN)
    elif kind == "error":
        status.config(fg=ERR)
    else:
        status.config(fg=FG_DIM)

# inline validation helpers
errors = {}
def show_error(field, msg):
    errors[field] = msg
    if field == "project":
        entry = entry_project
    elif field == "repo":
        entry = entry_repo
    else:
        return
    entry.configure(style="Invalid.TEntry")
    set_status(msg, "warn")

def clear_error(field):
    if field in errors:
        del errors[field]
    entry_project.configure(style="TEntry")
    entry_repo.configure(style="TEntry")

# style for invalid entries
style.configure("Invalid.TEntry", fieldbackground="#3a2530", foreground=FG)
style.map("Invalid.TEntry", fieldbackground=[("focus", "#3a2530")])

# style for drag over state
style.configure("DragOver.TEntry", fieldbackground="#2a3a4a", foreground=FG, bordercolor=ACCENT)
style.map("DragOver.TEntry", fieldbackground=[("focus", "#2a3a4a")])

# shortcuts
root.bind("<Control-Return>", push_to_git)

# responsive columns
for f in (card1, card2, card3):
    f.grid_columnconfigure(1, weight=1)

root.mainloop()
