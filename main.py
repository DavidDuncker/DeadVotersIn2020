import upload_registrations_to_sqlite
import death_webscraper
import upload_obituaries_to_sqlite
import join_registrations_with_obituaries
import scan_ballot_submissions

def main():
    print("Downloading most recent Michigan registration data. This will take a few minutes.")
    upload_registrations_to_sqlite.download_and_unzip_data()
    print("Create database, and then upload all data to it. This will take a few minutes")
    print('This subroutine creates the file "data/voters.db"')
    upload_registrations_to_sqlite.initialize_database()

    print("This is a webscraper that uses Selenium and a Firefox webdriver to download ~45,000 obituaries")
    print("Warning: You need to stop this manually after ~3 hours, "
          "otherwise you will end up with a bunch of duplicates")
    death_webscraper.main()

    print("This will upload obituaries to sqlite")
    print("Warning: you may have to change the json_data variable's value to 'data/obituaries2.json' "
          "to get this to work")
    upload_obituaries_to_sqlite.main()

    print("Now we will create a bunch of json files that combines registration data with obituary data")
    print("Give this a few minutes")
    join_registrations_with_obituaries.main()

    print("Now we will invoke yet another webscraper to determine if an individual with an identifying "
          "first name, last name, and year of birth has submitted a ballot. We will use the birthmonth "
          "provided by the obituary")
    scan_ballot_submissions.main()

if __name__ == "__main__":
    main()
