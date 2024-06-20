import sqlite3
from datetime import datetime

# Nom de la base de données
db_name = 'chatroom.db'

def create_connection(db_file):
    """ Crée une connexion à la base de données SQLite spécifiée par db_file. """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def user_login(conn):
    """ Permet à l'utilisateur de se connecter en utilisant le nom d'utilisateur et le mot de passe. """
    username = input("Entrez votre nom d'utilisateur: ")
    password = input("Entrez votre mot de passe: ")

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM Users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        if user:
            print("Connexion réussie!")
            return user[0]  # Retourne l'ID de l'utilisateur
        else:
            print("Nom d'utilisateur ou mot de passe incorrect.")
            return None
    except sqlite3.Error as e:
        print(e)
        return None

def list_chatrooms(conn):
    """ Liste toutes les chatrooms disponibles. """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT room_id, room_name FROM ChatRooms")
        chatrooms = cursor.fetchall()
        print("\nSalles de chat disponibles :")
        for room in chatrooms:
            print(f"{room[0]}: {room[1]}")
        return chatrooms
    except sqlite3.Error as e:
        print(e)
        return []

def choose_chatroom(chatrooms):
    """ Permet à l'utilisateur de choisir une salle de chat. """
    room_id = input("Entrez l'ID de la salle de chat que vous souhaitez rejoindre: ")
    try:
        room_id = int(room_id)
        for room in chatrooms:
            if room[0] == room_id:
                return room_id
        print("ID de la salle de chat invalide.")
        return None
    except ValueError:
        print("Veuillez entrer un numéro valide.")
        return None

def display_messages(conn, room_id):
    """ Affiche tous les messages d'une salle de chat donnée. """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Users.username, Messages.message_text, Messages.created_at
            FROM Messages
            JOIN Users ON Messages.user_id = Users.user_id
            WHERE Messages.room_id=?
            ORDER BY Messages.created_at
        """, (room_id,))
        messages = cursor.fetchall()
        print("\nMessages dans cette salle de chat :")
        for msg in messages:
            print(f"[{msg[2]}] {msg[0]}: {msg[1]}")
    except sqlite3.Error as e:
        print(e)

def send_message(conn, user_id, room_id):
    """ Permet à l'utilisateur d'envoyer un message dans une salle de chat. """
    message_text = input("Entrez votre message : ")
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Messages (user_id, room_id, message_text, created_at) VALUES (?, ?, ?, ?)",
                       (user_id, room_id, message_text, datetime.now()))
        conn.commit()
        print("Message envoyé!")
    except sqlite3.Error as e:
        print(e)

def main():
    """ Fonction principale pour exécuter le script de chatroom. """
    conn = create_connection(db_name)
    if not conn:
        print("Erreur de connexion à la base de données.")
        return

    user_id = None
    while not user_id:
        user_id = user_login(conn)

    chatrooms = list_chatrooms(conn)
    if not chatrooms:
        print("Aucune salle de chat disponible.")
        return

    room_id = None
    while not room_id:
        room_id = choose_chatroom(chatrooms)

    while True:
        print("\nOptions:")
        print("1. Afficher les messages")
        print("2. Envoyer un message")
        print("3. Quitter")
        option = input("Choisissez une option: ")

        if option == '1':
            display_messages(conn, room_id)
        elif option == '2':
            send_message(conn, user_id, room_id)
        elif option == '3':
            print("Déconnexion. À bientôt!")
            break
        else:
            print("Option invalide, veuillez réessayer.")

    conn.close()

if __name__ == '__main__':
    main()
