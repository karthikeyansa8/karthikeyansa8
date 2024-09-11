import requests
import json
import time
import psycopg2 as psy
import pandas as pd
import logging
# Set up logging
logging.basicConfig(
    filename='discord_bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME=os.getenv("DB_NAME")
DB_USER=os.getenv("DB_USER")
DB_PASSWORD=os.getenv("DB_PASSWORD")
DB_HOST=os.getenv("DB_HOST")
DB_PORT=os.getenv("DB_PORT")
DISCORD_AUTH_TOKEN=os.getenv("DISCORD_AUTH_TOKEN")


HEADERS={
    "Authorization": DISCORD_AUTH_TOKEN
}





session = requests.Session()
channel_ids = [1281499568630136842,1281499626742222870]


# Predefined data
predefined_responses = {
    'hi': 'Hello',
    'how are you': 'Fine',
    'how is your day': 'Yeah it\'s fine, How about you?',
    'hello this is karthikeyan': 'Hi, I am a discord bot..!'

}


def fetch_recent_message(channel_id:int,session,HEADERS:dict):
    """_summary_

    Args:
        channel_id (int): _description_
        session (_type_): _description_
        HEADERS (dict): _description_

    Returns:
        _type_: _description_
    """

    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    response = session.get(url, headers=HEADERS)

    if response.status_code == 200:
        messages = response.json()[0]  
        logging.info(f"Message fetched from channel {channel_id}: {messages}")
        return messages
    else:
        logging.error(f"Failed to fetch messages from channel {channel_id}: {response.status_code}")
        print(f"Failed to fetch messages from channel {channel_id}: {response.status_code}")
    
    return None


def post_message_to_discord(channel_id:int,session,HEADERS:dict, message_content:str):
    """_summary_

    Args:
        channel_id (int): _description_
        session (_type_): _description_
        HEADERS (dict): _description_
        message_content (str): _description_
    """
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    payload = {"content": message_content}
    logging.info(f"Posting message to channel {channel_id}: {message_content}")
    response = session.post(url, payload, headers=HEADERS)

    if response.status_code == 200:
        logging.info(f"Message sent to channel {channel_id}: {message_content}")
        print(f"Message sent to channel {channel_id}: {message_content}")
    else:
        logging.error(f"Failed to send message to channel {channel_id}: {response.status_code}")
        print(f"Failed to send message to channel {channel_id}: {response.status_code}")


def DB_connection():
         
    try:
        conn = psy.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        print("Successfully connected")
        return conn
    
    except Exception as e:
        print("Connection Failed...",e)
        return None


def insert_message_to_db(df,conn):
    """_summary_

    Args:
        df (_type_): _description_
    """  
    try:  
        cur = conn.cursor()
        for i, row in df.iterrows():

            cur.execute("""
                INSERT INTO discord (cont, ts, msg_id, chan_id, author_id, username, globalname, content_type, img_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (row['cont'], row['ts'], row['msg_id'], row['chan_id'], row['author_id'], row['username'], 
                  row['globalname'], row['content_type'], row['img_url']))
        conn.commit()
    except psy.errors.UniqueViolation as u:
        logging.error(f"Unique value repeated: {u}")
        print(f"Unique value repeated: {u}")
        conn.rollback()
    except psy.DatabaseError as e:
        logging.error(f"Database error: {e}")
        print(f"Database error: {e}")
        conn.rollback()
    finally:
        cur.close()


def process_discord_message(conn,channel_id:int,session,HEADERS:dict, predefined_responses:dict):
    """_summary_

    Args:
        channel_id (int): _description_
        session (_type_): _description_
        HEADERS (dict): _description_
        predefined_responses (dict): _description_
    """

    recent_message = fetch_recent_message(channel_id,session,HEADERS)

    if recent_message:
        message_content = recent_message.get('content').lower()
        author_id = recent_message['author']['id']

        # Respond if the message matches predefined data
        if message_content in predefined_responses:
            response_message = predefined_responses[message_content]
            post_message_to_discord(channel_id,session,HEADERS, response_message)

        # Collect message data for storage
        cont = recent_message['content']
        ts = recent_message['timestamp']
        msg_id = recent_message['id']
        chan_id = recent_message['channel_id']
        username = recent_message['author']['username']
        globalname = recent_message['author']['global_name']

        attachments = recent_message.get('attachments', [])
        if attachments:
            content_type = attachments[0].get('content_type')
            img_url = attachments[0].get('url')
        else:
            content_type = None
            img_url = None

        # Create a DataFrame for the message
        discord_list = {
            'cont': [cont],
            'ts': [ts],
            'msg_id': [msg_id],
            'chan_id': [chan_id],
            'author_id': [author_id],
            'username': [username],
            'globalname': [globalname],
            'content_type': [content_type],
            'img_url': [img_url]
        }

        df = pd.DataFrame(discord_list)
        logging.info(f"Dataframe created: {df.to_dict()}")
        #print(df.to_string())

        insert_message_to_db(df,conn)


def sync_multiple_channels(conn,channel_ids:int,session,HEADERS:dict, predefined_responses:dict):
    """_summary_

    Args:
        channel_ids (int): _description_
        session (_type_): _description_
        HEADERS (dict): _description_
        predefined_responses (dict): _description_
    """

    while True:
        for channel_id in channel_ids:
            process_discord_message(conn,channel_id,session,HEADERS,predefined_responses)
        time.sleep(2)


if __name__ == '__main__':
    conn = DB_connection()  # Establish the connection once
    if conn:
        sync_multiple_channels(conn, channel_ids, session, HEADERS, predefined_responses)
        conn.close() 
