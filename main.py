import hashlib, requests, os, time

from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

songs_dir = 'G:/Steam/steamapps/common/Quaver/Songs/'


# opens Steam and allows a user to log in, creating login cookies that are then returned in a session
def login_set_cookies(): 
    binary = FirefoxBinary('Firefox.exe')
    driver = webdriver.Firefox(executable_path=r'geckodriver.exe')
    driver.get('https://quavergame.com/download/mapset/1')
    input("Press Enter to continue...")
    cookies = driver.get_cookies()
    new_cookies = {}
    for x in cookies:
        new_cookies[x['name']] = x['value']
    new_cookies.pop('currentPage')
    driver.close()
    return new_cookies


# downloads a quaver map using a session containing Steam login cookies
def download_map(cookies, mapset_id): 
    with open(songs_dir + str(mapset_id) + '.qp', 'wb') as file:
        file.write(requests.get('https://quavergame.com/download/mapset/' + str(mapset_id), cookies=cookies).content)


# main, currently scans all files in songs_dir and checks for update. if there is one then get cookies and download map (TESTING ONLY)
# TODO: Handly scanning of inner directories in a real quaver song folder structure
cookies = login_set_cookies()
print('Cookies Set')
print(cookies)
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
                print('File Hash:', file_hash)
                print('Server Hash:', server_hash)
                print('Update:', update)
                
                if(update):
                    download_map(cookies, mapset_id)
                    print('Map Downloaded')
                    break
            except:
                break
