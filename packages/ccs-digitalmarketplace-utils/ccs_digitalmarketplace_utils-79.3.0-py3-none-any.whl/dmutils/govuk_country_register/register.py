
import csv
import json
from io import TextIOWrapper
from os import PathLike
from importlib.resources import files


class CSVRegister:

    __metadata_keys__ = [
        "index-entry-number",
        "entry-number",
        "entry-timestamp",
        "key",
    ]

    def find(self, key):
        """Find a record using the register key"""

        return self.data[key]["item"]

    @classmethod
    def read_csv(cls, csvfile, metadata_keys=None):
        if metadata_keys is None:
            metadata_keys = cls.__metadata_keys__

        for entry in csv.DictReader(csvfile):
            key = entry["key"]
            metadata = {k: v for k, v in entry.items() if k in metadata_keys and v}
            item = {k: v for k, v in entry.items() if k not in metadata_keys and v}
            new_entry = metadata.copy()
            new_entry["item"] = item.copy()
            yield (key, new_entry)

    @classmethod
    def from_csv(cls, csvfile):
        """Create a register object from a CSV file

        :param csvfile:  CSV file path or stream
        :type csvfile: os.PathLike or file object
        """

        if isinstance(csvfile, (str, PathLike)):
            with open(csvfile, newline="", encoding="utf-8") as f:
                data = dict(cls.read_csv(f))
        else:
            data = dict(cls.read_csv(csvfile))

        register = cls.__new__(cls)
        register.data = data

        return register

    @classmethod
    def from_pkg_resource(cls, csvfile, pkg=__name__):
        """Create a register object from a CSV file
        that is included with a package

        :param csvfile str: CSV file name
        :param pkg str: package name (defaults to this package)
        """

        if pkg == __name__:
            pkg = 'dmutils.govuk_country_register'

        f = TextIOWrapper(files(pkg).joinpath(csvfile).open('rb'), encoding="utf-8")
        return cls.from_csv(f)


class JSONRegister:
    def find(self, key):
        """Find a record using the register key"""

        return self.data[key]

    @classmethod
    def read_json(cls, jsonfile):
        for country_name, country_code in json.load(jsonfile):
            yield (country_code, country_name)

    @classmethod
    def from_json(cls, jsonfile):
        """Create a register object from a JSON file

        :param jsonfile:  JSON file path or stream
        :type jsonfile: os.PathLike or file object
        """

        if isinstance(jsonfile, (str, PathLike)):
            with open(jsonfile, newline="", encoding="utf-8") as f:
                data = dict(cls.read_json(f))
        else:
            data = dict(cls.read_json(jsonfile))

        register = cls.__new__(cls)
        register.data = data

        return register

    @classmethod
    def from_pkg_resource(cls, jsonfile, pkg=__name__):
        """Create a register object from a JSON file
        that is included with a package

        :param jsonfile str: JSON file name
        :param pkg str: package name (defaults to this package)
        """

        if pkg == __name__:
            pkg = 'dmutils.govuk_country_register'

        f = TextIOWrapper(files(pkg).joinpath(jsonfile).open('rb'), encoding="utf-8")
        return cls.from_json(f)
