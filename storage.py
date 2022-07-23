import csv

from os.path import exists as file_exists

class Store:
    storage = []
    storage_lookup = {}

    def __init__(self, filename):
        self.filename = "output/" + filename

        if not file_exists(self.filename):
            f = open(self.filename, "x")
            f.close()

        data = []
        with open(self.filename, "r", encoding="UTF8") as f:
            reader = csv.reader(f, delimiter=";")
            data = []
            for row in reader:
                if row:
                    data.append(tuple(row))

        self.storage = data

        for entry in data:
            self.storage_lookup[entry[0]] = True

    def save(self, key, *args):
        row = [key] + list(args)

        with open(self.filename, "a", newline="", encoding="UTF8") as f:
            writer = csv.writer(
                f,
                quoting=csv.QUOTE_NONE,
                quotechar="'",
                delimiter=";",
                escapechar="\\")
            writer.writerow(row)

        self.storage.append(row)
        self.storage_lookup[key] = True

    def get_all(self):
        return self.storage

    def exists(self, key):
        return key in self.storage_lookup
