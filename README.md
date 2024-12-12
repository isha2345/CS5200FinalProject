# CS5200FinalProject

## MORE VISUALS + EXPLANATION CAN BE FOUND IN 'Remo project.pptx'

## Team Members - Please don't hesitate to reach out with further questions
### Isha Bhanot
#### bhanot.i@northeastern.edu
### Kaitlin Stenberg
#### stenberg.k@northeastern.edu
### Ryan Webb
#### webb.ry@northeastern.edu

## General Description
This project has two components to it. The first is building a database using the files that were provided by Remo. The architecture for adding each file type to that database is included in "book_api.ipynb". Of note, at least one of each file type (.xlsx, .xml, and .mrc) was ran through this architecture, but not all files were added to the database. The code in this file must be ran before the GUI (graphical user interface), contained entirely in gui.py, can be ran and used.

## book_api.ipynb
#### Run this file to populate the database.
Here, we handle files and read them into Pandas dataframes. Then we attempt to standardize the dataframes for insertion to the database. We then attempt to populate missing values based on ISBN using a Google Books API call. Then values from the Pandas dataframes are extracted and added to the database.

## gui.py
#### Run this file to interact with the database through the GUI. 
Here, we can add book data based on ISBN to the database using the Google Books API call. One can also add a title and author but we weren't able to find a great API for this data alone. The goal was to automatically upload files entered by users, but there were formatting issues described below and in the powerpoint available in this repository. For this feature to be used, standardized entries would be required. Users can also query the database. The only book query we set up was based on genre, but the data is so variable that this method is not very well established yet. Future goals would involve added more premade queries for users.

## Notes
- Each individual file had to be hard coded into the database, therefore book_api.ipynb demonstrates how we initially handle the files to format them into Pandas dataframes. These dataframes were then added to the database once in a standardized format. Our team recommends this approach to achieve a standard, easy to parse format in the database.
- Not all files were uploaded to the database due to time constraints. We hope that the pipeline can be understood from the files and Pandas dataframes that were handled by this project.
- MRC handling: Used back door ability of Zotero to convert MRC to .csv for easier conversion to Pandas; this approach is not scalable. Otherwise we would need to decompile with NodeJS.
- XML: Due to varied structure, we needed to manually read and enter specific details to read each file, which was not scalable.

## Challenges
- Creating a uniform pipeline for file intake
- Multiple file types (MRC, XML, XLS, etc).
- Within file types, files have different headings and data, so they need to be processed differently.
- Data requested by the client was often unavailable (missing fields in data).
- Data within files is sparse and does not conform to desired categories.
- APIs were not entirely helpful in filling in missing data, they were also limited in our ability to use them:
- Cleaning each of the larger data files had a run time of >25 minutes per file in some cases.
- A significant manual and automated effort was needed to convert each file into a standardized format.
- Some of the files couldn’t be entered into the DB due to size limitations in phpMyAdmin.

## Plan going forward
- Expanded functionality allowing users to find and enter more data from the interface.
- More functionality and ability to look up books.
- Ability to modify records and input additional data for sparse records.
- Different access abilities for Student, Teacher, and Admin.
- Setting a standard data format for participating schools/resources. CSV would be easiest for the sake of our methods, or at least a format that is easily converted to CSV. The manual lift required to handle each individual file will cause a challenge without standards. We suggest .xlsx files as these are the easiest to manage with our current pipeline using Python, generating DataFrames, and entering records into a SQL database.
- Book data is itself messy with many overlapping attributes between records (titles, authors, even ISBNs in some cases). We would want to spend far more time cleaning this data which would require input from Michelle at multiple stages.
