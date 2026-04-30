"""Tournament utilities"""
import re
from typing import List
from models.tournament import TnrSearchOutput, Tournament
from models.error import TournamentNotHaveInfoError
from api_urls import BASE_API_URL
from . import decode_html_entities

def get_tnr(html_content: str) -> List[TnrSearchOutput]:
    """Get tournament list from html search"""
    index = html_content.find('<table class="CRs2"')
    if index != -1:
        search_content = html_content[index:]
        end_index = search_content.find('</table>')
        search_content = search_content[:end_index]
        urls = re.finditer('<a href', search_content)
        tnr_arr = []
        for url in urls:
            start_tnr_idx = url.start()
            end_tnr_idx = start_tnr_idx
            while search_content[end_tnr_idx] != '>':
                end_tnr_idx += 1
            url_tag = search_content[start_tnr_idx:end_tnr_idx + 1]
            tnr = url_tag.split('"')[1]
            end_tnr_name_idx = end_tnr_idx
            while (search_content[end_tnr_name_idx] != '<'
                   or search_content[end_tnr_name_idx + 1] != '/'
                   or search_content[end_tnr_name_idx + 2] != 'a'
                   or search_content[end_tnr_name_idx + 3] != '>'):
                end_tnr_name_idx += 1
            tnr_name = search_content[end_tnr_idx + 1:end_tnr_name_idx]
            tnr_arr.append({
                "url": tnr,
                "name": tnr_name
            })
        return tnr_arr
    return []

def get_tnr_info(html_content: str,
                 prev_phrase_str: str,
                 prev_end_phrase_str: str,
                 info_start_str: str,
                 info_end_str: str,
                 find_direction = "asc"):
    """Get tournament info from html"""
    index = html_content.find(prev_phrase_str)
    if index != -1:
        content = html_content[index + len(prev_phrase_str):]
        if prev_end_phrase_str is not None:
            end_index = content.find(prev_end_phrase_str)
            content = content[:end_index]
        if find_direction == "asc":
            selected_start_index = content.find(info_start_str)
            selected_end_index = content.find(info_end_str)
        else:
            selected_start_index = content.rfind(info_start_str)
            selected_end_index = content.rfind(info_end_str)
        info = content[selected_start_index + len(info_start_str) : selected_end_index]
        return info
    return None

def get_tnr_name(html_content: str):
    """Get tournament name from html"""
    prev_phrase_str = '<table'
    info_start_str = '<h2>'
    info_end_str = '</h2>'
    tnr_name = get_tnr_info(html_content, prev_phrase_str, None, info_start_str, info_end_str)
    tnr_name = decode_html_entities(tnr_name)
    return tnr_name

def get_tnr_group(html_content: str):
    """Get tournament froup name from html"""
    prev_phrase_str = '<td class="CRnowrap b">Tournament selection</td>'
    info_start_str = '<b>'
    info_end_str = '</b>'
    group_name = get_tnr_info(html_content, prev_phrase_str, None, info_start_str, info_end_str)
    if group_name is not None:
        group_name = group_name.split(':')[-1].strip()
        return group_name
    else:
        return ""

def get_tnr_round(html_content: str):
    """Get tournament total rounds from html"""
    prev_phrase_str = '<td class="CR">Number of rounds</td>'
    info_start_str = '<td class="CR">'
    info_end_str = '</td>'
    tnr_round = get_tnr_info(html_content, prev_phrase_str, None, info_start_str, info_end_str)
    return tnr_round

def get_tnr_current_max_round(html_content: str):
    """Get tournament current max round from html"""
    prev_phrase_str = '<td class="CRnowrap b">Ranking list after</td>'
    prev_end_phrase_str = "</tr>"
    info_start_str = 'Rd.'
    info_end_str = '</a>'
    tnr_current_max_round = get_tnr_info(html_content,
                                         prev_phrase_str,
                                         prev_end_phrase_str,
                                         info_start_str,
                                         info_end_str,
                                         find_direction="desc")
    return tnr_current_max_round

def get_chess_results_tournament_info_from_html(key, html_content: str) -> Tournament:
    """Get tournament full info from html"""
    try:
        tnr_name = get_tnr_name(html_content)
        group_name = get_tnr_group(html_content)
        max_round = get_tnr_round(html_content)
        current_max_round = get_tnr_current_max_round(html_content)
        url = get_chess_results_homepage_link(key)
        if (max_round is not None and current_max_round is not None):
            is_final = int(max_round) == int(current_max_round)
        else:
            is_final = False
        tnr = Tournament(key,
                         url,
                         tnr_name,
                         group_name,
                         is_final,
                         current_max_round,
                         max_round, None)
        return tnr
    except Exception as exc:
        raise TournamentNotHaveInfoError() from exc

def get_tnr_key(api_url: str):
    """Get tournament key from url"""
    tnr_start_idx = api_url.find('tnr') + 3
    tnr_end_idx = api_url.find('.aspx')
    return api_url[tnr_start_idx:tnr_end_idx]

def get_chess_result_link_from_key_and_round(key: str, rd: int):
    """Get chessresults link from key and round"""
    url = f'{BASE_API_URL}/tnr{key}.aspx?lan=1&art=1&rd={rd}&turdet=YES'
    return url

def check_chess_results_link(value: str):
    """Check is chessresults link"""
    return (value.startswith('http://') or value.startswith('https://')) and 'chess-results' in value

def get_chess_results_excel_link(key: str, rd: int = None):
    """Get chess results excel link"""
    url = f'{BASE_API_URL}/tnr{key}.aspx?lan=1&art=1&zeilen=0&prt=4&excel=2010&'
    if rd is None:
        url += "rd=9"
    else:
        url += f"rd={rd}"
    return url

def get_chess_results_homepage_link(key: str):
    """Get chess results homepage link"""
    url = f'{BASE_API_URL}/tnr{key}.aspx?lan=1&turder=YES'
    return url
