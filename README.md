# ThreatConnect Indicator Query Tool

This Python script allows users to interactively search ThreatConnect for indicator content based on various types of indicators such as IP addresses, hostnames, email addresses, and more. It utilizes the ThreatConnect API to retrieve and display information about indicators in a user-friendly format.

## Features

- **Interactive Search**: Allows users to input indicators directly or via a file for querying ThreatConnect.
- **Support for Multiple Indicator Types**: Search by IP addresses, hostnames, email addresses, URLs, and more.
- **Colorized Output**: Displays search results in a visually appealing, colorized format for easy reading.
- **Flexible Input**: Accepts multiple indicators separated by space, line, or comma.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.6 or higher installed on your system.
- Access to a ThreatConnect instance with API access enabled.
- Your ThreatConnect API Access ID and Secret Key.

## Installation

1. **Clone the Repository**

   Clone this repository to your local machine using:

   ```sh
   git clone https://github.com/Arizona-Cyber-Threat-Response-Alliance/threatconnect-cli.git
   ```

2. **Install Required Python Packages**

   Navigate to the cloned directory and install the required Python packages using:

   ```sh
   pip install -r requirements.txt
   ```

   Here's the content for `requirements.txt`:

   ```
   requests
   colorama
   ```

3. **Set Environment Variables**

   Set the following environment variables in your system:

   - `tc_accessid`: Your ThreatConnect API Access ID.
   - `tc_secretkey`: Your ThreatConnect API Secret Key.

   For Unix/Linux/macOS:

   ```sh
   export tc_accessid='your_access_id_here'
   export tc_secretkey='your_secret_key_here'
   ```

   For Windows:

   ```cmd
   set tc_accessid=your_access_id_here
   set tc_secretkey=your_secret_key_here
   ```

## Usage

To use the ThreatConnect Indicator Query Tool, follow these steps:

1. **Run the Script**

   Navigate to the directory where the script is located and run:

   ```sh
   python3 tc-indicator.py
   ```

2. **Enter Indicators**

   When prompted, enter the indicators you wish to search for. You can separate multiple indicators using space, line, or comma.

3. **View Results**

   The script will query ThreatConnect for the entered indicators and display the results in a colorized format. Each indicator's details will be shown, including type, date added, last modified, rating, confidence, and more.
