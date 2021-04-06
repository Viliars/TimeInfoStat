import vk_api
from vk_api import VkUpload
import configparser
from collections import Counter, defaultdict
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import re
import click
from pathlib import Path

regex = re.compile("\d+")

config = configparser.ConfigParser()
config.read('example.ini')

def auth_handler():
    key = input("Enter authentication code: ")
    
    remember_device = True
    return key, remember_device

login = config["vk_api"].get("login")
password = config["vk_api"].get("password")

vk_session = vk_api.VkApi(login=login, password=password, api_version="5.130", auth_handler=auth_handler)
vk_session.auth()

vk = vk_session.get_api()

@click.command()
@click.argument('domain', type=str)
@click.argument('output_dir', default="./", type=click.Path(dir_okay=True, exists=True))
def main(domain, output_dir):

    output_dir = Path(output_dir)

    if regex.match(domain):
        flag_nickname = False
        domain = int(domain)
    else:
        flag_nickname = True

    if flag_nickname:
        info = vk.wall.get(domain=domain, count=100)
    else:
        info = vk.wall.get(owner_id=domain, count=100)

    posts = info["items"]
    count = len(posts)

    counter = Counter()
    parts = defaultdict(float)

    for post in posts:
        counter[datetime.fromtimestamp(post["date"]).hour] += 1

    for i in range(0, 24, 3):
        for j in range(i, i+3):
            parts[f"{i}-{i+2}"] += counter[j] / count * 100

    keys = list(parts.keys())
    values = list(parts.values())

    x = np.arange(len(keys))
    width = 0.75

    fig, ax = plt.subplots()
    rects = ax.bar(x, values, width)

    ax.set_ylabel('% постов')
    ax.set_title('Посты по временным отрезкам')
    ax.set_xticks(x)
    ax.set_xticklabels(keys)

    fig.savefig(output_dir / f"{domain}.jpg")


if __name__ == "__main__":
    main()