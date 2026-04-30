"""JSON local file DB Service"""
import os
import json
from models.tournament import Tournament, TournamentResult
from models.error import DatabaseError, DATABASE_ERROR_MESSAGE
from .base_db_service import BaseDBService

KEY_FIELD = "key"
JSON_DIR_PATH = "db_json"

class JSONFileDBService(BaseDBService):
    """JSON File DB Service"""
    def __init__(self) -> None:
        super().__init__()
        os.makedirs(JSON_DIR_PATH, exist_ok=True)

    def __read_json_file_tnr_content(self, key):
        try:
            with open(os.path.join(JSON_DIR_PATH, f'{key}.json'), 'r', encoding='utf-8') as file:
                json_data = json.load(file)
            return json_data
        except Exception as exc:
            raise DatabaseError(DATABASE_ERROR_MESSAGE) from exc

    def __write_json_file_tnr_content(self, key, json_data):
        try:
            with open(os.path.join(JSON_DIR_PATH, f'{key}.json'), 'w', encoding='utf-8') as file:
                json.dump(json_data, file, ensure_ascii=False)
        except Exception as exc:
            raise DatabaseError(DATABASE_ERROR_MESSAGE) from exc

    def insert_tnr_info(self, tnr: Tournament):
        try:
            json_data = tnr.to_dict()
            self.__write_json_file_tnr_content(tnr.key, json_data)
        except Exception as exc:
            raise DatabaseError(DATABASE_ERROR_MESSAGE) from exc

    def add_round_to_tnr(self, tournament_key: str, value: TournamentResult):
        try:
            json_data = self.__read_json_file_tnr_content(tournament_key)
            new_round = {
                "round": value.round,
                "rows": value.rows
            }
            if 'results' in json_data:
                json_data['results'].append(new_round)
            else:
                json_data |= {'results': [new_round]}
            self.__write_json_file_tnr_content(tournament_key, json_data)
        except Exception as exc:
            raise DatabaseError(DATABASE_ERROR_MESSAGE) from exc

    def update_tnr_info(self, tournament_key: str, tnr: Tournament):
        try:
            json_data = self.__read_json_file_tnr_content(tournament_key)
            update_data = tnr.get_update_data_dict()
            json_data |= update_data
            self.__write_json_file_tnr_content(tournament_key, json_data)
        except Exception as exc:
            raise DatabaseError(DATABASE_ERROR_MESSAGE) from exc

    def get_tnr(self, tournament_key: str, rd: int = None) -> Tournament:
        try:
            if os.path.exists(os.path.join(JSON_DIR_PATH, f'{tournament_key}.json')):
                json_data = self.__read_json_file_tnr_content(tournament_key)
                if rd is None:
                    tnr = Tournament.from_dict(json_data)
                else:
                    if 'results' not in json_data:
                        return None
                    result = any(d.get('round') == rd for d in json_data['results'])
                    if result:
                        tnr = Tournament.from_dict(json_data)
                    return None
                return tnr
            return None
        except Exception as exc:
            raise DatabaseError(DATABASE_ERROR_MESSAGE) from exc
