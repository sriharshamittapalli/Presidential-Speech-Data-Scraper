import os
import csv
import requests
from bs4 import BeautifulSoup

def get_soup(url):
    """Fetches the content from the URL and returns a BeautifulSoup object."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx, 5xx)
        return BeautifulSoup(response.content, 'lxml')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def format_for_url(text):
    """Formats the name or date to match the URL structure (may need refinement)."""
    text = text.lower().replace(',', '')
    text = text.replace('.', '')
    return text.replace(' ', '-')

def save_text_to_file(text, president_name, date):
    """Saves the text of the address to a file and returns the file path."""
    # Create a directory to save the files (if not exists)
    directory = 'presidential_addresses'
    os.makedirs(directory, exist_ok=True)
    
    # Format the filename
    filename = f"{president_name.replace(' ', '_')}_{date.replace(' ', '_').replace(',', '')}.txt"
    filepath = os.path.join(directory, filename)
    
    # Write the text to a file
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(text)
    
    return filepath

def extract_info(soup):
    """Extracts names, dates, URLs, and text content from the soup and stores them in a list."""
    if soup is None:
        return []

    extracted_data = []
    target_href_for_link = '/primary-sources/government/presidential-speeches/'
    
    for link in soup.find_all('a', href=lambda href: href and target_href_for_link in href):
        if '(' in link.text and ')' in link.text:
            name_part, date_part = link.text.split('(', 1)
            name = name_part.strip()
            date = date_part.replace(')', '').strip()
            link_url = 'https://www.infoplease.com' + link.get('href')
            
            # Fetch and parse the detailed page for each address
            try:
                link_soup = get_soup(link_url)
                if link_soup:
                    article_div = link_soup.find('div', class_='article')
                    paragraphs = ''
                    if article_div:
                        for paragraph in article_div.find_all('p'):
                            paragraphs += paragraph.text
                    else:
                        print(f"Article not found for {name} ({date})")
                        paragraphs = 'No content found'
                    
                    # Save the text to a file and get the filename
                    filename = save_text_to_file(link_url, name, date)
                    
                    # Append name, date, link_url, filename, and full text
                    extracted_data.append([name, date, link_url, filename, paragraphs])
                else:
                    print(f"Failed to parse {link_url}")
            except Exception as e:
                print(f"Error processing {link_url}: {e}")
    return extracted_data

def save_to_csv(data, filename='presidential_speeches.csv'):
    """Saves the extracted data into a CSV file."""
    headers = ['Name of President', 'Date of Union Address', 'Link to Address', 'Filename of Address', 'Text of Address']
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)  # Write the header
        writer.writerows(data)    # Write the data

def main():
    """Main function to coordinate the scraping process."""
    url = 'https://www.infoplease.com/primary-sources/government/presidential-speeches/state-union-addresses'
    soup = get_soup(url)
    data = extract_info(soup)
    save_to_csv(data)

if __name__ == '__main__':
    main()