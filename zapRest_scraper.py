import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import pandas as pd
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime  # Import datetime module for timestamp

# Initialize the WebDriver (make sure to adjust the path to your WebDriver)
driver_path = r'C:\Users\i9\Desktop\Code\Python Projects\webScraperNews\chromedriver-win64\chromedriver.exe'  # Update this path
service = Service(driver_path)
driver = webdriver.Chrome(service=service)

# Load the website
url = 'https://www.rest.co.il/restaurants/israel/'
driver.get(url)

# Wait for the page to load fully
time.sleep(3)  # Adjust this based on your internet speed or implement WebDriverWait for dynamic loading

# Click the "show more" button 5 times to load more restaurants
for _ in range(40):
    try:
        # Locate and click the "show more" button
        show_more_button = driver.find_element(By.CSS_SELECTOR, 'a.next-results[aria-label="עוד תוצאות"]')
        show_more_button.click()
        # Wait for new content to load after each click
        time.sleep(3)
    except NoSuchElementException:
        print("No more 'show more' button found.")
        break  # Exit loop if the button is not found

# Extract the restaurant data elements (after clicking 'show more' 5 times)
restaurant_elements = driver.find_elements(By.CLASS_NAME, 'feature-column')

# Create an empty list to store the restaurant data
restaurant_data = []

# Loop through each restaurant block
for restaurant in restaurant_elements:
    # Extract restaurant name
    name = restaurant.find_element(By.CLASS_NAME, 'rest-title').text.strip()

    # Extract image URL
    image_url = restaurant.find_element(By.CLASS_NAME, 'feature-column-photo img').get_attribute('src')

    # Extract reviews and number of reviews
    try:
        reviews = restaurant.find_element(By.CLASS_NAME, 'reviews_box').text.strip()
    except:
        reviews = 'No reviews'

    # Extract type of restaurant and address safely
    try:
        p_text = restaurant.find_element(By.XPATH, './/p').text.split("\n")
        if len(p_text) >= 2:
            restaurant_type = p_text[0]
            address = p_text[1]
        else:
            restaurant_type = p_text[0] if len(p_text) > 0 else 'No type available'
            address = 'No address available'
    except:
        restaurant_type = 'No type available'
        address = 'No address available'

    # Try extracting phone number from phone-link or fallback to phone-icon
    try:
        phone_number = restaurant.find_element(By.CSS_SELECTOR, 'a.phone-link').get_attribute('href')
        phone_number = phone_number.replace('tel:', '').strip()  # Remove the 'tel:' prefix
    except:
        try:
            phone_number = restaurant.find_element(By.CSS_SELECTOR, 'a.phone-icon').get_attribute('href')
            phone_number = phone_number.replace('tel:', '').strip()
        except:
            phone_number = 'No phone number'

    # Extract opening hours
    try:
        opening_hours = restaurant.find_element(By.CLASS_NAME, 'open-link').text.strip()
    except:
        opening_hours = 'No opening hours'

    # Extract link to restaurant page
    try:
        restaurant_link = restaurant.find_element(By.CSS_SELECTOR, '.rest-title a').get_attribute('href')
    except:
        restaurant_link = 'No restaurant link'

    # Fix delivery link extraction by ensuring it targets the right class and aria-label
    try:
        delivery_link = restaurant.find_element(By.CSS_SELECTOR, 'a.details-link-item[aria-label="הזמנת משלוח"]').get_attribute('href')
    except:
        delivery_link = 'No delivery link'

    # Append the data for this restaurant to the list
    restaurant_data.append({
        'Name': name,
        'Image URL': image_url,
        'Reviews': reviews,
        'Type': restaurant_type,
        'Address': address,
        'Phone Number': phone_number,
        'Opening Hours': opening_hours,
        'Restaurant Page Link': restaurant_link,
        'Delivery Link': delivery_link
    })

# Convert the data to a pandas DataFrame
df = pd.DataFrame(restaurant_data)

# Generate a timestamp for the CSV filename
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # Format: YYYY-MM-DD_HH-MM-SS
filename = f'restaurants_data_{timestamp}.csv'  # Create a unique filename

# Export to CSV, ensuring that Hebrew characters are properly encoded with UTF-8
df.to_csv(filename, encoding='utf-8-sig', index=False)

# Close the WebDriver
driver.quit()

print(f"Scraping complete, data saved to '{filename}'.")
