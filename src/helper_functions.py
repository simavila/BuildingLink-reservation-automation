import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_login_page(session, login_page_url):
    """
    Fetches the login page and extracts the CSRF token.

    Args:
        session (requests.Session): The session object.
        login_page_url (str): URL of the login page.

    Returns:
        str: CSRF token if successful, None otherwise.
    """
    try:
        response = session.get(login_page_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_input = soup.find('input', {'name': '__RequestVerificationToken'})
        if csrf_input and csrf_input.get('value'):
            csrf_token = csrf_input['value']
            return csrf_token
        else:
            print("CSRF token not found on the login page.")
            return None
    except Exception as e:
        print(f"Error fetching login page: {e}")
        return None

def login(session, login_url, username, password, csrf_token):
    """
    Submits the login form with credentials and CSRF token.

    Args:
        session (requests.Session): The session object.
        login_url (str): URL to submit the login form.
        username (str): Username for login.
        password (str): Password for login.
        csrf_token (str): CSRF token extracted from login page.

    Returns:
        bool: True if login is successful, False otherwise.
    """
    # Add headers to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://www.buildinglink.com',
        'Referer': login_url
    }

    payload = {
        "Username": username,
        "Password": password,
        "__RequestVerificationToken": csrf_token,
        "ReturnUrl": "/connect/authorize/callback?client_id=bl-web&response_mode=form_post&response_type=code+id_token&scope=openid+profile+email+bl-api&state=OpenIdConnect.AuthenticationProperties%3D&nonce=",
        "RememberLogin": "false"
    }

    try:
        response = session.post(login_url, data=payload, headers=headers, allow_redirects=False)
        
        # Debug information
        print(f"Status code: {response.status_code}")
        
        # Check response content for login failure indicators
        response_text = response.text.lower()
        if ("invalid username or password" in response_text or 
            "incorrect credentials" in response_text or
            "login failed" in response_text or
            'class="validation-summary-errors"' in response.text):
            print("Login failed - Invalid credentials")
            return False
            
        # Check if we're actually logged in by looking for success indicators
        if response.status_code == 302:  # Successful login usually redirects
            redirect_url = response.headers.get('Location', '')
            if 'connect/authorize' in redirect_url or 'dashboard' in redirect_url:
                print("Login successful - Proper redirect detected")
                return True
        
        print("Login failed - Unexpected response")
        return False
        
    except Exception as e:
        print(f"Error during login: {e}")
        return False

def access_amenity_reservations(session):
    """
    Accesses the Amenity Reservations page.
    """
    amenity_url = "https://www.buildinglink.com/V2/Tenant/Amenities/CalendarView.aspx"
    try:
        response = session.get(amenity_url)
        # Save the response for debugging
        with open("amenity_page.html", "w", encoding='utf-8') as f:
            f.write(response.text)
            
        print(f"\nDebug Info - Amenity Page:")
        print(f"Status Code: {response.status_code}")
        print(f"URL after redirect: {response.url}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error accessing Amenity Reservations page: {e}")
        return False

def make_tennis_court_reservation(session, selected_date, selected_time):
    # Step 1: First verify we're still on the amenity page
    amenity_url = "https://www.buildinglink.com/V2/Tenant/Amenities/CalendarView.aspx"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Referer': 'https://www.buildinglink.com/',
        'Upgrade-Insecure-Requests': '1'
    }
    
    response = session.get(amenity_url, headers=headers)
    print(f"\nVerifying amenity page access: {response.status_code}")
    
    if "Access is denied" in response.text:
        print("Lost access to amenity page")
        return False
        
    # Step 2: Access the tennis court page directly with all required parameters
    tennis_url = "https://www.buildinglink.com/V2/Tenant/Amenities/NewReservation.aspx"
    params = {
        'amenityId': '25328',
        'from': '0',
        'selectedDate': selected_date
    }
    
    # Update headers with the correct referer
    headers['Referer'] = amenity_url
    
    # Add any auth-related cookies from the previous request
    auth_cookie = session.cookies.get('.AspNetCore.Identity.Application')
    if auth_cookie:
        print(f"\nUsing auth cookie: {auth_cookie[:30]}...")
    
    response = session.get(tennis_url, params=params, headers=headers)
    print(f"\nAccessing tennis court page: {response.status_code}")
    
    # Save the response content for debugging
    with open("tennis_response.html", "w") as f:
        f.write(response.text)
    print(f"Response saved to tennis_response.html")
    
    # Check if we got the actual form page
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Look for specific elements that would indicate we're on the correct page
    title = soup.find('title')
    print(f"\nPage title: {title.text if title else 'No title found'}")
    
    # Look for any form elements or reservation-related content
    form_elements = soup.find_all(['form', 'input', 'select'])
    print(f"\nFound {len(form_elements)} form-related elements")
    
    for elem in form_elements[:5]:  # Print first 5 elements
        print(f"- {elem.name}: {elem.get('id', 'No ID')} {elem.get('name', 'No name')}")
    
    return True