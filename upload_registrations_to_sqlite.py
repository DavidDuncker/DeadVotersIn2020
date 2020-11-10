import sqlite3
import requests
import os
from zipfile import ZipFile


def main():
    download_and_unzip_data()

    connection, cursor = initialize_database()
    #while(True):
    #    user_input = input("Enter SQLite statement to execute: ")
    #    cursor.execute(user_input)
    #    connection.commit()
    #    results = cursor.fetchall()
    #    for row in results:
    #        print(row)


def download_and_unzip_data():
    #Check if data is already downloaded
    if os.path.exists("data/EntireStateVoters.csv"):
        print("Data found on local hard drive")
        return

    #Connect to internet
    print("Connecting to network to download data")
    url = "http://69.64.83.144/~mi/download/20201012/Entire%20State%20October.zip"
    download_filename = "data/Entire State October.zip"
    network_file = requests.get(url)

    #Download data
    print("Writing data to disk")
    download_file = open(download_filename, 'wb')
    download_file.write(network_file.content)
    download_file.close()

    #Unzip data and delete zipfile
    print("Extracting relevant data from compressed file")
    downloaded_zipfile = ZipFile(download_filename, 'r')
    downloaded_zipfile.extract(member="EntireStateVoters.csv", path="data/")
    downloaded_zipfile.close()
    print("Finished extracting, deleting original compressed download")
    os.remove("data/Entire State October.zip")
    return


def initialize_database():
    #Connect to SQLite
    conn = sqlite3.connect('data/voters.db')
    cursor = conn.cursor()

    #Check if database table already exists; create it if necessary
    query_if_database_exists = "SELECT name FROM sqlite_master WHERE type='table' AND name='registrations';"
    print("Querying if database exists")
    cursor.execute(query_if_database_exists)
    conn.commit()
    if cursor.fetchone() is None:
        print("No database is found, creating one from scratch")
        create_database(cursor)
        print("Loading data into database")
        load_database(cursor)
        conn.commit()
    else:
        print("Database is found")
    return conn, cursor


def create_database(cursor):
    sql_statement = 'CREATE TABLE IF NOT EXISTS registrations ( ' \
                    'FIRST_NAME varchar(50), ' \
                    'MIDDLE_NAME varchar(50), ' \
                    'LAST_NAME varchar(50), ' \
                    'NAME_SUFFIX varchar(50), ' \
                    'YEAR_OF_BIRTH int, ' \
                    'GENDER varchar(1), ' \
                    'REGISTRATION_DATE varchar(12), ' \
                    'STREET_NUMBER_PREFIX varchar(10), ' \
                    'STREET_NUMBER int, ' \
                    'STREET_NUMBER_SUFFIX varchar(10), ' \
                    'DIRECTION_PREFIX varchar(10), ' \
                    'STREET_NAME varchar(50), ' \
                    'STREET_TYPE varchar(10), ' \
                    'DIRECTION_SUFFIX varchar(10), ' \
                    'EXTENSION varchar(50), ' \
                    'CITY varchar(50), ' \
                    'STATE varchar(3), ' \
                    'ZIP_CODE INT, ' \
                    'MAILING_ADDRESS_LINE_ONE varchar(50), ' \
                    'MAILING_ADDRESS_LINE_TWO varchar(50), ' \
                    'MAILING_ADDRESS_LINE_THREE varchar(50), ' \
                    'MAILING_ADDRESS_LINE_FOUR varchar(50), ' \
                    'MAILING_ADDRESS_LINE_FIVE varchar(50), ' \
                    'VOTER_IDENTIFICATION_NUMBER INT, ' \
                    'COUNTY_CODE varchar(15), ' \
                    'COUNTY_NAME varchar(50), ' \
                    'JURISDICTION_CODE varchar(50), ' \
                    'JURISDICTION_NAME varchar(50), ' \
                    'PRECINCT varchar(10), ' \
                    'WARD varchar(10), ' \
                    'SCHOOL_DISTRICT_CODE varchar(10), ' \
                    'SCHOOL_DISTRICT_NAME varchar(50), ' \
                    'STATE_HOUSE_DISTRICT_CODE varchar(10), ' \
                    'STATE_HOUSE_DISTRICT_NAME varchar(50), ' \
                    'STATE_SENATE_DISTRICT_CODE varchar(10), ' \
                    'STATE_SENATE_DISTRICT_NAME varchar(50), ' \
                    'US_CONGRESS_DISTRICT_CODE varchar(10), ' \
                    'US_CONGRESS_DISTRICT_NAME varchar(50), ' \
                    'COUNTY_COMMISSIONER_DISTRICT_CODE varchar(10), ' \
                    'COUNTY_COMMISSIONER_DISTRICT_NAME varchar(50), ' \
                    'VILLAGE_DISTRICT_CODE varchar(10), ' \
                    'VILLAGE_DISTRICT_NAME varchar(50), ' \
                    'VILLAGE_PRECINCT varchar(50), ' \
                    'SCHOOL_PRECINCT varchar(50), ' \
                    'IS_PERMANENT_ABSENTEE_VOTER varchar(10), ' \
                    'VOTER_STATUS_TYPE_CODE varchar(50), ' \
                    'UOCAVA_STATUS_CODE varchar(50), ' \
                    'UOCAVA_STATUS_NAME varchar(50)' \
                    '); '
    cursor.execute(sql_statement)


def load_database(cursor):
    #Count number of lines in file
    data_file = open("data/EntireStateVoters.csv", "r",  encoding="latin-1")
    total_lines = 0
    for line in data_file:
        total_lines = total_lines + 1
    data_file.close()

    #Read each line
    data_file = open("data/EntireStateVoters.csv", "r",  encoding="latin-1")
    line_count = 0
    for line in data_file:
        line_tuple = parse_line_data_into_dictionary(line)
        sql_statement = "INSERT INTO registrations VALUES " \
                        "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, " \
                        "?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? );"
        cursor.executemany(sql_statement, line_tuple)
        line_count = line_count + 1
        if line_count % 10000 == 0:
            print(f"{line_count} out of {total_lines} uploaded.")

    data_file.close()


def parse_line_data_into_dictionary(line):
    line_data = {}

    line_data['LAST_NAME'], line_data['FIRST_NAME'], line_data['MIDDLE_NAME'], line_data['NAME_SUFFIX'],  \
    line_data['YEAR_OF_BIRTH'], line_data['GENDER'], line_data['REGISTRATION_DATE'], line_data['STREET_NUMBER_PREFIX'], \
    line_data['STREET_NUMBER'], line_data['STREET_NUMBER_SUFFIX'], line_data['DIRECTION_PREFIX'],  \
    line_data['STREET_NAME'], line_data['STREET_TYPE'], line_data['DIRECTION_SUFFIX'], line_data['EXTENSION'],  \
    line_data['CITY'], line_data['STATE'], line_data['ZIP_CODE'], line_data['MAILING_ADDRESS_LINE_ONE'],  \
    line_data['MAILING_ADDRESS_LINE_TWO'], line_data['MAILING_ADDRESS_LINE_THREE'],  \
    line_data['MAILING_ADDRESS_LINE_FOUR'], line_data['MAILING_ADDRESS_LINE_FIVE'],  \
    line_data['VOTER_IDENTIFICATION_NUMBER'], line_data['COUNTY_CODE'], line_data['COUNTY_NAME'],  \
    line_data['JURISDICTION_CODE'], line_data['JURISDICTION_NAME'], line_data['PRECINCT'], line_data['WARD'],  \
    line_data['SCHOOL_DISTRICT_CODE'], line_data['SCHOOL_DISTRICT_NAME'], line_data['STATE_HOUSE_DISTRICT_CODE'],  \
    line_data['STATE_HOUSE_DISTRICT_NAME'], line_data['STATE_SENATE_DISTRICT_CODE'],  \
    line_data['STATE_SENATE_DISTRICT_NAME'], line_data['US_CONGRESS_DISTRICT_CODE'],  \
    line_data['US_CONGRESS_DISTRICT_NAME'], line_data['COUNTY_COMMISSIONER_DISTRICT_CODE'],  \
    line_data['COUNTY_COMMISSIONER_DISTRICT_NAME'], line_data['VILLAGE_DISTRICT_CODE'],  \
    line_data['VILLAGE_DISTRICT_NAME'], line_data['VILLAGE_PRECINCT'], line_data['SCHOOL_PRECINCT'],  \
    line_data['IS_PERMANENT_ABSENTEE_VOTER'], line_data['VOTER_STATUS_TYPE_CODE'], line_data['UOCAVA_STATUS_CODE'],  \
    line_data['UOCAVA_STATUS_NAME'] = line[1:-2].split('","')

    line_tuple = [( line_data['FIRST_NAME'], line_data['MIDDLE_NAME'], line_data['LAST_NAME'],  line_data['NAME_SUFFIX'],  \
        line_data['YEAR_OF_BIRTH'], line_data['GENDER'], line_data['REGISTRATION_DATE'], line_data['STREET_NUMBER_PREFIX'], \
        line_data['STREET_NUMBER'], line_data['STREET_NUMBER_SUFFIX'], line_data['DIRECTION_PREFIX'],  \
        line_data['STREET_NAME'], line_data['STREET_TYPE'], line_data['DIRECTION_SUFFIX'], line_data['EXTENSION'],  \
        line_data['CITY'], line_data['STATE'], line_data['ZIP_CODE'], line_data['MAILING_ADDRESS_LINE_ONE'],  \
        line_data['MAILING_ADDRESS_LINE_TWO'], line_data['MAILING_ADDRESS_LINE_THREE'],  \
        line_data['MAILING_ADDRESS_LINE_FOUR'], line_data['MAILING_ADDRESS_LINE_FIVE'],  \
        line_data['VOTER_IDENTIFICATION_NUMBER'], line_data['COUNTY_CODE'], line_data['COUNTY_NAME'],  \
        line_data['JURISDICTION_CODE'], line_data['JURISDICTION_NAME'], line_data['PRECINCT'], line_data['WARD'],  \
        line_data['SCHOOL_DISTRICT_CODE'], line_data['SCHOOL_DISTRICT_NAME'], line_data['STATE_HOUSE_DISTRICT_CODE'],  \
        line_data['STATE_HOUSE_DISTRICT_NAME'], line_data['STATE_SENATE_DISTRICT_CODE'],  \
        line_data['STATE_SENATE_DISTRICT_NAME'], line_data['US_CONGRESS_DISTRICT_CODE'],  \
        line_data['US_CONGRESS_DISTRICT_NAME'], line_data['COUNTY_COMMISSIONER_DISTRICT_CODE'],  \
        line_data['COUNTY_COMMISSIONER_DISTRICT_NAME'], line_data['VILLAGE_DISTRICT_CODE'],  \
        line_data['VILLAGE_DISTRICT_NAME'], line_data['VILLAGE_PRECINCT'], line_data['SCHOOL_PRECINCT'],  \
        line_data['IS_PERMANENT_ABSENTEE_VOTER'], line_data['VOTER_STATUS_TYPE_CODE'], line_data['UOCAVA_STATUS_CODE'],  \
        line_data['UOCAVA_STATUS_NAME'] )]
    return line_tuple


if __name__ == '__main__':
    main()

