from bs4 import BeautifulSoup
import requests
import re
import progressbar

# Function to fetch the HTML content of a page
def fetch_page_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return None

# Placeholder function to simulate fetching configuration based on userId
def fetch_configuration(user_id):
    # Replace this with actual logic to fetch configuration based on userId
    return {
        'wishOwner': 'claud.xiao',  # Replace with the actual wishOwner value
        'itemsPerPage': 10  # Replace with the actual itemsPerPage value
    }

def fetch_wish_list(wishOwner, config_set):
    # Generate the URL based on the configuration
    url = f'http://book.douban.com/people/{wishOwner}/wish'
    
    # Fetch the page content
    page_content = fetch_page_content(url)

    # Function to parse the page and get the list of page links
    def get_page_links(content):
        soup = BeautifulSoup(content, 'html.parser')
        page_links = [int(link.text) for link in soup.select('.paginator a')]
        return page_links

    # Function to fetch book list from a page
    def fetch_books_from_page(page_url):
        page_content = fetch_page_content(page_url)
        if page_content:
            soup = BeautifulSoup(page_content, 'html.parser')
            books_on_page = [
                {'title': book.select_one('.subject-item .info h2 a')['title'],
                 'href': book.select_one('.subject-item .info h2 a')['href']}
                for book in soup.select('.subject-item')
            ]
            return books_on_page
        else:
            return []

    # Get the list of page links
    page_links = get_page_links(page_content)

    # Initialize progress bar
    progress = progressbar.ProgressBar()

    # List to store book information
    book_list = []

    # Loop through each page and fetch book list
    for page_link in progress(page_links):
        page_url = f'{url}?start={page_link * config_set["itemsPerPage"]}'
        books_on_page = fetch_books_from_page(page_url)
        book_list.extend(books_on_page)

    return book_list

# Test the fetch_wish_list function
def main():
    user_id = 1  # Replace with the actual user ID
    config_set = fetch_configuration(user_id)
    wish_owner = config_set['wishOwner']
    books = fetch_wish_list(wish_owner, config_set)
    print(books)

if __name__ == "__main__":
    main()

