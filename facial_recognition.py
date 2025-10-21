import cv2
import face_recognition
import mysql.connector as mys
import numpy as np
import time
import tkinter as tk
from tkinter import messagebox, simpledialog, Tk
from tkinter import ttk  # Import ttk for Treeview

# MySQL connection details
con = mys.connect(
    host='localhost',
    user='root',
    password='141007',
    database='face_recognition'
)

# Function to retrieve all user details
def retrieve_all_users():
    try:
        cursor = con.cursor()
        query = "SELECT id, name FROM users"  # Adjust the query to select the desired fields
        cursor.execute(query)
        results = cursor.fetchall()

        # Create a new window for displaying user data
        user_window = Tk()
        user_window.title("User Data")

        # Create a Treeview widget
        tree = ttk.Treeview(user_window, columns=("ID", "Name"), show='headings')
        tree.heading("ID", text="User ID")
        tree.heading("Name", text="Name")
        tree.pack(fill=tk.BOTH, expand=True)

        # Insert data into the Treeview
        for row in results:
            tree.insert("", tk.END, values=row)

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(user_window, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        user_window.mainloop()

    except mys.Error as err:
        messagebox.showerror("Error", f"Error: {err}")

# Function to retrieve user details by ID
def get_user_details(user_id):
    try:
        cursor = con.cursor()
        query = "SELECT name, image FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()

        if result:
            name, image_binary = result
            # Convert the binary image back to a format for display
            nparr = np.frombuffer(image_binary, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Display the retrieved details
            cv2.imshow('Retrieved Image', image)
            cv2.waitKey(0)  # Wait for a key press to close the image window
            cv2.destroyAllWindows()
            messagebox.showinfo("User Details", f"Name: {name}")
        else:
            messagebox.showwarning("Not Found", "No user found with that ID.")

    except mys.Error as err:
        messagebox.showerror("Error", f"Error: {err}")

# Function to register a new face
def register_face():
    # Capture video from the webcam
    cap = cv2.VideoCapture(0)

    print("Press 's' to save a face, or 'q' to quit.")

    last_face_locations = []
    smoothing_factor = 0.3
    last_print_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "Failed to capture frame")
            break

        # Resize frame for faster processing (optional)
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Detect face locations
        face_locations = face_recognition.face_locations(rgb_small_frame)

        # Smooth face locations
        if last_face_locations:
            smoothed_face_locations = []
            for i, face_location in enumerate(face_locations):
                if i < len(last_face_locations):
                    smoothed_location = tuple(int(smoothing_factor * a + (1 - smoothing_factor) * b)
                                              for a, b in zip(face_location, last_face_locations[i]))
                    smoothed_face_locations.append(smoothed_location)
                else:
                    smoothed_face_locations.append(face_location)
            face_locations = smoothed_face_locations

        last_face_locations = face_locations

        # Print number of faces detected every 2 seconds
        current_time = time.time()
        if current_time - last_print_time >= 2:
            print(f"Faces detected: {len(face_locations)}")
            last_print_time = current_time

        for (top, right, bottom, left) in face_locations:
            # Scale face locations back to original size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a rectangle around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        # Display the resulting frame
        cv2.imshow('Video', frame)

        # Wait for a key press
        key = cv2.waitKey(1) & 0xFF

        # If 's' is pressed, save the face data
        if key == ord('s'):
            if face_locations:
                # Encode the face
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                if face_encodings:
                    face_encoding = face_encodings[0]

                    # Convert the face encoding to a string
                    face_encoding_str = ','.join(map(str, face_encoding))

                    # Capture the face image
                    (top, right, bottom, left) = face_locations[0]
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4
                    face_image = frame[top:bottom, left:right]
                    _, face_image_encoded = cv2.imencode('.jpg', face_image)
                    face_image_binary = face_image_encoded.tobytes()

                    # Prompt for the person's name
                    name = simpledialog.askstring("Input", "Enter the name of the person:")

                    if name:
                        try:
                            cursor = con.cursor()

                            # Insert the face data into the database
                            query = "INSERT INTO users (name, image, embedding) VALUES (%s, %s, %s)"
                            cursor.execute(query, (name, face_image_binary, face_encoding_str))
                            con.commit()  # Commit the transaction

                            # Retrieve the new user ID
                            new_user_id = cursor.lastrowid
                            print(f"Inserted {name} into the database with ID: {new_user_id}")

                            # Display the new user ID
                            messagebox.showinfo("Success",
                                                f"Face data for {name} has been stored in the database with ID: {new_user_id}")

                        except mys.Error as err:
                            messagebox.showerror("Error", f"Error: {err}")

                        finally:
                            cursor.close()

                    else:
                        messagebox.showwarning("Input Error", "Name cannot be empty.")

                else:
                    messagebox.showwarning("Encoding Error", "Failed to encode face. Please try again.")
            else:
                messagebox.showwarning("No Face Detected", "No face detected. Please try again when a face is visible.")

        # Break the loop if 'q' is pressed
        elif key == ord('q'):
            break

    # Release the capture and close the window
    cap.release()
    cv2.destroyAllWindows()

# Function to delete a user
def delete_user():
    user_id = simpledialog.askinteger("Input", "Enter User ID to delete:")
    if user_id is not None:
        try:
            cursor = con.cursor()
            query = "DELETE FROM users WHERE id = %s"
            cursor.execute(query, (user_id,))
            con.commit()  # Commit the transaction

            if cursor.rowcount > 0:
                messagebox.showinfo("Success", f"User with ID {user_id} has been deleted.")
            else:
                messagebox.showwarning("Not Found", f"No user found with ID {user_id}.")

        except mys.Error as err:
            messagebox.showerror("Error", f"Error: {err}")

        finally:
            cursor.close()

# Function to recognize faces
def recognize_faces():
    cap = cv2.VideoCapture(0)

    # Retrieve all user embeddings from the database
    cursor = con.cursor()
    cursor.execute("SELECT id, name, embedding FROM users")
    users = cursor.fetchall()
    cursor.close()

    # Convert embeddings from string to numpy arrays
    user_embeddings = []
    user_ids = []
    user_names = []
    for user in users:
        user_id, name, embedding_str = user
        # Ensure embedding_str is a string before processing
        if isinstance(embedding_str, bytes):
            embedding_str = embedding_str.decode('utf-8')  # Decode bytes to string
        # Convert the string to a numpy array
        embedding = np.fromstring(embedding_str, dtype=np.float64, sep=',')  # Use sep to split by comma
        user_embeddings.append(embedding)
        user_ids.append(user_id)
        user_names.append(name)

    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "Failed to capture frame")
            break

        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Detect face locations and encodings
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        for face_encoding, face_location in zip(face_encodings, face_locations):
            # Compare the detected face with all known faces
            matches = face_recognition.compare_faces(user_embeddings, face_encoding)
            name = "Unknown"
            user_id = "Unknown"

            # Use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(user_embeddings, face_encoding)
            best_match_index = np.argmin(face_distances)

            if matches[best_match_index]:
                name = user_names[best_match_index]
                user_id = user_ids[best_match_index]

            # Draw a rectangle around the face and label it
            (top, right, bottom, left) = face_location
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, f"{name} (ID: {user_id})", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

        # Display the resulting frame
        cv2.imshow('Video', frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Create the main GUI window
def main_gui():
    root = Tk()
    root.title("Facial Recognition System")

    # Create buttons for registration and retrieval
    register_button = tk.Button(root, text="Register Face", command=register_face)
    register_button.pack(pady=20)

    retrieve_button = tk.Button(root, text="Retrieve User Details",
                                command=lambda: get_user_details(simpledialog.askinteger("Input", "Enter User ID:")))
    retrieve_button.pack(pady=20)

    # New button to retrieve all user data
    all_users_button = tk.Button(root, text="Retrieve All Users", command=retrieve_all_users)
    all_users_button.pack(pady=20)

    # New button to recognize faces
    recognize_button = tk.Button(root, text="Recognize Faces", command=recognize_faces)
    recognize_button.pack(pady=20)

    # New button to delete users
    delete_button = tk.Button(root, text="Delete User", command=delete_user)
    delete_button.pack(pady=20)

    # Run the application
    root.mainloop()

if __name__ == "__main__":
    main_gui()