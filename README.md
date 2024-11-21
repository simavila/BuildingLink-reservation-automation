# BuildingLink Reservation Automation

## Introduction

This project automates the process of logging into BuildingLink and making reservations for the tennis court. It utilizes Python's `requests` and `BeautifulSoup` libraries to handle web interactions.

## Features

- **Automated Login**: Logs into BuildingLink using provided credentials.
- **Access Amenities**: Navigates to the Amenity Reservations page.
- **Make Reservations**: Automates the reservation process for the Tennis Court.

## Technologies Used

- [Python 3.x](https://www.python.org/)
- [Requests](https://docs.python-requests.org/)
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)
- [python-dotenv](https://saurabh-kumar.com/python-dotenv/)
- [unittest](https://docs.python.org/3/library/unittest.html)

## Setup Instructions

1. **Clone the Repository**

    ```bash
    git clone https://github.com/yourusername/buildinglink-reservation.git
    cd buildinglink-reservation
    ```

2. **Create a Virtual Environment**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Configure Environment Variables**

    - Rename `.env.example` to `.env`:

        ```bash
        cp .env.example .env
        ```

    - Open `.env` and add your BuildingLink credentials:

        ```
        BUILDINGLINK_USERNAME=your_username
        BUILDINGLINK_PASSWORD=your_password
        ```

5. **Run the Script**

    ```bash
    python src/main_script.py
    ```

## Usage Examples

After setting up, run the main script to automate the reservation process:

```bash
python src/main_script.py
