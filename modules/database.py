import os
import logging
import time
import mysql.connector as mysql_connector
from modules.config_reader import read_config
from mysql.connector import pooling
from constants.db_constansts import insert_table_queries, create_table_queries, misc_queries


def create_pool():
    conf = read_config()
    db_config = conf['local_database'] if str(conf['exec_mode']) == 'local' else conf['database']
    dbconfig = {
        "host": os.getenv('DB_HOST') or db_config['host'],
        "user": os.getenv('DB_USER') or db_config['user'],
        "password": os.getenv('DB_PASSWORD') or db_config['password'],
        "database": os.getenv('DB_NAME') or db_config['db']
    }
    pool = pooling.MySQLConnectionPool(pool_name="mypool",
                                       pool_size=32,
                                       pool_reset_session=True,
                                       **dbconfig)
    logging.debug(
        f'Database connection created with host: {dbconfig["host"]}, port: 3306, database name: {dbconfig["database"]}')
    return pool


connection_pool = create_pool()


# Connect to the database
# using the psycopg2 adapter.
# Pass your database name ,# username , password ,
# hostname and port number
def create_connection():
    conn = None
    try:
        # connection_pool = create_pool()
        conn = connection_pool.get_connection()
    except Exception as err:
        conn = create_connection_with_retry(err)
    curr = conn.cursor()
    curr.execute(misc_queries.SAFE_MODE % 0)
    return conn, curr


def create_connection_with_retry(error, retries=3, delay=5):
    for _ in range(retries):
        try:
            logging.info(f'Retrying to connect to database as we have caught an error: {error}')
            # connect_pool = create_pool()
            return connection_pool.get_connection()
        except mysql_connector.errors.PoolError:
            time.sleep(delay)
    raise Exception("Failed to get a connection from the pool after retries.")


def create_trigger():
    trigger_sql = """CREATE TRIGGER update_identification_records_trigger
    BEFORE UPDATE ON identification_records
    FOR EACH ROW
    BEGIN
        IF NEW.valid_till < NOW() THEN
            SET NEW.is_identified = 0;
        END IF;
    END;"""

    conn, curr = create_connection()
    try:
        curr.execute(trigger_sql)
        conn.commit()
    except mysql_connector.Error as err:
        if err.errno == 1304:  # Error code for trigger already exists
            logging.info("Trigger already exists.")
        else:
            logging.error(f"Error while inserting trigger in database: {err}")
    finally:
        curr.close()
        conn.close()


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


def populate_users(file, name, contact='', email='', address='', city='', state='', country='India'):
    try:
        # Read database configuration
        conn, cursor = create_connection()
        try:
            create_table(create_table_queries.USERS)
            # Execute the INSERT statement
            query = insert_table_queries.USERS, (name, file, contact, email, address, city, state, country)
            logging.debug(f'Query inserted: {query}')
            cursor.execute(query)
            # Commit the changes to the database
            conn.commit()
        except Exception as error:
            logging.error("Error while inserting data in users table. Retrying...")
            logging.debug(f'DB error while inserting data {error}')
            try:
                cursor.execute(insert_table_queries.USERS_IF_FAILED, (name, file, contact, email, address, city, state, country))
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
