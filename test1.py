import streamlit as st
import sqlite3

# Initialize database connection
def init_db():
    conn = sqlite3.connect("event_manager.db")
    cursor = conn.cursor()
    # Create the Event Details table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS EventDetails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn

# Push event details into EventDetails table
def add_event(conn, name, description):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO EventDetails (name, description) VALUES (?, ?)", (name, description))
    conn.commit()
    # Create a table for the specific event
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS "{name}" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_number TEXT NOT NULL
        )
    """)
    conn.commit()

# Fetch all events
def fetch_events(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM EventDetails")
    return cursor.fetchall()

# Add user entry to specific event table
def add_user_to_event(conn, event_name, roll_number):
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO \"{event_name}\" (roll_number) VALUES (?)", (roll_number,))
    conn.commit()

# Fetch users for a specific event
def fetch_users_for_event(conn, event_name):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM \"{event_name}\"")
    return cursor.fetchall()

# Streamlit app code
st.title("Event Manager Application")

# Initialize database
conn = init_db()

# Event creation form
with st.form("create_event"):
    st.subheader("Create New Event")
    event_name = st.text_input("Event Name")
    event_description = st.text_area("Event Description")
    submit_event = st.form_submit_button("Add Event")

    if submit_event:
        if event_name and event_description:
            add_event(conn, event_name, event_description)
            st.success(f"Event '{event_name}' created successfully!")
        else:
            st.error("Please fill in both Event Name and Description.")

# Display events as tiles
st.subheader("All Events")
events = fetch_events(conn)
for event in events:
    event_id, event_name, event_description = event
    with st.expander(event_name):
        st.write(event_description)

        # Add User Form
        user_roll = st.text_input(f"Enter Roll Number for {event_name}", key=f"roll_{event_id}")
        add_user = st.button(f"Add User to {event_name}", key=f"add_{event_id}")
        
        if add_user:
            if user_roll:
                add_user_to_event(conn, event_name, user_roll)
                st.success(f"User with roll number '{user_roll}' added to '{event_name}'.")
            else:
                st.error("Please enter a roll number.")

        # Show Users Button
        show_users = st.button(f"Show Users for {event_name}", key=f"show_{event_id}")
        if show_users:
            users = fetch_users_for_event(conn, event_name)
            if users:
                st.write(f"Users registered for '{event_name}':")
                for user in users:
                    st.write(f"Roll Number: {user[1]}")
            else:
                st.write(f"No users registered for '{event_name}' yet.")

        # Display the number of users
        users = fetch_users_for_event(conn, event_name)
        st.write(f"Number of Users: {len(users)}")
