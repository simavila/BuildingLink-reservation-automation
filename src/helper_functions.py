import requests
from bs4 import BeautifulSoup
from datetime import datetime
import urllib.parse

def get_login_page(session, login_page_url):
    """
    Gets the login page and extracts the CSRF token.
    """
    try:
        # Get the login page with the proper OAuth parameters
        initial_url = 'https://auth.buildinglink.com/Account/Login?ReturnUrl=%2Fconnect%2Fauthorize%2Fcallback%3Fclient_id%3Dbl-web%26response_mode%3Dform_post%26response_type%3Dcode%2520id_token%2520token%26scope%3Dopenid%2520profile%2520groups%2520buildinglink%2520offline_access%2520uuids'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Upgrade-Insecure-Requests': '1'
        }
        
        response = session.get(initial_url, headers=headers)
        print(f"Login page status: {response.status_code}")
        
        # Extract CSRF token from the HTML
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_input = soup.find('input', {'name': '__RequestVerificationToken'})
        
        if csrf_input:
            csrf_token = csrf_input.get('value')
        else:
            # Fallback to antiforgery cookie
            csrf_token = session.cookies.get('.AspNetCore.Antiforgery.I_06S-EykLg')
            
        return csrf_token
        
    except Exception as e:
        print(f"Error getting login page: {e}")
        return None

def login(session, login_url, username, password, csrf_token):
    """
    Performs the login request with the provided credentials.
    """
    try:
        # Get the initial login page with ReturnUrl
        initial_url = 'https://auth.buildinglink.com/Account/Login?ReturnUrl=%2Fconnect%2Fauthorize%2Fcallback%3Fclient_id%3Dbl-web%26response_mode%3Dform_post%26response_type%3Dcode%2520id_token%2520token%26scope%3Dopenid%2520profile%2520groups%2520buildinglink%2520offline_access%2520uuids'
        
        # Prepare the login data - note we're using Input. prefix again
        login_data = {
            'Input.Username': username,
            'Input.Password': password,
            'Input.RememberLogin': 'false',
            '__RequestVerificationToken': csrf_token,
            'ReturnUrl': '/connect/authorize/callback?client_id=bl-web&response_mode=form_post&response_type=code%20id_token%20token&scope=openid%20profile%20groups%20buildinglink%20offline_access%20uuids'
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://auth.buildinglink.com',
            'Referer': initial_url,
            'Connection': 'keep-alive',
            'Host': 'auth.buildinglink.com',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Upgrade-Insecure-Requests': '1'
        }

        # Add the antiforgery cookie explicitly
        antiforgery_cookie = session.cookies.get('.AspNetCore.Antiforgery.I_06S-EykLg')
        if antiforgery_cookie:
            session.cookies.set('.AspNetCore.Antiforgery.I_06S-EykLg', antiforgery_cookie)

        print("\nSending login request...")
        print(f"URL: {login_url}")
        print(f"Antiforgery cookie: {antiforgery_cookie}")
        print(f"CSRF token: {csrf_token}")
        
        # Make the login request
        response = session.post(
            login_url,
            data=login_data,
            headers=headers,
            allow_redirects=True
        )
        
        print(f"Login response status: {response.status_code}")
        print(f"Final URL: {response.url}")
        
        # Save response for debugging
        with open("login_response.html", "w", encoding='utf-8') as f:
            f.write(response.text)
            
        # Print response headers for debugging
        print("\nResponse headers:")
        for header, value in response.headers.items():
            print(f"{header}: {value}")
            
        # Check if we got redirected to the success page
        return 'buildinglink.com/v2/' in response.url or response.status_code == 302
        
    except Exception as e:
        print(f"Login error: {e}")
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
    
    # Find the form and extract necessary hidden fields
    form = soup.find('form', id='form1')
    if not form:
        print("Reservation form not found")
        return False
    
    # Extract VIEWSTATE and other ASP.NET hidden fields
    hidden_fields = {}
    for hidden in form.find_all('input', type='hidden'):
        hidden_fields[hidden.get('name')] = hidden.get('value')
    
    # Prepare the reservation data
    reservation_data = {
        **hidden_fields,  # Include all hidden fields
        'ctl00$ContentPlaceHolder1$StartTime': selected_time,
        'ctl00$ContentPlaceHolder1$Duration': '60',  # Assuming 1-hour reservation
        'ctl00$ContentPlaceHolder1$Notes': '',  # Optional notes
        'ctl00$ContentPlaceHolder1$btnReserve': 'Reserve'
    }
    
    # Submit the reservation
    headers['Referer'] = tennis_url
    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    
    response = session.post(tennis_url, data=reservation_data, headers=headers)
    print(f"\nReservation submission status: {response.status_code}")
    
    # Save the response for debugging
    with open("reservation_response.html", "w") as f:
        f.write(response.text)
    print(f"Reservation response saved to reservation_response.html")
    
    # Check for success indicators in the response
    if "successfully" in response.text.lower() or "confirmed" in response.text.lower():
        print("Reservation appears to be successful!")
        return True
    else:
        print("Reservation might have failed. Check reservation_response.html for details")
        return False