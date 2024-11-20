import os
import requests
from helper_functions import (
    get_login_page,
    login,
    access_amenity_reservations,
    make_tennis_court_reservation
)
from dotenv import load_dotenv
from datetime import datetime, timedelta

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Debug prints
    print(f"Username loaded: {os.getenv('BUILDINGLINK_USERNAME')}")
    print(f"Password loaded: {os.getenv('BUILDINGLINK_PASSWORD')} (length: {len(os.getenv('BUILDINGLINK_PASSWORD') or '')}")

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })

    # URLs and credentials
    login_page_url = "https://auth.buildinglink.com/Account/Login?ReturnUrl=%2Fconnect%2Fauthorize..."
    login_url = "https://auth.buildinglink.com/Account/Login"
    username = os.getenv("BUILDINGLINK_USERNAME")
    password = os.getenv("BUILDINGLINK_PASSWORD")

    if not username or not password:
        print("Username or password not set. Please check your environment variables.")
        return

    # Debug: After loading credentials
    print(f"Login URL: {login_url}")
    print(f"Username length: {len(username)}")
    print(f"Password length: {len(password)}")

    # Step 1: Get CSRF token from the login page
    csrf_token = get_login_page(session, login_page_url)
    print(f"CSRF Token: {csrf_token}")  # Print the CSRF token to verify
    if csrf_token is None:
        print("Unable to retrieve CSRF token. Exiting.")
        return

    # Step 2: Perform the login
    login_successful = login(session, login_url, username, password, csrf_token)
    if not login_successful:
        print("Login failed. Exiting.")
        return

    # Step 3: Access the Amenity Reservations page
    if not access_amenity_reservations(session):
        print("Failed to access the Amenity Reservations page. Exiting.")
        return
    
    # Add a verification step and potential re-login
    response = session.get('https://www.buildinglink.com/V2/Tenant/Amenities/CalendarView.aspx')
    if response.status_code != 200:
        print("Session appears to be invalid, attempting to re-login...")
        # Re-login
        csrf_token = get_login_page(session, login_page_url)
        if not login(session, login_url, username, password, csrf_token):
            print("Re-login failed. Exiting.")
            return
        if not access_amenity_reservations(session):
            print("Failed to access the Amenity Reservations page after re-login. Exiting.")
            return

    # Calculate a valid future date (e.g., next available Saturday)
    today = datetime.now()
    # Find next Saturday (assuming tennis bookings open on Saturdays)
    days_until_saturday = (5 - today.weekday()) % 7  # 5 represents Saturday
    next_saturday = today + timedelta(days=days_until_saturday)
    
    # Format the date as required
    selected_date = next_saturday.strftime("%Y-%m-%d")
    selected_time = "07:00 AM"
    
    print(f"\nAttempting to book:")
    print(f"Date: {selected_date}")
    print(f"Time: {selected_time}")
    
    # Step 4: Make a reservation for the Tennis Court
    make_tennis_court_reservation(session, selected_date, selected_time)

if __name__ == "__main__":
    main()