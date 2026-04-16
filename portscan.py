#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, scrolledtext
import socket
import threading

# ---------------- SERVICE DETECTION ---------------- #
def get_service_name(port):
    try:
        return socket.getservbyport(port)
    except:
        return "Unknown"

# ---------------- VERSION DETECTION ---------------- #
def grab_banner(sock, port, target):
    try:
        # HTTP
        if port in [80, 8080]:
            sock.send(f"GET / HTTP/1.1\r\nHost: {target}\r\n\r\n".encode())
            response = sock.recv(1024).decode(errors="ignore")
            return response.split("\n")[0]

        # SMTP
        elif port == 25:
            sock.send(b"HELO test\r\n")
            return sock.recv(1024).decode(errors="ignore").strip()

        # FTP / SSH usually send banner automatically
        else:
            return sock.recv(1024).decode(errors="ignore").strip()

    except:
        return "No version info"

# ---------------- SCAN FUNCTION ---------------- #
def scan_ports():
    target = target_entry.get()
    start_port = int(start_entry.get())
    end_port = int(end_entry.get())

    total_ports = end_port - start_port + 1
    progress["maximum"] = total_ports
    progress["value"] = 0

    result_box.delete(1.0, tk.END)
    status_label.config(text="Resolving target...")

    try:
        ip = socket.gethostbyname(target)
        result_box.insert(tk.END, f"Scanning {ip}...\n\n")
        status_label.config(text="Scanning...")

        def scan():
            open_count = 0

            for i, port in enumerate(range(start_port, end_port + 1), start=1):
                sock = socket.socket()
                sock.settimeout(1)

                if sock.connect_ex((ip, port)) == 0:
                    service = get_service_name(port)
                    banner = grab_banner(sock, port, target)

                    result_box.insert(
                        tk.END,
                        f"[OPEN] Port {port} ({service}) | {banner}\n"
                    )
                    open_count += 1

                sock.close()

                # Progress update
                progress["value"] = i
                percent = (i / total_ports) * 100
                progress_label.config(text=f"{percent:.1f}%")

            status_label.config(
                text=f"Completed | Open Ports: {open_count}"
            )

        threading.Thread(target=scan, daemon=True).start()

    except Exception as e:
        result_box.insert(tk.END, str(e))
        status_label.config(text="Error occurred")

# ---------------- GUI SETUP ---------------- #
root = tk.Tk()
root.title("Port Scanner")
root.geometry("600x500")
root.configure(bg="#1e1e1e")

# Title
title = tk.Label(root, text="🔐 Port Scanner",
                 font=("Helvetica", 16, "bold"),
                 fg="white", bg="#1e1e1e")
title.pack(pady=10)

# Input Frame
frame = tk.Frame(root, bg="#1e1e1e")
frame.pack(pady=5)

tk.Label(frame, text="Target", fg="white", bg="#1e1e1e").grid(row=0, column=0)
target_entry = tk.Entry(frame, width=20)
target_entry.grid(row=0, column=1, padx=5)

tk.Label(frame, text="Start Port", fg="white", bg="#1e1e1e").grid(row=1, column=0)
start_entry = tk.Entry(frame, width=10)
start_entry.grid(row=1, column=1, padx=5)

tk.Label(frame, text="End Port", fg="white", bg="#1e1e1e").grid(row=2, column=0)
end_entry = tk.Entry(frame, width=10)
end_entry.grid(row=2, column=1, padx=5)

# Scan Button
scan_btn = tk.Button(root, text="Start Scan",
                     command=scan_ports,
                     bg="#4CAF50", fg="white",
                     font=("Helvetica", 10, "bold"),
                     padx=10, pady=5)
scan_btn.pack(pady=10)

# Progress Bar
progress = ttk.Progressbar(root, orient="horizontal",
                           length=400, mode="determinate")
progress.pack(pady=5)

progress_label = tk.Label(root, text="0%",
                          fg="white", bg="#1e1e1e")
progress_label.pack()

# Status Label
status_label = tk.Label(root, text="Idle",
                        fg="cyan", bg="#1e1e1e",
                        font=("Helvetica", 10))
status_label.pack(pady=5)

# Result Box
result_box = scrolledtext.ScrolledText(root,
                                       width=70, height=15,
                                       bg="#2d2d2d", fg="white",
                                       insertbackground="white")
result_box.pack(pady=10)

root.mainloop()
