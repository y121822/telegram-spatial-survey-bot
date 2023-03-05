import os
from dotenv import load_dotenv
import psycopg2
from engine.utils.utils import credentials

# Set environment variables
load_dotenv(os.path.join(os.path.abspath(__file__ + 3 * '/..'), '.env'))


class Tables:
    """Postgis extension and tables creation"""

    # Get the database string from the environment variable, convert it into the proper format
    cred = credentials(os.environ['DATABASE_URL'])

    # Database connection
    connection = psycopg2.connect(database=cred['NAME'], user=cred['USER'], password=cred['PASSWORD'],
                                  host=cred['HOST'], port=cred['PORT'])
    cursor = connection.cursor()

    def __init__(self, db=''):
        self.db = db

    def create(self):
        self.cursor.execute(f"create extension if not exists postgis")
        self.cursor.execute(f"create table if not exists {self.db}user_state (user_id bigint PRIMARY KEY, "
                            f"user_name text, user_state int, survey varchar(25))")
        self.cursor.execute(f"create table if not exists {self.db}features (id serial PRIMARY KEY, user_id bigint, "
                            f"user_name text, survey varchar(25), entr_time timestamp, photo text, video text, "
                            f"point geometry(POINT, 4326), polygon geometry(POLYGON, 4326), poly_points text, "
                            f"q_count int, ans_check int)")
        self.cursor.execute(f"create table if not exists {self.db}questions (id serial PRIMARY KEY, "
                            f"survey varchar(25), author bigint, question varchar(50))")
        self.cursor.execute(f"create table if not exists {self.db}answers (id serial PRIMARY KEY, f_id int, "
                            f"q_id int, answer varchar(255))")
        self.connection.commit()

    def drop(self):
        self.cursor.execute(f"drop table if exists {self.db}user_state")
        self.cursor.execute(f"drop table if exists {self.db}features")
        self.cursor.execute(f"drop table if exists {self.db}questions")
        self.cursor.execute(f"drop table if exists {self.db}answers")
        self.connection.commit()
