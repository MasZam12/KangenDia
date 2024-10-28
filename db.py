import mysql.connector

def create_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',  # Ganti dengan username database Anda
        password='',  # Ganti dengan password database Anda
        database='sispakdao'  # Ganti dengan nama database Anda
    )
    return connection