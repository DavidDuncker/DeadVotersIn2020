import json
import math
import os
from zipfile import ZipFile

import requests


def main():
    download_data("http://69.64.83.144/~mi/download/20201012/Entire%20State%20October.zip",
                  "data/Entire State October.zip",
                  "EntireStateVoters.csv")
    convert_data("data/EntireStateVoters.csv")


def download_data(download_link, download_zipfile, uncompressed_file):
    if os.path.exists("data/EntireStateVoters.csv"):
        print("Data found on local hard drive")
        return
    print("Connecting to network to download data")
    download_filename = "data/Entire State October.zip"
    network_file = requests.get(download_link)
    print("Writing data to disk")
    download_file = open(download_zipfile, 'wb')
    download_file.write(network_file.content)
    download_file.close()
    print("Extracting relevant data from compressed file")
    downloaded_zipfile = ZipFile(download_zipfile, 'r')
    downloaded_zipfile.extract(member=uncompressed_file, path="data/")
    downloaded_zipfile.close()
    print("Finished extracting, deleting original compressed download")
    os.remove(download_zipfile)
    return


def convert_data(original_file):
    data_file = open(original_file, "r", encoding="latin-1")
    data_file.readline()
    all_data = []
    line_count = 0
    save_file_count = 0
    for line in data_file:
        data = parse_line_data_into_dictionary(line)
        all_data.append(data)
        line_count = line_count + 1
        if line_count % 10000 == 0:
            print(data)
            print(line_count)
        if line_count % 1000000 == 0:
            save_batch(all_data, save_file_count)
            save_file_count = save_file_count + 1
            all_data = []
    data_file.close()


def save_batch(all_data, save_file_count):
    save_file = open(f"data/registrations{save_file_count}.json", 'w')
    print("Save file open")
    save_file.write(json.dumps(all_data))
    print("Save file written")
    save_file.close()
    print("Save file closed")


def parse_line_data_into_dictionary(line):
    data_keys = ["LAST_NAME", "FIRST_NAME", "MIDDLE_NAME", "NAME_SUFFIX", "YEAR_OF_BIRTH", "GENDER",
                 "REGISTRATION_DATE", "STREET_NUMBER_PREFIX", "STREET_NUMBER", "STREET_NUMBER_SUFFIX",
                 "DIRECTION_PREFIX", "STREET_NAME", "STREET_TYPE", "DIRECTION_SUFFIX", "EXTENSION", "CITY", "STATE",
                 "ZIP_CODE", "MAILING_ADDRESS_LINE_ONE", "MAILING_ADDRESS_LINE_TWO", "MAILING_ADDRESS_LINE_THREE",
                 "MAILING_ADDRESS_LINE_FOUR", "MAILING_ADDRESS_LINE_FIVE", "VOTER_IDENTIFICATION_NUMBER", "COUNTY_CODE",
                 "COUNTY_NAME", "JURISDICTION_CODE", "JURISDICTION_NAME", "PRECINCT", "WARD", "SCHOOL_DISTRICT_CODE",
                 "SCHOOL_DISTRICT_NAME", "STATE_HOUSE_DISTRICT_CODE", "STATE_HOUSE_DISTRICT_NAME",
                 "STATE_SENATE_DISTRICT_CODE", "STATE_SENATE_DISTRICT_NAME", "US_CONGRESS_DISTRICT_CODE",
                 "US_CONGRESS_DISTRICT_NAME", "COUNTY_COMMISSIONER_DISTRICT_CODE", "COUNTY_COMMISSIONER_DISTRICT_NAME",
                 "VILLAGE_DISTRICT_CODE", "VILLAGE_DISTRICT_NAME", "VILLAGE_PRECINCT", "SCHOOL_PRECINCT",
                 "IS_PERMANENT_ABSENTEE_VOTER", "VOTER_STATUS_TYPE_CODE", "UOCAVA_STATUS_CODE", "UOCAVA_STATUS_NAME"]
    line_split = line.replace('"', '').split(",")
    line_data = {}
    for i in range(0, len(data_keys) ):
        line_data[ data_keys[i] ] = line_split[i]
    return line_data


if __name__ == "__main__":
    main()

