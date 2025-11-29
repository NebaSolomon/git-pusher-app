import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import subprocess, os, sys, shlex, shutil
import re
from urllib.parse import urlparse

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

# ---------- Security validation functions ----------
def validate_repo_url(url: str) -> tuple[bool, str]:
    """Validate repository URL format and safety"""
    if not url or not url.strip():
        return False, "Repository URL is required"
    
    url = url.strip()
    
    # Allow only HTTPS, SSH (git@), or HTTP protocols
    allowed_schemes = ['https', 'http', 'git', 'ssh']
    parsed = urlparse(url)
    
    # Check if it's an SSH format (git@github.com:user/repo.git)
    if '@' in url and ':' in url and not url.startswith('http'):
        # SSH format: git@host:path
        parts = url.split('@', 1)
        if len(parts) == 2 and ':' in parts[1]:
            host_path = parts[1].split(':', 1)
            if len(host_path) == 2:
                # Validate SSH host (basic check)
                if not re.match(r'^[a-zA-Z0-9\.\-]+$', host_path[0]):
                    return False, "Invalid SSH host format"
                # Valid SSH format
                return True, ""
    
    # Check HTTP/HTTPS format
    if parsed.scheme and parsed.scheme not in allowed_schemes:
        return False, f"Invalid protocol. Only HTTPS, SSH, or HTTP allowed."
    
    # Block dangerous patterns
    dangerous_patterns = [
        r'[;&|`$]',  # Command injection attempts
        r'\.\./',     # Path traversal
        r'%00',       # Null byte
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, url):
            return False, f"URL contains potentially dangerous characters"
    
    return True, ""

def validate_branch_name(branch: str) -> tuple[bool, str]:
    """Validate branch name safety"""
    if not branch:
        return False, "Branch name cannot be empty"
    
    # Git branch name rules
    if re.search(r'[~^:?*\[\]\\]', branch):
        return False, "Branch name contains invalid characters"
    
    if branch.startswith('.') or branch.endswith('.'):
        return False, "Branch name cannot start or end with a dot"
    
    if '..' in branch or '@{' in branch:
        return False, "Branch name contains dangerous patterns"
    
    if len(branch) > 255:
        return False, "Branch name too long (max 255 characters)"
    
    return True, ""

def validate_version_tag(version: str) -> tuple[bool, str]:
    """Validate version tag safety"""
    if not version:
        return True, ""  # Optional field
    
    # Allow semantic versioning: v1.0, v1.2.3, etc.
    if not re.match(r'^v?\d+\.\d+(\.\d+)?(-[a-zA-Z0-9]+)?$', version):
        return False, "Invalid version format. Use: v1.0, v1.2.3, etc."
    
    # Check for dangerous characters
    if re.search(r'[;&|`$<>]', version):
        return False, "Version tag contains dangerous characters"
    
    return True, ""

def validate_project_path(path: str) -> tuple[bool, str]:
    """Validate project path is safe and exists"""
    if not path:
        return False, "Path is required"
    
    # Resolve to absolute path
    try:
        abs_path = os.path.abspath(os.path.normpath(path))
    except Exception:
        return False, "Invalid path format"
    
    # Check if path exists
    if not os.path.exists(abs_path):
        return False, "Path does not exist"
    
    if not os.path.isdir(abs_path):
        return False, "Path is not a directory"
    
    # Prevent access to system directories (Windows)
    dangerous_paths = [
        r'C:\Windows',
        r'C:\Program Files',
        r'C:\Program Files (x86)',
        r'C:\System32',
    ]
    
    for dangerous in dangerous_paths:
        if abs_path.lower().startswith(dangerous.lower()):
            return False, f"Cannot use system directories: {dangerous}"
    
    # Check for path traversal attempts
    if '..' in path:
        # Resolved path should not contain these in a dangerous way
        normalized = os.path.normpath(abs_path)
        if '..' in normalized:
            return False, "Path contains invalid traversal characters"
    
    return True, abs_path

def sanitize_env_var(value: str) -> str:
    """Sanitize environment variable to prevent injection"""
    # Remove null bytes and control characters
    value = value.replace('\x00', '').replace('\r', '')
    # Limit length to prevent DoS
    if len(value) > 10000:
        value = value[:10000]
    return value

def verify_git_auth(repo_url: str, bash_exe: str) -> tuple[bool, str]:
    """Verify Git authentication before attempting push"""
    try:
        # Test if we can access the repository
        test_cmd = [
            bash_exe, "-c",
            f"git ls-remote --heads {shlex.quote(repo_url)} 2>&1"
        ]
        
        result = subprocess.run(
            test_cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.lower()
            if 'permission denied' in error_msg or 'authentication' in error_msg:
                return False, "Authentication failed. Check your SSH keys or credentials."
            elif 'not found' in error_msg:
                return False, "Repository not found or you don't have access."
            else:
                return False, f"Cannot access repository: {result.stderr[:200]}"
        
        return True, ""
    except subprocess.TimeoutExpired:
        return False, "Connection timeout. Check your internet connection."
    except Exception as e:
        return False, f"Error verifying access: {str(e)}"

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

def push_to_git(event=None):
    """Push to Git - main function called by button click"""
    try:
        # Debug: Confirm function is being called
        set_status("Button clicked - starting push...", "info")
        root.update_idletasks()
        
        # Get values from UI
        project = project_var.get().strip()
        version = version_var.get().strip() or "v1.0"
        repo    = repo_var.get().strip()
        branch  = branch_var.get().strip() or "main"
        commit  = commit_var.get().strip()
        whats_new = whats_new_box.get("1.0", "end-1c").strip()  # CTkTextbox uses same indexing as tk.Text, end-1c removes trailing newline

        # Validate project path
        if not project:
            show_error("project", "Required")
            set_status("Please fill the required fields.", "warn")
            return
        
        path_valid, path_error = validate_project_path(project)
        if not path_valid:
            show_error("project", path_error)
            set_status(path_error, "error")
            return
        
        # Use validated absolute path
        project = path_error  # validate_project_path returns (bool, abs_path)
        
        # Validate repository URL
        if not repo:
            show_error("repo", "Required")
            set_status("Please fill the required fields.", "warn")
            return
        
        repo_valid, repo_error = validate_repo_url(repo)
        if not repo_valid:
            show_error("repo", repo_error)
            set_status(repo_error, "error")
            return
        
        # Validate branch name
        branch_valid, branch_error = validate_branch_name(branch)
        if not branch_valid:
            set_status(branch_error, "error")
            messagebox.showerror("Invalid Branch", branch_error)
            return
        
        # Validate version tag
        version_valid, version_error = validate_version_tag(version)
        if not version_valid:
            set_status(version_error, "error")
            messagebox.showerror("Invalid Version", version_error)
            return
        
        # Sanitize commit message (remove dangerous characters)
        if commit:
            commit = re.sub(r'[`$]', '', commit)  # Remove backticks and dollar signs
            if len(commit) > 500:
                commit = commit[:500]
                set_status("Commit message truncated to 500 characters", "warn")

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

        # Verify authentication before proceeding
        push_btn.configure(state="disabled")
        set_status("Verifying repository access...", "info")
        root.update_idletasks()
        
        auth_ok, auth_error = verify_git_auth(repo, bash_exe)
        if not auth_ok:
            messagebox.showerror("Authentication Error", 
                                f"Cannot access repository:\n\n{auth_error}\n\n"
                                "Please verify:\n"
                                "• SSH keys are configured (for SSH URLs)\n"
                                "• Credentials are saved (for HTTPS URLs)\n"
                                "• You have push access to this repository")
            set_status("Authentication failed", "error")
            push_btn.configure(state="normal")
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
            env["WHATS_NEW"] = sanitize_env_var(whats_new)

        # Disable push button during run
        set_status("Pushing… please wait.", "info")
        root.update_idletasks()

        try:
            result = subprocess.run(
                cmd, 
                check=True, 
                env=env,
                timeout=300,  # 5 minute timeout
                capture_output=True,
                text=True
            )
            human_commit = commit if commit else f"Git Pusher {version}"
            msg = f"Commit:\n{human_commit}\n\nPushed to:\n{repo}\nBranch: {branch}\nTag: {version}"
            if whats_new:
                msg += "\n\nWhat's new saved to WHATS_NEW.txt"
            messagebox.showinfo("Success", msg)
            set_status("Push completed successfully.", "ok")
        except subprocess.TimeoutExpired:
            messagebox.showerror("Timeout", 
                                "Operation timed out after 5 minutes.\n"
                                "The repository might be too large or network is slow.")
            set_status("Operation timed out", "error")
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if hasattr(e, 'stderr') and e.stderr else str(e)
            messagebox.showerror("Failed", f"Push failed.\n\n{error_msg}")
            set_status("Push failed. See error.", "error")
    except NameError as e:
        # Handle case where variables might not be defined
        error_msg = f"Variable not found: {str(e)}\n\nThis might indicate a code order issue."
        messagebox.showerror("Configuration Error", error_msg)
        set_status(f"Error: Variable not found - {str(e)}", "error")
        import traceback
        print(f"NameError traceback:\n{traceback.format_exc()}")
    except AttributeError as e:
        # Handle case where UI elements might not be accessible
        error_msg = f"UI element not found: {str(e)}\n\nPlease check that all UI elements are properly initialized."
        messagebox.showerror("UI Error", error_msg)
        set_status(f"Error: UI element issue - {str(e)}", "error")
        import traceback
        print(f"AttributeError traceback:\n{traceback.format_exc()}")
    except Exception as e:
        # Catch any other unexpected errors
        error_msg = f"Unexpected error occurred:\n\n{str(e)}\n\nType: {type(e).__name__}"
        messagebox.showerror("Unexpected Error", error_msg)
        set_status(f"Error: {str(e)}", "error")
        import traceback
        print(f"Unexpected error traceback:\n{traceback.format_exc()}")
    finally:
        push_btn.configure(state="normal")

# ---------- UI (ServiceToon-inspired design) ----------
# Dark blue-green gradient with teal accents
BG      = "#0a0e1a"  # Deep dark blue background
PANEL   = "#0f1625"  # Dark blue panel with slight transparency
ENTRYBG = "#151b2e"  # Darker blue for inputs
TEXTBG  = "#0f1625"  # Text area background
FG      = "#ffffff"  # White text
FG_DIM  = "#7dd3fc"  # Light teal for hints
ACCENT  = "#00d9ff"  # Bright teal/cyan (ServiceToon style)
ACCENT_DARK = "#00a8cc"  # Darker teal for hover
WARN    = "#ffb454"
ERR     = "#ff6b6b"
OK      = "#00ff88"  # Teal-green for success
GLOW    = "#00d9ff"  # Glowing border color

# Set CustomTkinter appearance
ctk.set_appearance_mode("dark")
# Custom color theme matching ServiceToon design

# Create root window with drag and drop support
# CustomTkinter works with TkinterDnD by using the underlying tk window
root = ctk.CTk()
root.title("Git Pusher App")
root.geometry("900x750")
root.minsize(850, 650)  # Minimum size to ensure buttons are visible
root.resizable(True, True)  # Allow resizing so users can see all content
root.configure(fg_color=BG)  # Set background color


# icon
try:
    icon_path = resource_path("pusher.ico")
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
except Exception:
    pass

# Main container - simplified layout
content_frame = ctk.CTkFrame(root, corner_radius=0, fg_color="transparent")
content_frame.pack(fill="both", expand=True, padx=20, pady=(20, 0))  # Less bottom padding for button

# Title - ServiceToon style
title = ctk.CTkLabel(
    content_frame,
    text="GIT PUSHER",
    font=ctk.CTkFont(size=32, weight="bold"),
    text_color=ACCENT
)
title.pack(pady=(0, 10))
subtitle = ctk.CTkLabel(
    content_frame,
    text="Push your projects to GitHub with ease",
    font=ctk.CTkFont(size=12),
    text_color=FG_DIM
)
subtitle.pack(pady=(0, 20))

# Push button frame - pack FIRST to reserve space at bottom
button_frame = ctk.CTkFrame(content_frame, corner_radius=0, fg_color="transparent")
push_btn = ctk.CTkButton(
    button_frame,
    text="🚀 Push to Git",
    command=push_to_git,
    height=55,
    corner_radius=14,
    font=ctk.CTkFont(size=18, weight="bold"),
    fg_color=ACCENT_DARK,
    hover_color=ACCENT,
    border_width=2,
    border_color=GLOW,
    text_color="white"
)
push_btn.pack(pady=10, fill="x", padx=20)
button_frame.pack(fill="x", padx=0, pady=(0, 10), side="bottom")

# Outer container for cards - scrollable
# Pack AFTER button_frame so it fills remaining space
outer = ctk.CTkScrollableFrame(content_frame, corner_radius=0, fg_color="transparent")
outer.pack(fill="both", expand=True)

# sections (cards) with rounded corners and glowing borders (ServiceToon style)
card1 = ctk.CTkFrame(outer, corner_radius=16, fg_color=PANEL, border_width=2, border_color=GLOW)
card2 = ctk.CTkFrame(outer, corner_radius=16, fg_color=PANEL, border_width=2, border_color=GLOW)
card3 = ctk.CTkFrame(outer, corner_radius=16, fg_color=PANEL, border_width=2, border_color=GLOW)

for c in (card1, card2, card3):
    c.pack(fill="x", padx=0, pady=12)

# --- Card 1: Project & Repo ---
card1_header = ctk.CTkFrame(card1, fg_color="transparent")
card1_header.pack(fill="x", padx=20, pady=(15, 10))
ctk.CTkLabel(
    card1_header,
    text="Project & Repository",
    font=ctk.CTkFont(size=18, weight="bold"),
    text_color=ACCENT
).pack(side="left")
drag_hint = ctk.CTkLabel(
    card1_header,
    text="💡 Click Browse to select a folder",
    font=ctk.CTkFont(size=11),
    text_color=FG_DIM
)
drag_hint.pack(side="right")

# Project folder
ctk.CTkLabel(card1, text="Project Folder *").pack(anchor="w", padx=20, pady=(0, 5))
project_frame = ctk.CTkFrame(card1, fg_color="transparent")
project_frame.pack(fill="x", padx=20, pady=5)

project_var = tk.StringVar()
entry_project = ctk.CTkEntry(
    project_frame,
    textvariable=project_var,
    placeholder_text="Click Browse to select project folder...",
    height=40,
    corner_radius=10,
    fg_color=ENTRYBG,
    border_color=GLOW,
    border_width=1,
    text_color=FG,
    placeholder_text_color=FG_DIM
)
entry_project.pack(side="left", fill="x", expand=True, padx=(0, 10))

# Drag-and-drop removed due to incompatibility with CustomTkinter
# Users can use the Browse button to select folders

def set_project_from_dialog():
    folder = filedialog.askdirectory()
    if folder:
        set_project_folder(folder)

browse_btn = ctk.CTkButton(
    project_frame,
    text="Browse…",
    width=100,
    corner_radius=10,
    fg_color=ACCENT_DARK,
    hover_color=ACCENT,
    border_width=1,
    border_color=GLOW,
    command=set_project_from_dialog,
    font=ctk.CTkFont(size=12, weight="bold")
)
browse_btn.pack(side="right")

# Repository URL
ctk.CTkLabel(card1, text="Repository URL *").pack(anchor="w", padx=20, pady=(15, 5))
repo_var = tk.StringVar()
entry_repo = ctk.CTkEntry(
    card1,
    textvariable=repo_var,
    placeholder_text="https://github.com/USER/REPO.git",
    height=40,
    corner_radius=10,
    fg_color=ENTRYBG,
    border_color=GLOW,
    border_width=1,
    text_color=FG,
    placeholder_text_color=FG_DIM
)
entry_repo.pack(fill="x", padx=20, pady=5)

# Branch
ctk.CTkLabel(card1, text="Branch").pack(anchor="w", padx=20, pady=(15, 5))
branch_var = tk.StringVar(value="main")
entry_branch = ctk.CTkEntry(
    card1,
    textvariable=branch_var,
    height=40,
    corner_radius=10,
    width=200,
    fg_color=ENTRYBG,
    border_color=GLOW,
    border_width=1,
    text_color=FG,
    placeholder_text_color=FG_DIM
)
entry_branch.pack(anchor="w", padx=20, pady=5)

# --- Card 2: Version & Commit ---
ctk.CTkLabel(
    card2,
    text="Version & Commit",
    font=ctk.CTkFont(size=18, weight="bold")
).pack(anchor="w", padx=20, pady=(15, 10))

ctk.CTkLabel(card2, text="Version (tag)").pack(anchor="w", padx=20, pady=(0, 5))
version_var = tk.StringVar(value="v1.0")
entry_version = ctk.CTkEntry(
    card2,
    textvariable=version_var,
    height=40,
    corner_radius=10,
    width=200,
    fg_color=ENTRYBG,
    border_color=GLOW,
    border_width=1,
    text_color=FG,
    placeholder_text_color=FG_DIM
)
entry_version.pack(anchor="w", padx=20, pady=5)

ctk.CTkLabel(card2, text="Commit message").pack(anchor="w", padx=20, pady=(15, 5))
commit_var = tk.StringVar()
entry_commit = ctk.CTkEntry(
    card2,
    textvariable=commit_var,
    height=40,
    corner_radius=10,
    fg_color=ENTRYBG,
    border_color=GLOW,
    border_width=1,
    text_color=FG,
    placeholder_text_color=FG_DIM
)
entry_commit.pack(fill="x", padx=20, pady=5)

# --- Card 3: What's New (multiline) ---
ctk.CTkLabel(
    card3,
    text="What's New (optional)",
    font=ctk.CTkFont(size=18, weight="bold"),
    text_color=ACCENT
).pack(anchor="w", padx=20, pady=(15, 10))
whats_new_box = ctk.CTkTextbox(
    card3,
    height=80,  # Reduced height to ensure button is visible
    corner_radius=10,
    fg_color=TEXTBG,
    text_color=FG,
    border_color=GLOW,
    border_width=1,
    wrap="word"
)
whats_new_box.pack(fill="x", expand=False, padx=20, pady=(0, 10))

# Button frame and button are defined above (before outer frame)
# This ensures the button is always visible at the bottom

# status bar
status_frame = ctk.CTkFrame(root, corner_radius=0, height=30, fg_color=PANEL)
status_frame.pack(side="bottom", fill="x")
status_var = tk.StringVar(value="Ready.")
status = ctk.CTkLabel(
    status_frame,
    textvariable=status_var,
    anchor="w",
    font=ctk.CTkFont(size=11),
    text_color=FG_DIM
)
status.pack(side="left", padx=15, pady=5)

def set_status(text, kind="info"):
    status_var.set(text)
    if kind == "ok":
        status.configure(text_color=OK)
    elif kind == "warn":
        status.configure(text_color=WARN)
    elif kind == "error":
        status.configure(text_color=ERR)
    else:
        status.configure(text_color=FG_DIM)

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
    entry.configure(border_color=ERR, border_width=2)
    set_status(msg, "warn")

def clear_error(field):
    if field in errors:
        del errors[field]
    entry_project.configure(border_color=GLOW, border_width=1)
    entry_repo.configure(border_color=GLOW, border_width=1)

# shortcuts
root.bind("<Control-Return>", push_to_git)

root.mainloop()
