import requests
from collections import namedtuple, Counter
from bs4 import BeautifulSoup

OUTPUT_FILE = 'data.csv'
RESULTS_URL = ('http://www.orionsportstiming.com/results/'
               'RunTheRiver10KOverall2016.html')

GROUP_LABELS = ['80-97M', '75-79M', '70-74M', '70-74F', '65-69M', '65-69F',
                '60-64M', '60-64F', '55-59M', '55-59F', '50-54M', '50-54F',
                '45-49M', '45-49F', '40-44M', '40-44F', '35-39M', '35-39F',
                '30-34M', '30-34F', '25-29M', '25-29F', '20-24M', '20-24F',
                '15-19M', '15-19F', '11-14M', '11-14F', '0-10M', '0-10F']

MINUTES_STR_TUPLE_LIST = [(group_label, '{:02d}:{:02d}'.format(hour, minute))
                          for hour in range(2)
                          for minute in range(0, 60, 10)
                          for group_label in GROUP_LABELS]

Entry = namedtuple('Entry', ['place', 'name', 'bib_number', 'age', 'gender',
                             'age_group', 'chip_time', 'gun_time', 'pace'])

def get_html(url):
    response = requests.get(url)
    response.raise_for_status()
    html = response.text

    return html

def reformat_gun_time(gun_time_str):
    updated_gun_time = gun_time_str.rsplit(':', maxsplit=1)[0]
    # Round down to ten minute intervals
    updated_gun_time = '{}0'.format(updated_gun_time[:-1])
    # Add zero hour prefix if time is less than 60 minutes
    if len(updated_gun_time) == 2:
        updated_gun_time = '0:{}'.format(updated_gun_time)
    # Add a leading zero to the chip time
    updated_gun_time = '0{}'.format(updated_gun_time)

    return updated_gun_time

def get_entry_list(html):
    soup = BeautifulSoup(html)
    table = soup.find("table")
    tr_list = table.find_all('tr')[1:]

    row_entry_list = []
    for tr in tr_list:
        td_list = [td.get_text().strip() for td in tr.find_all("td")]

        if td_list[0] == 'Place':
            continue

        td_list[7] = reformat_gun_time(td_list[7])

        row_entry = Entry(*td_list)
        row_entry_list.append(row_entry)

    return row_entry_list

def get_tuple_list(row_entry_list):
    values_dict = Counter(
        [(row.gun_time, '{}{}'.format(row.age_group, row.gender))
         for row in row_entry_list]
    )

    tuples_list = [(label, value, this_time)
                   for (this_time, label), value in values_dict.items()]

    return tuples_list

def write_out_tuple_list(tuple_list):
    with open(OUTPUT_FILE, 'w') as fh:
        fh.write('key,value,date\n')

        for label, time_str in MINUTES_STR_TUPLE_LIST:
            magnitude = 0

            for recorded_label, recorded_number, recorded_time in tuple_list:
                if label == recorded_label and time_str == recorded_time:
                    magnitude = recorded_number

            fh.write('{},{},{}\n'.format(label, magnitude, time_str))

def run():
    html = get_html(RESULTS_URL)
    entry_list = get_entry_list(html)
    tuple_list = get_tuple_list(entry_list)
    write_out_tuple_list(tuple_list)

if __name__ == '__main__':
    run()
