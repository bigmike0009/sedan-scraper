import json
import boto3
from botocore.exceptions import NoCredentialsError
from headless_chrome import create_driver
from selenium.webdriver.common.by import By
from botofuncs import read_csv_from_s3, upload_csv_to_s3, duplicate_file_in_s3, get_last_modified_date, send_email, grant_public_read_access
from datetime import datetime
from email_html import format_html
import traceback



def parse_car_info(car_string):
    car_info = {}

    # Split the input string into lines
    lines = car_string.split('\n')

    # Iterate through each line and extract information
    for line in lines:
        # Split each line into key and value
        parts = line.split(':')

        # Remove leading/trailing whitespace from key and value
        key = parts[0].strip()
        value = parts[1].strip() if len(parts) > 1 else None

        # Store key-value pairs in the dictionary
        car_info[key] = value

    return car_info
    
def scrapeSe(comparisonDict, resultCsv):
    driver = create_driver()
    pages_remaining = True
    page=1
        
    while pages_remaining:
        driver.get(f"https://www.secars.com/inventory.aspx?_sort=photoasc&_page={page}")
        car_listings = driver.find_elements(By.CLASS_NAME, 'ebiz-viewport-item')
        
        listings_per_page= len(car_listings)
        print(f'Listings on page {str(page)} : {str(listings_per_page)}')
        if listings_per_page <= 0:
            pages_remaining = False
            break
            
    
    # Extract and print details for each car
        for car_listing in car_listings:
            vin_number = car_listing.get_attribute('vin-number')
            title = car_listing.find_element(By.CLASS_NAME, 'ebiz-vdp-title').text
            subtitle = car_listing.find_element(By.CLASS_NAME, 'ebiz-vdp-subtitle').text
            promo_text = car_listing.find_element(By.CLASS_NAME, 'ebiz-promo-text').text
            promo_text = promo_text.replace(',','-')
    
            
            # Extract additional details like engine, transmission, exterior, interior, etc.
            details = car_listing.find_element(By.CLASS_NAME, 'srp-vehicle-details').text
            detailMap=parse_car_info(details)
            
            # Extract price
            price = car_listing.find_element(By.CLASS_NAME, 'money-sign-disp').text
            price = ''.join(char for char in price if char.isdigit())
            
            # Print the details for the current car
            #print(f"VIN: {vin_number}")
            #print(f"Title: {title}")
            #print(f"Subtitle: {subtitle}")
            #print(f"Promo Text: {promo_text}")
            #print(f"Details: {details}")
            #print(f"Price: {price}")
            #print("\n---\n")
            
            resultCsv.append([vin_number, title, price, subtitle, promo_text, detailMap['Engine'],detailMap['Transmission'],detailMap['Miles'],detailMap['Exterior'],detailMap['Interior'],detailMap['Stock #']])
            comparisonDict[vin_number]={'new_price':price, 'title':title, 'subtitle':subtitle}
            
        page = page + 1
        
    return comparisonDict, resultCSV

def pullPrevRunData(comparisonDict, resultCsv):
    previousRunData = read_csv_from_s3('sedan-scraper-data', 'secars_latest.csv')    
        
    for car in previousRunData:
        if car[0] in comparisonDict.keys():
            #if the car is still on the site
            comparisonDict[car[0]]['old_price'] = car[2]
        else:
            comparisonDict[car[0]] = {'new_price':-1, 'old_price':car[2], 'title':car[1], 'subtitle':car[3]}

    return comparisonDict, resultCsv

def lambda_handler(event, context):
    
    if 'env' in event and event['env'] == 'prod':
        distribution_list=['mikea0009@gmail.com', 'Jd3@tomlinsonmotorco.com']#, 'Jd3@tomlinsonmotorco.com', 'sez2000@cox.net']
    else:
        distribution_list=['2022.allcen@gmail.com']
    
    try:

        resultCsv = [['VIN', 'Title', 'Price', 'Subtitle', 'Promo Text', 'Details', 'Engine','Transmission','Miles','Exterior','Interior','Stock #']]
        comparisonDict={}
        
        comparisonDict, resultCsv = scrapeSe(comparisonDict, resultCsv)
        comparisonDict, resultCsv = pullPrevRunData(comparisonDict, resultCsv)
                
        email_type, email_message = format_html(comparisonDict)
        print(email_type)
        print(email_message)
        
        last_run = get_last_modified_date('sedan-scraper-data', 'secars_latest.csv')
        duplicate_file_in_s3('sedan-scraper-data', 'secars_latest.csv', 'sedan-scraper-data', f'secars_{last_run}.csv')
        upload_csv_to_s3(resultCsv, 'sedan-scraper-data', 'secars_latest.csv')
        grant_public_read_access('sedan-scraper-data', 'secars_latest.csv')
        
        if email_type == 'Text':
            print('Sending no update email')
            send_email(f'SECAR: No update {last_run}', email_type, email_message, ['2022.allcen@gmail.com'], '2022.allcen@gmail.com')
    
        else:
            print('Sending update email')

            send_email(f'SECAR: update {last_run}', email_type, email_message, distribution_list, '2022.allcen@gmail.com')
    
        return {
            'statusCode': 200,
            'body': json.dumps('Update Performed succesfully')
        }
        
    except Exception as e:
        currtime = datetime.now().strftime('%b-%d %I:%M%p')
        print(traceback.format_exc())
        send_email(f'SECAR: Failure {currtime}', 'Text', traceback.format_exc(), ['2022.allcen@gmail.com'], '2022.allcen@gmail.com')
        return {
            'statusCode': 404,
            'body': str(e)
        }
