# sServe: HTTP & HTTPS Python Server

A lightweight Python server for **HTTP** and **HTTPS**, designed for developers to quickly serve files locally or on a network. Works seamlessly on **Windows**, **Linux**, and **macOS**. Auto-generates self-signed certificates for HTTPS and supports clean shutdown with `Ctrl+C`.

---

## Features

- **HTTPS Server** with auto-generated self-signed certificates
- **HTTP Server** for plain HTTP connections
- Displays both **Local** and **Network** IP addresses
- Works on **Windows**, **Linux**, and **macOS**
- Clean **Ctrl+C shutdown**
- **Easy CLI commands:**

  - `phttps [port]` – start HTTPS server (default port 5555)
  - `phttp [port]` – start HTTP server (default port 5555)

> ⚡ **Tip:** If the commands are not recognized, ensure your Python Scripts folder is added to your system PATH.

### Adding Python Scripts folder to PATH

- **Windows:**
  Usually `C:\Users\<YourUsername>\AppData\Local\Programs\Python\Python3X\Scripts`
  Add this path to **Environment Variables → Path**

- **Linux/macOS:**
  Usually `~/.local/bin`
  Add this line to your shell config (`.bashrc` / `.zshrc`):

  ```bash
  export PATH="$HOME/.local/bin:$PATH"
  ```

After updating PATH, you can run from anywhere:

```bash
phttps 3000    # HTTPS server on port 3000
phttp 8080     # HTTP server on port 8080
```

- Compatible with **Python 3.12+**
- Uses **cryptography** library for certificate generation

---

## Installation

Clone the repository and install locally:

```bash
git clone https://github.com/nextsai/sServe.git
cd sServe
pip install .
```

---

## Usage

### HTTPS Server

Default port 5555:

```bash
phttps
```

Custom port (e.g., 3000):

```bash
phttps 3000
```

### HTTP Server

Default port 5555:

```bash
phttp
```

Custom port (e.g., 8080):

```bash
phttp 8080
```

### Using Python Module

You can also run using Python's `-m` flag:

```bash
python -m phttps 3000   # HTTPS server
python -m phttp 8080    # HTTP server
```

---
