import mysql.connector
from mysql.connector import errorcode

DB_NAME = 'user_odjeca'

config = {
    'user': 'user',
    'password': 'pw',
    'host': '127.0.0.1',
    'port': 3306
}


def create_database(cursor):
    try:
        cursor.execute(
            f"CREATE DATABASE {DB_NAME} DEFAULT CHARACTER SET 'utf8'"
        )
    except mysql.connector.Error as err:
        print(f"Failed creating database: {err}")
        exit(1)


cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

try:

    cursor.execute(f"USE {DB_NAME}")
except mysql.connector.Error as err:

    print(f"Database {DB_NAME} does not exist.")
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor)
        print(f"Database {DB_NAME} created successfully.")
        cnx.database = DB_NAME
    else:
        print(err)
        exit(1)


cursor.close()
cnx.close()
