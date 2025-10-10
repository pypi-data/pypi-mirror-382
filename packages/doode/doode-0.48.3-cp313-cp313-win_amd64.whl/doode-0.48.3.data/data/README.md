# 🎬 Doode: DoodStream CLI, API Client, Url link Generator

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.7%2B-blue)
![Rich UI](https://img.shields.io/badge/featured-rich%20UI-green)

A **feature-rich**, **user-friendly** command-line interface and Python API client for [DoodStream](https://doodstream.com) — with **real-time progress bars**, **clipboard integration**, **IDM support (Windows)**, and **comprehensive error handling**.

---

## ✨ Features

- ✅ **Full DoodStream API coverage**: account, files, folders, remote upload, DMCA, reports
- 📊 **Real-time monitoring** of remote uploads with live progress bar (% complete, ETA)
- 🔗 **Generate direct download links** from DoodStream shareable URLs
- 💾 **Local file upload** with progress tracking
- 🖥️ **IDM integration** (Windows only) for one-click downloads
- 📋 **Auto-copy to clipboard** for generated download links
- 🎨 **Beautiful terminal UI** powered by [Rich](https://github.com/Textualize/rich)
- 🛡️ **Robust error handling** with clear, actionable messages
- 🧪 **Dual usage**: as a CLI tool **or** as a Python library
- 📚 **Comprehensive documentation** with examples for every method

---

## 📦 Installation

### Prerequisites
- Python 3.7 or higher
- A [DoodStream API key](https://doodstream.com/settings) (free account required)

### Install via pip
```bash
pip install doode
```

> **Note**: If installing from source, clone this repo and run:
> ```bash
> pip install -r requirements.txt
> ```

### Optional Dependencies
- **Windows users**: Install [IDM](https://www.internetdownloadmanager.com/) for direct download integration.
- **Debug mode**: Install `pydebugger` if you plan to use debug features.

---

## 🔑 Authentication

You must provide your **DoodStream API key** in one of two ways:

### 1. Environment Variable (Recommended)
```bash
export DOOD_API_KEY="your_api_key_here"
```

### 2. Command-Line Flag
```bash
dood --api-key "your_api_key_here" account info
```

> 💡 The environment variable method is preferred for security and convenience.

---

## 🚀 Quick Start

### Generate a Download Link
```bash
dood generate "https://dood.li/abc123xyz" -v -c
```
- `-v`: Verbose output (shows download URL in a styled panel)
- `-c`: Copy URL to clipboard automatically

### Upload a Video Remotely
```bash
dood remote upload "https://example.com/video.mp4" --new-title "My Movie"
```
> This starts the upload **and monitors it in real-time** with a live progress bar!

### Upload from Local Disk
```bash
dood upload local ./my_video.mp4
```

### View Account Info
```bash
dood account info
```

---

## 🧰 Full Command Reference

### Account Management
| Command | Description |
|--------|-------------|
| `dood account info` | Show account details (email, balance, storage) |
| `dood account reports --last 7` | Get usage stats for last 7 days |
| `dood account reports --from-date 2025-01-01 --to-date 2025-01-31` | Custom date range report |

---

### Remote Upload
| Command | Description |
|--------|-------------|
| `dood remote upload <URL>` | Start remote upload |
| `dood remote upload <URL> --new-title "Title"` | Upload with custom name |
| `dood remote upload <URL> --no-monitor` | Start upload without monitoring |
| `dood remote status <file_code>` | Check status of a specific upload |
| `dood remote list` | List all remote upload jobs |
| `dood remote slots` | Show available upload slots |
| `dood remote action --restart-errors` | Restart all failed uploads |
| `dood remote action --delete-code abc123` | Delete a specific upload job |

> 🔍 **Real-time monitoring** shows:
> - Current download percentage
> - Estimated time remaining
> - Automatic success/failure detection

---

### File Management
| Command | Description |
|--------|-------------|
| `dood files list` | List all files |
| `dood files list --fld-id folder123` | List files in a folder |
| `dood files info abc123` | Get detailed file info |
| `dood files rename abc123 "New Title"` | Rename a file |
| `dood files search "vacation"` | Search files by title |

---

### Folder Management
| Command | Description |
|--------|-------------|
| `dood folders create "Movies"` | Create a new folder |
| `dood folders create "Sub" --parent-id folder123` | Create subfolder |
| `dood folders rename folder123 "Renamed"` | Rename a folder |

---

### DMCA & Uploads
| Command | Description |
|--------|-------------|
| `dood dmca list` | List DMCA-reported files |
| `dood upload local ./video.mp4` | Upload local file |

---

## 📊 Real-Time Upload Monitoring

When you run a remote upload, you’ll see a live progress bar like this:

```
⠴ Uploading... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  42% 0:02:15
```

- Automatically detects **completion** or **failure**
- Updates every **3 seconds**
- Supports **keyboard interrupt** (Ctrl+C to stop monitoring)
- Times out after **1 hour** (configurable)

---

## 🛠️ Requirements

- `requests`
- `beautifulsoup4`
- `lxml`
- `rich`
- `rich-argparse`
- `configset`
- `pyperclip` (for clipboard)
- `licface` (custom help formatter)
- `requests-toolbelt` (for local upload progress)

> All dependencies are installed automatically via `pip`.

---

## 🐞 Error Handling & Debugging

### Common Errors
| Error | Solution |
|------|--------|
| `Invalid API key` | Check your API key at [DoodStream Settings](https://doodstream.com/settings) |
| `File not found` | Ensure local file path is correct |
| `Unsupported video format` | Use: mp4, mkv, avi, mov, webm, etc. |
| `Network error` | Check internet connection or DoodStream status |

### Debug Mode
Set environment variable to enable debug output:
```bash
export DEBUG=1
dood generate "https://dood.li/abc123"
```

> Requires `pydebugger` to be installed.

---

## 📜 License

see the [LICENSE](LICENSE) file for details.

---

## 🙌 Acknowledgements

- [DoodStream](https://doodstream.com) for their API
- [Rich](https://github.com/Textualize/rich) for beautiful terminal rendering
- [requests](https://docs.python-requests.org/) & [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for HTTP and parsing

---

> **Note**: This tool is **unofficial** and not affiliated with DoodStream. Use responsibly and in compliance with their [Terms of Service](https://doodstream.com/terms).

## author
[Hadi Cahyadi](mailto:cumulus13@gmail.com)
    

[![Buy Me a Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/cumulus13)

[![Donate via Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/cumulus13)

[Support me on Patreon](https://www.patreon.com/cumulus13)
