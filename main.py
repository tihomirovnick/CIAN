import time

from fake_useragent import UserAgent
import requests
from bs4 import BeautifulSoup
import re
import sqlite3

ua = UserAgent()


def collect_id(regions_arr):
    region_id = 0
    while region_id < 85:
        page_count = 1
        while region_id < 85:
            a = []
            response = requests.get(
                url=f'https://api.cian.ru/agent-catalog-search/v1/get-realtors/?regionId={regions_arr[region_id]}&page={page_count}&limit=10',
                headers={'user-agent': f'{ua.random}'}
            )

            try:
                data = response.json()
            except Exception as e:
                while Exception == e:
                    data = response.json()

            i = 0

            try:
                while i != 10:
                    a.append(data['items'][i]['cianUserId'])
                    i += 1

                for idx in range(int(len(a))):
                    collect_number(a[idx], region_id)
                    idx += 1
                page_count += 1

            except:
                for idx in range(int(len(a))):
                    collect_number(a[idx], region_id)
                    idx += 1
                page_count += 1
                region_id += 1
                break

    print('Script worked successfully...')
    return 0


def collect_number(id, region_id):
    try:
        response = requests.get(f'https://www.cian.ru/agents/{str(id)}/', headers={'user-agent': f'{ua.random}'})
        if str(response) == '<Response [200]>':
            pass
        else:
            return 0

        html_doc = response.text
        soup = BeautifulSoup(html_doc, 'lxml')

        scripts = soup.find_all("script", type="text/javascript")

        region = get_region_name(region_id)
        companies = re.findall(r'[\'\"]name[\'\"]\s*\:\s*[\'\"]([^\'\"]*)[\'\"],[\'\"]regionsNames[\'\"]', str(scripts),
                               flags=re.I)
        name = companies[0]

        companies = re.findall(r'[\'\"]number[\'\"]\s*\:\s*[\'\"]([^\'\"]*)[\'\"]', str(scripts), flags=re.I)
        try:
            phone = f"+7{companies[1]}"
        except:
            try:
                phone = f"+7{companies[0]}"
            except:
                phone = ''

        companies = re.findall(r'[\'\"]contactEmail[\'\"]\s*\:\s*[\'\"]([^\'\"]*)[\'\"]', str(scripts), flags=re.I)
        try:
            email = companies[0]
        except:
            email = ''

        try:
            print(id, region, name, phone, email)
            cursor.execute("INSERT INTO users (id, region, name, phone, email) VALUES (?, ?, ?, ?, ?)",
                           (id, region, name, phone, email))
            sqlite_connection.commit()

        except sqlite3.IntegrityError:
            pass
    except:
        time.sleep(10)
        response = requests.get(f'https://www.cian.ru/agents/{str(id)}/', headers={'user-agent': f'{ua.random}'})
        html_doc = response.text
        soup = BeautifulSoup(html_doc, 'lxml')

        scripts = soup.find_all("script", type="text/javascript")

        region = get_region_name(region_id)
        companies = re.findall(r'[\'\"]name[\'\"]\s*\:\s*[\'\"]([^\'\"]*)[\'\"],[\'\"]regionsNames[\'\"]', str(scripts),
                               flags=re.I)
        name = companies[0]

        companies = re.findall(r'[\'\"]number[\'\"]\s*\:\s*[\'\"]([^\'\"]*)[\'\"]', str(scripts), flags=re.I)
        try:
            phone = f"+7{companies[1]}"
        except:
            try:
                phone = f"+7{companies[0]}"
            except:
                phone = ''

        companies = re.findall(r'[\'\"]contactEmail[\'\"]\s*\:\s*[\'\"]([^\'\"]*)[\'\"]', str(scripts), flags=re.I)
        try:
            email = companies[0]
        except:
            email = ''

        try:
            print(id, region, name, phone, email)
            cursor.execute("INSERT INTO users (id, region, name, phone, email) VALUES (?, ?, ?, ?, ?)",
                           (id, region, name, phone, email))
            sqlite_connection.commit()

        except sqlite3.IntegrityError:
            pass


def get_regions():
    url = "https://api.cian.ru/geo-temp-layer/v1/get-federal-subjects-of-russia/"
    response = requests.get(url=url, headers={'user-agent': f'{ua.random}'})
    regions = response.json()
    regions_arr = []
    for i in range(85):
        regions_arr.append(regions['items'][i]['id'])
    collect_id(regions_arr)


def get_region_name(region_id):
    url = "https://api.cian.ru/geo-temp-layer/v1/get-federal-subjects-of-russia/"
    response = requests.get(url=url, headers={'user-agent': f'{ua.random}'})
    regions = response.json()
    regions_arr = []
    for i in range(85):
        regions_arr.append(regions['items'][i]['name'])
    return regions_arr[region_id]


def main():
    global cursor, sqlite_connection
    sqlite_connection = sqlite3.connect('rieltors.db')
    cursor = sqlite_connection.cursor()
    if sqlite_connection:
        print("DataBase connected")
    sqlite_connection.execute(
        'CREATE TABLE IF NOT EXISTS users(id TEXT, region TEXT, name TEXT, phone PRIMARY KEY, email TEXT)')
    sqlite_connection.commit()

    get_regions()


if __name__ == '__main__':
    main()
