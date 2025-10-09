import os
import ssl
import socket
import platform
from pathlib import Path
from datetime import datetime, timedelta, timezone
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# -----------------------------
# Cross-platform certificate folder
# -----------------------------
def get_cert_folder():
    system = platform.system()
    if system == "Windows":
        # Windows: %APPDATA%\sServe
        base = os.getenv("APPDATA", str(Path.home() / "AppData" / "Roaming"))
    elif system == "Darwin":
        # macOS: ~/Library/Application Support/sServe
        base = str(Path.home() / "Library" / "Application Support")
    else:
        # Linux/Unix: ~/.config/sServe
        base = str(Path.home() / ".config")
    
    cert_folder = Path(base) / "sServe"
    cert_folder.mkdir(parents=True, exist_ok=True)
    return cert_folder

CERT_FOLDER = get_cert_folder()
CERT_FILE = CERT_FOLDER / "cert.pem"
KEY_FILE = CERT_FOLDER / "key.pem"

# -----------------------------
# Certificate utilities
# -----------------------------
def cert_expired(certfile: str) -> bool:
    if not os.path.exists(certfile):
        return True
    with open(certfile, "rb") as f:
        data = f.read()
    cert = x509.load_pem_x509_certificate(data, default_backend())
    return datetime.now(timezone.utc) > cert.not_valid_after_utc

def generate_self_signed_cert(certfile=CERT_FILE, keyfile=KEY_FILE):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    with open(keyfile, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"CA"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Localhost"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"MyServer"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
    ])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=365))
        .add_extension(x509.SubjectAlternativeName([x509.DNSName(u"localhost")]), False)
        .sign(key, hashes.SHA256(), default_backend())
    )
    with open(certfile, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    print(f"Generated self-signed cert:\n   Cert: {certfile}\n   Key: {keyfile}")

# -----------------------------
# HTTPS Request Handler
# -----------------------------
class HTTPSRequestHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"{self.client_address[0]} - - [{self.log_date_time_string()}] {format % args}")

# -----------------------------
# Run HTTPS server
# -----------------------------
def run_https(port=5555):
    if not CERT_FILE.exists() or not KEY_FILE.exists() or cert_expired(CERT_FILE):
        generate_self_signed_cert()
    
    server_address = ("0.0.0.0", port)
    httpd = ThreadingHTTPServer(server_address, HTTPSRequestHandler)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(CERT_FILE, KEY_FILE)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    local_ip = "localhost"
    try:
        network_ip = socket.gethostbyname(socket.gethostname())
    except:
        network_ip = "127.0.0.1"

    print(f"\n✅ HTTPS server running!\n   • Local:    https://{local_ip}:{port}\n   • Network:  https://{network_ip}:{port}\n   • Cert folder: {CERT_FOLDER}\n")
    
    try:
        httpd.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, shutting down server...")
        httpd.shutdown()
        httpd.server_close()
        print("Server stopped successfully.")

# -----------------------------
# Run HTTP server
# -----------------------------
def run_http(port=5555):
    server_address = ("0.0.0.0", port)
    httpd = ThreadingHTTPServer(server_address, SimpleHTTPRequestHandler)
    
    local_ip = "localhost"
    try:
        network_ip = socket.gethostbyname(socket.gethostname())
    except:
        network_ip = "127.0.0.1"

    print(f"\n✅ HTTP server running!\n   • Local:    http://{local_ip}:{port}\n   • Network:  http://{network_ip}:{port}\n")
    
    try:
        httpd.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, shutting down server...")
        httpd.shutdown()
        httpd.server_close()
        print("Server stopped successfully.")
