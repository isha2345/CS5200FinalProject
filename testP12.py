from PIL import Image, ImageTk
import os
import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter import filedialog
import pandas as pd
import mysql.connector

# Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'database': 'Remo'
}


def modify_isbn(isbn):
    isbn = str(isbn)
    if not (isbn[:3] == '978' or isbn[:3] == '979'):
        if len(isbn) == 10:
            return '978' + isbn
    return isbn[:13]


def process_isbn(isbn):  # Cleaning and Formatting ISBN
    if not pd.isna(isbn):
        isbn = str(isbn)
        isbn = isbn.split()[0]
        isbn = isbn.replace('-', '')
        if len(isbn) > 13:
            isbn = isbn[:13]
        isbn = modify_isbn(isbn)
        return isbn
    return None


def manual_entry():
    entries = []  # To store manually entered data

    try:
        # Establish database connection
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        while True:
            manual_isbn = simpledialog.askstring("Manual Entry", "Enter ISBN (or leave blank to enter Title and Author):")

            if manual_isbn:
                processed_isbn = process_isbn(manual_isbn)
                if processed_isbn:
                    # Insert ISBN into the database
                    cursor.execute("INSERT INTO LastTest (isbn) VALUES (%s)", (processed_isbn,))
                    connection.commit()
                    entries.append(processed_isbn)
            else:
                title = simpledialog.askstring("Manual Entry", "Enter Title/Subtitle:")
                author = simpledialog.askstring("Manual Entry", "Enter Author:")

                if title and author:
                    # Insert Title and Author into the database
                    cursor.execute("INSERT INTO LastTest (title, author) VALUES (%s, %s)", (title, author))
                    connection.commit()
                    entries.append(f"[{title}, {author}]")
                else:
                    messagebox.showinfo("Incomplete Entry", "Both Title/Subtitle and Author are required.")
                    continue

            more_entries = messagebox.askyesno("Manual Entry", "Do you want to add another entry?")
            if not more_entries:
                break

        cursor.close()
        connection.close()

    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")

    return entries


def query_genre():
    genre = simpledialog.askstring("Query Genre", "Enter Genre to Search:")

    if not genre:
        messagebox.showinfo("Invalid Input", "Genre cannot be empty.")
        return

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # SQL query to get ISBN, or Title and Author if ISBN is not available
        query = """SELECT IF(title IS NOT NULL AND title != '' AND author IS NOT NULL AND author != '', CONCAT('[', title, ', ', author, ']'), isbn) AS Result FROM LastTest WHERE genre = %s;"""
        cursor.execute(query, (genre,))
        results = cursor.fetchall()

        if results:
            # Display results in a messagebox
            output = "\n".join([row["Result"] for row in results])
            messagebox.showinfo(f"Books in Genre '{genre}'", output)
        else:
            messagebox.showinfo("No Results", f"No books found in genre '{genre}'.")

        cursor.close()
        connection.close()

    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")


def UploadAction(event=None):
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


# GUI Setup (Frontend)
root = tk.Tk()
root.title("Book Data Processor")

icon_path = "book_icon.png"  
if not os.path.exists(icon_path):
    print(f"Error: Icon file {icon_path} not found.")
else:
    root.iconphoto(False, tk.PhotoImage(file=icon_path))

bg_path = "library_background.png"
if not os.path.exists(bg_path):
    print(f"Error: Background file {bg_path} not found.")
else:
    bg_image = Image.open(bg_path)
    bg_photo = ImageTk.PhotoImage(bg_image)
    background_label = tk.Label(root, image=bg_photo)
    background_label.place(relwidth=1, relheight=1)

header = tk.Label(root, text="Welcome to Remo!",
                  font=("Georgia", 24, "bold"), fg="darkred", bg="#f5f5dc")
header.pack(pady=20)

button_frame = tk.Frame(root, bg="#f5f5dc", padx=10, pady=10)
button_frame.pack(pady=20)

upload_button = tk.Button(button_frame, text="Upload File or Manual Entry",
                          command=UploadAction, font=("Georgia", 16),
                          bg="#8B4513", fg="white",
                          activebackground="#A0522D", activeforeground="white")
upload_button.pack(pady=10)

query_button = tk.Button(button_frame, text="Query Genre",
                         command=query_genre, font=("Georgia", 16),
                         bg="#8B4513", fg="white",
                         activebackground="#A0522D", activeforeground="white")
query_button.pack(pady=10)

footer = tk.Label(root, text="Happy Reading! 📚",
                  font=("Georgia", 14, "italic"), fg="darkgreen", bg="#f5f5dc")
footer.pack(side=tk.BOTTOM, pady=20)

root.mainloop()