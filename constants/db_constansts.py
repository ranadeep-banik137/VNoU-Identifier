class create_table_queries:
    USERS = "CREATE TABLE IF NOT EXISTS \
			identifiers (CustID TEXT PRIMARY KEY, Name TEXT NOT NULL,\
			CustImg LONGBLOB NOT NULL, Contact TEXT, DOB TEXT, Email TEXT, Address TEXT, City TEXT, State TEXT, Country TEXT)"

class insert_table_queries:
    USERS = """INSERT INTO identifiers (CustID, Name, CustImg, Contact, DOB, Email, Address, City, State, Country)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    USERS_IF_FAILED = "INSERT INTO identifiers\
			(CustID,Name,CustImg,Contact,DOB,Email,Address,City,State,Country)\
					VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"


class query_data:
    ID_FOR_NAME = """ SELECT CustID from identifiers where Name = '%s' """
    EMAIL_FOR_ID = """ SELECT Email from identifiers where CustID = '%s' """
    ALL_USER_DETAILS_FOR_ID = """ SELECT * from identifiers where CustID = '%s' """
    ALL_FOR_NAME = """ SELECT * from identifiers where Name = '%s' """
    CONTACT_FOR_ID = """ SELECT Contact from identifiers where CustID = '%s' """


class misc_queries:
    SAFE_MODE = 'SET SQL_SAFE_UPDATES = %s'


class Tables:
    USERS = 'identifiers'
