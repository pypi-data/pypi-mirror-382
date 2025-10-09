<h1 align="center" margin-bottom="50px">🔐 trackignore</h1>

<div align="center" margin-top="20px">

![Version](https://img.shields.io/badge/version-0.0.1-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Git](https://img.shields.io/badge/git-2.30+-orange.svg)

## **Version control for your private files in public repositories**

### *Work freely with private docs • Push safely to public repos • Never leak sensitive content*

---

</div>

## 🎯 The Problem

You're building an **open source project** on GitHub, but you have files you want to keep private:

```
my-awesome-project/
├── src/                    ✅ Public code
├── docs/                   ✅ Public docs
└── __PRIVATE__/           
    ├── notes.md            ⚠️ Private notes, planning documents,
    ├── AGENTS.md           ⚠️ maybe just something you're
    └── embarrassing-ideas/ ⚠️ a little embarassed about!
```

**The Dilemma:**
- 🚫 `.gitignore` them → You lose version control
- 🚫 Commit them → They appear in your public GitHub history
- ✅ **trackignore** → Version control locally, never publish to GitHub, all in the same repo

---

## 🎬 How It Works

![Workflow Diagram](./readme-svg.svg)

---

## ✨ Key Features

<table>
<tr>
<td width="50%" valign="top">

### 🛡️ **Safety First**
- Pre-push hook prevents accidental leaks
- Blocks pushes to public remotes
- Configurable remote whitelist

</td>
<td width="50%" valign="top">

### 🧹 **Clean History**
- Uses `git-filter-repo` for complete removal
- No trace of private files in public repo
- Fresh, clean commits every time

</td>
</tr>
<tr>
<td width="50%" valign="top">

### 🔄 **Dual Remotes**
- Public remote: cleaned, safe code
- Private remote: full history (optional)
- Subtree support for syncing private docs

</td>
<td width="50%" valign="top">

### ⚡ **Simple Workflow**
- Work locally as normal
- One repo, no sub-modules, easy config
- Guaranteed privacy for selected files

</td>
</tr>
</table>

---

## 🚀 Quick Start

### 1. Install (pipx recommended)

```bash
pipx install trackignore
```

`pipx` installs trackignore in an isolated environment together with the required `pathspec` and `git-filter-repo` packages—no extra setup per project.

```bash
# Upgrade or remove later
pipx upgrade trackignore
pipx uninstall trackignore
```

### 2. Initialize your repository

```bash
cd my-awesome-project
trackignore init --public-remote origin --private-remote origin-private
```

This command:
- creates a `.trackignore` file seeded with `__PRIVATE__/`
- installs a pre-push hook that prompts (or auto-runs) `trackignore push`
- writes `.trackignore.d/config.sh` with your preferred remotes

### 3. Add or confirm remotes

```bash
git remote add origin git@github.com:username/public-repo.git               # sanitized history
git remote add origin-private git@github.com:username/private-repo.git    # optional private mirror
```

### 4. Day-to-day workflow

```bash
# Work normally with public and private files
vim src/main.py
vim __PRIVATE__/planning.md
git add .
git commit -m "Add feature X"

# Publish a cleaned history to the public remote
trackignore push --remote origin --branches main

# (Optional) sync the private-only subtree to your private remote
trackignore sync --remote origin-private --branch main --path __PRIVATE__
```

---

## 📋 Commands Reference

<div align="center">

| Command | Description | What it does |
|---------|-------------|--------------|
| `trackignore init` | **Bootstrap** | Seeds `.trackignore`, installs hook, and writes config |
| `trackignore push` | **Publish** | Clones, runs `git-filter-repo`, and force-pushes sanitized branches |
| `trackignore sync` | **Sync private** | Uses `git subtree push` for a protected directory (e.g., `__PRIVATE__/`) |
| `trackignore cleanup --dry-run` | **Audit history** | Detects committed secrets and prints the cleanup plan before rewriting |
| `trackignore config-check --json` | **Inspect** | Lists normalized patterns plus any loader warnings |

</div>

---

## 🔧 Configuration

### Custom Private Directory

Edit `scripts/publish.sh`:
```bash
PRIVATE_DIR="my-private-stuff"  # default: __PRIVATE__
```

### Custom Remote Pattern

Edit `.githooks/pre-push`:
```bash
ALLOW_REMOTES_REGEX="^origin-private$|^backup-"  # Allow multiple patterns
```

### Publish Specific Branches

```bash
# Publish single branch
PUBLIC_BRANCHES="release/v2" make publish

# Publish multiple branches
PUBLIC_BRANCHES="main develop release/v1" make publish
```

---

## 🎓 How It Works (Deep Dive)

### 1. Pre-Push Hook 🛡️

Installed in `.git/hooks/pre-push`, this hook:
- Intercepts all `git push` commands
- Checks if you're pushing to a public remote
- Blocks the push if `__PRIVATE__/` exists in the branch
- Only allows pushes to remotes matching `ALLOW_REMOTES_REGEX`

```bash
# Example: trying to push to public remote
git push origin main
# ❌ Blocked! Use 'make publish-main' instead
```

### 2. Publish Script 🧹

The `scripts/publish.sh` script does the heavy lifting:

1. **Creates temporary clone** → `/tmp/repo-publish-<random>/`
2. **Runs git-filter-repo** → Removes all `__PRIVATE__/` from history
3. **Checks out branch** → e.g., `main`
4. **Force pushes to public** → `origin`
5. **Cleans up** → Removes temporary directory

```bash
# What happens under the hood
git clone . /tmp/repo-publish-abc123
cd /tmp/repo-publish-abc123
git-filter-repo --path __PRIVATE__ --invert-paths --force
git push --force origin main
```

### 3. Subtree Sync (Optional) 🌳

For syncing `__PRIVATE__/` to a separate private repo:

```bash
# First time setup
git subtree split --prefix=__PRIVATE__ -b private-branch
git push origin-private private-branch:main

# Subsequent syncs
make sync-private
```

---

## ⚠️ Important Notes

- **Backup first**: Test this workflow on a non-critical project first
- **Force push warning**: The publish script uses `--force` to rewrite history
- **Not a submodule**: `__PRIVATE__/` must be a regular directory, not a Git submodule
- **git-filter-repo**: Must be installed (officially recommended tool by [git docs](https://git-scm.com/docs/git-filter-branch#_warning))
- **One-way sync**: Changes in public remote won't sync back to private files

---

## 🔒 Security Considerations

### What This Protects Against
✅ Accidental `git push` of private files  
✅ Private files appearing in public commit history  
✅ Leaking sensitive data to public repositories  

### What This Does NOT Protect Against
❌ Files already pushed before setup (see cleanup below)  
❌ Local repository compromise  
❌ Intentional bypass of the hook (e.g., `git push --no-verify`)  

### Cleaning Existing History

If you've already pushed `__PRIVATE__/` to your public repo:

```bash
# ⚠️ WARNING: This rewrites history and breaks clones!

# 1. Backup your repo
git clone your-repo your-repo-backup

# 2. Remove private files from all history
git filter-repo --path __PRIVATE__ --invert-paths --force

# 3. Force push to public remote (coordinate with team!)
git push origin --force --all
git push origin --force --tags
```

---

## 🤔 FAQ

<details>
<summary><b>Why not just use <code>.gitignore</code>?</b></summary>

`.gitignore` prevents files from being *staged*, but you lose version control. This solution lets you version control private files locally while keeping them out of public repos, and avoids alternative solutions (submodules, symlinks, etc.) which may confuse you, your IDE, or your coding assistant - all complexity is abstracted away into a few easily configurable scripts.

</details>

<details>
<summary><b>Can I use multiple private directories?</b></summary>

Yes! Edit `PRIVATE_DIR` in the scripts to support patterns, or run filter-repo multiple times with different paths.

</details>

<details>
<summary><b>What if I forget and push directly?</b></summary>

You can't. The pre-push hook will block it. (If you bypass with `--no-verify`, you'll need to force-push a cleaned version to fix it.)

</details>

<details>
<summary><b>Does this work with GitHub Actions?</b></summary>

Yes! You can automate the publish script in CI/CD. Just ensure `git-filter-repo` is installed in the runner.

</details>

<details>
<summary><b>Does this work with git worktrees?</b></summary>

Yes! Create separate worktrees for main, feature branches, or private development:

```bash
git worktree add ../proj-main main
git worktree add ../proj-dev dev-private
```

Only one worktree should be used to publish:

```bash
cd ../proj-main
make publish-main
```

</details>

<details>
<summary><b>Performance with large repos?</b></summary>

`git-filter-repo` is fast, but creating temporary clones takes time. For very large repos, consider using shallow clones or selective branch publishing.

</details>

---

## 🛠️ Troubleshooting

### Hook not working?

```bash
# Check if hook is executable
ls -la .git/hooks/pre-push

# Make it executable
chmod +x .git/hooks/pre-push

# Verify hook is installed
cat .git/hooks/pre-push
```

### `git-filter-repo` not found?

```bash
# Verify installation
which git-filter-repo

# Install via pip
pip install git-filter-repo

# Or download directly
wget https://raw.githubusercontent.com/newren/git-filter-repo/main/git-filter-repo
chmod +x git-filter-repo
sudo mv git-filter-repo /usr/local/bin/
```

### Publish fails with "ref already exists"?

```bash
# The script uses --force, but if you need to manually fix:
cd /tmp/repo-publish-*/
git push origin main --force
```

---

## 📚 Additional Resources

- [git-filter-repo Documentation](https://github.com/newren/git-filter-repo/)
- [Git Subtree Tutorial](https://www.atlassian.com/git/tutorials/git-subtree)
- [Git Hooks Guide](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks)

---

## 🤝 Contributing

Contributions welcome! Here's how:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-idea`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

Please open an issue first to discuss major changes.

---

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Thanks to [newren](https://github.com/newren) for the amazing `git-filter-repo` tool
- Inspired by various discussions about managing private files in public repos
- Built out of necessity and a healthy dose of paranoia

---

<div align="center">

**⭐ Star this repo if you find it useful!**

Made with ❤️ and a healthy dose of privacy

[Report Bug](https://github.com/hesreallyhim/track-ignored-stuff/issues) • [Request Feature](https://github.com/hesreallyhim/track-ignored-stuff/issues)

</div>
