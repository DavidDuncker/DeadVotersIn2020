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
            submit_data(driver, potential_voter["FIRST_NAME"], potential_voter["LAST_NAME"],
                        int( potential_voter["birthmonth"] ), int( potential_voter["YEAR_OF_BIRTH"] ),
                        potential_voter["ZIP_CODE"])
            is_registered, no_ballot, invalid_voter, person_voted, vote_rejected, app_received_date, \
            ballot_sent_date, ballot_received_date = analyze_submission_result(driver.page_source)
            new_dead_voter = convert_data(save_file, potential_voter, is_registered, no_ballot, invalid_voter,
                                              person_voted, vote_rejected, app_received_date, ballot_sent_date, ballot_received_date)
            if not is_registered and not invalid_voter:
                new_dead_voter = pause_and_try_again(save_file, driver, potential_voter)
            print(new_dead_voter)
            potential_dead_voters.append(new_dead_voter)
            submission_count = submission_count + 1
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
    sleep(0.5)


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
        vote_rejected = True


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


def convert_data(savefile, potential_voter, is_registered, no_ballot, invalid_voter, person_voted, vote_rejected, app_received_date, \
                ballot_sent_date, ballot_received_date):
    new_dead_voter = {}
    new_dead_voter['firstname'] = potential_voter["FIRST_NAME"]
    new_dead_voter['middlename'] = potential_voter["MIDDLE_NAME"]
    new_dead_voter['lastname'] = potential_voter["LAST_NAME"]
    new_dead_voter['fullname'] = potential_voter["fullname"]
    new_dead_voter["person_voted"] = person_voted
    new_dead_voter["vote_rejected"] = vote_rejected
    new_dead_voter["death"] = potential_voter['death']
    new_dead_voter["birth"] = potential_voter["birthday"]
    new_dead_voter["zip_code"] = potential_voter["ZIP_CODE"]
    new_dead_voter["is_registered"] = is_registered
    new_dead_voter["no_ballot"] = no_ballot
    new_dead_voter["invalid_voter"] = invalid_voter
    new_dead_voter["app_received_date"] = app_received_date
    new_dead_voter["ballot_sent_date"] = ballot_sent_date
    new_dead_voter["ballot_received_date"] = ballot_received_date
    new_dead_voter["proof_of_death"] = potential_voter["link"]
    new_dead_voter["voter_id"] = potential_voter["VOTER_IDENTIFICATION_NUMBER"]
    return new_dead_voter


def pause_and_try_again(save_file, driver, potential_voter):
    sleep(2)
    is_registered, no_ballot, invalid_voter, person_voted, vote_rejected, app_received_date, \
    ballot_sent_date, ballot_received_date = analyze_submission_result(driver.page_source)
    new_dead_voter = convert_data(save_file, potential_voter, is_registered, no_ballot, invalid_voter,
                                  person_voted, vote_rejected, app_received_date, ballot_sent_date,
                                  ballot_received_date)

    if not is_registered and not invalid_voter:
        sleep(4)
        is_registered, no_ballot, invalid_voter, person_voted, vote_rejected, app_received_date, \
        ballot_sent_date, ballot_received_date = analyze_submission_result(driver.page_source)
        new_dead_voter = convert_data(save_file, potential_voter, is_registered, no_ballot, invalid_voter,
                                      person_voted, vote_rejected, app_received_date, ballot_sent_date,
                                      ballot_received_date)
    if not is_registered and not invalid_voter:
        sleep(8)
        is_registered, no_ballot, invalid_voter, person_voted, vote_rejected, app_received_date, \
        ballot_sent_date, ballot_received_date = analyze_submission_result(driver.page_source)
        new_dead_voter = convert_data(save_file, potential_voter, is_registered, no_ballot, invalid_voter,
                                      person_voted, vote_rejected, app_received_date, ballot_sent_date,
                                      ballot_received_date)
    if not is_registered and not invalid_voter:
        sleep(16)
        is_registered, no_ballot, invalid_voter, person_voted, vote_rejected, app_received_date, \
        ballot_sent_date, ballot_received_date = analyze_submission_result(driver.page_source)
        new_dead_voter = convert_data(save_file, potential_voter, is_registered, no_ballot, invalid_voter,
                                      person_voted, vote_rejected, app_received_date, ballot_sent_date,
                                      ballot_received_date)

    return new_dead_voter


if __name__ == '__main__':
    main()