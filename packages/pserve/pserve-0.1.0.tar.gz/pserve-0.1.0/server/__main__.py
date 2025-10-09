import sys
from server.core import run_http, run_https

def main():
    protocol = "http"
    port = 5555

    if len(sys.argv) > 1:
        protocol = sys.argv[1].lower()
    if len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except:
            print("Invalid port, using default 5555")

    if protocol == "https":
        run_https(port)
    else:
        run_http(port)

if __name__ == "__main__":
    main()
