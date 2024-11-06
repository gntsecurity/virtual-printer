import os
import time
import fitz  # PyMuPDF for PDF handling
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Directory to monitor
PRINT_DIRECTORY = r"C:\PrintPreviews"

# PDF Preview Function
def display_pdf_preview(pdf_path):
    try:
        # Load the PDF
        pdf_document = fitz.open(pdf_path)
        first_page = pdf_document[0]  # Display only the first page as preview

        # Render page to an image
        zoom = 2  # Adjust zoom for quality
        mat = fitz.Matrix(zoom, zoom)
        pix = first_page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Setup preview window
        preview_window = tk.Toplevel()
        preview_window.title("Print Preview")
        preview_window.geometry(f"{img.width}x{img.height}")

        # Convert image for tkinter
        tk_img = ImageTk.PhotoImage(img)
        img_label = tk.Label(preview_window, image=tk_img)
        img_label.image = tk_img  # Keep reference to prevent garbage collection
        img_label.pack()

        # Confirmation buttons
        def confirm_print():
            messagebox.showinfo("Print Confirmation", "Print confirmed!")
            preview_window.destroy()
            pdf_document.close()
            os.remove(pdf_path)  # Remove after confirmation

        def cancel_print():
            messagebox.showinfo("Print Canceled", "Print job canceled.")
            preview_window.destroy()
            pdf_document.close()
            os.remove(pdf_path)

        btn_frame = tk.Frame(preview_window)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Confirm Print", command=confirm_print).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Cancel Print", command=cancel_print).pack(side="left", padx=10)

        preview_window.mainloop()
    except Exception as e:
        print(f"Error displaying PDF: {e}")

# Watchdog Event Handler
class PrintJobHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        # Check if the new file is a PDF
        if event.src_path.endswith(".pdf"):
            print(f"New print job detected: {event.src_path}")
            time.sleep(1)  # Small delay to ensure file is fully written
            display_pdf_preview(event.src_path)

# Main monitoring function
def start_monitoring():
    if not os.path.exists(PRINT_DIRECTORY):
        os.makedirs(PRINT_DIRECTORY)
    print(f"Monitoring directory: {PRINT_DIRECTORY}")

    event_handler = PrintJobHandler()
    observer = Observer()
    observer.schedule(event_handler, PRINT_DIRECTORY, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# Initialize monitoring
if __name__ == "__main__":
    start_monitoring()
