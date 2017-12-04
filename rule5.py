import requests, re, pandas, bs4
from lxml import html

def get_status(tree):
    status = tree.xpath('//*[@id="stats_current"]/div[1]/ul[1]/li[1]/text()')
    return status

def get_id(url):
    url = str(url)
    return url[-6:]

def get_club(tree):
    club = tree.xpath('//*[@id="stats_team"]/ul/li[2]/a/text()')
    return club

def get_level(tree):
    level = tree.xpath('//*[@id="stats_team"]/ul/li[1]/text()')
    return level

def get_birthdate(tree):
    birthdate = tree.xpath('//*[@id="stats_current"]/div[1]/ul[1]/li[3]/text()')
    return birthdate

def get_position(tree):
    position = tree.xpath('//*[@id="player_position"]/text()')
    return position

def get_name(tree):
    name = tree.xpath('//*[@id="stats_career_wrapper"]/h3/text()')
    return name

def get_height(tree):
    height = tree.xpath('//*[@id="stats_current"]/div[1]/ul[1]/li[5]/text()[2]')
    return height

def get_weight(tree):
    weight = tree.xpath('//*[@id="stats_current"]/div[1]/ul[1]/li[5]/text()[3]')
    return weight

def get_signing_date(soup):
    try:
        last_row = soup('td')[-2]
        last_row = str(last_row)
        last_row = last_row.replace('<td data-col="1">', '')
        last_row = last_row.replace('</td>', '')
    except:
        return None
    return last_row

def get_signing_info(soup):
    try:
        last_row = soup('td')[-1]
        last_row = str(last_row)
        last_row = last_row.replace('<td data-col="2">', '')
        last_row = last_row.replace('</td>', '')
    except:
        return None
    return last_row

def get_num_seasons(player_id):
    url1 = 'http://www.milb.com/lookup/json/named.sport_pitching_composed.bam?game_type=%27R%27&league_list_id=%27mlb_milb%27&sort_by=%27season_asc%27&player_id='
    url2 = '&sport_pitching_composed.season=2017'
    player_id = str(player_id)
    fullurl = url1+player_id+url2
    response = requests.get(fullurl)
    stats = response.json()
    totalSize = int(stats['sport_pitching_composed']['sport_pitching_tm']['queryResults']['totalSize'])
    rownum = 0
    season_list = []
    if totalSize == 0:
        url1 = 'http://www.milb.com/lookup/json/named.sport_hitting_composed.bam?game_type=%27R%27&league_list_id=%27mlb_milb%27&sort_by=%27season_asc%27&player_id='
        url2 = '&sport_hitting_composed.season=2017'
        fullurl = url1+player_id+url2
        response = requests.get(fullurl)
        stats = response.json()
        totalSize = int(stats['sport_hitting_composed']['sport_hitting_tm']['queryResults']['totalSize'])
        if totalSize == 1:
            num_seasons = 1
            return num_seasons
        else:
            for item in range(0, totalSize):
                season = stats['sport_hitting_composed']['sport_hitting_tm']['queryResults']['row'][rownum]['season']
                season_list.append(season)
                rownum = rownum + 1
    elif totalSize == 1:
        num_seasons = 1
        return num_seasons
    else:
        for item in range(0, totalSize):
            season = stats['sport_pitching_composed']['sport_pitching_tm']['queryResults']['row'][rownum]['season']
            season_list.append(season)
            rownum = rownum + 1
    season_list = list(set(season_list))
    num_seasons = len(season_list)
    return num_seasons

def import_urls():
    player_urls = []
    with open("2017_player_links.csv", 'r') as f:
        json_str = f.readlines()
        for line in json_str:
            player_urls.append(line.strip())
    return player_urls

def import_protected():
    player_urls = []
    with open("2017_protected.csv", 'r') as f:
        json_str = f.readlines()
        for line in json_str:
            player_urls.append(line.strip())
    return player_urls

def export_data(data_to_export):
    data_to_export.to_csv('rule5_parsing.csv')

###################
# MAIN PROGRAM
###################
player_urls = import_urls()
all_player_info = []
protected = import_protected()
counter = 0

for item in player_urls:
    counter += 1
    res = requests.get(item)
    tree = html.fromstring(res.content)
    soup = bs4.BeautifulSoup(res.content, 'lxml')

    player_id = get_id(item)
    status = get_status(tree)
    club = get_club(tree)
    level = get_level(tree)
    birthdate = get_birthdate(tree)
    position = get_position(tree)
    name = get_name(tree)
    height = get_height(tree)
    weight = get_weight(tree)
    signing_date = get_signing_date(soup)
    signing_info = get_signing_info(soup)
    num_seasons = get_num_seasons(player_id)
    if str(item)[-6:] in protected:
        protected_status = 1
    else:
        protected_status = 0
    player_info = [player_id, name, status, club, level, birthdate, position, height, weight, signing_date, signing_info, protected_status, num_seasons]
    all_player_info.append(player_info)
    print("Added {}, # {} of {}" .format(str(item)[-6:], counter, len(player_urls)))


df = pandas.DataFrame(all_player_info, columns=['Player_ID', 'Name', 'Status', 'Club', 'Level', 'Birthdate', 'Position', 'Height', 'Weight', 'Signing_Date', 'Signing_Info', 'Protected_Status', 'Num_Seasons'])
print(df.sample(10))
export_data(df)
