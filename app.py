
#site is https://3.19.6.103/

#After every save run $ sudo systemctl restart scrapes_flask.service

## DICTIONARY ASSIGNMENTS scrape_dict(scrape dict variable = variable in code above)(scrape_num=marky_mark)

# from flask import Flask

# app = Flask(__name__)

# @app.route('/')
# def hello_world():
#     return 'Hello, World!'

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, send_file, jsonify, request, render_template, redirect, url_for
from markupsafe import escape
import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
import json
import logging
from urllib.parse import quote_plus, quote
from urllib import parse
from flask_functions import scrape_dict, esearch_texas_flask, tyler_scrape_flask, safe_jsonify
import time
import requests
import pymysql
import re
import urllib.parse
import argparse


app = Flask(__name__)

#### Trying new header starter code ######

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'DNT': '1',  # Do Not Track request header
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Referer': 'https://www.google.com/',  # Optional, but sometimes useful
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1'
}

@app.route('/')
def hello_world():
    return 'Hello, Marky!'

# @app.route('/txharrjuris/<parcel>')
# def txharrjuris(parcel):
#     from flask_functions import get_table_html, find_not_certified, extract_data_from_table,juris_dict, reassign_keys, find_not_certified_with_retries
#     from flask import Flask, jsonify
#     from selenium import webdriver
#     from selenium.webdriver.support.ui import Select
#     from selenium.webdriver.firefox.options import Options
#     from selenium.webdriver.firefox.service import Service
#     from selenium.common.exceptions import TimeoutException
#     from selenium.webdriver.common.by import By
#     from selenium.webdriver.support.ui import WebDriverWait
#     from selenium.webdriver.support import expected_conditions as EC
#     from bs4 import BeautifulSoup
#     #TXHarr Jurisdiction Mappings
#     key_mapping = {
#         'Districts': 'distcode',
#         'Jurisdictions': 'jurisName',
#         'Exemption Value': 'exemptionValue',
#         'ARB Status': 'status',
#         '2023 Rate': 'taxRate',
#     }

#     url = 'https://hcad.org/quick-search/'
#     options = Options()
#     options.add_argument('-headless')
#     options.binary_location = '/usr/bin/firefox'
#     service = Service(executable_path='/usr/local/bin/geckodriver', log_path='/dev/null')
#     driver = webdriver.Firefox(service=service, options=options)
#     driver.get(url)

#     wait = WebDriverWait(driver, 10)
#     iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'iframe')))
#     driver.switch_to.frame(iframe)

#     input_field = driver.find_element(By.ID, 'acct')
#     input_field.send_keys(parcel)


#     button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/table/tbody/tr[2]/td[3]/form/table/tbody/tr[3]/td[3]/nobr/input')))
#     button.click()
#     # Attempt to switch to the quickframe with repeated checks
#     success = False
#     for _ in range(5):  # Try up to 5 times
#         try:
#             WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "quickframe")))
#             # After switching, wait for the specific element
#             if WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "th.sub_header[colspan='7']"))):
#                 success = True
#                 break
#         except TimeoutException:
#             print("Waiting for quickframe to load, retrying...")
#             driver.switch_to.default_content()  # Go back to the main content and retry
#             WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'iframe')))
#             driver.switch_to.frame(iframe)  # Reswitch to iframe before button click frame

#     if not success:
#         raise Exception("Failed to load quickframe and its contents properly.")

#     # Find the jurisdiction table 
#     table = get_table_html(driver)

#     if find_not_certified_with_retries(table):   
#     #if find_not_certified(table):
#         # Select the Previous Year in the top left drop down
#         dropdown = Select(driver.find_element(By.NAME, 'cboTaxYear'))
#         dropdown.select_by_index(1)
#         table = get_table_html(driver)
            
#     # Data Extraction 
#     data = extract_data_from_table(table)
#     # Change the headings and flip to JSON
#     reassigned_data = reassign_keys(data, key_mapping, juris_dict)
#     #json.dumps(reassigned_data, indent=4)
#     return jsonify(reassigned_data)


@app.route('/txbonds/<path:url_string>')# Using 'path' to include slashes and other special characters
def txbondsjson(url_string):
    try:
        # Base URL
        encoded_url_string = quote(url_string, safe='+')
        url = f'https://www.har.com/texasrealestate/waterdistricts?district_search={encoded_url_string}'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises HTTPError for bad responses

        # Parse the content if the request was successful
        soup = BeautifulSoup(response.content, "html.parser")
        innertable = soup.find("div", class_="table_wrapper__inner")
        table = innertable.find("table", class_="table table--medium") if innertable else None

        # Check if table is found
        if not table:
            return jsonify({"error": "No table found on the page"}), 404

        # Extract rows
        rows = table.find("tbody").find_all("tr") if table else []

        # Check if the table is empty
        if not rows:
            return jsonify({"message": "Table is present but contains no data"}), 200

        # Extract headers dynamically
        header_elements = table.find("thead").find("tr").find_all("th")
        headers = [header.text.strip() for header in header_elements]

        # List to hold all data
        all_data = []

        # Iterate over each row to extract the required information
        for row in rows:
            columns = row.find_all("td")
            row_data = {}
            for header, column in zip(headers, columns):
                row_data[header] = column.text.strip()

            # Check and update the "Tax Year"
            year = row_data.get("Tax Year", "").strip()
            if not year:
                year = "-1"  # Use "-1" for missing years
            row_data["Tax Year"] = year

            all_data.append(row_data)

        # Find the most recent year, considering all rows except those with "-1"
        max_year = max(int(item["Tax Year"]) for item in all_data if item["Tax Year"] != "-1")

        # Filter data for the most recent year, include all with year "-1" for completeness
        recent_data = [item for item in all_data if item["Tax Year"] == str(max_year) or item["Tax Year"] == "-1"]

        return jsonify(recent_data)
    except requests.HTTPError as e:
        return jsonify({"HTTP Error": str(e)}), e.response.status_code
    except Exception as e:
        return jsonify({"Error": str(e)}), 400  # Changed from 500 to 400 for general errors

# def txbondsjson(url_string):
#     try:
#         # Base URL
#         encoded_url_string = quote(url_string, safe='+')
#         url = f'https://www.har.com/texasrealestate/waterdistricts?district_search={encoded_url_string}'

#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
#         }
#         response = requests.get(url, headers=headers)
#         response.raise_for_status()  # Raises HTTPError for bad responses

#         # Parse the content if the request was successful
#         soup = BeautifulSoup(response.content, "html.parser")
#         innertable = soup.find("div", class_="table_wrapper__inner")  # Adjust if there are multiple tables or specific identifiers
#         table = innertable.find("table", class_="table table--medium")  # Adjust if there are multiple tables or specific identifiers

#         # Check if table is found
#         if not table:
#             return jsonify({"error": "No table found on the page"}), 404

#         # Extract headers dynamically
#         header_elements = table.find("thead").find("tr").find_all("th")
#         headers = [header.text.strip() for header in header_elements]

#         # Extract all rows from the table
#         rows = table.find("tbody").find_all("tr")

#         # List to hold all data
#         all_data = []

#         # Iterate over each row to extract the required information
#         for row in rows:
#             columns = row.find_all("td")
#             row_data = {}
#             for header, column in zip(headers, columns):
#                 row_data[header] = column.text.strip()

#             # Check and update the "Tax Year"
#             year = row_data.get("Tax Year", "").strip()
#             if not year:
#                 year = "-1"  # Use "-1" for missing years
#             row_data["Tax Year"] = year

#             all_data.append(row_data)

#         # Find the most recent year, considering all rows except those with "-1"
#         max_year = max(int(item["Tax Year"]) for item in all_data if item["Tax Year"] != "-1")

#         # Filter data for the most recent year, include all with year "-1" for completeness
#         recent_data = [item for item in all_data if item["Tax Year"] == str(max_year) or item["Tax Year"] == "-1"]

#         return jsonify(recent_data)
#     except requests.HTTPError as e:
#         return jsonify({"HTTP Error": str(e)}), e.response.status_code
#     except Exception as e:
#         return jsonify({"Error": str(e)}), 500


@app.route('/fetch-page')

def fetch_page():
    
    #url = 'https://travis.prodigycad.com/property-detail/127801'
    #url = 'https://search.wcad.org/Property-Detail/PropertyQuickRefID/R314258'
    url = 'https://www.larimer.gov/assessor/search#/detail/R1613852/general'

    options = Options()
    options.headless = True
    options.binary_location = '/usr/bin/firefox'  # Update this path

    # Set the path to the geckodriver executable
    geckodriver_path = '/usr/local/bin/geckodriver'  # Update this path

    service = Service(executable_path=geckodriver_path)
    driver = webdriver.Firefox(service=service, options=options)
    driver.get(url)
    # Wait for the element to be present on the page
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "col-sm-9"))
    )

    # Scroll down one page length
    driver.execute_script("window.scrollBy(0, window.innerHeight);")

    # Optional: Add a small delay to ensure the scroll is complete
    import time
    time.sleep(2)

    # Take a screenshot
# Wait until the header element with the specified class names is present on the page
    # element = wait.until(
    #     EC.presence_of_element_located((By.CSS_SELECTOR, "header.sc-eKZiaR.iapWze > h4.sc-fgfRvd.fVVcSZ"))
    # )

    screenshot_path = '/home/ec2-user/scrapes_flask/screenshot.png'  
    driver.save_screenshot(screenshot_path)

# Print the current URL after loading the page
    # current_url = driver.current_url
    # print(f"Current URL after loading: {current_url}")
    html = driver.page_source
    driver.quit()

    # Optionally, parse the HTML with BeautifulSoup if needed
    soup = BeautifulSoup(html, 'html.parser')
    
    return send_file(screenshot_path, mimetype='image/png')

@app.route('/txmontjuris/<parcel>')
def txjuris(parcel):
    try:
        #url = 'https://mcad-tx.org/property-detail/460712/2023'
        url = f'https://mcad-tx.org/property-detail/{parcel}/2023'
        options = Options()
        options.headless = True
        options.binary_location = '/usr/bin/firefox'
        service = Service(executable_path='/usr/local/bin/geckodriver')
        driver = webdriver.Firefox(service=service, options=options)
        driver.get(url)

        # Wait for the specific element to be visible
        wait = WebDriverWait(driver, 90)
        css_selector = 'p.sc-bGbJRg.hGNnst'
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))

        # Fetch HTML and parse it
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Example of using a specific class to find data
        juris = soup.find_all('div', {'class': 'sc-hUMlYv ouuwg'})
        if not juris:
            app.logger.info("No div with the specified class found.")
            return jsonify({"error": "Data not found"}), 404

        # Process found data
        data = []
        # Assuming you expect exactly one such div and it contains a table
        table = juris[0].find('table', class_='MuiTable-root')
        if table:
            headers = [th.get_text(strip=True) for th in table.find('thead').find_all('th')]
            for row in table.find('tbody').find_all('tr'):
                cells = row.find_all('td')
                row_data = {headers[i]: cells[i].get_text(strip=True) for i in range(len(cells))}
                data.append(row_data)
            return jsonify(data)
        else:
            app.logger.info("No table found within the specified div.")
            return jsonify({"error": "Table not found"}), 404

    except Exception as e:
        app.logger.error(f"Exception occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        driver.quit()



######### COLORADO FLASKS ##############

#####################################################
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#                   COLORADO                        #
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#####################################################


@app.route('/colari/<parcel>')

def colari(parcel):

    try:
    
        url = 'https://www.larimer.gov/assessor/search#/detail/{}/general'.format(parcel)

        options = Options()
        options.headless = True
        options.binary_location = '/usr/bin/firefox'  # Update this path

        # Set the path to the geckodriver executable
        geckodriver_path = '/usr/local/bin/geckodriver'  # Update this path

        service = Service(executable_path=geckodriver_path)
        driver = webdriver.Firefox(service=service, options=options)
        driver.get(url)

        wait = WebDriverWait(driver, 8)
        html = driver.page_source
        driver.quit()

        # Optionally, parse the HTML with BeautifulSoup if needed
        soup = BeautifulSoup(html, 'html.parser')
        # Find the element containing the string 'Parcel Number:'
        treasacct = soup.find(string='Parcel Number:').find_next('strong').get_text() 
        schedule = soup.find(string='Schedule Number:').find_next('strong').get_text() 
        scrape_num = soup.find(string='Account Number:').find_next('strong').get_text() 
        situsstreet = ' '.join([sibling.strip() for sibling in soup.find(string='Property Address:').find_next('br').find_all_next(string=True, limit=2) if isinstance(sibling, str)])
        owner = soup.find('span',{'ng-show':'vm.dtl.ownername1.length>0'}).get_text()
        mailstreet = soup.find('span',{'ng-show':'vm.dtl.mailaddress2.length>0'}).get_text()
        legal = soup.find(string='Legal Description:').parent.find_next_sibling(string=True).strip()
        return jsonify(scrape_dict(assrparcel=parcel,scrape_num=scrape_num,owner=owner, situsstreet=situsstreet, legal=legal, schedule=schedule, treasacct=treasacct, mailstreet=mailstreet))
    
    except Exception as e:
    # If any exception occurs, fall back to an empty scrape_dict
        return safe_jsonify(scrape_dict)


@app.route('/coarap/<parcel>')
def coarap(parcel):
    try:
        url = 'https://taxsearch.arapahoegov.com/ReReport.aspx?PIN={}'.format(parcel)
        res = requests.get(url)
        soup = BeautifulSoup(res.content, "html.parser")
        owner = (td.find_next_sibling('td').get_text(strip=True) for td in soup.find_all('td', text='Owner:')).__next__()
        situsstreet = (td.find_next_sibling('td').get_text(strip=True) for td in soup.find_all('td', text='Situs Address:')).__next__()
        situscity = (td.find_next_sibling('td').get_text(strip=True) for td in soup.find_all('td', text='Situs City:')).__next__()
        assrparcel = (td.find_next_sibling('td').get_text(strip=True) for td in soup.find_all('td', text='AIN:')).__next__()
        treasacct = (td.find_next_sibling('td').get_text(strip=True) for td in soup.find_all('td', text='PIN:')).__next__()
        return jsonify(scrape_dict(scrape_num=parcel,owner=owner, situsstreet=situsstreet,situscity=situscity,assrparcel=assrparcel,treasacct=treasacct))
    except Exception as e:
        # If any exception occurs, fall back to an empty scrape_dict
        return safe_jsonify(scrape_dict)

###### END OF NEW JSONIFY EMPTY FUNCTION ###### 
@app.route('/codenv/<parcel>')
def DenverSearch(parcel):

    try:
    
        if len(parcel) <= 9:
            parcel = (parcel.zfill(9))
        else:
            parcel = (parcel.zfill(13))

        # len testing above
        search_url = 'https://denvergov.org/property/realproperty/search/search/0/?searchText={}'.format(parcel)
        search_res = requests.get(search_url)
        search_soup = BeautifulSoup(search_res.content, "html.parser")
        search_json = requests.get(search_url).json()
        
        parcel_num = search_json['Properties'][0]['ParcelID']
        url = 'https://denvergov.org/property/realproperty/taxes/{}'.format(parcel_num)
        res = requests.get(url)
        soup = BeautifulSoup(res.content, "html.parser")

        owner = soup.find_all('td')[0].get_text().replace('\r', '').replace('\n\n', '\n').strip().split('\n')[0].strip()
        mailstreet = soup.find('td',{'style':'padding-left:2em;'}).get_text().split('\n')[3].strip()
        mailcity = soup.find('td',{'style':'padding-left:2em;'}).get_text().split('\n')[5].strip()
        schedule_nbr = soup.find_all('td')[2].get_text().replace('\n', ' ').replace('\r', ' ').strip()
        legal_desc = soup.find_all('td')[3].get_text().replace('\n', ' ').replace('\r', ' ').strip()
        address = soup.find("h1").get_text().strip()
        try:
            taxes = soup.find_all('td')[13].get_text().replace('\n', ' ').replace('\r', ' ').strip()
        except:
            taxes = 'Real Property Tax is Unavailable'
            
        return jsonify(scrape_dict(scrape_num=parcel,parcel=schedule_nbr, owner=owner, situsstreet=address, legal=legal_desc, taxes=taxes, treasacct=parcel_num, schedule=schedule_nbr, assrparcel=schedule_nbr, mailstreet=mailstreet, mailcity=mailcity))

    except Exception as e:
    # If any exception occurs, fall back to an empty scrape_dict
        return safe_jsonify(scrape_dict)

@app.route('/coeagl/<parcel>')
def EagleSearch(parcel):

    try:
    
    
        url = 'https://propertytax.eaglecounty.us/PropertyTaxSearch/TaxAccount/BillHistory/{}'.format(parcel)
        res = requests.get(url)
        soup = BeautifulSoup(res.content, "html.parser")

        owner_mailing = soup.find_all('td')[2].get_text().replace('\r', '').replace('\n\n', '\n').strip().split('\n')
        legal = soup.find_all('td')[1].get_text().replace('\r', '').replace('\n\n', '\n').strip().split('\n')
        eagle_owner = owner_mailing[1]
        eagle_mailing_street = owner_mailing[-2]
        eagle_mailing_city_state = owner_mailing[-1]
        eagle_parcel = legal[-1].split('Parcel:')[1].strip()
        eagle_legal = legal[-2].strip()
        eagle_situs_st = legal[1].strip()
        eagle_situs_city = legal[2].strip()

        return jsonify(scrape_dict(scrape_num=parcel,parcel=parcel, owner=eagle_owner, schedule=eagle_parcel,situsstreet=eagle_situs_st, situscity=eagle_situs_city, legal=eagle_legal, assrparcel = parcel))

    except Exception as e:
        # If any exception occurs, fall back to an empty scrape_dict
            return safe_jsonify(scrape_dict)

@app.route('/coelpa/<parcel>')
def ElPasoSearch(parcel):
    try:
   
        url = 'http://epmt.trs.elpasoco.com/epui/PropertyTaxDetails.aspx?schd={}'.format(parcel)
        res = requests.get(url)
        soup = BeautifulSoup(res.content, "html.parser")

        owner = soup.find('textarea', {'id':"ContentPlaceHolder1_txtName"}).get_text().replace('\r\n', ' ').strip()
        mailstreet = soup.find('textarea', {'id':"ContentPlaceHolder1_txtMailingAddress"}).get_text().replace('\r\n', ' ').strip()
        legal = soup.find('span', {'id':'ContentPlaceHolder1_lblLegalDescription'}).get_text()
        taxes = soup.find('span', {'id': 'ContentPlaceHolder1_lblTotalAmount'}).get_text()
        situsstreet = soup.find('textarea', {'id':'ContentPlaceHolder1_txtPropertyAddress'}).get_text().replace('\r\n', ' ').strip()
        parcel = soup.find('span', {'id':'ContentPlaceHolder1_lblPropertyAccountNumber'}).get_text()

        return jsonify(scrape_dict(scrape_num=parcel, parcel=parcel, owner=owner, mailstreet=mailstreet, situsstreet=situsstreet, legal=legal, assrparcel = parcel, treasacct=parcel, totaltax=taxes))
    except Exception as e:
        # If any exception occurs, fall back to an empty scrape_dict
            return safe_jsonify(scrape_dict)

@app.route('/cosmmt/<parcel>')
def COSmmt(parcel):
    try:


        response = requests.get('http://gis.summitcountyco.gov/Map/DetailData.aspx?Schno={}'.format(parcel))
        soup = BeautifulSoup(response.content, "html.parser")
        assrparcel = soup.find(string='PPI:').find_next('td').get_text()
        legal = soup.find(string='Property Desc:').find_next('td').get_text()
        owner = soup.find(string='Primary:').find_next('td').get_text()
        mailstreet = soup.find(string='Addr:').find_next('td').get_text()
        situsstreet = soup.find(string='Phys. Address:').find_next('td').get_text()
        mailcity = soup.find(string='CSZ').find_next('td').get_text()
        return jsonify(scrape_dict(scrape_num=parcel, schedule=parcel, mailcity=mailcity,mailstreet=mailstreet,assrparcel=assrparcel, owner=owner, situsstreet=situsstreet, legal=legal))

    except Exception as e:
        # If any exception occurs, fall back to an empty scrape_dict
            return safe_jsonify(scrape_dict)


@app.route('/copueb/<parcel>')
def PuebloSearch_debug(parcel):

    try:
    
        url = 'http://www.co.pueblo.co.us/cgi-bin/webatrallbroker.wsc/propertyinfo.p?par={}'.format(parcel)

        res = requests.get(url)
        soup = BeautifulSoup(res.content, "html.parser")

        try:
            parcel = soup.find('dt', text='Schedule: ').findNext('dd').string
        except:
            parcel = 'No Parcel'
        try:
            owner_tag = soup.find('dt', text='Name(s): ').findNext('dd')
            owner = soup.find('dt', text='Name(s): ').findNext('dd').string
            if not owner:
                owner_tag_2 = owner_tag.findNext('dd')
                owner= owner_tag.findNext('dd').string
                if not owner:
                    owner= owner_tag_2.findNext('dd').string
        except:
            owner = 'No Owner'
        try:
            mailstreet = soup.find('dt', text='Mailing Address: ').findNext('dd').string
        except:
            mailstreet = 'No Mailing Address'
    #       
        try:
            situsstreet = soup.find('dt', text='Location Address: ').findNext('dd').string
            
            if situsstreet == '0   00000-':
                situsstreet = 'VACANT LAND'
            
        except:
            situsstreet = 'VACANT LAND'
        try:
            legal = str(''.join(x.get_text() for x in soup.find('dt', text='Legal Description: ').find_next_siblings('dd')))
            
        except:
            legal = 'No legal'
        try:
            taxes = soup.find_all('table', {'class':'propertySearchTable'})[1].get_text().split('\n')[-2]
            if taxes[0].isdigit():
                taxes = float(taxes)
            else:
                taxes = '0'
        except:
            taxes = '0'
        
        return jsonify(scrape_dict(parcel=parcel, owner=owner, situsstreet=situsstreet, legal=legal, totaltax=taxes, mailstreet=mailstreet, treasacct=parcel, assrparcel=parcel,scrape_num=parcel))

    except Exception as e:
        # If any exception occurs, fall back to an empty scrape_dict
            return safe_jsonify(scrape_dict)

### COGrnd Put on CAPTCHA so Flasking ARCGIS  

@app.route('/cogrnd/<parcel>')
def cogrand(parcel):

    try:
        import urllib.parse

        base_url = 'https://gis.co.grand.co.us:6443/arcgis/rest/services/Property/AssesssorMap/MapServer/0/query'

        params = {
            'f': 'json',
            'where': "SCHEDULE = '{}'".format(parcel),
            'returnGeometry': 'false',
            'spatialRel': 'esriSpatialRelIntersects',
            'outFields': '*',
            'outSR': '102740'
        }

        encoded_params = urllib.parse.urlencode(params)
        url = '{}?{}'.format(base_url, encoded_params)
        
        response = requests.get(url)
        
        if response.status_code == 200:
            response_json = response.json()
            if 'features' in response_json and len(response_json['features']) > 0:
                features = response_json['features'][0]
                owner = response_json['features'][0]['attributes']['OWNER']
                assrparcel = response_json['features'][0]['attributes']['SCHEDULE']
                schedule = response_json['features'][0]['attributes']['PIN']
                mailstreet = response_json['features'][0]['attributes']['MAILINGADD']
                mailcity = response_json['features'][0]['attributes']['CITY']
                situsstreet = response_json['features'][0]['attributes']['GIS_ADD']
                legal = response_json['features'][0]['attributes']['LEGAL_NC']
                return jsonify(scrape_dict(scrape_num=parcel, assrparcel=assrparcel, owner=owner, situsstreet=situsstreet,mailstreet=mailstreet, mailcity=mailcity, legal=legal, schedule=schedule))
                #return jsonify(features), 200
            else:
                return jsonify({"error": "No features found"}), 404
        else:
            return jsonify({"error": "Request failed"}), response.status_code
    except Exception as e:
        # If any exception occurs, fall back to an empty scrape_dict
            return safe_jsonify(scrape_dict)


######### COLORADO TYLER COUNTIES ######
@app.route('/coadam/<parcel>')
def coadam(parcel):
    from db_counties_web import COadam
    main, countyweb, count = COadam(1)
    json_result = tyler_scrape_flask(parcel, countyweb)
    return(json_result)

@app.route('/coarch/<parcel>')
def coarch(parcel):
    from db_counties_web import COarch
    main, countyweb, count = COarch(1)
    json_result = tyler_scrape_flask(parcel, countyweb)
    return(json_result)


@app.route('/coboul/<parcel>')
def coboul(parcel):
    from db_counties_web import COboul
    main, countyweb, count = COboul(1)
    json_result = tyler_scrape_flask(parcel, countyweb)
    return(json_result)


@app.route('/cobrmf/<parcel>')
def cobrmf(parcel):
    from db_counties_web import CObrmf
    main, countyweb, count = CObrmf(1)
    json_result = tyler_scrape_flask(parcel, countyweb)
    return(json_result)

@app.route('/coccrk/<parcel>')
def coccrk(parcel):
    from db_counties_web import COccrk
    main, countyweb, count = COccrk(1)
    json_result = tyler_scrape_flask(parcel, countyweb)
    return(json_result)

@app.route('/coconj/<parcel>')
def coconj(parcel):
    from db_counties_web import COconj
    main, countyweb, count = COconj(1)
    json_result = tyler_scrape_flask(parcel, countyweb)
    #json_result = tyler_scrape_flask_with_option(parcel,countyweb)
    return(json_result)

@app.route('/cocrow/<parcel>')
def cocrow(parcel):
    from db_counties_web import COcrow
    main, countyweb, count = COcrow(1)
    json_result = tyler_scrape_flask(parcel, countyweb)
    return(json_result)

@app.route('/codelt/<parcel>')
def codelt(parcel):
    from db_counties_web import COdelt
    main, countyweb, count = COdelt(1)
    json_result = tyler_scrape_flask(parcel, countyweb)
    return(json_result)

@app.route('/codoug/<parcel>')
def codoug(parcel):
    from db_counties_web import COdoug
    main, countyweb, count = COdoug(1)
    json_result = tyler_scrape_flask(parcel, countyweb)
    return(json_result)

@app.route('/coelbt/<parcel>')
def coelbt(parcel):
    from db_counties_web import COelbt
    main, countyweb, count = COelbt(1)
    json_result = tyler_scrape_flask(parcel, countyweb)
    return(json_result)

@app.route('/cofrmt/<parcel>')
def cofrmt(parcel):
    from db_counties_web import COfrmt
    main, countyweb, count = COfrmt(1)
    json_result = tyler_scrape_flask(parcel, countyweb)
    return(json_result)


@app.route('/cogarf/<parcel>')
def cogarf(parcel):
    from db_counties_web import COgarf
    main, countyweb, count = COgarf(1)
    json_result = tyler_scrape_flask(parcel, countyweb)
    return(json_result)


@app.route('/cogilp/<parcel>')
def cogilp(parcel):
    from db_counties_web import COgilp
    main, countyweb, count = COgilp(1)
    json_result = tyler_scrape_flask(parcel, countyweb)
    return(json_result)

# COGrnd has CAPTCHA so moving to ARGGIS 7-15-25
# @app.route('/cogrnd/<parcel>')
# def cogrnd(parcel):
#     from db_counties_web import COgrnd
#     main, countyweb, count = COgrnd(1)
#     json_result = tyler_scrape_flask(parcel, countyweb)
#     return(json_result)

@app.route('/colake/<parcel>')
def colake(parcel):
    from db_counties_web import COlake
    main, countyweb, count = COlake(1)
    json_result = tyler_scrape_flask(parcel, countyweb)
    return(json_result)

@app.route('/colplt/<parcel>')
def colplt(parcel):
    from db_counties_web import COlplt
    main, countyweb, count = COlplt(1)
    json_result = tyler_scrape_flask(parcel, countyweb)
    return(json_result)

@app.route('/colcln/<parcel>')
def colcln(parcel):
    from db_counties_web import COlcln
    main, countyweb, count = COlcln(1)
    json_result = tyler_scrape_flask(parcel, countyweb)
    return(json_result)

@app.route('/comesa/<parcel>')
def comesa(parcel):
    from db_counties_web import COmesa
    main, countyweb, count = COmesa(1)
    json_result = tyler_scrape_flask(parcel, countyweb)
    return(json_result)

@app.route('/comtrs/<parcel>')
def comtrs(parcel):
    from db_counties_web import COmtrs
    main, countyweb, count = COmtrs(1)
    json_result = tyler_scrape_flask(parcel, countyweb)
    return(json_result)

@app.route('/comorg/<parcel>')
def comorg(parcel):
    from db_counties_web import COmorg
    main, countyweb, count = COmorg(1)
    json_result = tyler_scrape_flask(parcel, countyweb)
    return(json_result)


@app.route('/copark/<parcel>')
def copark(parcel):
    from db_counties_web import COpark
    main, countyweb, count = COpark(1)
    json_result = tyler_scrape_flask(parcel, countyweb)
    return(json_result)

@app.route('/copitk/<parcel>')
def copitk(parcel):
    from db_counties_web import COpitk
    main, countyweb, count = COpitk(1)
    json_result = tyler_scrape_flask(parcel, countyweb)
    return(json_result)

@app.route('/corout/<parcel>')
def corout(parcel):
    from db_counties_web import COrout
    main, countyweb, count = COrout(1)
    json_result = tyler_scrape_flask(parcel, countyweb)
    return(json_result)

@app.route('/cosagu/<parcel>')
def cosagu(parcel):
    from db_counties_web import COsagu
    main, countyweb, count = COsagu(1)
    json_result = tyler_scrape_flask(parcel, countyweb)
    return(json_result)

@app.route('/cotell/<parcel>')
def cotell(parcel):
    from db_counties_web import COtell
    main, countyweb, count = COtell(1)
    json_result = tyler_scrape_flask(parcel, countyweb)
    return(json_result)

@app.route('/coweld/<parcel>')
def coweld(parcel):
    from db_counties_web import COweld
    main, countyweb, count = COweld(1)
    json_result = tyler_scrape_flask(parcel, countyweb)
    return(json_result)

######### TEXAS FLASKS WITHOUT FUNCTIONS ##############

                                                            
                 #############                              
                 ##         ##                              
                 ##         ##                              
                 ##         ##                              
                 ##         ##                              
                 ##          #####                          
                 ##               ########  #  #####        
                 ##                       ## ###   #####    
                 ##                                    #    
                 ##                                    #    
                 ##                                    #    
 #######         ##                                    ##   
  ##   ############        TEXAS                         ##  
   ###                                                   ## 
     ###                                                 ## 
        ##                                              ##  
        ##                                              ##  
         ##      #########                           #####  
           ### ###      ###                         ##      
              ##          ###                    ####       
                            ##               #####          
                             ##           ####              
                              ##         ###                
                               ###       ##                 
                                ##      ###                 
                                 ##     ##                  
                                  ##     ##                 
                                    ########                
                                                            



@app.route('/txbexa/<parcel>')
def txbexa(parcel):
    try:
        url = 'https://bexar.trueautomation.com/clientdb/Property.aspx?cid=110&prop_id={}'.format(parcel)
        response = requests.get(url,headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        assrparcel = soup.find(text='Property ID:').findNext('td').contents[0]
        treasacct = soup.find(text='Geographic ID:').findNext('td').contents[0]
        legal = soup.find(text='Legal Description:').findNext('td').contents[0].strip()
        situsstreet = soup.find(text='Address:').findNext('td').contents[0]
        situscity = situsstreet.next_sibling.next_sibling
        owner = soup.find(text='Name:').findNext('td').contents[0]
        mailstreet = soup.find(text='Mailing Address:').findNext('td').contents[0]
        mailcity = mailstreet.next_sibling.next_sibling
        return jsonify(scrape_dict(scrape_num=parcel, situscity=situscity, mailcity=mailcity,assrparcel=assrparcel, owner=owner, situsstreet=situsstreet, treasacct=treasacct,legal=legal, mailstreet=mailstreet))
    except Exception as e:
    # If any exception occurs, fall back to an empty scrape_dict
        return safe_jsonify(scrape_dict)


### TXHarris  for legal, have it pull from cPanel and insert.  
@app.route('/txharr/<parcel>')
def txharr(parcel):
    try:    
        cpanel_parcel = parcel
        url = 'https://arcweb.hcad.org/server/rest/services/public/public_query/MapServer/0/query?f=json&where=HCAD_NUM%20=%20%27{}%27&returnGeometry=true&spatialRel=esriSpatialRelIntersects&outFields=*&outSR=102740'.format(parcel)
        response = requests.get(url).json()
        assrparcel = response['features'][0]['attributes']['HCAD_NUM']
        scrape_num = response['features'][0]['attributes']['HCAD_NUM']
        #parcel = response['features'][0]['attributes']['LOWPARCELID']
        situsstreet = response['features'][0]['attributes']['address']
        situscity = response['features'][0]['attributes']['city']
        owner = response['features'][0]['attributes']['owner']
        totalassessedvalue = response['features'][0]['attributes']['appr_val']
        
        try:
            connection = pymysql.connect(db='cocrscom_cocrs', user='cocrscom', passwd='bA3sbSHIc3', host='qsoftserver1.qsoftdesigns.com', port=3306)
            cursor = connection.cursor()
            query = "SELECT legal FROM `TXHarr` WHERE assrparcel = {} LIMIT 1".format(cpanel_parcel)
            cursor.execute(query)
            result = cursor.fetchone()
            legal = result[0] if result else "No legal found for the given parcel."
        except Exception as e:
            legal = f"Database error: {e}"
        finally:
            cursor.close()
            connection.close()
        ##### End of Modified Code ####

        return jsonify(scrape_dict(assrparcel=assrparcel, owner=owner, situsstreet=situsstreet, situscity=situscity, totalassessedvalue=totalassessedvalue, legal=legal, scrape_num=parcel))
    
    except Exception as e:
    # If any exception occurs, fall back to an empty scrape_dict
        return safe_jsonify(scrape_dict)
    
@app.route('/txmont/<parcel>')

def txmont(parcel):
    try:
        url = 'https://services1.arcgis.com/PRoAPGnMSUqvTrzq/arcgis/rest/services/Tax_Parcel_Public_View/FeatureServer/0/query?where=PIN%20=%20%27{}%27&returnGeometry=true&spatialRel=esriSpatialRelIntersects&outFields=*&outSR=102740&f=pjson'.format(parcel)
        response = requests.get(url).json()
        assrparcel = response['features'][0]['attributes']['PIN']
        treasacct = response['features'][0]['attributes']['pid']
        situsstreet = response['features'][0]['attributes']['situs']
        owner = response['features'][0]['attributes']['ownerName']
        mailstreet = response['features'][0]['attributes']['ownerAddress']
        return jsonify(scrape_dict(scrape_num=parcel,assrparcel=assrparcel, owner=owner, situsstreet=situsstreet, treasacct=treasacct, mailstreet=mailstreet))
    except Exception as e:
    # If any exception occurs, fall back to an empty scrape_dict
        return safe_jsonify(scrape_dict)

@app.route('/txtrnt/<parcel>')

def txtrnt(parcel):
    try:
        base_url = 'https://mapit.tarrantcounty.com/arcgis/rest/services/Tax/TCProperty/MapServer/0/query'
        params = {
        'f': 'json',
        'where': "ACCOUNT = '{}'".format(parcel),
        'returnGeometry': 'false',
        'spatialRel': 'esriSpatialRelIntersects',
        'outFields': '*',
        'outSR': '102740'
        }
        encoded_params = urllib.parse.urlencode(params)
        url = '{}?{}'.format(base_url, encoded_params)
        response = requests.get(url).json()

        assrparcel = response['features'][0]['attributes']['ACCOUNT']
        treasacct = response['features'][0]['attributes']['TAXPIN']
        situsstreet = response['features'][0]['attributes']['SITUS_ADDR']
        situscity = response['features'][0]['attributes']['CITY']
        owner = response['features'][0]['attributes']['OWNER_NAME']
        mailstreet = response['features'][0]['attributes']['OWNER_ADDR']
        mailcity = response['features'][0]['attributes']['OWNER_CITY']
        legal = response['features'][0]['attributes']['LEGAL_1']
        return jsonify(scrape_dict(scrape_num=parcel,mailcity=mailcity,situscity=situscity,legal=legal,assrparcel=assrparcel, owner=owner, situsstreet=situsstreet, treasacct=treasacct, mailstreet=mailstreet))
    except Exception as e:
    # If any exception occurs, fall back to an empty scrape_dict
        return safe_jsonify(scrape_dict)


# @app.route('/txtrvs/<parcel>')
# def txtrvs(parcel):
     
#     url = 'https://travis.prodigycad.com/property-detail/{}'.format(parcel)

#     options = Options()
#     options.headless = True
#     options.binary_location = '/usr/bin/firefox'  # Update this path

#     # Set the path to the geckodriver executable
#     geckodriver_path = '/usr/local/bin/geckodriver'  # Update this path

#     service = Service(executable_path=geckodriver_path)
#     driver = webdriver.Firefox(service=service, options=options)
#     driver.get(url)

#     wait = WebDriverWait(driver, 90)
#     # Wait until the header element with the specified class names is present on the page
#     element = wait.until(
#         EC.presence_of_element_located((By.CSS_SELECTOR, "header.sc-eKZiaR.iapWze > h4.sc-fgfRvd.fVVcSZ"))
#     )
#     time.sleep(1)  # Wait for an additional 5 seconds
#     html = driver.page_source
#     driver.quit()
#     # Optionally, parse the HTML with BeautifulSoup if needed
#     soup = BeautifulSoup(html, 'html.parser')
#     scrape_num = soup.find(string='Property ID:').find_next('p').get_text()
#     treasacct = soup.find(string='Geographic ID:').find_next('p').get_text()    
#     legal = soup.find(string='Legal Description:').find_next('p').get_text()    
#     owner = soup.find(string='Name:').find_next('p').get_text()
#     mailstreet = soup.find(string='Mailing Address:').find_next('p').get_text()
#     situsstreet = soup.find(string='Address:').find_next('p').get_text()
#     return jsonify(scrape_dict(assrparcel=parcel,scrape_num=scrape_num, owner=owner, situsstreet=situsstreet, treasacct=treasacct,legal=legal, mailstreet=mailstreet))


# @app.route('/txwill/<parcel>')
# def txwill(parcel):
     
#     url = 'https://search.wcad.org/Property-Detail/PropertyQuickRefID/{}'.format(parcel)

#     options = Options()
#     options.headless = True
#     options.binary_location = '/usr/bin/firefox'  # Update this path

#     # Set the path to the geckodriver executable
#     geckodriver_path = '/usr/local/bin/geckodriver'  # Update this path

#     service = Service(executable_path=geckodriver_path)
#     driver = webdriver.Firefox(service=service, options=options)
#     driver.get(url)

#     wait = WebDriverWait(driver, 90)
#     # Wait until the header element with the specified class names is present on the page

#     time.sleep(1)  # Wait for an additional 5 seconds
#     html = driver.page_source
#     driver.quit()
#     # Optionally, parse the HTML with BeautifulSoup if needed
#     soup = BeautifulSoup(html, 'html.parser')

#     owner = soup.find(text='Owner Name').find_next('td').get_text()
#     mailstreet = soup.find(text='Mailing Address').find_next('td').get_text().strip()
#     treasacct = soup.find(text='Account').find_next('td').get_text().strip()
#     legal = soup.find(text='Legal Description').find_next('td').get_text().strip()
#     situsstreet = soup.find('td',{'id':'dnn_ctr1460_View_tdPropertyAddress'}).get_text().replace('Property Address: ','')


#     return jsonify(scrape_dict(assrparcel=parcel, owner=owner, situsstreet=situsstreet, treasacct=treasacct,legal=legal, mailstreet=mailstreet))




# @app.route('/txgrim/<parcel>')
# def txgrim(parcel):
     
#     url = 'https://grimescad.org/Property-Detail/PropertyQuickRefID/{}'.format(parcel)

#     options = Options()
#     options.headless = True
#     options.binary_location = '/usr/bin/firefox'  # Update this path

#     # Set the path to the geckodriver executable
#     geckodriver_path = '/usr/local/bin/geckodriver'  # Update this path

#     service = Service(executable_path=geckodriver_path)
#     driver = webdriver.Firefox(service=service, options=options)
#     driver.get(url)

#     wait = WebDriverWait(driver, 90)
#     # Wait until the header element with the specified class names is present on the page

#     time.sleep(1)  # Wait for an additional 5 seconds
#     html = driver.page_source
#     driver.quit()
#     # Optionally, parse the HTML with BeautifulSoup if needed
#     soup = BeautifulSoup(html, 'html.parser')

#     owner = soup.find(text='Owner Name').find_next('td').get_text()
#     mailstreet = soup.find(text='Mailing Address').find_next('td').get_text().strip()
#     treasacct = soup.find(text='Account').find_next('td').get_text().strip()
#     legal = soup.find(text='Legal Description').find_next('td').get_text().strip()
#     situsstreet = soup.find('td',{'id':'dnn_ctr477_View_tdPropertyAddress'}).get_text().replace('Property Address: ','')


#     return jsonify(scrape_dict(assrparcel=parcel, owner=owner, situsstreet=situsstreet, treasacct=treasacct,legal=legal, mailstreet=mailstreet))


######### TEXAS ESearch COUNTIES #########

@app.route('/txaran/<parcel>')
def txaran(parcel):
    url = 'https://esearch.aransascad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txatas/<parcel>')
def txatas(parcel):
    url = 'https://esearch.atascoscad.com/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result


@app.route('/txaust/<parcel>')
def txaust(parcel):
    url = 'https://esearch.austincad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txband/<parcel>')
def txband(parcel):
    url = 'https://esearch.bancad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txbast/<parcel>')
def txbast(parcel):
    url = 'https://esearch.bastropcad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txbell/<parcel>')
def txbell(parcel):
    url = 'https://esearch.bellcad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txblan/<parcel>')
def txblan(parcel):
    url = 'https://esearch.blancocad.com/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txbraz/<parcel>')
def txbraz(parcel):
    url = 'https://esearch.brazoscad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txbrza/<parcel>')
def txbrza(parcel):
    url = 'https://esearch.brazoriacad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result


@app.route('/txbrew/<parcel>')
def txbrew(parcel):
    url = 'https://esearch.brewstercotad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txbrow/<parcel>')
def txbrow(parcel):
    url = 'https://esearch.brown-cad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txburl/<parcel>')
def txburl(parcel):
    url = 'https://esearch.burlesonappraisal.com/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txburn/<parcel>')
def txburn(parcel):
    url = 'https://esearch.burnet-cad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txcald/<parcel>')
def txcald(parcel):
    url = 'https://esearch.caldwellcad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txcamp/<parcel>')
def txcamp(parcel):
    url = 'https://esearch.campcad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txcoll/<parcel>')
def txcoll(parcel):
    url = 'https://esearch.collincad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txcolo/<parcel>')
def txcolo(parcel):
    url = 'https://esearch.coloradocad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txcoma/<parcel>')
def txcoma(parcel):
    url = 'https://esearch.comalad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txcory/<parcel>')
def txcory(parcel):
    url = 'https://esearch.coryellcad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txdent/<parcel>')
def txdent(parcel):
    url = 'https://esearch.dentoncad.com/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txduva/<parcel>')
def txduva(parcel):
    url = 'https://esearch.duvalcad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txerat/<parcel>')
def txerat(parcel):
    url = 'https://esearch.erath-cad.com/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txfall/<parcel>')
def txfall(parcel):
    url = 'https://esearch.fallscad.net/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txfaye/<parcel>')
def txfaye(parcel):
    url = 'https://esearch.fayettecad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txfort/<parcel>')
def txfort(parcel):
    url = 'https://esearch.fbcad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txgalv/<parcel>')
def txgalv(parcel):
    url = 'https://esearch.galvestoncad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txguad/<parcel>')
def txguad(parcel):
    url = 'https://esearch.guadalupead.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txhale/<parcel>')
def txhale(parcel):
    url = 'https://esearch.halecad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txhard/<parcel>')
def txhard(parcel):
    url = 'https://esearch.hardin-cad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txhays/<parcel>')
def txhays(parcel):
    url = 'https://esearch.hayscad.com/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result


@app.route('/txhill/<parcel>')
def txhill(parcel):
    url = 'https://esearch.hillcad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txjeff/<parcel>')
def txjeff(parcel):
    url = 'https://esearch.jcad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txjohn/<parcel>')
def txjohn(parcel):
    url = 'https://esearch.johnsoncad.com/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txkend/<parcel>')
def txkend(parcel):
    url = 'https://esearch.kendallad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txlamp/<parcel>')
def txlamp(parcel):
    url = 'https://esearch.lampasascad.com/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txlee/<parcel>')
def txlee(parcel):
    url = 'https://esearch.lee-cad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txlibe/<parcel>')
def txlibe(parcel):
    url = 'https://esearch.libertycad.com/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txllan/<parcel>')
def txllan(parcel):
    url = 'https://esearch.llanocad.net/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txmcle/<parcel>')
def txmcle(parcel):
    url = 'https://esearch.mclennancad.com/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txmata/<parcel>')
def txmata(parcel):
    url = 'https://esearch.matagorda-cad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txmilm/<parcel>')
def txmilm(parcel):
    url = 'https://esearch.milamad.com/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txmedi/<parcel>')
def txmedi(parcel):
    url = 'https://esearch.medinacad.com/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txnava/<parcel>')
def txnava(parcel):
    url = 'https://esearch.navarrocad.com/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txnuec/<parcel>')
def txnuec(parcel):
    url = 'https://esearch.nuecescad.net/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txoran/<parcel>')
def txoran(parcel):
    url = 'https://esearch.orangecad.net/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txpolk/<parcel>')
def txpolk(parcel):
    url = 'https://esearch.polkcad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txreal/<parcel>')
def txreal(parcel):
    url = 'https://esearch.realcad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txsjac/<parcel>')
def txsjac(parcel):
    url = 'https://esearch.sjcad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txtrin/<parcel>')
def txtrin(parcel):
    url = 'https://esearch.trinitycad.net/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txwall/<parcel>')
def txwall(parcel):
    url = 'https://esearch.waller-cad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txwalk/<parcel>')
def txwalk(parcel):
    url = 'https://esearch.walkercad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txwash/<parcel>')
def txwash(parcel):
    url = 'https://esearch.washingtoncad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txwils/<parcel>')
def txwils(parcel):
    url = 'https://esearch.wilson-cad.org/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

@app.route('/txwise/<parcel>')
def txwise(parcel):
    url = 'https://esearch.wise-cad.com/Property/View'
    result = esearch_texas_flask(url,parcel,headers)
    return result

##################################################
#                                                #
#                                                #
#                                                #
#                                                #
#                                                #
#                                                #
#              PENNSYLVANIA                       #####
#                                                     #
#                                                      #
#                                                       #
#                                                        ####
#                                                           #
#                                                         ###
#                                                      ####
##################################################

@app.route('/paberk/<parcel>')

def PABerk_Mstr(parcel):
    url = 'https://services3.arcgis.com/dGYe1jDYrTw1wwpc/arcgis/rest/services/Berks_Assessment_CAMA_Master_File/FeatureServer/0//query?where=PARID+%3D+%27{}%27&objectIds=&time=&resultType=none&outFields=PARID%2C+OWN1%2C+MAILING%2C+CITYNAME%2C+TOTAL_VALUE%2C+SCHDIST%2C+ADRNO%2CADRADD%2C+ADRDIR%2CADRSTR%2CADRSUF&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&sqlFormat=none&f=pjson'.format(parcel) 
    result = requests.get(url)
    q_result = result.json()

    owner = q_result['features'][0]['attributes']['OWN1']
    assrparcel = q_result['features'][0]['attributes']['PARID']
    scrape_num = q_result['features'][0]['attributes']['PARID']
    mailstreet = q_result['features'][0]['attributes']['MAILING']
    mailcity = q_result['features'][0]['attributes']['CITYNAME']
    totalactualvalue =  q_result['features'][0]['attributes']['TOTAL_VALUE']
    legal =  q_result['features'][0]['attributes']['SCHDIST']
    schedule =  q_result['features'][0]['attributes']['PARID']
    treasacct =  q_result['features'][0]['attributes']['PARID']
    adno = q_result['features'][0]['attributes']['ADRNO'] 
    adradd = q_result['features'][0]['attributes']['ADRADD']
    adrdir = q_result['features'][0]['attributes']['ADRDIR']
    adrstr = q_result['features'][0]['attributes']['ADRSTR'] 
    adrsuf = q_result['features'][0]['attributes']['ADRSUF'] 
    address = [adno,adradd,adrdir,adrstr,adrsuf]
    stringheaders = [str(item) for item in address if item is not None]
    situsstreet = ' '.join(stringheaders)
    
    return jsonify(scrape_dict(assrparcel=assrparcel, owner=owner, situsstreet=situsstreet,mailstreet=mailstreet, mailcity=mailcity, totalactualvalue=totalactualvalue, legal=legal, schedule=schedule,treasacct=treasacct, scrape_num=scrape_num))



app.route('/palack/<parcel>')
def PALack_Flask(parcel):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}
    data = {'mapno':'{}'.format(parcel)}
    response = requests.post('https://ao.lackawannacounty.org/details2.php?mapno={}'.format(parcel), data=data, verify=False)

    #response = requests.get('https://ao.lackawannacounty.org/details2.php?mapno={}'.format(parcel), headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    parcel = soup.find(text='PIN Number:').findNext('td').contents[0].text
    owner = soup.find(text='Name: ').findNext('td').contents[0].text
    mailstreet = soup.find(text='Address: ').findNext('td').contents[0].text
    situsstreet = soup.find(text='Address:').findNext('td').contents[0].text
    situscity = soup.find(text='Municipality:').findNext('td').contents[0].text
    totalassessedvalue = soup.find(text='Total Value: ').findNext('td').contents[0].text
    return jsonify(scrape_dict(parcel=parcel, owner=owner, situsstreet=situsstreet, mailstreet=mailstreet, totalassessedvalue=totalassessedvalue))


@app.route('/palanc/<parcel>')
def PALanc(parcel):
    url = 'http://lancasterpa.devnetwedge.com/parcel/view/{}/2021#PropertyCharacteristics'.format(parcel)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    parcel = soup.find(text='Property ID').findNext('div').contents[0].strip()
    assrparcel = soup.find(text='Property ID').findNext('div').contents[0].strip()
    situsstreet = soup.find(text='Site Address').findNext('div').contents[0].strip()
    owner = soup.find(text='Parcel Owner').findNext('div').contents[0]
    legal = soup.find(text='Township').findNext('div').contents[0]
    #scrape_num = soup.find(text='Property ID').findNext('div').contents[0].replace('-','')
    ownerlabel = soup.find(text='Related Names').findNext('div')
    mailstreet = ownerlabel.find_all('div',{'class':'col-sm-8'})[1].text
    mailcity = ownerlabel.find_all('div',{'class':'col-sm-8'})[2].text
    return jsonify(scrape_dict(parcel=parcel,assrparcel=assrparcel,situsstreet=situsstreet,owner=owner,legal=legal,mailtreet=mailstreet,mailcity=mailcity))


@app.route('/pamonr/<parcel>')
def PAMonr(parcel):
    url = 'http://agencies.monroecountypa.gov/monroepa_prod/Datalets/PrintDatalet.aspx?pin={}&gsp=PROFILEALL&taxyear=2022&jur=045&ownseq=0&card=1&roll=REAL&State=1&item=1&items=-1&all=all&ranks=Datalet'.format(parcel)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    parcel = soup.find(text='Parcel ID').findNext('td').contents[0].strip()
    assrparcel = soup.find(text='Parcel ID').findNext('td').contents[0].strip()
    treasacct = soup.find(text='Map Number').findNext('td').contents[0].strip()
    situsstreet = soup.find(text='Property Location').findNext('td').contents[0].strip()
    owner = soup.find(text='Owner(s)').findNext('td').contents[0].strip()
    mailstreet = soup.find(text='Mailing Address').findNext('td').contents[0].strip()
    legal = soup.find(text='Township').findNext('td').contents[0].strip()
    return jsonify(scrape_dict(parcel=parcel,assrparcel=assrparcel,situsstreet=situsstreet,owner=owner,legal=legal,mailtreet=mailstreet,treasacct=treasacct))


@app.route('/pamont/<parcel>')
def PAMont(parcel):
    url = 'https://propertyrecords.montcopa.org/PT/Datalets/Datalet.aspx?mode=&UseSearch=no&pin={}&jur=046&taxyr=2022'.format(parcel)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    owner_table = soup.find('table',{'id':'Owner'})
    prop_table = soup.find('table',{'id':'Parcel'})
    prop_data = prop_table.find_all('td')
    data = owner_table.find_all('td')
    owner = data[1].text
    mailstreet = data[5].text
    mailcity = data[11].text
    schedule = prop_data[1].text
    parcel = prop_data[3].text
    legal = prop_data[7].text
    situsstreet = prop_data[9].text
    scrape_num = parcel.replace('-','')
    treasacct= parcel.replace('-','')

    return jsonify(scrape_dict(parcel=parcel, schedule=schedule,treasacct=treasacct,owner=owner, situsstreet=situsstreet, legal=legal, mailstreet=mailstreet,mailcity=mailcity,scrape_num=parcel, active=1))

###### CATCH ALL ROUTE DEAL  ######

# Catch-all route to handle undefined routes
@app.route('/<path:path>')
def catch_all(path):
    # Define the regular expression pattern to match six alphanumeric characters
    route_pattern = re.compile(r'^(\w{6})$')
    
    # Extract the first segment of the path
    first_segment = path.split('/')[0]
    
    # Check if the first segment matches the pattern
    if route_pattern.match(first_segment):
        # Call safe_jsonify if the pattern matches
        return safe_jsonify(scrape_dict_func=scrape_dict, path=path)
    
    # If it doesn't match the pattern, return a 404 not found
    return jsonify(error="Not found"), 404








if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

