import sqlite3
from datetime import datetime
import bcrypt

# Nom de la base de données SQLite
db_name = 'chatroom.db'


def create_connection(db_file):
    """ Crée une connexion à la base de données SQLite spécifiée par db_file. """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connexion établie avec SQLite, version {sqlite3.version}")
    except sqlite3.Error as e:
        print(e)
    return conn


def create_table(conn, create_table_sql):
    """ Crée une table à partir de la requête create_table_sql. """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)


def initialize_database(conn):
    """ Crée les tables de la base de données et insère des données de test. """

    # Définition des requêtes SQL pour la création des tables
    create_users_table = """
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );"""

    create_chatrooms_table = """
    CREATE TABLE IF NOT EXISTS ChatRooms (
        room_id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_name TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );"""

    create_userchatrooms_table = """
    CREATE TABLE IF NOT EXISTS UserChatRooms (
        user_chatroom_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        room_id INTEGER NOT NULL,
        role TEXT DEFAULT 'member',
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES Users(user_id),
        FOREIGN KEY (room_id) REFERENCES ChatRooms(room_id)
    );"""

    create_messages_table = """
    CREATE TABLE IF NOT EXISTS Messages (
        message_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        room_id INTEGER NOT NULL,
        message_text TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES Users(user_id),
        FOREIGN KEY (room_id) REFERENCES ChatRooms(room_id)
    );"""

    create_files_table = """
    CREATE TABLE IF NOT EXISTS Files (
        file_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        room_id INTEGER NOT NULL,
        message_id INTEGER NOT NULL,
        file_name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES Users(user_id),
        FOREIGN KEY (room_id) REFERENCES ChatRooms(room_id),
        FOREIGN KEY (message_id) REFERENCES Messages(message_id)
    );"""

    create_reactions_table = """
    CREATE TABLE IF NOT EXISTS Reactions (
        reaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        message_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        reaction_type TEXT NOT NULL,
        reacted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (message_id) REFERENCES Messages(message_id),
        FOREIGN KEY (user_id) REFERENCES Users(user_id)
    );"""

    # Créer les tables dans la base de données
    create_table(conn, create_users_table)
    create_table(conn, create_chatrooms_table)
    create_table(conn, create_userchatrooms_table)
    create_table(conn, create_messages_table)
    create_table(conn, create_files_table)
    create_table(conn, create_reactions_table)

    # Insérer des données de test dans la base de données
    insert_initial_data(conn)


def insert_initial_data(conn):
    """ Insère des données de test dans les tables. """
    print("Insertion des données de test dans la base de données...")
    users = [
        ('Alice', 'password123', 'alice@example.com'),
        ('Bob', 'password456', 'bob@example.com'),
        ('Charlie', 'password789', 'charlie@example.com')
    ]

    chatrooms = [
        ('General',),
        ('Music',)
    ]

    # Insérer les utilisateurs
    try:
        c = conn.cursor()
        c.executemany('INSERT INTO Users (username, password, email) VALUES (?, ?, ?)', users)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de l'insertion des utilisateurs : {e}")

    # Insérer les chatrooms
    try:
        c.executemany('INSERT INTO ChatRooms (room_name) VALUES (?)', chatrooms)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de l'insertion des chatrooms : {e}")

    # Associer les utilisateurs aux chatrooms
    userchatrooms = [
        (1, 1, 'admin'),  # Alice est admin de "General"
        (2, 1, 'member'),  # Bob est membre de "General"
        (3, 2, 'member'),  # Charlie est membre de "Music"
        (1, 2, 'member'),  # Alice est membre de "Music"
        (2, 2, 'admin')  # Bob est admin de "Music"
    ]

    try:
        c.executemany('INSERT INTO UserChatRooms (user_id, room_id, role, joined_at) VALUES (?, ?, ?, ?)',
                      [(uc[0], uc[1], uc[2], datetime.now()) for uc in userchatrooms])
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de l'insertion des associations utilisateur-chatroom : {e}")

    # Insérer des messages de test
    messages = [
        (1, 1, "Hello everyone!"),  # Alice envoie un message dans "General"
        (2, 1, "Hi Alice!"),  # Bob envoie un message dans "General"
        (3, 2, "Great song!"),  # Charlie envoie un message dans "Music"
    ]

    try:
        c.executemany('INSERT INTO Messages (user_id, room_id, message_text) VALUES (?, ?, ?)', messages)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de l'insertion des messages : {e}")

    # Insérer des fichiers de test
    files = [
        (1, 1, 1, "image.png", "/files/image.png"),  # Alice partage un fichier dans "General"
        (2, 1, 2, "doc.pdf", "/files/doc.pdf"),  # Bob partage un fichier dans "General"
        (3, 2, 3, "song.mp3", "/files/song.mp3")  # Charlie partage un fichier dans "Music"
    ]

    try:
        c.executemany('INSERT INTO Files (user_id, room_id, message_id, file_name, file_path) VALUES (?, ?, ?, ?, ?)',
                      files)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de l'insertion des fichiers : {e}")

# Exécution du script pour initialiser la base de données
if __name__ == '__database__' or 1:
    conn = create_connection(db_name)
    if conn is not None:
        initialize_database(conn)
        conn.close()
    else:
        print("Erreur! impossible de créer la connexion à la base de données.")
else:
    print("Le script database.py a été importé.")
