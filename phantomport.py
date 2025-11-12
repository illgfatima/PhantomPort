# PhantomPort
toy server + scanner + simple GUI
#!/usr/bin/env python3
# phantomport.py
# Mini toy server + smart port scanner, handwritten style.
# Educational use only. Run on localhost / lab VMs only.

import socket
import threading
import queue
import time
import sys

TIMEOUT = 0.6

def toy_server(host='127.0.0.1', port=4444):
    """Simple server that greets and logs connections."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(5)
    print(f"[Server] Listening on {host}:{port}")
    try:
        while True:
            conn, addr = s.accept()
            print(f"[Server] Connected: {addr}")
            try:
                conn.sendall(b"Welcome to PhantomPort!\n")
            except Exception:
                pass
            conn.close()
    except KeyboardInterrupt:
        print("\n[Server] Stopping.")
    finally:
        s.close()

def parse_ports(spec):
    """Accept '1-100' or '22,80,443' or '1-100,443'."""
    parts = spec.split(',')
    ports = set()
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if '-' in p:
            a,b = p.split('-',1)
            ports.update(range(int(a), int(b)+1))
        else:
            ports.add(int(p))
    return sorted([p for p in ports if 1 <= p <= 65535])

def grab_banner(ip, port):
    try:
        s = socket.socket()
        s.settimeout(0.8)
        s.connect((ip, port))
        try:
            s.sendall(b'\r\n')
            data = s.recv(1024)
            return data.strip().decode('utf-8', errors='ignore')
        except Exception:
            return ''
        finally:
            s.close()
    except Exception:
        return ''

def worker(ip, q, out_list):
    while True:
        try:
            port = q.get_nowait()
        except Exception:
            return
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(TIMEOUT)
        try:
            start = time.time()
            s.connect((ip, port))
            elapsed = time.time() - start
            banner = grab_banner(ip, port)
            out_list.append((port, elapsed, banner))
        except Exception:
            pass
        finally:
            try: s.close()
            except: pass
            q.task_done()

def scan(target, port_spec="1-1024", threads=40, verbose=True):
    ports = parse_ports(port_spec)
    q = queue.Queue()
    for p in ports:
        q.put(p)
    results = []
    tlist = []
    for _ in range(min(threads, len(ports))):
        t = threading.Thread(target=worker, args=(target, q, results), daemon=True)
        t.start()
        tlist.append(t)
    try:
        q.join()
    except KeyboardInterrupt:
        if verbose:
            print("\n[Scanner] Interrupted by user.")
    results.sort(key=lambda x: x[0])
    if verbose:
        if not results:
            print("[Scanner] No open ports found (or host unreachable).")
        else:
            print(f"\n[Scanner] Open ports on {target}:")
            for port, elapsed, banner in results:
                svc = {
                    22:'ssh',80:'http',443:'https',3306:'mysql',6379:'redis'
                }.get(port, '')
                svc_part = f" ({svc})" if svc else ""
                banner_part = f" — banner: {banner}" if banner else ""
                print(f"  {port}{svc_part}  [{elapsed:.2f}s]{banner_part}")
    return results

def main():
    # Simple CLI entry
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 phantomport.py server            # run server on localhost:4444")
        print("  python3 phantomport.py scan 127.0.0.1 1-1024 [threads]")
        sys.exit(1)
    cmd = sys.argv[1].lower()
    if cmd == 'server':
        toy_server()
    elif cmd == 'scan':
        target = sys.argv[2] if len(sys.argv) > 2 else '127.0.0.1'
        port_spec = sys.argv[3] if len(sys.argv) > 3 else '1-1024'
        threads = int(sys.argv[4]) if len(sys.argv) > 4 else 40
        scan(target, port_spec, threads)
    else:
        print("Unknown command.")

if __name__ == "__main__":
    main()
