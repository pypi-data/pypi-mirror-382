"""
Different usefull functions to interact with the database.json file
"""

import os
from datetime import datetime

from pathlib import Path
import lock

from lemmings import __version__ as lemmings_version


class Database:
    """Abstraction to interact with the database"""

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = "./database.json"
        self.db_path = db_path
        self._initialise_db()

    @property
    def _database(self):
        """
        Get the informations from the database.json file.*
        """
        return lock.load_JSON(self.db_path)

    def _dump_database(self, data):
        """
        Dump information to the database.json"""
        lock.save_JSON(self.db_path, data)

    @property
    def latest_chain_name(self):
        """Get the last chain name"""
        db = self._database
        chain_dates = list()
        chain_names = list()
        for chain in db:
            time_ = db[chain][0]["datetime"]
            datetime_obj = datetime.strptime(time_, "%Y-%m-%d %H:%M:%S")
            chain_names.append(chain)
            chain_dates.append(datetime_obj)

        max_time_idx = chain_dates.index(max(chain_dates))
        return chain_names[max_time_idx]

    @property
    def count(self):
        """
        *Get the loop number of a chain*
        """
        return int(len(self._database[self.latest_chain_name]))

    def _initialise_db(self):
        """
        *Create a Database if doesn't exist.*
        """
        if not Path(self.db_path).is_file():
            self._dump_database({})

    def initialise_new_chain(self, chain_name):
        """
        *Create a new chain dict{ } in the DB*
        """
        version = lemmings_version
        database = self._database

        database[chain_name] = [
            {
                "lemmings_version": version,
                "datetime": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                "safe_stop": False,
                "submit_path": "./",
            }
        ]
        self._dump_database(database)

    def initialise_new_loop(self):
        """Create a new loop in a chain"""
        database = self._database
        database[self.latest_chain_name].append(
            {
                "datetime": str(
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ),  # pylint: disable=line-too-long
                "safe_stop": False,
                "submit_path": "./",
            }
        )
        self._dump_database(database)

    def add_farming_list(self):
        """Add a nested level in database
        TODO:
            1) add loop options
            2) use Nob if more nested levels will be present
        """
        database = self._database
        loop_num = self.get_current_loop_val("loop_count")
        database[self.latest_chain_name][loop_num - 1]["parallel_runs"] = []

        self._dump_database(database)

    def update_farming_list(self, key, value):
        """Add a nested level in database
        TODO:
            1) add loop options
            2) use Nob if more nested levels will be present
        """
        database = self._database
        loop_num = self.get_current_loop_val("loop_count")

        nested_key_list = database[self.latest_chain_name][loop_num - 1][
            "parallel_runs"
        ]
        if nested_key_list == []:
            nested_key_list.append({key: value})
        else:
            nested_key_list[0][key] = value

        self._dump_database(database)

    def update_loop(self, key, value, index):
        """
        Update the database of the current folder

        :param index: The loop number of the desired job
        :type index: int
        :param key: The name of the parameter to update or create
        :type key: str
        :param value: The value of the parameter
        :type value: all
        """
        database = self._database
        database[self.latest_chain_name][index - 1][key] = value

        self._dump_database(database)

    def update_current_loop(self, key, value):
        """
        *Update the database of the current folder*

        :param key: The name of the parameter to update or create
        :type key: str
        :param value: The value of the parameter
        :type value: all
        """
        self.update_loop(key, value, self.count)

    def update_previous_loop(self, key, value):
        """
        *Update the database of the current folder*

        :param key: The name of the parameter to update or create
        :type key: str
        :param value: The value of the parameter
        :type value: all
        """
        self.update_loop(key, value, self.count - 1)

    def update_first_loop(self, key, value):
        """
        *Update the database of the current folder*

        :param key: The name of the parameter to update or create
        :type key: str
        :param value: The value of the parameter
        :type value: all
        """
        self.update_loop(key, value, 1)

    def get_loop_val(self, key, index):
        """
        *Get the value of a parameter in a loop of a job.*

        index here is not the python reference, but the loop ID

        :param key: The name of the parameter to update or create
        :type key: str
        """
        database = self._database

        db_path = os.path.abspath(self.db_path)
        loop_db = database[self.latest_chain_name][index - 1]
        try:
            out = loop_db[key]
        except KeyError as e:
            msg = f"Key not found for key {key} and loop ID {index} , or list index {index-1}"
            msg += f"\n in database {db_path}"
            msg += f"\n whose content is {loop_db}"

            raise KeyError(msg)

        return out

    def get_current_loop_val(self, key):
        """
        *Get the value of a parameter in a loop of a job.*

        :param key: The name of the parameter to update or create
        :type key: str
        """
        return self.get_loop_val(key, self.count)

    def get_first_loop_val(self, key):
        """
        *Get the value of a parameter in a loop of a job.*

        :param key: The name of the parameter to update or create
        :type key: str
        """
        return self.get_loop_val(key, 1)

    def get_previous_loop_val(self, key):
        """
        *Get the value of a parameter in a loop of a job.*

        :param key: The name of the parameter to update or create
        :type key: str
        """

        return self.get_loop_val(key, self.count - 1)

    def get_chain_names(self):
        """
        *Get chain names from the database*
        """
        return list(self._database.keys())
