#Facial Recognition

This a Python-based facial-recognition system integrated with MySQL for storing and managing user data.
The system allows you to **register faces**, **recognize users in real time**, **retrieve stored used details**, and **manage the database** through a simple Tkinter GUI.

----

#Project Overview

This project provides a local, GUI-based facial recognition system that uses **OpenCV** and **face_recognition** for image processing and facial encoding, while storing user information and face embeddings in a **MySQL database**.
It supports face registration, recognition, user retrieval, and deletion - all from a clean, and interactive interface.

---

#Installation

###1. Clone the repository
'''bash
git clone https://github.com/jellyyyzzz/facial-recognition.git
cd Facial-Recognition

###2. Install dependencies
pip install -r requirements.txt

###3. Set up the MySQL database
 -Create a database name face_recognition and a table named users

CREATE DATABASE face_recognition;

USE face_recognition;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    image LONGBLOB,
    embedding LONGTEXT
);
