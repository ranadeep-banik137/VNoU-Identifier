import os
import logging
import mysql.connector as connector
from constants.db_constansts import insert_table_queries, create_table_queries, misc_queries


# Connect to the database
# using the psycopg2 adapter.
# Pass your database name ,# username , password ,
# hostname and port number
def create_connection():
	host = os.getenv('DB_HOST') or 'localhost'
	user = os.getenv('DB_USER') or 'ranadeep'
	password = os.getenv('DB_PASSWORD') or 'rana#123'
	db = os.getenv('DB_NAME') or 'profiles'
	logging.debug(f'Database connection created with host : {host}, user : {user}, password : {password}, database name : {db}')
	conn = connector.connect(host=host,
							 user=user,
							 passwd=password,
							 database=db)
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
			logging.error("Error while creating users table", error)
		finally:
			# Close the connection object
			conn.commit()
			conn.close()
	finally:
		# Since we do not have to do anything here we will pass
		pass


def populate_users(userID,file,name):
	try:
		# Read database configuration
		conn, cursor = create_connection()
		try:
			create_table(create_table_queries.USERS)
			# Execute the INSERT statement
			# Convert the image data to Binary
			cursor.execute("INSERT INTO users\
					(userID,name,userImg) " +
					"VALUES(%s,%s,%s)",
					(userID, name, file))
			#cursor.execute(insert_table_queries.USERS % (userID, name, file))
			# Commit the changes to the database
			conn.commit()
		except Exception as error:
			logging.error("Error while inserting data in users table", error)
		finally:
			# Close the connection object
			conn.close()
			cursor.close()
	finally:
		# Since we do not have to do
		# anything here we will pass
		pass


def populate_identification_record(userID, time, is_identified, valid_till):
	try:
		# Read database configuration
		conn, cursor = create_connection()
		try:
			create_table(create_table_queries.IDENTIFICATION_RECORDS)
			# Execute the INSERT statement
			# Convert the image data to Binary
			cursor.execute(insert_table_queries.IDENTIFICATION_RECORDS % (userID, time, is_identified, valid_till))
			# Commit the changes to the database
			conn.commit()
		except Exception as error:
			logging.error("Error while inserting data in users table", error)
		finally:
			# Close the connection object
			conn.close()
	finally:
		# Since we do not have to do
		# anything here we will pass
		pass


# Call the create table method
def insert_table_data(id, blob, name):
	populate_users(id, blob, name)


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
			# Execute the INSERT statement
			# Convert the image data to Binary
			# cursor.execute(query, (name,))
			# Commit the changes to the database
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
		cursor.execute(query)
	except Exception as error:
		logging.error("Error while updating data in table", error)
	finally:
		# Close the connection object
		conn.commit()
		conn.close()
