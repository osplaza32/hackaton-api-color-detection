from json.decoder import JSONDecodeError
import pandas as pd
import colorgram
import requests
import io

df = pd.read_csv("FACL.csv", sep=',', error_bad_lines=False, index_col=False, dtype='unicode')


def get_color(url):
    response = None
    try:
        response = requests.request("GET", url, headers={}, data={})
    except requests.exceptions.RequestException:

        return get_color(url)

    if response is None:
        return get_color(url)
    else:
        try:
            return response.json()
        except JSONDecodeError:
            print("json except")
            return get_color(url)


def image_manipulate(url,dict):
    fd = None
    try:
        fd = requests.request("GET", url,

                              headers={}, data={}, stream=True)
    except requests.exceptions.RequestException:
        return image_manipulate(url,dict)

    if fd is None:
        return image_manipulate(url,dict)
    else:
        f = io.BytesIO(fd.content)
        colors = colorgram.extract(f, 4)
        colorsname = []
        for first_color in colors:
            rgb = first_color.rgb
            urlColor = 'http://thecolorapi.com/id?rgb=' + str(rgb[0]) + ',' + str(rgb[1]) + ',' + str(
                rgb[2]) + '&format=json'
            try:
                color = dict[urlColor]
            except KeyError:
             info = get_color(urlColor)
             dict[urlColor] = info["name"]["value"].upper()
             color = info["name"]["value"].upper()
            colorsname.append(color)
        return (','.join(colorsname),dict)


data = []
dict = {}
cout = 0
for row in df.iterrows():
    (color,dict)= image_manipulate(row[1]["SKU_ID_PHOTO_URL"],dict)
    data.append({"SKU_ID": row[1]["SKU_ID"], "SKU_ID_PHOTO_URL": row[1]["SKU_ID_PHOTO_URL"],
                 "COLORS": color})
    cout = cout + 1
    print(str(cout) + " De " + str(df.size)+ " Registros creados")

df2 = pd.DataFrame(data, columns=['SKU_ID', 'SKU_ID_PHOTO_URL', 'COLORS'])
print("END")
df2.to_csv('file1.csv')
