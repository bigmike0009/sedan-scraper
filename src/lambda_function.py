import json
import traceback
from datetime import datetime
from headless_chrome import create_driver
from selenium.webdriver.common.by import By
from botofuncs import read_csv_from_s3, upload_csv_to_s3, duplicate_file_in_s3, get_last_modified_date, send_email, grant_public_read_access
from email_html import format_html

def parse_car_info(car_string):
    """
    Parse car information from a string and return a dictionary.
    """
    car_info = {}
    lines = car_string.split('\n')
    
    for line in lines:
        parts = line.split(':')
        key = parts[0].strip()
        value = parts[1].strip() if len(parts) > 1 else None
        car_info[key] = value

    return car_info

def scrape_se(comparison_dict, result_csv):
    """
    Scrape car information from a website and update the comparison dictionary and result CSV.
    """
    driver = create_driver()
    pages_remaining = True
    page = 1

    while pages_remaining:
        driver.get(f"https://www.secars.com/inventory.aspx?_sort=photoasc&_page={page}")
        car_listings = driver.find_elements(By.CLASS_NAME, 'ebiz-viewport-item')
        listings_per_page = len(car_listings)

        print(f'Listings on page {str(page)} : {str(listings_per_page)}')

        if listings_per_page <= 0:
            pages_remaining = False
            break

        for car_listing in car_listings:
            vin_number = car_listing.get_attribute('vin-number')
            title = car_listing.find_element(By.CLASS_NAME, 'ebiz-vdp-title').text
            subtitle = car_listing.find_element(By.CLASS_NAME, 'ebiz-vdp-subtitle').text
            promo_text = car_listing.find_element(By.CLASS_NAME, 'ebiz-promo-text').text
            promo_text = promo_text.replace(',', '-')

            details = car_listing.find_element(By.CLASS_NAME, 'srp-vehicle-details').text
            detail_map = parse_car_info(details)

            price = car_listing.find_element(By.CLASS_NAME, 'money-sign-disp').text
            price = ''.join(char for char in price if char.isdigit())

            result_csv.append([vin_number, title, price, subtitle, promo_text, detail_map['Engine'], detail_map['Transmission'], detail_map['Miles'], detail_map['Exterior'], detail_map['Interior'], detail_map['Stock #']])
            comparison_dict[vin_number] = {'new_price': price, 'title': title, 'subtitle': subtitle}

        page = page + 1

    return comparison_dict, result_csv

def pull_prev_run_data(comparison_dict, result_csv):
    """
    Pull previous run data from S3 and update the comparison dictionary and result CSV.
    """
    previous_run_data = read_csv_from_s3('sedan-scraper-data', 'secars_latest.csv')

    for car in previous_run_data:
        if car[0] in comparison_dict.keys():
            comparison_dict[car[0]]['old_price'] = car[2]
        else:
            comparison_dict[car[0]] = {'new_price': -1, 'old_price': car[2], 'title': car[1], 'subtitle': car[3]}

    return comparison_dict, result_csv

def lambda_handler(event, context):
    """
    Lambda function handler.
    """
    if 'env' in event and event['env'] == 'prod':
        distribution_list = ['mikea0009@gmail.com', 'Jd3@tomlinsonmotorco.com']
    else:
        distribution_list = ['2022.allcen@gmail.com']

    try:
        result_csv = [['VIN', 'Title', 'Price', 'Subtitle', 'Promo Text', 'Details', 'Engine', 'Transmission', 'Miles', 'Exterior', 'Interior', 'Stock #']]
        comparison_dict = {}

        comparison_dict, result_csv = scrape_se(comparison_dict, result_csv)
        comparison_dict, result_csv = pull_prev_run_data(comparison_dict, result_csv)

        email_type, email_message = format_html(comparison_dict)
        print(email_type)
        print(email_message)

        last_run = get_last_modified_date('sedan-scraper-data', 'secars_latest.csv')
        duplicate_file_in_s3('sedan-scraper-data', 'secars_latest.csv', 'sedan-scraper-data', f'secars_{last_run}.csv')
        upload_csv_to_s3(result_csv, 'sedan-scraper-data', 'secars_latest.csv')
        grant_public_read_access('sedan-scraper-data', 'secars_latest.csv')

        if email_type == 'Text':
            print('Sending no update email')
            send_email(f'SECAR: No update {last_run}', email_type, email_message, ['2022.allcen@gmail.com'], '2022.allcen@gmail.com')
        else:
            print('Sending update email')
            send_email(f'SECAR: update {last_run}', email_type, email_message, distribution_list, '2022.allcen@gmail.com')

        return {
            'statusCode': 200,
            'body': json.dumps('Update Performed successfully')
        }

    except Exception as e:
        curr_time = datetime.now().strftime('%b-%d %I:%M%p')
        print(traceback.format_exc())
        send_email(f'SECAR: Failure {curr_time}', 'Text', traceback.format_exc(), ['2022.allcen@gmail.com'], '2022.allcen@gmail.com')
        return {
            'statusCode': 404,
            'body': str(e)
        }
