import os
import logging
from modules.config_reader import read_config
from mysql.connector import pooling
from constants.db_constansts import insert_table_queries, create_table_queries, misc_queries


def create_pool():
    conf = read_config()
    db_config = conf['database']
    dbconfig = {
        "host": os.getenv('DB_HOST') or db_config['host'],
        "user": os.getenv('DB_USER') or db_config['user'],
        "password": os.getenv('DB_PASSWORD') or db_config['password'],
        "database": os.getenv('DB_NAME') or db_config['db']
    }
    pool = pooling.MySQLConnectionPool(pool_name="mypool",
                                       pool_size=5,
                                       pool_reset_session=True,
                                       **dbconfig)
    return pool


connection_pool = create_pool()


# Connect to the database
# using the psycopg2 adapter.
# Pass your database name ,# username , password ,
# hostname and port number
def create_connection():
    host = os.getenv('DB_HOST') or 'localhost'
    user = os.getenv('DB_USER') or 'ranadeep'
    password = os.getenv('DB_PASSWORD') or 'rana#123'
    db = os.getenv('DB_NAME') or 'profiles'
    logging.debug(
        f'Database connection created with host: {host}, port: 3306, database name: {db}')
    # conn = connector.connect(host=host,
    #                         user=user,
    #                         passwd=password,
    #                         database=db)
    conn = connection_pool.get_connection()
    curr = conn.cursor()
    curr.execute(misc_queries.SAFE_MODE % 0)
    return conn, curr


def create_table(creation_query):
    try:
        # Get the cursor object from the connection object
        conn, curr = create_connection()
        try:
            # Fire the CREATE query
            curr.execute(creation_query)

        except Exception as error:
            logging.error("Error while creating table", error)
        finally:
            # Close the connection object
            conn.commit()
            conn.close()
    finally:
        # Since we do not have to do anything here we will pass
        pass


def populate_users(file, name, contact='', address='', city='', state='', country='India'):
    try:
        # Read database configuration
        conn, cursor = create_connection()
        try:
            create_table(create_table_queries.USERS)
            # Execute the INSERT statement
            query = insert_table_queries.USERS, (name, file, contact, address, city, state, country)
            logging.debug(f'Query inserted: {query}')
            cursor.execute(query)
            # Commit the changes to the database
            conn.commit()
        except Exception as error:
            logging.error("Error while inserting data in users table. Retrying...")
            logging.debug(f'DB error while inserting data {error}')
            try:
                cursor.execute(insert_table_queries.USERS_IF_FAILED, (name, file, contact, address, city, state, country))
                # Commit the changes to the database
                logging.info(f'Inserted data for user {name}')
                conn.commit()
            except Exception as retry_err:
                logging.error("Error again while retrying data insertion in users table", retry_err)
        finally:
            # Close the connection object
            conn.close()
            cursor.close()
    finally:
        # Since we do not have to do
        # anything here we will pass
        pass


def populate_identification_record(userID, is_identified, time, valid_till, visit_count=0):
    try:
        # Read database configuration
        conn, cursor = create_connection()
        try:
            create_table(create_table_queries.IDENTIFICATION_RECORDS)
            # Execute the INSERT statement
            query = insert_table_queries.IDENTIFICATION_RECORDS % (userID, is_identified, time, valid_till, visit_count)
            logging.debug(f'Query inserted: {query}')
            cursor.execute(query)
            # Commit the changes to the database
            conn.commit()
        except Exception as error:
            logging.error("Error while inserting data in identification record table", error)
        finally:
            # Close the connection object
            conn.close()
    finally:
        # Since we do not have to do
        # anything here we will pass
        pass


def fetch_table_data_in_tuples(name='', query=None):
    try:
        # Read database configuration
        conn, cursor = create_connection()
        records = tuple
        try:
            # query = """ SELECT * from users where name = %s """
            if name == '' and query is None:
                cursor.execute(""" SELECT * from users """)
            elif query is not None:
                cursor.execute(query)
            else:
                cursor.execute(f"""" SELECT * from users where name = {name} """"")
            # Fetch all the records in tuple
            records = cursor.fetchall()

        except Exception as error:
            logging.error("Error while inserting data in users table", error)
        finally:
            # Close the connection object
            conn.close()
    finally:
        # Since we do not have to do
        # anything here we will pass
        return records


def fetch_last_user_id():
    last_record = 0
    try:
        # Read database configuration
        conn, cursor = create_connection()
        try:
            cursor.execute("SELECT userID FROM users ORDER BY userID DESC LIMIT 1")

            for (userID,) in cursor:
                last_record = int(userID)
        except Exception as error:
            logging.error("Error while fetching data from users table", error)
        finally:
            # Close the connection object
            conn.close()
    finally:
        # Since we do not have to do
        # anything here we will pass
        return last_record


def fetch_table_data(table_name):
    conn, cursor = create_connection()
    cursor.execute('select * from ' + table_name)

    header = [row[0] for row in cursor.description]

    rows = cursor.fetchall()

    # Closing connection
    conn.close()

    return header, rows


def update_table(query):
    conn, cursor = create_connection()
    try:
        logging.debug(f'Query inserted {query}')
        cursor.execute(query)
    except Exception as error:
        logging.error("Error while updating data in table", error)
    finally:
        # Close the connection object
        conn.commit()
        conn.close()
