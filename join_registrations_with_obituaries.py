import json
import math
import sqlite3


def main():
    REG_OBIT_JOIN_LIST = []
    obituary_datapath = "data/obituaries.json"
    save_filepath = "data/combined_data.json"
    combine_with_sql_search(obituary_datapath, REG_OBIT_JOIN_LIST, save_filepath)
    #combine_with_json_search(obituary_datapath, REG_OBIT_JOIN_LIST, save_filepath)


def combine_with_sql_search(obituary_datapath, REG_OBIT_JOIN_LIST, save_filepath):
    class_1_search = "SELECT * FROM registrations INNER JOIN obituaries " \
                     "ON obituaries.firstname = registrations.FIRST_NAME " \
                     "AND obituaries.lastname = registrations.LAST_NAME " \
                     "AND obituaries.middlename = registrations.MIDDLE_NAME " \
                     "AND obituaries.birthyear = registrations.YEAR_OF_BIRTH WHERE LENGTH(obituaries.middlename) > 2;"
    class_1_search_results = []
    class_2_search = "SELECT * FROM registrations INNER JOIN obituaries " \
                     "ON obituaries.firstname = registrations.FIRST_NAME " \
                     "AND obituaries.lastname = registrations.LAST_NAME " \
                     "AND obituaries.birthyear = registrations.YEAR_OF_BIRTH " \
                     "WHERE obituaries.middlename LIKE registrations.MIDDLE_NAME AND LENGTH(obituaries.middlename) > 0;"
    class_2_search_results = []
    class_3_search = "SELECT * FROM registrations INNER JOIN obituaries " \
                     "ON obituaries.firstname = registrations.FIRST_NAME " \
                     "AND obituaries.lastname = registrations.LAST_NAME " \
                     "AND obituaries.birthyear = registrations.YEAR_OF_BIRTH;"
    class_3_search_results = []
    conn = sqlite3.connect("data/voters.db")
    cursor = conn.cursor()
    columns = ['FIRST_NAME', 'MIDDLE_NAME', 'LAST_NAME', 'NAME_SUFFIX', 'YEAR_OF_BIRTH', 'GENDER', 'REGISTRATION_DATE',
               'STREET_NUMBER_PREFIX', 'STREET_NUMBER', 'STREET_NUMBER_SUFFIX', 'DIRECTION_PREFIX', 'STREET_NAME',
               'STREET_TYPE', 'DIRECTION_SUFFIX', 'EXTENSION', 'CITY', 'STATE', 'ZIP_CODE', 'MAILING_ADDRESS_LINE_ONE',
               'MAILING_ADDRESS_LINE_TWO', 'MAILING_ADDRESS_LINE_THREE', 'MAILING_ADDRESS_LINE_FOUR',
               'MAILING_ADDRESS_LINE_FIVE', 'VOTER_IDENTIFICATION_NUMBER', 'COUNTY_CODE', 'COUNTY_NAME',
               'JURISDICTION_CODE', 'JURISDICTION_NAME', 'PRECINCT', 'WARD', 'SCHOOL_DISTRICT_CODE',
               'SCHOOL_DISTRICT_NAME', 'STATE_HOUSE_DISTRICT_CODE', 'STATE_HOUSE_DISTRICT_NAME',
               'STATE_SENATE_DISTRICT_CODE', 'STATE_SENATE_DISTRICT_NAME', 'US_CONGRESS_DISTRICT_CODE',
               'US_CONGRESS_DISTRICT_NAME', 'COUNTY_COMMISSIONER_DISTRICT_CODE', 'COUNTY_COMMISSIONER_DISTRICT_NAME',
               'VILLAGE_DISTRICT_CODE', 'VILLAGE_DISTRICT_NAME', 'VILLAGE_PRECINCT', 'SCHOOL_PRECINCT',
               'IS_PERMANENT_ABSENTEE_VOTER', 'VOTER_STATUS_TYPE_CODE', 'UOCAVA_STATUS_CODE', 'UOCAVA_STATUS_NAME',
               'fullname', 'firstname', 'middlename', 'lastname', 'birthmonth', 'birthyear', 'birthday', 'link',
               'death', 'age', 'residence']


    print("About to execute class 1 search")
    cursor.execute(class_1_search)
    print("About to get search results")
    results = cursor.fetchall()
    for result in results:
        result_dict = {}
        for i in range(0, 59):
            result_dict[ columns[i] ] = result[i]
        class_1_search_results.append(result_dict)
    save_filepath = "data/class_1_search.json"
    save_file = open(save_filepath, 'w')
    save_file.write( json.dumps(class_1_search_results) )

    print("About to execute class 2 search")
    cursor.execute(class_2_search)
    print("About to get search results")
    results = cursor.fetchall()
    for result in results:
        result_dict = {}
        for i in range(0, 59):
            result_dict[ columns[i] ] = result[i]
        class_2_search_results.append(result_dict)
    save_filepath = "data/class_2_search.json"
    save_file = open(save_filepath, 'w')
    save_file.write( json.dumps(class_2_search_results) )

    print("About to execute class 3 search")
    cursor.execute(class_3_search)
    print("About to get search results")
    results = cursor.fetchall()
    for result in results:
        result_dict = {}
        for i in range(0, 59):
            result_dict[ columns[i] ] = result[i]
        class_3_search_results.append(result_dict)
    save_filepath = "data/class_3_search.json"
    save_file = open(save_filepath, 'w')
    save_file.write( json.dumps(class_3_search_results) )




def combine_with_json_search(obituary_datapath, REG_OBIT_JOIN_LIST, save_filepath):
    line_count = 0
    obituary_file = open(obituary_datapath, 'r')
    obituary_list = json.loads(obituary_file.read())
    obituary_file.close()
    for i in range(0, 7):
        registration_datapath = f"data/registrations{i}.json"
        registration_file = open(registration_datapath, 'r')
        print(f"Opened {registration_datapath}")
        registration_list = json.loads(registration_file.read())
        for registration in registration_list:
            for obituary in obituary_list:
                obituary_first_name = obituary['name'].lower().split()[0]
                obituary_last_name = obituary['name'].lower().split()[-1]
                try:
                    if registration['LAST_NAME'].lower() in obituary_last_name and registration['FIRST_NAME'].lower() in obituary_first_name and registration['YEAR_OF_BIRTH'] == obituary['birthyear']:
                        reg_obit_join = {}
                        for key in registration.keys():
                            reg_obit_join[key] = registration[key]
                        for key in obituary.keys():
                            reg_obit_join[key] = obituary[key]
                        print(f"{reg_obit_join['FIRST_NAME']} {reg_obit_join['MIDDLE_NAME']} {reg_obit_join['LAST_NAME']} {reg_obit_join['name']}; {reg_obit_join['YEAR_OF_BIRTH']} {reg_obit_join['birth']}; {reg_obit_join['ZIP_CODE']} {reg_obit_join['residence']}")
                        REG_OBIT_JOIN_LIST.append(reg_obit_join)
                except:
                    continue
                line_count = line_count + 1
                if math.log10(line_count) % 1 == 0:
                    print(f"Comparison count: {line_count}")
                if line_count % 10000000000 == 0:
                    print("Saving...")
                    save_file = open(save_filepath, 'w')
                    save_file.write(json.dumps(REG_OBIT_JOIN_LIST))
                    save_file.close()
        registration_file.close()
    save_file = open(save_filepath, 'w')
    save_file.write(json.dumps(REG_OBIT_JOIN_LIST))
    save_file.close()



if __name__ == "__main__":
    main()