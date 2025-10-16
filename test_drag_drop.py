#!/usr/bin/env python3
"""
Simple test script to verify drag and drop functionality
Run this to test the drag and drop feature before building the full app
"""

import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
import os

def handle_drop(event):
    """Handle drag and drop events"""
    files = root.tk.splitlist(event.data)
    if files:
        dropped_path = files[0].strip('"\'')
        if os.path.isdir(dropped_path):
            status_var.set(f"✅ Folder dropped: {os.path.basename(dropped_path)}")
            entry_var.set(dropped_path)
        elif os.path.isfile(dropped_path):
            parent_dir = os.path.dirname(dropped_path)
            status_var.set(f"✅ File dropped, using parent: {os.path.basename(parent_dir)}")
            entry_var.set(parent_dir)
        else:
            status_var.set("❌ Invalid path")

def handle_drag_enter(event):
    """Visual feedback on drag enter"""
    entry.config(bg="#2a3a4a", fg="white")
    status_var.set("📁 Drop folder here!")

def handle_drag_leave(event):
    """Reset visual feedback on drag leave"""
    entry.config(bg="#1c2130", fg="#e6e6e6")
    status_var.set("💡 Drag and drop a folder here")

# Create test window
root = TkinterDnD.Tk()
root.title("Drag & Drop Test - Git Pusher v1.3")
root.geometry("600x200")
root.configure(bg="#0f1115")

# Variables
entry_var = tk.StringVar()
status_var = tk.StringVar(value="💡 Drag and drop a folder here")

# UI Elements
tk.Label(root, text="Git Pusher v1.3 - Drag & Drop Test", 
         font=("Segoe UI", 14, "bold"), 
         bg="#0f1115", fg="#e6e6e6").pack(pady=20)

entry = tk.Entry(root, textvariable=entry_var, width=70, 
                 bg="#1c2130", fg="#e6e6e6", font=("Segoe UI", 10))
entry.pack(pady=10)

status = tk.Label(root, textvariable=status_var, 
                  bg="#0f1115", fg="#b9c0cb", font=("Segoe UI", 10))
status.pack(pady=10)

# Enable drag and drop
entry.drop_target_register(DND_FILES)
entry.dnd_bind('<<Drop>>', handle_drop)
entry.dnd_bind('<<DragEnter>>', handle_drag_enter)
entry.dnd_bind('<<DragLeave>>', handle_drag_leave)

# Instructions
instructions = tk.Label(root, 
                       text="Instructions: Drag a folder from Windows Explorer and drop it on the entry field above",
                       bg="#0f1115", fg="#b9c0cb", font=("Segoe UI", 9))
instructions.pack(pady=10)

root.mainloop()
