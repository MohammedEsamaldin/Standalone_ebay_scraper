def make_api_request(url, headers, data, part_number,first_item_id,timeout_duration, retry_delay, max_retries=3):
            global client_id, client_secret,c_user, current_count, token
            excel_file_path = script_path / 'output' / f'{full_scraped_data_filename}.xlsx'
            scraped_data = pd.read_excel(excel_file_path)

            for attempt in range(max_retries):
                
                if attempt >= 1:
                    print('secod retry with new token')
                try:
                    namespaces = {'ns0': 'urn:ebay:apis:eBLBaseComponents'}
                    response = requests.post(url, headers=headers, data=data, timeout=timeout_duration)
                    # Check the response status code
                    # print(response.content)
                    if response.status_code == 200:
                        print('second request successded')
                        # print(response.content) 
                    
                        root = ET.fromstring(response.content)
                        # XML data
                        xml_data = ET.tostring(root, encoding='utf8').decode('utf8')

                        doc = xmltodict.parse(xml_data)
                        # print(doc)

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
                        data_dict['Compatibility']= []
                        print('test1')
                        try:
                            # Extract basic information
                            title = root.find('.//ns0:Title', namespaces).text
                            price = root.find('.//ns0:ConvertedCurrentPrice', namespaces).text
                            data_dict.update({'Title': title, 'Price': price})
                            # Extract information from ItemSpecifics
                            for name_value_list in root.findall('.//ns0:NameValueList', namespaces):

                                try:    
                                    name = name_value_list.find('.//ns0:Name', namespaces).text
                                    value = name_value_list.find('.//ns0:Value', namespaces).text
                                    if name in categories:
                                        # 
                                        if name in ['PictureURL', 'Placement on Vehicle']:
                                            # Append existing value or create a new list
                                            if data_dict[name]:
                                                # 
                                                data_dict[name].append(value)
                                            else:
                                                # 
                                                data_dict[name] = [value]
                                        else:
                                            #  Update dictionary with extracted value
                                            data_dict[name] = value
                                            
                                except error as e:
                                    print(f" errror !!")
                            # Extract information from other elements
                            
                            
                            try:
                                for category in categories:
                                    element = root.find(f'.//ns0:{category}', namespaces)
                                    if element is not None:
                                        # Handle single values or lists depending on category
                                        if category in ['PictureURL', 'Placement on Vehicle']:
                                            data_dict[category].append(element.text)
                                        else:
                                            data_dict[category] = element.text
                                print('success')
                            except:
                                print(f" errror ")
                                pass  # Ignore missing elements instead of throwing an error
                           
                            ########## Compatibility Table ###########
                                
                            
                            # print('test3')
                            # try:
                            #     # Navigate to the Compatibility elements
                            #     print('Searching for Compatibility!!')
                            #     item_compatibility_list = doc['GetSingleItemResponse']['Item']['ItemCompatibilityList']
                            #     compatibilities = item_compatibility_list.get('Compatibility', [])

                            #     compatibility_list = []
                    

                            #     for comp in compatibilities:
                            #         # Process each Compatibility element
                            #         comp_data = {}
                            #         name_value_lists = comp.get('NameValueList', [])

                            #         # Make sure it's a list
                            #         if isinstance(name_value_lists, dict):
                            #             name_value_lists = [name_value_lists]

                            #         for nvl in name_value_lists:
                            #             if nvl:  # Skip None values
                            #                 name = nvl.get('Name')
                            #                 value = nvl.get('Value')
                            #                 if name and value:
                            #                     comp_data[name] = value

                            #         if comp_data:
                            #             compatibility_list.append(comp_data)
                            #             print(f'found compatibility \n {compatibility_list}')
                            #     data_dict['Compatibility']= compatibility_list
                            # except:
                            #     print('no compatbility')
                            try:
                                 # Parse the XML data
                                root = ET.fromstring(xml_data)

                                # Define the namespace
                                namespaces = {'ns': 'urn:ebay:apis:eBLBaseComponents'}

                                # Find the ItemCompatibilityList element
                                item_compat_list = root.find('ns:Item/ns:ItemCompatibilityList', namespaces)

                                # Initialize a list to store compatibility details
                                compatibilities = []

                                # Check if the ItemCompatibilityList element is found
                                if item_compat_list is not None:
                                    # Iterate over each Compatibility element
                                    for compatibility in item_compat_list.findall('ns:Compatibility', namespaces):
                                        compatibility_details = {}

                                        # Iterate over each NameValueList element within Compatibility
                                        for nv_list in compatibility.findall('ns:NameValueList', namespaces):
                                            name = nv_list.find('ns:Name', namespaces).text if nv_list.find('ns:Name', namespaces) is not None else None
                                            value = nv_list.find('ns:Value', namespaces).text if nv_list.find('ns:Value', namespaces) is not None else None

                                            # Add name and value to the compatibility details
                                            if name and value:
                                                compatibility_details[name] = value

                                        # Add the compatibility details to the compatibilities list
                                        if compatibility_details:
                                            compatibilities.append(compatibility_details)
                                    data_dict['Compatibility'] = compatibilities
                            except Exception as e:
                                print(f"Error in compatibility extraction: {e}")




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



                        except:
                            for error in root.findall(".//ns0:Errors", namespaces):
                                short_message = error.find('ns0:ShortMessage', namespaces).text
                                if short_message == "IP limit exceeded.":
                                    print(f'limit is exceeded for the current user' )
                                    
                                    
                                    
                                    # Making the current user count = 5000 to move to next item
                                    
                                    client_id, client_secret,c_user, current_count= user_credentials_selector()
                                    print(f'user number {c_user}')
                                    change_user_count(c_user)
                                    
                                    client_id, client_secret,c_user, current_count= user_credentials_selector()
                                    print(f'user number {c_user}')
                                    #  # Ensure we are updating the global token variable
                                    token = get_valid_application_token(client_id = client_id, client_secret= client_secret, user=c_user)
                               
                                    # token = get_valid_application_token(app_id, client_secret)
                                    headers["X-EBAY-API-IAF-TOKEN"] = f"Bearer {token}"
                                    break
                                    
                            
                            

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