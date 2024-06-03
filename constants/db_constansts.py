
class create_table_queries:

    USERS = "CREATE TABLE IF NOT EXISTS \
			users(userID INTEGER AUTO_INCREMENT NOT NULL PRIMARY KEY, name TEXT,\
			userImg LONGBLOB NOT NULL)"

    IDENTIFICATION_RECORDS = "CREATE TABLE IF NOT EXISTS \
			identification_records(userID INTEGER NOT NULL UNIQUE, is_identified BOOL NOT NULL,\
			time_identified TIMESTAMP NOT NULL, valid_till TIMESTAMP NOT NULL)"


class insert_table_queries:

    USERS = "INSERT INTO users\
			(userID,name,userImg)\
					VALUES(%s,'%s','%s')"

    IDENTIFICATION_RECORDS = "INSERT INTO identification_records\
			                (userID,is_identified,time_identified,valid_till)\
					                VALUES(%s,%s,'%s','%s')"


class query_data:

    ID_FOR_NAME = """ SELECT userID from users where name = '%s' """
    ALL_FOR_NAME = """ SELECT * from users where name = '%s' """
    ALL_FOR_ID = """ SELECT * from identification_records where userID = %s """
    IS_IDENTIFIED_FOR_ID = """ SELECT is_identified from identification_records where userID = %s """
    VALID_TILL_FOR_ID = """ SELECT valid_till from identification_records where userID = %s """

class update_data:
    UPDATE_BOOL_WITH_TIME = """ UPDATE identification_records SET is_identified = 0 WHERE valid_till >= '%s' """
    UPDATE_TIMESTAMP = """ UPDATE identification_records SET is_identified = 1, valid_till = '%s' WHERE userID = %s """
    UPDATE_BOOL_FOR_ID = """ UPDATE identification_records SET is_identified = %s WHERE userID = %s """
    UPDATE_TIMESTAMP_WITH_IDENTIFIER = """ UPDATE identification_records SET is_identified = %s, valid_till = '%s' WHERE userID = %s """
    UPDATE_ALL_TIMESTAMPS_WITH_IDENTIFIER = """ UPDATE identification_records SET is_identified = %s, valid_till = '%s', time_identified = '%s' WHERE userID = %s """
class misc_queries:
    SAFE_MODE = 'SET SQL_SAFE_UPDATES = %s'


class Tables:
    USERS = 'users'
    IDENTIFICATION_RECORDS = 'identification_records'
