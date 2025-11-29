![Python](https://img.shields.io/badge/Python-3.13-blue)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-informational)
![Shell](https://img.shields.io/badge/Shell-Bash-green)
![Packager](https://img.shields.io/badge/PyInstaller-onefile-success)
![Platform](https://img.shields.io/badge/Windows-10/11-lightgrey)

# 🚀 Git Pusher App  

A simple **GUI tool** that lets you push any project folder to **any GitHub repository** — no command line needed.  

![App Screenshot](https://via.placeholder.com/800x400?text=Git+Pusher+App+Screenshot)  
*(Replace this image link with your actual app screenshot)*  

---

## ✨ Features  
- Push any local folder to any GitHub repo  
- Enter custom commit messages and version tags  
- Add "What's New" notes for each release  
- Auto-creates missing `.git` or `.gitignore` files  
- Works with new or existing repositories  
- Modern CustomTkinter UI with rounded corners and smooth animations
- Built-in dark theme for comfortable use  
- Secure input validation and authentication checks
- Safe merge strategy (prevents data loss)
- One-click EXE — no setup required  

---

## 🪜 How to Use  

### 1️⃣ Open the App  
Double-click **`GitPusher.exe`**  
> 💡 Make sure **Git for Windows** is installed: [Download Here](https://git-scm.com/downloads)

---

### 2️⃣ Select Your Project  
Click **Browse**, then choose the folder you want to upload.

---

### 3️⃣ Fill in Details  
| Field | Description |
|--------|-------------|
| **Version** | Example: `v1.0`, `v1.2.1` |
| **Repository URL** | Example: `https://github.com/YourName/project.git` |
| **Branch** | Usually `main` or `master` |
| **Commit Message** | Short summary of changes |
| **What’s New** | Optional longer update notes |

---

### 4️⃣ Push to GitHub  
Click **🚀 Push to Git** and the app will:  
- Initialize Git (if needed)  
- Commit your changes  
- Sync with your GitHub repo  
- Tag your release version  

✅ When done, you’ll see a confirmation message.

---

## 💡 Tips  
- You can use this app for *any* repo or folder.  
- “What’s New” is saved automatically to a `WHATS_NEW.txt` file.  
- Works perfectly with new GitHub repositories.  

---

## ⚙️ Requirements  
- **Windows 10 or 11**  
- **Git for Windows** installed  
- **Internet connection** for GitHub access  

---

## 🧰 Troubleshooting  

| Problem | Solution |
|----------|-----------|
| 🟥 *“Git Bash not found”* | Install [Git for Windows](https://git-scm.com/downloads) |
| 🟨 *“Push failed: rejected”* | Pull the latest repo changes before pushing again |
| 🟦 *Antivirus warning* | The EXE is safe — sign it or whitelist it in your antivirus |

---

## 🧑‍💻 About  
Created by **[Neba Solomon](https://github.com/NebaSolomon)**  
> A lightweight productivity tool to make Git simple for everyone.  

---

## Tech Stack
- **Python (CustomTkinter)** – Modern GUI application with rounded UI
- **Shell / Bash** – Git automation script
- **PyInstaller** – build single-file Windows EXE
- **Git & GitHub** – versioning, tags, releases
- **Windows (Git for Windows / Git Bash)**


## Architecture

- The EXE bundles the GUI; the **shell script stays external**, so you can update it without rebuilding.
- "What's New" text is passed via env var and appended to `WHATS_NEW.txt` with timestamp.
- Modern CustomTkinter UI provides a professional, rounded interface with smooth animations.

## Security Features

- **URL Validation** – Prevents command injection via malicious repository URLs
- **Path Validation** – Blocks access to system directories
- **Input Sanitization** – All user inputs are validated and sanitized
- **Authentication Verification** – Checks repository access before attempting push
- **Safe Merge Strategy** – Prevents data loss from force merges, requires manual conflict resolution
- **Timeout Protection** – Prevents UI freezing from hanging operations


## Screenshots
<img width="1126" height="980" alt="image" src="https://github.com/user-attachments/assets/0508302b-f8f2-4a7a-9628-2059c520a502" />
<img width="1125" height="940" alt="image" src="https://github.com/user-attachments/assets/b8c00f0a-440f-4c76-9394-0e987ec30ee2" />


## How to Use
1. Open **GitPusher.exe** (Windows 10/11).
2. Click **Browse** to select your project folder.
3. Fill **Version**, **Repository URL**, **Branch**, **Commit message**.
4. (Optional) Add **What’s New** notes.
5. Click **🚀 Push to Git**.

