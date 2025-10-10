from server.core import run_https
import sys

def main():
    port = 5555
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except:
            print("Invalid port, using default 5555")
    run_https(port)

if __name__ == "__main__":
    main()
