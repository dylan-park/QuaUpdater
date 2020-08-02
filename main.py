import hashlib, requests, os, time, pickle, sys

from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from progress.bar import Bar

songs_dir = 'G:/Steam/steamapps/common/Quaver/Songs/'


# opens Steam and allows a user to log in, creating login cookies that are then returned in a session
def login_get_cookies(): 
    binary = FirefoxBinary('Firefox.exe')
    driver = webdriver.Firefox(executable_path=r'geckodriver.exe')
    driver.get('https://quavergame.com/download/mapset/1')
    while(driver.current_url != 'https://quavergame.com/'):
        pass
    time.sleep(.5)
    cookies = driver.get_cookies()
    new_cookies = {}
    for x in cookies:
        new_cookies[x['name']] = x['value']
    new_cookies.pop('currentPage')
    driver.close()
    return new_cookies


# downloads a quaver map using a session containing Steam login cookies
def download_map(cookies, mapset_id): 
    with open('Updated Songs/' + str(mapset_id) + '.qp', 'wb') as file:
        file.write(requests.get('https://quavergame.com/download/mapset/' + str(mapset_id), cookies=cookies).content)
        
def save_cookies(cookies):
    with open('cookies', 'wb') as file:
        pickle.dump(cookies, file)


def read_cookies():
    with open('cookies', 'rb') as file:
        cookies = pickle.load(file)
        return cookies

# main, currently scans all files in songs_dir and checks for update.
# cookies = login_get_cookies()
# save_cookies(cookies)
cookies = read_cookies()
print('\nCookies Set')
print(cookies)

# count all maps
map_count = 0
for path in os.listdir(songs_dir):
    map_count += 1

bar = Bar('Processing', max=map_count)


for foldername in os.listdir(songs_dir):
    for filename in os.listdir(songs_dir + foldername):
        if filename.endswith(".qua"):
            md5_hash = hashlib.md5()
            try:
                with open(songs_dir + foldername + '/' + filename, 'rb') as file:
                    request = requests.get('https://api.quavergame.com/v1/maps/' + filename.split('.')[0])
                    md5_hash.update(file.read())
                    file_hash = md5_hash.hexdigest()
                    mapset_id = request.json()['map']['mapset_id']
                    server_hash = request.json()['map']['md5']
                    update = (file_hash != server_hash)
                print('\nFile Hash:', file_hash)
                print('\nServer Hash:', server_hash)
                print('\nUpdate:', update)
                
                if(update):
                    download_map(cookies, mapset_id)
                    print('\nMap Downloaded')
                    break
            except:
                print(sys.exc_info()[0])
                break
        bar.next()
    bar.finish()
