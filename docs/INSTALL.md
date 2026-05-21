# Soul Browser Installation Guide

## Quick Install

```bash
pip install soulbrowser
```

## Platform-Specific Instructions

### Windows

**Using pip:**
```bash
pip install soulbrowser
```

**Using pipx (recommended for CLI):**
```bash
pipx install soulbrowser
```

### macOS

```bash
pip install soulbrowser
# or with Homebrew Python
python3 -m pip install soulbrowser
```

### Ubuntu/Debian

```bash
sudo apt update
sudo apt install python3-pip
pip3 install soulbrowser
```

### Fedora

```bash
sudo dnf install python3-pip
pip3 install soulbrowser
```

### Arch Linux

```bash
pip install soulbrowser
```

### Kali Linux

```bash
pip3 install soulbrowser
```

## From Source

```bash
git clone https://github.com/vikrant-project/soulbrowser.git
cd soulbrowser
pip install -e .
```

## Docker

```bash
docker pull soulbrowser/soulbrowser
docker run -it soulbrowser/soulbrowser
```

## Verify Installation

```bash
python -c "import soulbrowser; print(soulbrowser.__version__)"
```

## Dependencies

Soul Browser automatically installs required dependencies:
- playwright
- aiohttp
- cryptography
- And more...

## Troubleshooting

### Browser binary not found

```bash
python -m soulbrowser install
```

### Permission errors on Linux

```bash
sudo chown -R $USER:$USER ~/.soulbrowser
```
