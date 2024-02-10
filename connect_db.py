#For connecting to a postgres database(optional)
from crawl import Crawler 
import psycopg2 
from psycopg2 import Error
from dotenv import load_dotenv 
import os 


load_dotenv()
pg_config = {
    'dbname': os.getenv("db_name"),
    'user': os.getenv("user_name"),
    'password': os.getenv("password"),
    'host': 'localhost',
    'port': '5432'
}



def insert_into_db(): # Start crawling and putting into df 
    conn = psycopg2.connect(**pg_config)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vnexpress (
            url VARCHAR(255), 
            title VARCHAR(1000), 
            content TEXT, 
            created_at TIMESTAMP
            
        )
    """)
    conn.commit()
    #Crawling + inserting into db 
    crawler = Crawler()
    articles = crawler.main() 
    for article in articles: 
        if article is not None:
            try:  
                cur.execute("INSERT INTO vnexpress(url, title, content, created_at) VALUES (%s,%s, %s, %s)",
                ((article[0], article[1], article[2],article[3])))
                conn.commit()
            except psycopg2.IntegrityError as e: 
                conn.rollback() #If duplicate then not insert
    
    #Try retrieving data: 
    cur.execute("SELECT * FROM vnexpress LIMIT 5")
    rows = cur.fetchall()
    for row in rows: 
        print("URL:", row[0])
        print("Title:", row[1])
        print("Content:", row[2])
        print("Created at:", row[3])
    cur.close()
    conn.close()


insert_into_db()
