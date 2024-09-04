# Import neophodnih modula
import mysql.connector
from mysql.connector import errorcode

# Naziv baze podataka
DB_NAME = 'user_odjeca'

# Konfiguracija za konekciju na MySQL server
config = {
    'user': 'root',
    'password': 'ednan2544',
    'host': '127.0.0.1',
    'port': 3306
}

# Funkcija za kreiranje baze podataka
def create_database(cursor):
    try:
        cursor.execute(
            f"CREATE DATABASE {DB_NAME} DEFAULT CHARACTER SET 'utf8'"
        )
    except mysql.connector.Error as err:
        print(f"Failed creating database: {err}")
        exit(1)

# Konekcija na MySQL server
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

try:
    # Pokušaj korištenja baze podataka
    cursor.execute(f"USE {DB_NAME}")
except mysql.connector.Error as err:
    # Ako baza podataka ne postoji, kreiraj je
    print(f"Database {DB_NAME} does not exist.")
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor)
        print(f"Database {DB_NAME} created successfully.")
        cnx.database = DB_NAME
    else:
        print(err)
        exit(1)

# Zatvaranje kursora i konekcije
cursor.close()
cnx.close()
