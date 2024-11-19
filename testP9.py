from PIL import Image, ImageTk
import os
import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter import filedialog
import pandas as pd


def process_isbn(isbn):
    """Cleans and formats ISBN."""
    if not pd.isna(isbn):
        isbn = str(isbn)
        isbn = isbn.split()[0]  # Remove anything after spaces, such as " (l)" or " (p)"
        isbn = isbn.replace('-', '')  # Remove dashes
        if len(isbn) > 13:  # Ensure ISBN is at most 13 characters long
            isbn = isbn[:13]
        return isbn
    return None


def manual_entry():
    """
    Allows manual entry of a new ISBN, or Title/Subtitle and Author if no ISBN is provided.
    """
    entries = []  # To store manually entered ISBNs or Title/Author combinations
    
    while True:
        # Prompt for ISBN
        manual_isbn = simpledialog.askstring("Manual Entry", "Enter ISBN (or leave blank to enter Title and Author):")

        if manual_isbn:  # If ISBN is provided
            processed_isbn = process_isbn(manual_isbn)
            entries.append(processed_isbn)
        else:  # Prompt for Title and Author if ISBN is not available
            title = simpledialog.askstring("Manual Entry", "Enter Title/Subtitle:")
            author = simpledialog.askstring("Manual Entry", "Enter Author:")

            if title and author:
                entries.append(f"[{title}, {author}]")
            else:
                messagebox.showinfo("Incomplete Entry", "Both Title/Subtitle and Author are required.")
                continue

        # Ask if the user wants to enter more data
        more_entries = messagebox.askyesno("Manual Entry", "Do you want to add another entry?")
        if not more_entries:
            break

    return entries


def UploadAction(event=None):
    # Handle file upload or manual entry
    action = messagebox.askyesno("File or Manual Entry", "Do you want to upload a file? Click 'No' for manual entry.")

    if action:  # File upload
        filename = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if filename:
            try:
                file = pd.read_excel(filename)
                isbn_values = []

                if 'ISBN' in file.columns:
                    for _, row in file.iterrows():
                        isbn = process_isbn(row['ISBN'])
                        if isbn:
                            isbn_values.append(isbn)
                        else:
                            # Combine Title and Author if ISBN is missing
                            title = row.get('Title/Subtitle', 'Unknown')
                            author = row.get('Author', 'Unknown')
                            isbn_values.append(f"[{title}, {author}]")
                    
                    print("Processed ISBNs:", isbn_values)
                else:
                    print("Error: The file does not have an 'ISBN' column.")
            except Exception as e:
                print("Error processing the Excel file:", e)
        else:
            print("File selection was cancelled.")
    else:  # Manual entry
        manual_entries = manual_entry()
        print("Processed Manual Entries:", manual_entries)


# GUI Setup
root = tk.Tk()
root.title("Book Data Processor")

# Set Icon (ensure the file exists)
icon_path = "book_icon.png"  # Use a valid .png or .gif file
if not os.path.exists(icon_path):
    print(f"Error: Icon file {icon_path} not found.")
else:
    root.iconphoto(False, tk.PhotoImage(file=icon_path))

# Set Background Image (ensure the file exists)
bg_path = "library_background.png"
if not os.path.exists(bg_path):
    print(f"Error: Background file {bg_path} not found.")
else:
    bg_image = Image.open(bg_path)
    bg_photo = ImageTk.PhotoImage(bg_image)
    background_label = tk.Label(root, image=bg_photo)
    background_label.place(relwidth=1, relheight=1)

# Header
header = tk.Label(root, text="Welcome to Book Data Processor!",
                  font=("Georgia", 24, "bold"), fg="darkred", bg="#f5f5dc")
header.pack(pady=20)

# Button Frame
button_frame = tk.Frame(root, bg="#f5f5dc", padx=10, pady=10)
button_frame.pack(pady=20)

# Upload Button
upload_button = tk.Button(button_frame, text="Upload File or Manual Entry",
                          command=UploadAction, font=("Georgia", 16),
                          bg="#8B4513", fg="white",
                          activebackground="#A0522D", activeforeground="white")
upload_button.pack(pady=10)

# Footer
footer = tk.Label(root, text="Happy Reading! 📚",
                  font=("Georgia", 14, "italic"), fg="darkgreen", bg="#f5f5dc")
footer.pack(side=tk.BOTTOM, pady=20)

root.mainloop()