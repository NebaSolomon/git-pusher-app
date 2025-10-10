🚀 Git Pusher App

This is a simple GUI tool I built that lets you drag and drop any project folder, type in the version, repo link, and branch, and push it straight to GitHub (or any Git remote) with just one click.
It’s basically a shortcut to handle all my Git pushes without using the terminal.

🧠 What It Does

Lets you drag and drop a folder instead of typing paths

You can fill in your version tag, repo URL, and branch name

Automatically initializes Git, commits, tags, and pushes

Works with any repo (GitHub, GitLab, Bitbucket, etc.)

Simple GUI — no command line needed

Built for speed, minimalism, and convenience

⚙️ How It Works

Drag your project folder into the window

Enter your version (like v1.1)

Paste your Git repo URL

Choose the branch (default is main)

Hit Push to Git — the app handles everything:

Initializes the repo if needed

Adds and commits all files

Creates or updates the tag

Pushes both branch and tag to your remote

💻 Usage Example

If I drag a folder like:

C:\Users\LEGION\Desktop\productivity\created apps\kuku-V1.1


Then enter:

Version: v1.1  
Repo: https://github.com/NebaSolomon/kuku-app-.git  
Branch: main


and hit Push, it automatically uploads that project to GitHub with a version tag.

🧩 Folder Structure
git-pusher-app/
│
├── app.py              # GUI app (drag & drop window)
├── base/
│   └── push_it.sh      # The core Git automation script
├── press_and_push.cmd  # Windows one-click launcher
├── requirements.txt
└── README.md

🪶 Setup
git clone https://github.com/NebaSolomon/git-pusher-app.git
cd git-pusher-app
pip install -r requirements.txt
python app.py


Make sure Git is installed and added to your PATH.

🧾 License

MIT License — free to use, modify, and share.

✍️ Author

Neba Solomon

Built for anyone who wants to skip the boring Git commands and just push stuff fast.
