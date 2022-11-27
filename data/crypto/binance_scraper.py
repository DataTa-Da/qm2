from bs4 import BeautifulSoup
import requests
import os
import wget
import zipfile
from tqdm import tqdm
import csv

#url of zip file directory
binance_klines_base_url = 'https://data.binance.vision/data/spot/daily/klines/BTCUSDT/5m/'

#replaces ?prefix= if present in the url provided
if 'prefix' in binance_klines_base_url:
    binance_klines_base_url = binance_klines_base_url.replace('?prefix=','')


#tests if a given year int is a leap year
def is_leap_year(year):
    is_leap = False
    if year % 4 == 0:
        is_leap = True
    if year % 100 == 0:
        is_leap = False
    if year % 400 == 0:
        is_leap = True
    return is_leap

#generates the date of the next day in the forma yyyy-mm-dd from a date of the same format
def next_day(date):
    thirty_one_days = ['01','03','05','07','08','10','12']
    thirty_days = ['04','06','09','11']
    year,month,day = date.split('-')
    if month in thirty_one_days:
        if day == '31':
            if month == '12':
                new_year = str(int(year) + 1)
                return new_year + '-01' + '-01'
            else:
                new_month = str(int(month) + 1)
                if len(new_month) < 2:
                    new_month = '0' + new_month
                return year + '-' + new_month + '-01'
        else:
            new_day = str(int(day) + 1)
            if len(new_day) < 2:
                new_day = '0' + new_day
            return year + '-' + month + '-' + new_day
    elif month in thirty_days:
        if day == '30':
            new_month = str(int(month) + 1)
            if len(new_month) < 2:
                new_month = '0' + new_month
            return  year + '-' + new_month + '-01'
        else:
            new_day = str(int(day) + 1)
            if len(new_day) < 2:
                new_day = '0' + new_day
            return year + '-' + month + '-' + new_day
    else:
        if is_leap_year(int(year)):
            if day == '28':
                return year + '-' + month + '-29'
            if day == '29':
                return year + '-03' + '-01'

        else:
            if day == '28':
                return year + '-03' + '-01'
        new_day = str(int(day) + 1)
        if len(new_day) < 2:
            new_day = '0' + new_day
        return year + '-' + month + '-' + new_day


#generates a list of dates of the form yyyy-mm-dd from a given start date
def get_dates(start_date,number_of_days):
    all_dates=[]
    cur_date = start_date
    for i in range(number_of_days):
        all_dates.append(cur_date)
        cur_date = next_day(cur_date)
    return all_dates


#downloads and extracts the binance kline zip files for each date passed to it
def download_and_extract_zips(dates,base_url):
    url_components = base_url.split('/')
    asset = url_components[-3]
    time_interval = url_components[-2]
    all_csv_rows = []
    for i in tqdm(range(0,len(dates))):
        date=dates[i]
        zip_file_name = asset + '-' + time_interval + '-' + date + '.zip'
        download_url = base_url + zip_file_name
        wget.download(download_url,zip_file_name)
        zip = zipfile.ZipFile('./' + zip_file_name)
        zip.extractall('./')
        zip.close()
        os.remove('./'+zip_file_name)
        csv_file_name = asset + '-' + time_interval + '-' + date + '.csv'
        #opens the newly extract csv to save each row with the date prepended
        with open(csv_file_name, mode='r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                row.insert(0,date)
                all_csv_rows.append(row)
    #produces a csv with all the data in one, sorted by date.
    with open('combined_data.csv','w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerows(all_csv_rows)



temp_path = os.path.join(os.getcwd(),'temp')
if not os.path.exists(temp_path):
    os.mkdir(temp_path)
os.chdir('./temp')
dates = get_dates('2022-01-01',2)
download_and_extract_zips(dates,binance_klines_base_url)
