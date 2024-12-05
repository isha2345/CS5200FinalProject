from PIL import Image, ImageTk
import os
import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter import filedialog
import numpy as np
import pandas as pd
import mysql.connector
import requests

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

def add_attributes(df):
    '''
    This function adds desired features/attributes that are missing to the dataframe.

    Parameters:
    df - Dataframe that is set to be adjusted.

    Returns: None (Dataframe is updated)
    '''
    category_list = ['Title/Subtitle', 'Author', 'Copyright Date', 'Summary', 
                    'Series Name/Position', 'Genre', 'Subgenre', 'Form', 'Format', 'ISBN', 
                    'Page Count', 'Type', 'Publisher', 'Publication Year',
                    'Material Type', 'Subject', 'Lexile']
    for category in category_list:
        if category not in df.columns:
            df.loc[:,category] = np.nan


def manual_entry():
    entries = []  # To store manually entered ISBNs or Title/Author combinations
    test_isbns = []  # To store processed ISBNs

    while True:
        manual_isbn = simpledialog.askstring("Manual Entry", "Enter ISBN (or leave blank to enter Title and Author):")

        if manual_isbn:
            processed_isbn = process_isbn(manual_isbn)
            if processed_isbn:
                test_isbns.append(processed_isbn)  # Store processed ISBN in test_isbns
                entries.append(processed_isbn)   
            else:
                messagebox.showinfo("Invalid ISBN", "The provided ISBN is invalid. Please try again.")
                continue
        else:
            title = simpledialog.askstring("Manual Entry", "Enter Title/Subtitle:")
            author = simpledialog.askstring("Manual Entry", "Enter Author:")

            if title and author:
                entries.append(f"[{title}, {author}]")
            else:
                messagebox.showinfo("Incomplete Entry", "Both Title/Subtitle and Author are required.")
                continue

        more_entries = messagebox.askyesno("Manual Entry", "Do you want to add another entry?")
        if not more_entries:
            break

    print("Processed ISBNs:", test_isbns)  # Debug print to check the collected ISBNs
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
        data ={'isbn':manual_entries}
        test_df= pd.DataFrame(data)
        add_attributes(test_df)
        for isbn in test_df['isbn']:
            if pd.isna(isbn):
                continue  # Skip if ISBN is NaN
            url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
            response = requests.get(url)
            if response.status_code == 200: # Confirm request worked/is available
                book_data = response.json()
                if 'items' in book_data:
                    # Extract book details from the API response
                    book_info = book_data['items'][0]['volumeInfo']
                    book_details = {
                        'ISBN#': isbn,
                        'Title': book_info.get('title', np.nan),
                        'Subtitle': np.nan, # Not available
                        'Authors': ', '.join(book_info.get('authors', ['N/A'])),
                        'Publisher': book_info.get('publisher', np.nan),
                        'PublishedDate': book_info.get('publishedDate', np.nan),
                        'CopyrightDate': np.nan, # Not available
                        'Summary': book_info.get('description', 'No description available'), # NEED
                        'Genre': ', '.join(book_info.get('categories', ['N/A'])), # NEED
                        'PageCount': book_info.get('pageCount', np.nan), # NEED
                        'Type': book_info.get('printType', np.nan), # Need
                        'Categories': book_info.get('Categories', np.nan)
                    # Type of book - ficiton, nonfiction, blended
                    }
                    # Accessing the correct row using ISBN in the DataFrame
                    row_index = test_df[test_df['isbn'] == isbn].index
            
                    if not row_index.empty:  # Check if a matching ISBN was found
                        row_index = row_index[0]  # Get the first (and expected only) match
 
                        # Only update if the current value is NaN
                        if pd.isna(test_df.loc[row_index, 'Title/Subtitle']):
                            test_df.loc[row_index, 'Title/Subtitle'] = book_details['Title']
                        if pd.isna(test_df.loc[row_index, 'Author']):
                            test_df.loc[row_index, 'Author'] = book_details['Authors']
                        if pd.isna(test_df.loc[row_index, 'Publication Year']):
                            test_df.loc[row_index, 'Publication Year'] = book_details['PublishedDate']
                        if pd.isna(test_df.loc[row_index, 'Publisher']):
                            test_df.loc[row_index, 'Publisher'] = book_details['Publisher']
                        if pd.isna(test_df.loc[row_index, 'Material Type']):
                            test_df.loc[row_index, 'Material Type'] = book_details['Type']
                        if pd.isna(test_df.loc[row_index, 'Subject']):
                            test_df.loc[row_index, 'Subject'] = book_details['Genre']
                        if pd.isna(test_df.loc[row_index, 'Summary']):
                            test_df.loc[row_index, 'Summary'] = book_details['Summary']
                        if pd.isna(test_df.loc[row_index, 'Page Count']):
                            test_df.loc[row_index, 'Page Count'] = book_details['PageCount']
 
        test_df['Publication Year'] = pd.to_datetime(test_df['Publication Year'])
        test_sql_input = test_df.rename(columns={'Title/Subtitle':'title', "Author":"author",
                                                    "Subgenre":"subgenre", "Lexile":"lexileLevel",
                                                    "Publication Year":"copyrightDate", "Summary":"summary",
                                                    "Material Type":"type", "Form":"form", "Subject":'genre',
                                                    'ISBN':'isbn', "Publisher":'publisher',
                                                    'Series Name/Position':'seriesName/Position', 'Page Count':'pageCount'})
        test_sql_input = test_sql_input[['isbn','title',"author",'genre',"subgenre","lexileLevel",
                                            'publisher', "copyrightDate","summary","type","form",
                                            'seriesName/Position', 'pageCount']]
        test_sql_input = test_sql_input.replace(np.nan, 'None')
        sql_df = pd.DataFrame(test_sql_input)
        # type(sql_df)
        # cursor =  db_config.cursor()
        # SQL INSERT statement
        insert_stmt = """
            INSERT INTO LastTest (isbn, title, author, genre, subgenre, lexileLevel, publisher, copyrightDate, summary, type, form, seriesName/Position, pageCount)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
                
        # SQL SELECT statement
        select_stmt = """
            SELECT COUNT(*) FROM LastTest WHERE isbn = %s
        """
                
        # Loop through each row in the dataframe
        for _, row in sql_df.iterrows():
            # Convert datetime to string if it's not None
            copyright_date_str = row['copyrightDate'].strftime('%Y-%m-%d') if row['copyrightDate'] else None
                
            # Print the values being inserted to debug
            print(f"Inserting values: {row['isbn']}, {row['title']}, {row['author']}, {row['genre']}, {row['subgenre']}, "
                f"{row['lexileLevel']}, {row['publisher']}, {copyright_date_str}, {row['summary']}, {row['type']}, "
                f"{row['form']}, {row['seriesName/Position']}, {row['pageCount']}")
                
            # Extract values from each row
            values = (
                row['isbn'],
                row['title'],
                row['author'],
                row['genre'],
                row['subgenre'],
                row['lexileLevel'],
                row['publisher'],
                copyright_date_str,  # Use formatted date string (or None if missing)
                row['summary'],
                row['type'],
                row['form'],
                row['seriesName/Position'],
                row['pageCount']
            )
                
            # print(type(values))
            # Check if the record already exists by querying for the isbn
            cursor.execute(select_stmt, (row['isbn'],))
            result = cursor.fetchone()
                
            #If the record does not exist, insert it
            if result[0] == 0:  # result[0] contains the count from the SELECT query
                # Print the values being inserted to debug
                print(f"Inserting values: {row['isbn']}, {row['title']}, {row['author']}, {row['genre']}, "
                    f"{row['subgenre']}, {row['lexileLevel']}, {row['publisher']}, {copyright_date_str}, {row['summary']}, "
                    f"{row['type']}, {row['form']}, {row['seriesName/Publisher']}, {row['pageCount']}")
                
                #Execute the INSERT statement with the values
                cursor.execute(insert_stmt, values)
            else:
                # Print that the record is a duplicate and will not be inserted
                print(f"Duplicate found for ISBN {row['isbn']}, skipping insert.")
                
                # Commit the transaction to save changes
        db_config.commit()
                
        # Close the cursor and the connection
        cursor.close()
        db_config.close()
                
        print("Data processed successfully!")
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

# Database Configuration
db_config = mysql.connector.connect(
    host='localhost',
    user='root',
    database='Remo'
)
cursor =  db_config.cursor()

root.mainloop()
