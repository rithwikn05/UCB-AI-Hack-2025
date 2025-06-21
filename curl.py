import requests
from requests.auth import HTTPBasicAuth

username = "glad"
password = "ardpas"

lat = "13N"  # example
tile = "105E_13N"
interval = "920"
outfolder = "/Users/anikait/Downloads"
outfile = f"{outfolder}/{interval}.tif"

url = f"https://glad.umd.edu/dataset/glad_ard2/{lat}/{tile}/{interval}.tif"

response = requests.get(url, auth=HTTPBasicAuth(username, password), stream=True)

if response.status_code == 200:
    with open(outfile, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Downloaded: {outfile}")
else:
    print(f"Failed with status code {response.status_code}: {response.text}")
