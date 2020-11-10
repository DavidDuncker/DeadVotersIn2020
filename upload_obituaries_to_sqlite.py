import json
import sqlite3
import sys
import traceback



def main():
    database = "data/voters.db"
    tablename = "obituaries"
    json_data = "data/obituaries2.json"
    conn = sqlite3.connect('data/voters.db')
    cursor = conn.cursor()
    query_if_database_exists = "SELECT name FROM sqlite_master WHERE type='table' AND name='obituaries';"
    print("Querying if database exists")
    cursor.execute(query_if_database_exists)
    conn.commit()
    if cursor.fetchone() is None:
        print("No database is found, creating one from scratch")
        create_database(cursor)
        print("Loading data into database")
        load_database(cursor, json_data)
        conn.commit()
    else:
        print("Database is found")
    print("SQL sample code: SELECT name FROM sqlite_master WHERE type='table';")
    print("SQL sample code: SELECT sql FROM sqlite_master WHERE tbl_name = 'obituaries' AND type = 'table';")
    print("SQL sample code: ")
    while(True):
        user_input = input("Enter SQLite statement to execute: ")
        try:
            cursor.execute(user_input)
            conn.commit()
            results = cursor.fetchall()
            for row in results:
                print(row)
        except sqlite3.OperationalError:
            print(traceback.format_exc())

    return conn, cursor


def create_database(cursor):
    sql_statement = "CREATE TABLE IF NOT EXISTS obituaries (  " \
                    "fullname varchar(50), " \
                    "firstname varchar(25), " \
                    "middlename varchar(25), " \
                    "lastname varchar(25), " \
                    "birthmonth int, " \
                    "birthyear int, " \
                    "birthday varchar(15)," \
                    "link varchar(70), " \
                    "death varchar(15)," \
                    "age int," \
                    "residence varchar(50) ); "
    print(sql_statement)
    cursor.execute(sql_statement)


def load_database(cursor, data_file):
    #Load saved data
    data = json.loads( open(data_file, "r").read() )

    #Go through each and every obituary, one at a time
    for obituary in data:
        #Add null values for each and every missing key
        expected_keys = ["name", "birthyear", "birth", "link", "death", "age", "residence"]
        for expected_key in expected_keys:
            if expected_key not in obituary.keys():
                obituary[expected_key] = "null"
            if len(obituary[expected_key])<1:
                obituary[expected_key] = "null"

        # Split up name into first, last, and middle, and make it uppercase
        split_name = obituary["name"].split()
        name_suffix = 0
        obituary["firstname"] = split_name[0].upper().replace(",", "").replace(".", "")
        obituary["lastname"] = split_name[-1].upper().replace(",", "").replace(".", "")
        #Do not count name suffixes like "Jr" or "MD"
        if len(obituary["lastname"])<4:
            obituary["lastname"] = split_name[-2].upper().replace(",", "").replace(".", "")
            name_suffix = 1
        #If there are parentheses in the name, then add the parentheticals to the last name. Like Linda  (Ortega) Scheall
        if "(" in obituary["name"] and ")" in obituary["name"]:
            obituary["lastname"] = split_name[-2 - name_suffix] + " " + split_name[-1 - name_suffix]
            obituary["lastname"] = obituary["lastname"].upper().replace(",", "").replace(".", "")
        obituary["middlename"] = ""
        for word in range(1, len(split_name) - 1 - name_suffix):
            obituary["middlename"] = obituary["middlename"] + split_name[word].upper().replace(",", "").replace(".", "") + " "
            obituary["middlename"] = obituary["middlename"][0:-1]

        #Escape problematic quotation marks
        for item in obituary.keys():
            #obituary[item] = obituary[item].replace('"', '\\"')
            obituary[item] = obituary[item].replace('\'', "\'\'")

        #Create "birth month" column
        obituary["birthmonth"] = obituary['birth'].split("/")[0]

        #Construct SQL statement
        sql_statement = f"INSERT INTO obituaries VALUES ( \'{obituary['name']}\', \'{obituary['firstname']}\', \'{obituary['middlename']}\', " \
                        f"\'{obituary['lastname']}\', {obituary['birthmonth']}," \
                        f" {obituary['birthyear']}, \'{obituary['birth']}\', \'{obituary['link']}\', " \
                        f"\'{obituary['death']}\', {obituary['age']}, \'{obituary['residence']}\' );"
        print(sql_statement)
        #Run SQL statement
        cursor.execute(sql_statement)




if __name__ == "__main__":
    main()