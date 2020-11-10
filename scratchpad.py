line = ""
line_data = {'lastname': line[0:35].replace(" ", ""), 'firstname': line[35:55].replace(" ", ""),
             'middlename': line[55:75].replace(" ", ""), 'suffix': line[75:78].replace(" ", ""),
             'birthyear': line[78:82].replace(" ", ""), 'gender': line[82:83].replace(" ", ""),
             'month_of_registration': line[83:85].replace(" ", ""),
             'day_of_registration': line[85:87].replace(" ", ""),
             'year_of_registration': line[87:91].replace(" ", ""), 'house_character': line[91:92].replace(" ", ""),
             'street_number': line[92:99].replace(" ", ""), 'house_suffix': line[99:103].replace(" ", ""),
             'predirection': line[103:105].replace(" ", ""), 'street_name': line[105:135].replace(" ", ""),
             'street_type': line[135:141].replace(" ", ""), 'suffix_direction': line[141:143].replace(" ", ""),
             'residence_extension': line[143:156].replace(" ", ""), 'city': line[156:191].replace(" ", ""),
             'state': line[191:193].replace(" ", ""), 'zip': line[193:198].replace(" ", ""),
             'mail_addr1': line[198:248].replace(" ", ""), 'mail_addr2': line[248:298].replace(" ", ""),
             'mail_addr3': line[298:348].replace(" ", ""), 'mail_addr4': line[348:398].replace(" ", ""),
             'mail_addr5': line[398:448].replace(" ", ""), 'voter_id': line[448:461].replace(" ", "")}

sql_statement = "CREATE TABLE IF NOT EXISTS registrations (  " \
                   "firstname varchar(50), " \
                   "middlename varchar(50), " \
                   "lastname varchar(50), " \
                   "suffix varchar(50), " \
                   "birthyear int, " \
                   "gender varchar(1), " \
                   "month_of_registration int, " \
                   "day_of_registration int, " \
                   "year_of_registration int, " \
                   "house_character	varchar(10), " \
                   "street_number int, " \
                   "house_suffix varchar(20), " \
                   "predirection varchar(20), " \
                   "street_name varchar(50), " \
                   "street_type varchar(10), " \
                   "suffix_direction varchar(10), " \
                   "residence_extension varchar(30), " \
                   "city varchar(30), " \
                   "state varchar(10), " \
                   "zip int, " \
                   "mail_addr1 varchar(50), " \
                   "mail_addr2 varchar(50), " \
                   "mail_addr3 varchar(50), " \
                   "mail_addr4 varchar(50), " \
                   "mail_addr5 varchar(50), " \
                   "voter_id int ); "

import json
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup


def main():
    potential_dead_voters = []
    driver = webdriver.Firefox()
    save_file = "data/dead_voters.json"
    submission_count = 0
    load_files = ["data/class_1_search.json", "data/class_2_search.json", "data/class_3_search.json"]
    for load_file in load_files:
        potential_voters = load_data(load_file)
        for potential_voter in potential_voters:
            if (
                    potential_voter["FIRST_NAME"].lower() == potential_voter["name"].split()[0].lower()
                    and potential_voter["LAST_NAME"].lower() == potential_voter["name"].split()[-1].lower()
            ):
                submission_count = submission_count + 1
                submit_data(driver, potential_voter["FIRST_NAME"], potential_voter["LAST_NAME"],
                            int(potential_voter["birth"].split("/")[0]), int(potential_voter["YEAR_OF_BIRTH"]),
                            potential_voter["ZIP_CODE"])
                is_registered, no_ballot, invalid_voter, person_voted, vote_rejected, app_received_date, \
                ballot_sent_date, ballot_received_date = analyze_submission_result(driver.page_source)
                new_dead_voter = convert_data(save_file, potential_voter, is_registered, no_ballot, invalid_voter,
                                              person_voted, vote_rejected, app_received_date, ballot_sent_date,
                                              ballot_received_date)
                if not is_registered and not invalid_voter:
                    sleep(5)
                    is_registered, no_ballot, invalid_voter, person_voted, vote_rejected, app_received_date, \
                    ballot_sent_date, ballot_received_date = analyze_submission_result(driver.page_source)
                    new_dead_voter = convert_data(save_file, potential_voter, is_registered, no_ballot, invalid_voter,
                                                  person_voted, vote_rejected, app_received_date, ballot_sent_date,
                                                  ballot_received_date)
                if not is_registered and not invalid_voter:
                    sleep(10)
                    is_registered, no_ballot, invalid_voter, person_voted, vote_rejected, app_received_date, \
                    ballot_sent_date, ballot_received_date = analyze_submission_result(driver.page_source)
                    new_dead_voter = convert_data(save_file, potential_voter, is_registered, no_ballot, invalid_voter,
                                                  person_voted, vote_rejected, app_received_date, ballot_sent_date,
                                                  ballot_received_date)

                print(new_dead_voter)
                potential_dead_voters.append(new_dead_voter)
                if submission_count % 100 == 0:
                    print("Saving...")
                    file = open(save_file, 'w')
                    file.write(json.dumps(potential_dead_voters))
                    file.close()
    print("Saving...")
    file = open(save_file, 'w')
    file.write(json.dumps(potential_dead_voters))
    file.close()


def load_data(filepath):
    file = open(filepath, 'r')
    data = json.loads(file.read())
    file.close()
    return data


def submit_data(driver, firstname, lastname, birthmonth, birthyear, zipcode):
    ballot_checker_url = 'https://mvic.sos.state.mi.us/voter/index'
    driver.get(ballot_checker_url)
    firstname_element = driver.find_element_by_id("FirstName")
    firstname_element.send_keys(firstname)
    lastname_element = driver.find_element_by_id("LastName")
    lastname_element.send_keys(lastname)
    birthmonth_element = driver.find_element_by_id("NameBirthMonth")
    Select(birthmonth_element).select_by_index(birthmonth)
    birthyear_element = driver.find_element_by_id("NameBirthYear")
    birthyear_element.send_keys(birthyear)
    zipcode_element = driver.find_element_by_id("ZipCode")
    zipcode_element.send_keys(zipcode)
    submit = driver.find_element_by_id("btnSearchName")
    submit.click()
    sleep(1)


def analyze_submission_result(page_source):
    is_registered = False
    no_ballot = False
    invalid_voter = False
    person_voted = False
    vote_rejected = False
    app_received_date = ""
    ballot_sent_date = ""
    ballot_received_date = ""

    registered_text = "Yes, you are registered!"
    if registered_text in page_source:
        is_registered = True
    not_received_absentee_text = "Your clerk has not recorded receiving your AV Application."
    if not_received_absentee_text in page_source:
        no_ballot = True
    invalid_voter_text = "No voter record matched your search criteria"
    if invalid_voter_text in page_source:
        invalid_voter = True
    vote_rejected_text = "Your absent voter ballot was rejected. Contact your clerk as soon as possible to resolve the issue"
    if vote_rejected_text in page_source:
        vote_rejected_text = True

    html = BeautifulSoup(page_source, 'html.parser')
    bi = html.find(id="lblAbsenteeVoterInformation")
    if is_registered and not no_ballot and not invalid_voter:
        for bolded_title in bi.find_all('b'):
            if bolded_title.text == "Election date":
                person_voted = True
            if bolded_title.text == "Application received":
                app_received_date = bolded_title.next_sibling.next_sibling
            if bolded_title.text == "Ballot sent":
                ballot_sent_date = bolded_title.next_sibling.next_sibling
            if bolded_title.text == "Ballot received":
                ballot_received_date = bolded_title.next_sibling.next_sibling

    return is_registered, no_ballot, invalid_voter, person_voted, vote_rejected, app_received_date, \
           ballot_sent_date, ballot_received_date


def convert_data(savefile, potential_voter, is_registered, no_ballot, invalid_voter, person_voted, vote_rejected,
                 app_received_date, \
                 ballot_sent_date, ballot_received_date):
    new_dead_voter = {}
    new_dead_voter['firstname'] = potential_voter["FIRST_NAME"]
    new_dead_voter['middlename'] = potential_voter["MIDDLE_NAME"]
    new_dead_voter['lastname'] = potential_voter["LAST_NAME"]
    new_dead_voter['fullname'] = potential_voter["name"]
    new_dead_voter["birth"] = potential_voter["birth"]
    new_dead_voter["zip_code"] = potential_voter["ZIP_CODE"]
    new_dead_voter["is_registered"] = is_registered
    new_dead_voter["no_ballot"] = no_ballot
    new_dead_voter["invalid_voter"] = invalid_voter
    new_dead_voter["person_voted"] = person_voted
    new_dead_voter["vote_rejected"] = vote_rejected
    new_dead_voter["app_received_date"] = app_received_date
    new_dead_voter["ballot_sent_date"] = ballot_sent_date
    new_dead_voter["ballot_received_date"] = ballot_received_date
    new_dead_voter["proof_of_death"] = potential_voter["link"]
    return new_dead_voter


if __name__ == '__main__':
    main()