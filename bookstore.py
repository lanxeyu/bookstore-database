import sqlite3

# Connect to the database
conn = sqlite3.connect('ebookstore.db')
c = conn.cursor()

# Create the books table
c.execute('''CREATE TABLE IF NOT EXISTS books (ID INTEGER PRIMARY KEY, Title TEXT, Author TEXT, Qty INTEGER)''')

# Populate the books table with these initial values
initvalues = [
    (3001, "A Tale of Two Cities", "Charles Dickens", 30),
    (3002, "Harry Potter and the Philosopher's Stone", "J.K. Rowling", 40),
    (3003, "The Lion, the Witch and the Wardrobe", "C.S. Lewis", 25),
    (3004, "The Lord of the Rings", "J.R.R. Tolkien", 37),
    (3005, "Alice in Wonderland", "Lewis Carroll", 12)]
c.executemany('''
    INSERT OR IGNORE INTO books(ID, Title, Author, Qty)
    VALUES(?,?,?,?)''', initvalues)
conn.commit()

print('''
┌─────────────────────────────────────────────────────┐
│                                                     │
│         Welcome to Bookstore Manager v1.0!          │
│                                                     │
└─────────────────────────────────────────────────────┘
''')

# Main menu loop
while True:
    menu = input('''
 ► Select option:

1   -   Enter a new book
2   -   Update an existing book
3   -   Delete a book
4   -   Search for books
0   -   Exit
: ''')

    # START of 'Enter a new book' block
    if menu == "1":
        
        # Get data inputs from user to be added as a new record in the books table
        try:
            id = int(input(" ► Enter book ID: "))
            if id < 0:
                    print(" ► ID cannot be negative.")
                    continue
        except ValueError:
            print(" ► Invalid input for ID.")
            continue

        title = input(" ► Enter book title: ")
        if title.strip() == "":
            print(" ► Title cannot be empty.")
            continue

        author = input(" ► Enter book author: ")
        if author.strip() == "":
            print(" ► Author cannot be empty.")
            continue

        try:
            qty = int(input(" ► Enter quantity: "))
            if qty < 0:
                print(" ► Quantity cannot be negative.")
                continue
        except ValueError:
            print(" ► Invalid input for quantity.")
            continue
        
        # Insert obtained data as a new record in the books table
        c.execute("INSERT INTO books (ID, Title, Author, Qty) VALUES (?, ?, ?, ?)", (id, title, author, qty))
        conn.commit()
        print(" ► Book added successfully!")
    # END of 'Enter a new book' block
    

    # START of 'Update an existing book' block
    elif menu == "2":

        # Get id input from user
        try:
            id = int(input(" ► Enter book ID: "))
        except ValueError:
            print(" ► Invalid input for ID.")
            continue
        c.execute("SELECT * FROM books WHERE ID = ?", (id,))
        result = c.fetchone()
        if not result:
            print(" ► Book not found.")
            continue
        
        # Display the selected book to the user
        print("")
        column_names = [desc[0] for desc in c.description]
        for name, value in zip(column_names, result):
            print(f"{name}: {value}")
        print("")

        # Get data input from user to be used for updating the record in the books table
        title = input("Enter new book title (press enter to keep the current value): ")
        author = input("Enter new book author (press enter to keep the current value): ")
        try:
            qty = input("Enter new quantity (press enter to keep the current value): ")
            if qty.strip() != "":
                qty = int(qty)
                if qty < 0:
                    print("Quantity cannot be negative.")
                    continue
        except ValueError:
            print("Invalid input for quantity.")
            continue

        # Fetch current book details
        c.execute("SELECT Title, Author, Qty FROM books WHERE ID = ?", (id,))
        current_details = c.fetchone()

        # Update the record in the books table only if the input is not empty
        if title.strip() == "":
            title = current_details[0]
        if author.strip() == "":
            author = current_details[1]
        if qty == "":
            qty = current_details[2]

        c.execute("UPDATE books SET Title = ?, Author = ?, Qty = ? WHERE ID = ?", (title, author, qty, id))
        conn.commit()
        print("Book updated successfully!")
    # END of 'Update an existing book' block
        
        
    # START of 'Delete a book' block
    elif menu == "3":

        # Get id input from user
        try:
            id = int(input(" ► Enter book ID: "))
        except ValueError:
            print(" ► Invalid input for ID.")
            continue
        c.execute("SELECT * FROM books WHERE ID = ?", (id,))
        result = c.fetchone()
        if not result:
            print(" ► Book not found.")
            continue

        # Display the selected book and ask for delete confirmation
        print("")
        column_names = [desc[0] for desc in c.description]
        for name, value in zip(column_names, result):
            print(f"{name}: {value}")
        print("")
        confirm = input(" ► Are you sure you want to delete this book? (yes/no): ")

        # Delete the selected record from the books table
        if confirm.lower() == "yes":
            c.execute("DELETE FROM books WHERE ID = ?", (id,))
            conn.commit()
            print(" ► Book deleted successfully!")
        else:
            print(" ► Delete operation cancelled.")
    # END of 'Delete a book' block


    # START of 'Search for books' block    
    elif menu == "4":

        # Get search input from user
        searchinput = input(" ► Enter book ID or title: ")

        # If search input is in numbers, proceed here
        if searchinput.isdigit():
            id = searchinput
            c.execute("SELECT * FROM books WHERE ID = ?", (id,))
            result = c.fetchone()
            if not result:
                print(" ► Book not found.")
                continue
            
            # Display the selected book to the user
            print("")
            column_names = [desc[0] for desc in c.description]
            for name, value in zip(column_names, result):
                print(f"{name}: {value}")

        # If search input is not in numbers, proceed here
        else:
            title = searchinput
            if title.strip().lower() in ('a', 'an', 'the') and len(title.strip().split()) == 1:
                print(" ► Title cannot be empty.")
                continue
            if title.strip() == "":
                print(" ► Title cannot be empty.")
                continue

            # Create list containing the words from the title input
            search_terms = title.split()

            # Remove words that are articles
            search_terms = [word for word in search_terms if word.lower() not in ['a', 'an', 'the']]

            # Store the search query to be used for the execute function
            search_query = "SELECT * FROM books WHERE "
            # For every word in the title, concatenate multiples of "Title LIKE ? AND " to the search_query
            for i, term in enumerate(search_terms):
                search_query += "Title LIKE ?"
                if i < len(search_terms) - 1:
                    search_query += " AND "
            search_query += ";"
            # Modify the list of words to include wildcard symbol '%' at either side of each word
            search_terms = ["%" + term + "%" for term in search_terms]
            c.execute(search_query, search_terms)
            result = c.fetchall()

            # Display the results of the search
            if not result:
                print(" ► No books found matching that title.")
            else:
                print(" ► Search results:")
                column_names = [desc[0] for desc in c.description]
                for book in result:
                    print("")
                    for name, value in zip(column_names, book):
                        print(f"{name}: {value}")
    # END of 'Search for books' block
    
    elif menu == "0":
        break
    
    else:
        print(" ► Invalid input.")

conn.close()
