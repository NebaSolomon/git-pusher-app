import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess, os, sys, shlex, shutil

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
        project_var.set(folder)

def push_to_git():
    project = project_var.get().strip()
    version = version_var.get().strip() or "v1.0"
    repo    = repo_var.get().strip()
    branch  = branch_var.get().strip() or "main"

    if not project or not repo:
        messagebox.showerror("Error", "Please provide project folder and repo URL.")
        return

    bash_exe = find_git_bash()
    if not bash_exe:
        messagebox.showerror("Error", "Git Bash not found. Install Git for Windows.")
        return

    sh_script = resource_path("base", "push_it.sh")
    if not os.path.exists(sh_script):
        messagebox.showerror("Error", f"push_it.sh not found at:\n{sh_script}")
        return

    cmd = [bash_exe, "-c", f"bash {shlex.quote(sh_script)} {shlex.quote(project)} {shlex.quote(version)} {shlex.quote(repo)} {shlex.quote(branch)}"]

    try:
        subprocess.run(cmd, check=True)
        messagebox.showinfo("Success", f"Pushed to {repo} ({branch}, {version})")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Failed", f"Push failed.\n\n{e}")

# ---- UI ----
root = tk.Tk()
root.title("Git Pusher App")
root.geometry("520x340")
root.resizable(False, False)

# Window/EXE icon
try:
    icon_path = resource_path("pusher.ico")
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
except Exception:
    pass

padx = 18

tk.Label(root, text="Project Folder:").pack(anchor="w", padx=padx, pady=(16,5))
project_var = tk.StringVar()
tk.Entry(root, textvariable=project_var, width=60).pack(padx=padx)
tk.Button(root, text="Browse", command=browse_folder).pack(padx=padx, pady=6)

tk.Label(root, text="Version (e.g. v1.0):").pack(anchor="w", padx=padx)
version_var = tk.StringVar()
tk.Entry(root, textvariable=version_var, width=25).pack(padx=padx, pady=6)

tk.Label(root, text="Repository URL:").pack(anchor="w", padx=padx)
repo_var = tk.StringVar()
tk.Entry(root, textvariable=repo_var, width=60).pack(padx=padx, pady=6)

tk.Label(root, text="Branch (default main):").pack(anchor="w", padx=padx)
branch_var = tk.StringVar()
tk.Entry(root, textvariable=branch_var, width=25).pack(padx=padx, pady=6)

tk.Button(root, text="🚀 Push to Git", width=20, command=push_to_git).pack(pady=18)

root.mainloop()
