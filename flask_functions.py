


def esearch_texas_flask(url, parcel, headers):
    from bs4 import BeautifulSoup
    import requests
    from flask_functions import scrape_dict, safe_jsonify
    from flask import jsonify

    try:
            
        # parcel_page = url+'{}'.format(parcel)
        parcel_page = f"{url}/{parcel}"
        print(f"Constructed URL: {parcel_page}")  # Debug print statement

        response = requests.get(parcel_page, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Initialize all variables to None
        legal = situsstreet = scrape_num = schedule = owner = mailstreet = None
        
        try:
            legal = soup.find(text='Legal Description:').findNext('td').text
            situsstreet = soup.find(text='Situs Address:').findNext('td').text
            scrape_num = soup.find(text='Property ID:').findNext('td').text
        except AttributeError:
            try:
                scrape_num = soup.find(text='Quick Ref ID:').findNext('td').text
            except AttributeError:
                scrape_num = None  # Handle the case where neither ID is found
        try:
            schedule = soup.find(text='Map ID:').findNext('td').text
            owner = soup.find(text='Name:').findNext('td').text
            mailstreet = soup.find(text='Mailing Address:').findNext('td').text
        except AttributeError:
            pass  # If any of these elements are not found, they remain None

        # Check if all fields are None
        if all(value is None for value in [legal, situsstreet, scrape_num, schedule, owner, mailstreet]):
            return jsonify(scrape_dict())  # Return an empty dictionary

        # Return the populated dictionary
        return jsonify(scrape_dict(owner=owner, situsstreet=situsstreet, mailstreet=mailstreet, legal=legal, schedule=schedule, parcel_num=scrape_num, assrparcel=parcel))
    
    except Exception as e:
    # If any exception occurs, fall back to an empty scrape_dict
        return safe_jsonify(scrape_dict)


# def esearch_texas_flask(url,parcel,headers):
#     from bs4 import BeautifulSoup
#     import requests
#     from flask_functions import scrape_dict
#     from flask import jsonify

#     #parcel_page = url+'{}'.format(parcel)
#     parcel_page = f"{url}/{parcel}"
#     print(f"Constructed URL: {parcel_page}")  # Debug print statement


#     response = requests.get(parcel_page, headers=headers)
#     soup = BeautifulSoup(response.content, "html.parser")
#     legal = soup.find(text='Legal Description:').findNext('td').text
#     situsstreet = soup.find(text='Situs Address:').findNext('td').text
#     try:
#         scrape_num = soup.find(text='Property ID:').findNext('td').text
#     except AttributeError:
#         try:
#             scrape_num = soup.find(text='Quick Ref ID:').findNext('td').text
#         except AttributeError:
#             scrape_num = None  # Handle the case where neither ID is found
#     schedule = soup.find(text='Map ID:').findNext('td').text
#     owner = soup.find(text='Name:').findNext('td').text
#     mailstreet = soup.find(text='Mailing Address:').findNext('td').text
#     return jsonify(scrape_dict(owner=owner,situsstreet=situsstreet,mailstreet=mailstreet,legal=legal, schedule=schedule, scrape_num=scrape_num, assrparcel=parcel))


def scrape_dict( **kwargs ):
    from datetime import datetime
    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
    scrape = {
        'parcel': '',
        'owner': '',
        'situsstreet': '',
        'situscity': '', 
        'mailstreet': '', 
        'mailcity': '', 
        'legal': '', 
        'taxdistrict':'', 
        'totalassessedvalue':'', 
        'totalactualvalue': '', 
        'totaltax' : '', 
        'totallevy' : '', 
        'totaldue' : '', 
        'payment1' : '', 
        'datepaid1' : '', 
        'payment2' : '', 
        'datepaid2' : '', 
        'payment3' : '', 
        'datepaid3': '', 
        'resv1' : '', 
        'resv2' : '',
        'resv3' : '',
        'resv4' : '',
        'resv5' : '',
        'resv6' : '', 
        'county': '', 
        'assrparcel': '', 
        'treasacct': '', 
        'schedule': '',
        'lastUpdatedDate': formatted_date,
        'active':'1',
        'ID': '',
        'scrape_num': '', 
        }
    scrape.update(kwargs)
    return (scrape)
    
def safe_jsonify(scrape_dict_func=scrape_dict, **kwargs):
    from flask import jsonify
    from flask_functions import scrape_dict  # Assuming scrape_dict i
    
    try:
        # Attempt to jsonify the result of the scrape_dict function
        return jsonify(scrape_dict_func(**kwargs))
    except Exception as e:
        # If any exception occurs, return an empty scrape_dict
        return jsonify(scrape_dict_func())
    
def tyler_scrape_flask(parcel_num, countyweb):
    
    import requests
    import pandas as pd
    from bs4 import BeautifulSoup 
    import urllib3
    from flask import jsonify 
    
    urllib3.disable_warnings()

    
    try:

        headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}
        
        login = countyweb+'/treasurer/web/loginPOST.jsp'
        parcel_page = countyweb+'/treasurer/treasurerweb/account.jsp?account={}'.format(parcel_num)
        #COElbt https://services.elbertcounty-co.gov/assessor/taxweb/account.jsp?accountNum=R101590  

        #Cookie Install, worked on Elbert, TEST###########
        s = requests.Session()
        res = s.get(parcel_page, headers=headers, verify=False)
        yum = s.cookies
        ### End of Cookie Install

        try:
            payload = {
            'submit': 'Login',
            'guest' : 'true'
            }
        except:
            payload = {
            'submit': 'Click Here',
            'guest' : 'true'
            }

        with requests.session() as session:
            post = session.post(login, data=payload, headers=headers,verify=False,cookies=yum)
            response = session.get(parcel_page, headers=headers, cookies=yum)
            #print(response.text)
            soup = BeautifulSoup(response.content, "html.parser")
        
        table_body = soup.find('div',{'id':'taxAccountSummary'})
        h1tags = soup.find_all('h1')

            #print(x, 'else NOT dead')
            # If len is over 3, it will have owner/legal info on inactives or actives need to find out which way so I can adjust index on scrape
        rows = table_body.find_all('tr',{'class':'hasLabel'})
        stats = [(i.contents[0], i.contents[1].text) for i in rows]

        table_title = h1tags[-3].text

        # ACTIVE property if it only lists 'summary'
        if table_title == 'Summary':
            try:
                treasacct = stats[0][-1]
            except:
                pass
            try:
                parcel = stats[1][1]
            except:
                pass
            try:
                owner = stats[2][1]
            except:
                pass
            try:
                mailstreet = stats[3][1]
            except:
                pass
            try:
                situsstreet = stats[4][1]
            except:
                pass
            try:
                legal = stats[5][1]
            except:
                pass
            try:
                scrape_num = stats[0][-1]
            except:
                pass

        return jsonify(scrape_dict(treasacct=treasacct, parcel=parcel, owner=owner, mailstreet=mailstreet, situsstreet=situsstreet, assrparcel=parcel, legal=legal, parcel_num=scrape_num, active=1))
    
    except Exception as e:
    # If any exception occurs, fall back to an empty scrape_dict
        return safe_jsonify(scrape_dict)

# arrCAD['taxYear']
# arrCAD['status']
# arrCAD['distcode']
# arrCAD['jurisName']
# arrCAD['marketValue']
# arrCAD['assessedValue']
# arrCAD['taxableValue']
# arrCAD['exemptionValue']
# arrCAD['taxRate']
# arrCAD['estTax']

def juris_dict( **kwargs ):
    scrape = {
        'taxYear': '',
        'status': '',
        'distcode': '',
        'jurisName': '', 
        'marketValue': '', 
        'assessedValue': '', 
        'taxableValue': '', 
        'exemptionValue':'', 
        'taxRate':'', 
        'estTax': '', 
        }
    scrape.update(kwargs)
    return (scrape)

#Park this function in Flask Functions
def reassign_keys(data, key_mapping, juris_dict_func):
    new_data = []
    for item in data:
        kwargs = {key_mapping[k]: v for k, v in item.items() if k in key_mapping}
        new_item = juris_dict_func(**kwargs)
        new_data.append(new_item)
    return new_data

############### TXHarr Jurisdiction Specific Functions ######################

#Park this function in Flask Functions - TXHarr
def get_table_html(driver):
    from bs4 import BeautifulSoup
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find_all('table', class_='bgcolor_1')[9]
    return table

#Park this function in Flask Functions - TXHarr - It was hit and miss finding the Not Cert so
def find_not_certified_with_retries(table, retries=3, delay=2):
    for attempt in range(retries):
        if find_not_certified(table):
            return True
        if attempt < retries - 1:
            time.sleep(delay)
    return False

#Park this function in Flask Functions - TXHarr
def find_not_certified(table):
    rows = table.find_all('tr', align='center')
    not_certified_found = False
    for row in rows:
        cells = row.find_all('td', class_='data')
        if cells:
            for cell in cells:
                a_tag = cell.find('a')
                if a_tag and 'Not Certified' in a_tag.get_text(strip=True):
                    not_certified_found = True
                    break
        if not_certified_found:
            break
    return not_certified_found

#Park this function in Flask Functions - TXHarr
def extract_data_from_table(table):
    data = []
    header_row = table.find_all('tr')[1]
    headings = [th.get_text(strip=True) for th in header_row.find_all('th')[1:]]
    rows = table.find_all('tr')[2:]
    for index, row in enumerate(rows):
        cells = row.find_all('td')
        if cells and cells[0].get('rowspan'):
            rowspan_depth = int(cells[0].get('rowspan'))
            if index < rowspan_depth:
                cells = cells[1:]
        if len(cells) == len(headings):
            row_data = {headings[i]: cells[i].get_text(strip=True) for i in range(len(cells))}
            data.append(row_data)
    return data

############### TXHarr Jurisdiction Specific Functions END ######################
