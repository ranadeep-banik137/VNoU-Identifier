import requests
from PIL import Image
from io import BytesIO
import threading
from modules.database import populate_users


# Function to fetch random user data
def fetch_random_user_data(n):
    response = requests.get(f'https://randomuser.me/api/?results={n}')
    data = response.json()
    return data['results']


# Function to convert image URL to binary blob
def image_url_to_blob(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr


def main(n):
    users = fetch_random_user_data(n)
    for user in users:
        name = f"{user['name']['first']} {user['name']['last']}"
        userImg = image_url_to_blob(user['picture']['large'])
        address = f"{user['location']['street']['number']} {user['location']['street']['name']}, {user['location']['postcode']}"
        city = f"{user['location']['city']}"
        state = f"{user['location']['state']}"
        contact = user['phone']
        country = user['location']['country']
        threading.Thread(target=populate_users, args=(userImg, name, contact, address, city, state, country)).start()
    # insert_user_data_into_db(users)
    print(f"Inserted {n} users into the database.")


if __name__ == "__main__":
    number_of_users = 1000  # Set the number of users to fetch and insert
    main(number_of_users)
