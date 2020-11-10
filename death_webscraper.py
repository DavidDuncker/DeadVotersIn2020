from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
import json

def main():
    list_of_obituaries = []
    page_count = 1
    save_file = "data/obituaries.json"
    print("Opening Firefox.")
    driver, parsed_HTML = initialize_webdriver()
    print("Extracting obituaries")
    list_of_obituaries.extend( extract_obituaries(parsed_HTML) )
    print("Moving to next page")
    page_count = load_next_page(driver, page_count)
    while(page_count < 3000):
        try:
            print("Page Count: " + str(page_count))
            print("Number of obituaries:" + str(len(list_of_obituaries)))
            print("Extracting obituaries")
            parsed_HTML = BeautifulSoup(driver.page_source, 'html.parser')
            list_of_obituaries.extend(extract_obituaries(parsed_HTML))
            print("Moving to next page")
            page_count = load_next_page(driver, page_count)
            if page_count % 10 == 0:
                print("Saving Data")
                save_data(save_file, list_of_obituaries)
        except:
            continue
    save_data(save_file, list_of_obituaries)


def initialize_webdriver():
    driver = webdriver.Firefox()
    driver.implicitly_wait(0.5)
    driver.get("https://obitmichigan.com/Results")
    page_source = driver.page_source
    parsed_HTML = BeautifulSoup(page_source, 'html.parser')
    sleep(60)
    return driver, parsed_HTML

def extract_obituaries(parsed_HTML):
    new_obituaries = []
    obituaries = parsed_HTML.find_all(class_="row mb-2 d-lg-none")
    for obituary in obituaries:
        try:
            new_obituaries.append( extract_obituary_attributes(obituary) )
        except:
            continue
    return new_obituaries


def extract_obituary_attributes(obituary):
    obituary_info = {}
    obituary_info['name'] = obituary.find("h2").text
    obituary_info['link'] = "https://obitmichigan.com" + obituary.find("a").attrs['href']
    w = obituary.find_all("strong")
    for i in w:
        attribute_name = i.text.replace(" ", '')[0:-1].lower()
        attribute_value = i.next_sibling.replace(" ", "").lower()
        obituary_info[attribute_name] = attribute_value
        if attribute_name == "birth":
            obituary_info["birthyear"] = attribute_value[-4:]
    print(obituary_info)
    return obituary_info


def load_next_page(driver, page_count):
    if page_count == 1:
        first_NEXT_button = driver.find_element_by_class_name("btn_theme_primary_blue")
        driver.execute_script("arguments[0].click()", first_NEXT_button)
    else:
        next_button = driver.find_element_by_css_selector("a[aria-label='Next']")
        driver.execute_script("arguments[0].click()", next_button)
    sleep(2)
    return page_count + 1


def save_data(filepath, list_of_obituaries):
    saved_data = open(filepath, 'w')
    saved_data.write(json.dumps(list_of_obituaries))
    saved_data.close()


if __name__ == '__main__':
    main()