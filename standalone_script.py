import requests
from xml.etree import ElementTree as ET
import pandas as pd
import keys
import json
import time
from pathlib import Path
from token_manager import get_valid_application_token
from user_counter import *
from user_selector import *
from datetime import datetime,timedelta
from itertools import cycle


def main():
    proxies = ["http://54.36.175.129:8000 ", "http://54.36.122.54:8000", "http://135.148.90.31:8000"]
    proxy_pool = cycle(proxies)
    global token
    client_id, client_secret,c_user, current_count= user_credentials_selector()
    if c_user is None:
        return
    token = get_valid_application_token(client_id = client_id, client_secret= client_secret, user=c_user)
    script_path  = Path(__file__).parent
    timeout_duration = 10
    max_retries = 3
    retry_delay = 5 
    max_request = 5000
    # print(f'current count for user {current_count}')
    # countig_range = max_request - current_count
    # print('counting range is ',countig_range)
    # Example timeout duration in seconds
    timeout_duration = 10

    print('function started')
    # Your eBay app ID
    # /home/qparts/ebay_scraper/input_data
    # /home/qparts/ebay_scraper/input_data/chunk_1.xlsx
    app_id = keys.app_id
    client_secret = keys.client_secret
    partnumber_file_path = f"{script_path}/input_data/chunk_3.xlsx"
    part_numbers  = pd.read_excel(partnumber_file_path)
    file_name  = Path(partnumber_file_path).stem
    # Dates
    current_date = datetime.now()
    data_of_scraping = time.strftime("%d-%m-%Y")
    yesterday_date = current_date - timedelta(days=1)
    data_of_yesterday_scraped_file = yesterday_date.strftime("%d-%m-%Y")

    full_scraped_data_filename = file_name+'_'+data_of_scraping
    yesterday_scraped_file = file_name+'_'+data_of_yesterday_scraped_file
    # token = get_valid_application_token(app_id, client_secret)
    try:
        # /home/qparts/ebay_scraper/output
        excel_file_path = script_path / 'output' / f'{full_scraped_data_filename}.xlsx'
        last_scraped_file = pd.read_excel(excel_file_path)
        print(f'Last scraped file is \t : {excel_file_path}')
        last_processed_value = last_scraped_file['Part Number'].iloc[-1]
        start_index = part_numbers[part_numbers['Part Number'] == last_processed_value].index[0] + 1
    except:
        print('It is a new scarping cycle for today')
        excel_file_path = script_path / 'output' / f'{yesterday_scraped_file}.xlsx'
        print(f'Last scraped file is \t : {excel_file_path}')
        n_path = script_path / 'output' / f'{full_scraped_data_filename}.xlsx'
        new_file = pd.DataFrame(columns = ['Part Number'])
        new_file.to_excel(n_path)
        last_scraped_file = pd.read_excel(excel_file_path)
        last_processed_value = last_scraped_file['Part Number'].iloc[-1]
        start_index = part_numbers[part_numbers['Part Number'] == last_processed_value].index[0] + 1
    


    # eBay Shopping API endpoint
    url_shopping = 'https://open.api.ebay.com/shopping?'
    # Headers for the API request
    shoppin_headers = {
        "X-EBAY-API-IAF-TOKEN": f"Bearer {token}",  # Replace with your actual access token
        "X-EBAY-API-SITE-ID": "0",
        "X-EBAY-API-CALL-NAME": "GetSingleItem",
        "X-EBAY-API-VERSION": "863",
        "X-EBAY-API-REQUEST-ENCODING": "XML",
        "Content-Type": "application/xml"  # Specify the content type as XML
    }
    
    
# functions 
    def xml_to_dict(element):
        if not element:
            # If it's a leaf node, return the text directly
            return element.text
        return {subelem.tag: xml_to_dict(subelem) for subelem in element}
    

    def make_api_request(url, headers, data, part_number,first_item_id,timeout_duration, retry_delay, max_retries=3):
            excel_file_path = script_path / 'output' / f'{full_scraped_data_filename}.xlsx'
            scraped_data = pd.read_excel(excel_file_path)

            for attempt in range(max_retries):
                if attempt >= 2:
                    print('secod retry with new token')
                try:
                    response = requests.post(url, headers=headers, data=data, timeout=timeout_duration)
                    # Check the response status code
                    # print(response.content)
                    if response.status_code == 200:
                        print('second request successded')
                        # print(response.content) 
                    
                        root = ET.fromstring(response.content)
                        # XML data
                        xml_data = ET.tostring(root, encoding='utf8').decode('utf8')

                        # converting to json format 
        
                        d = xml_to_dict(root)
                        json_data = json.dumps(d, indent=4)
                        

                        # Define categories to extract
                        categories = [
                            'PictureURL', 'PrimaryCategoryID', 'PrimaryCategoryName', 'Make','Superseded Part Number','OE/OEM Part Number','Interchange Part Number',
                            'Manufacturer Part Number', 'Model', 'Other Part Number','Replaces Part Number', 'Part Brand','Brand','FOR','Fit',
                            'Placement on Vehicle', 'Type', 'Year'
                        ]
                        # Parse the XML data
                        root = ET.fromstring(xml_data)

                        # Initialize an empty dictionary to store extracted data
                        data_dict = {
                            category: [] if category in ['PictureURL', 'Placement on Vehicle'] else None for category in categories
                        }
                        
                        # Extract basic information
                        title = root.find('.//ns0:Title', namespaces={'ns0': 'urn:ebay:apis:eBLBaseComponents'}).text
                        price = root.find('.//ns0:ConvertedCurrentPrice', namespaces={'ns0': 'urn:ebay:apis:eBLBaseComponents'}).text
                        data_dict.update({'Title': title, 'Price': price})
                        # Extract information from ItemSpecifics
                        for name_value_list in root.findall('.//ns0:NameValueList', namespaces={'ns0': 'urn:ebay:apis:eBLBaseComponents'}):
                            name = name_value_list.find('.//ns0:Name', namespaces={'ns0': 'urn:ebay:apis:eBLBaseComponents'}).text
                            value = name_value_list.find('.//ns0:Value', namespaces={'ns0': 'urn:ebay:apis:eBLBaseComponents'}).text
                            if name in categories:
                                if name in ['PictureURL', 'Placement on Vehicle']:
                                    # Append existing value or create a new list
                                    if data_dict[name]:
                                        data_dict[name].append(value)
                                    else:
                                        data_dict[name] = [value]
                                else:
                                    # Update dictionary with extracted value
                                    data_dict[name] = value
                        # Extract information from other elements
                        for category in categories:
                            try:
                                element = root.find(f'.//ns0:{category}', namespaces={'ns0': 'urn:ebay:apis:eBLBaseComponents'})
                                if element is not None:
                                    # Handle single values or lists depending on category
                                    if category in ['PictureURL', 'Placement on Vehicle']:
                                        data_dict[category].append(element.text)
                                    else:
                                        data_dict[category] = element.text
                            except AttributeError:
                                pass  # Ignore missing elements instead of throwing an error
                        df = pd.DataFrame([data_dict])
                        dn = pd.DataFrame([{'Part Number':part_number, 'Item ID':first_item_id}])
                        dr = pd.concat([dn, df],axis=1, join='outer', ignore_index=False)
                        scraped_data = pd.concat([scraped_data,dr],ignore_index= True)


                        # Display the dataframe
                        
                        excel_file_path = script_path / 'output' / f'{full_scraped_data_filename}.xlsx'
                        scraped_data.to_excel(f"./output/{full_scraped_data_filename}.xlsx",index= False)
                        scraped_data.to_csv(f"./output/{full_scraped_data_filename}.csv",index= False)
                        print('data saved')
                        break  # If successful, break out of the retry loop
                    else:
                        global app_id
                        # Authentication error, token might have expired
                        print("Authentication failed, fetching a new token...")
                          # Ensure we are updating the global token variable
                        token = get_valid_application_token(app_id, client_secret)
                        headers["X-EBAY-API-IAF-TOKEN"] = f"Bearer {token}"  # Update the header with the new token
                        continue  # Retry with the new token
                except requests.exceptions.Timeout:
                    print(f"Request timed out, retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                except requests.exceptions.RequestException as e:
                    print(f"An error occurred: {e}")
                    break  # Break if other request-related exceptions occur


    # print(start_index)
    for current_index, row in part_numbers.iloc[start_index:].iterrows():
        proxy = next(proxy_pool)
        
        if current_index == 2661:
            print(f'{current_index}it is now time to change the last scraped P N to not duplicate the numbers !!')

            
        client_id, client_secret,c_user, current_count= user_credentials_selector()
        if c_user is None:
            break
        token = get_valid_application_token(client_id = client_id, client_secret= client_secret, user=c_user)
        
        if current_count < max_request:
            current_count = update_counter(user = c_user)
            part_number = row['Part Number'] 
            product_name  = part_number
            print('loop started at ',part_number)

            # Step 1: Search for the item using keywords
            url = f"https://svcs.ebay.com/services/search/FindingService/v1?OPERATION-NAME=findItemsByKeywords&SERVICE-VERSION=1.0.0&SECURITY-APPNAME={app_id}&RESPONSE-DATA-FORMAT=JSON&REST-PAYLOAD&keywords={product_name}"
            for attempt in range(max_retries):
                try:
                    search_response = requests.get(url, proxies={"http": proxy, "https": proxy},timeout=timeout_duration)
                    # , proxies={"http": proxy, "https": proxy} 
                    # print(search_response.content)
                    # Process the response...
                    if search_response.status_code==200:
                        print('first request success')
                        # print(search_response.content)
                        search_data = search_response.json()
                        break  # If successful, break out of the retry loop
                except requests.exceptions.Timeout:
                    print(f"Request timed out, retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                except requests.exceptions.RequestException as e:
                    print(f"An error occurred: {e}")
                    break  # Break if other request-related exceptions occur
                except requests.exceptions.ProxyError:
                    # Handle the proxy error by continuing with the next proxy
                    continue
            else:
                print(search_response.content)
                print("Maximum retries reached for this part number, moving to next.")
                continue  # Continue to the next part number

            try:
                first_item_id = search_data['findItemsByKeywordsResponse'][0]['searchResult'][0]['item'][0]['itemId'][0]
                
                # Construct the XML request body
                body = f'''
                <?xml version="1.0" encoding="utf-8"?>
                <GetSingleItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
                <ItemID>{first_item_id}</ItemID>
                <IncludeSelector>Details,ItemSpecifics,Variations,ShippingCosts</IncludeSelector>
                </GetSingleItemRequest>
                '''
                response = make_api_request(url_shopping, headers=shoppin_headers, data=body, part_number= part_number,first_item_id=first_item_id,timeout_duration = timeout_duration, retry_delay= retry_delay)
                # print(response.content)
                if response is None:
                    continue  # Skip to the next part number if the request failed


                else:
                    print("Maximum retries reached for this part number, moving to next.")
                    continue  # Continue to the next part number
                # Make the API request
                
            except ConnectionError as e:
                print(e)
                print(e.response.dict())
            except:
                continue
        
        else:
            print('reach the limit of 5000 request/day for all the users')
            break
        


main()
