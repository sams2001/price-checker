from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pymysql
import os


endpoint = os.environ.get("ENDPOINT")

username = os.environ.get("USERNAME")

password = os.environ.get("DB_PASSWORD")

database_name = os.environ.get("DB_NAME")


def get_product_name(inputUrl):
    page = requests.get(inputUrl)
    soup2 = BeautifulSoup(page.text, 'html.parser')
    productName = soup2.find('h1', {'class', "typography-module__xdsH1___zrXla ProductDetailsHeader-module__productTitle___l-kbD"})
    nameText = str(productName.get_text())
    
    return nameText

def add_to_items_table(name, url, c):

    c.execute(f"INSERT INTO items VALUES ('{name}','{url}')")

    return None


def check_in_table(input, c):
    sql = ("SELECT EXISTS(SELECT 1 FROM items WHERE url = %s)")
    c.execute(sql, input)
    a = c.fetchone()
    if (a[0] == 1):
        return True

    else:
        return False


def delete_item(url, name, c):

    if (check_in_table(url, c)):
        c.execute("DELETE FROM items WHERE url = %s", url)
        c.execute(f"DROP TABLE {name} ")

    else:
        print("Item not being tracked, cannot be deleted")

    return None

def delete_all(c):

    c.execute("DELETE FROM items")
    return None

if (__name__ == "__main__"):
    
    try:
        conn = pymysql.connect(host=endpoint,user=username,
                               passwd=password,db=database_name)
        c = conn.cursor()
    except:
        sys.exit()


    url = ''

    name = get_product_name(url)

    strippedName = ''.join( chr for chr in name if chr.isalnum() )

    ok = c.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'prices';")
    ok = str(c.fetchall())



    if(strippedName not in ok):
        add_to_items_table(name, url, c)
        
    #delete_item(url, strippedName, c)
    
    #c.execute(f"DROP TABLE {strippedName} ")


    conn.commit()
    conn.close()
    