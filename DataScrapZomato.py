from bs4 import BeautifulSoup
import pandas as pd
import requests
import re
import math

restaurant_names = []
restaurant_areas = []
restaurant_type = []
restaurant_ID = []
restaurant_votes = []
restaurant_ratings = []

to_be_displayed = 80
restaurant_per_page = 15
max_pages = math.ceil(to_be_displayed / restaurant_per_page)

# User Agents used to create Absraction layer to look as if requests coming from browsers
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0'}
page_number = 0

# Since each page contains 15 entries, number of pages to be accessed = 6 to scrap 80 entries.
while page_number < max_pages:

    page_number = page_number + 1
    print("Page number:", page_number)
    url = "https://www.zomato.com/bangalore/south-bangalore-restaurants?page=%d" % page_number

    session = requests.session()

    response = session.get(url, headers=headers)
    content = response.text

    soup = BeautifulSoup(content, features="html.parser")

    for main_div in soup.find_all('div', {'id': "orig-search-list"}):

        # Traversing through card of each restaurant
        for div in main_div.find_all('div', {'class': "content"}):

            if len(restaurant_names) < to_be_displayed:

                for name in div.find_all('a', href=True, attrs={'class': 'result-title'}):
                    restaurant_names.append(name.text.strip())

                for area in div.find_all('a', href=True, attrs={'class': 'mr10'}):
                    restaurant_areas.append(area.text.strip())

                # Since some types are empty, they need to be checked.
                if len(div.find_all('div', {'class': "res-snippet-small-establishment mt5"})) != 0:
                    for types in div.find_all('div', {'class': "res-snippet-small-establishment mt5"}):
                        temp = []

                        for r_type in types.find_all('a', href=True, attrs={'class': 'ttupper'}):
                            temp.append(r_type.text.strip())
                        restaurant_type.append(", ".join(temp))
                else:
                    restaurant_type.append('-')

                for rate in div.find_all('div', {'class': 'search_result_rating'}):

                    for rating in rate.find_all('div', {'class': 'rating-popup'}):
                        restaurant_ratings.append(rating.text.strip())

                        # Since some votes are empty, they need to be checked.
                        if rating.text.strip() != "NEW":
                            for vote in rate.find_all('span'):
                                restaurant_votes.append(vote.text.strip())
                        else:
                            restaurant_votes.append('0 votes')

            else:
                break

print("Number of Restaurants:", len(restaurant_names))
print("Scraping done")

# Generation of Restaurant ID
for i in range(len(restaurant_names)):
    ID = restaurant_names[i][0:5] + "_" + restaurant_areas[i][0:4]
    restaurant_ID.append(re.sub(r"\s+", "", ID))

# Creating a dictionary
t = {'Restaurant ID': restaurant_ID,
     'Restaurant Name': restaurant_names,
     'Area': restaurant_areas,
     'Restaurant Type': restaurant_type,
     'Rating': restaurant_ratings,
     'Votes': restaurant_votes}

# Creating a dataframe
df = pd.DataFrame.from_dict(t)

# Conversion to different formats
df.to_csv('restaurant.csv', index=False, encoding='utf-8')
df.to_json('restaurant.json', orient='records', lines=True)

print("Converted to CSV and JSON format")
