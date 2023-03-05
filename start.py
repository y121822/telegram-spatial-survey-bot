import os
import boto3
from time import sleep
from dotenv import load_dotenv

load_dotenv()


def main():
    """Start the bot. In the case of a failure (e.g. caused by a database maintenance or
       webhook issues), the bot at the current AWS EC2 instance will be restarted up
       to 20 times with increasing intervals between the tries. If the number of restarts
       reaches 20, the EC2 instance will be terminated. AWS EC2 Auto Scaling Group will
       automatically launch another instance from the fully configured template and
       the whole cycle will be repeated."""
    count = 21
    while True:
        if os.system(f"python {os.environ['BOT_PATH']}/bot.py"):
            sleep(25-count)
            count -= 1
        if not count:
            boto3.resource('ec2').Instance(os.environ['ID']).terminate()


if __name__ == "__main__":
    main()
