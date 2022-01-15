from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pymysql
from email.message import EmailMessage
import os
import smtplib

endpoint = os.environ.get("ENDPOINT")

username = os.environ.get("USERNAME")

password = os.environ.get("DB_PASSWORD")

database_name = os.environ.get("DB_NAME")

def send_email(message):
    SENDER = os.environ.get("SENDER")
    RECIPIENT  = os.environ.get("RECIPIENT")
    USERNAME_SMTP = os.environ.get("USERNAME_SMTP")
    PASSWORD_SMTP = os.environ.get("PASSWORD_SMTP")
    HOST = os.environ.get("HOST")
    PORT = os.environ.get("PORT")
    SUBJECT = "Game(s) on sale Today!"
    
    
    msg = EmailMessage()
    msg['Subject'] = SUBJECT
    msg['From'] = SENDER
    msg['To'] = RECIPIENT
    
    msg.set_content(message)

    try:  
        server = smtplib.SMTP(HOST, PORT)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(USERNAME_SMTP, PASSWORD_SMTP)
        server.sendmail(SENDER, RECIPIENT, str(msg))
        server.close()
        
# Display an error message if something goes wrong.
    except Exception as e:
        print ("Error: ", e)
    else:
        print ("Email sent!")

def get_current_price(pageUrl):
    pricePage = requests.get(pageUrl)
    soup1 = BeautifulSoup(pricePage.text, 'html.parser')
    price = soup1.find('span', {'class' , "Price-module__srOnly___2mBg_"})
    priceText = str(price.get_text())
    
    finalPrice = float(priceText[priceText.rfind("$")+1:])
    
    if("on sale for" in priceText):
        nonSalePrice = float(priceText[priceText.find("$")+1:priceText.find(",")])
        return nonSalePrice, finalPrice
    else:
        return None, finalPrice


def get_product_name(inputUrl):
    page = requests.get(inputUrl)
    soup2 = BeautifulSoup(page.text, 'html.parser')
    productName = soup2.find('h1', {'class', "typography-module__xdsH1___zrXla ProductDetailsHeader-module__productTitle___l-kbD"})
    nameText = str(productName.get_text())
    
    return nameText



def add_to_price_table(strippedName, price, date, c):
    
    c.execute(f"INSERT INTO {strippedName} VALUES (DEFAULT, '{price}' , '{date}')")

    return None


def create_price_table(name, c):

    c.execute(f"""CREATE TABLE {name} (
    id INT AUTO_INCREMENT primary key NOT NULL,
    price REAL,
    date TEXT
    )""")

    return None


def check_in_table(input, c):
    sql = ("SELECT EXISTS(SELECT 1 FROM items WHERE url = %s)")
    c.execute(sql, input)
    a = c.fetchone()
    if (a[0] == 1):
        return True

    else:
        return False


def delete_item(url, name):

    if (check_in_table(input)):
        c.execute("DELETE FROM items WHERE url = ?", (url,))
        c.execute(f"DROP TABLE {name} ")

    else:
        print("Item not being tracked, cannot be deleted")

    return None

def delete_all():
    
    c.execute("DELETE FROM items")
    return None


if (__name__ == "__main__"):
    
    try:
        conn = pymysql.connect(host=endpoint,user=username,
                               passwd=password,db=database_name)
        c = conn.cursor()
    except:
        sys.exit()

    today = str(datetime.now())

    
    allTableNames = c.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'prices';")
    allTableNames = str(c.fetchall())
    c.close()
    c = conn.cursor()

    if('items' not in allTableNames):
        c.execute("""CREATE TABLE items (
        name TEXT, 
        url TEXT
        )""")
        
    
        
    current_tracked_items = c.execute("SELECT * from items")
    current_tracked_items = c.fetchall()
    email_message = ''
    
    if(len(current_tracked_items) > 0):
        for i in (current_tracked_items):
            
            name = i[0]

            url = i[1]

            nonSalePrice, currentPrice = get_current_price(url)

            strippedName = ''.join( chr for chr in name if chr.isalnum() )
            
            if(strippedName not in allTableNames):
                create_price_table(strippedName,c)
                email_message += f"\n \n {name} has been entered too recently to compare to yesterdays price, but today it costs ${price}, the URL is {url}"
            
            else:
                last_price = (c.execute(f"SELECT price from prices.{strippedName} order by id DESC LIMIT 1"))
                last_price = float(c.fetchone()[0])
                sale_amount = 1.0 - (float(currentPrice)/last_price)

                if(x is not None):
                    email_message += f"\n \n {name} is currently on sale for ${currentPrice}, the regular price is ${nonSalePrice}, the URL is {url}"
                    
                else:
                    email_message += f"\n \n The price for {name} is now ${currentPrice}, {sale_amount}% less than yesterday! The URL is {url}"
                
                
                
                
            add_to_price_table(strippedName, currentPrice, today,c)
        
    if (len(email_message) > 0):
        send_email(email_message)
        
  
    conn.commit()
    conn.close()