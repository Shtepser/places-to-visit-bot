import re


class Place:

    def __init__(self, name, lat, lon):
        self.name = name
        self.lat = lat
        self.lon = lon

    def __repr__(self):
        lat, lon = round(self.lat, 6), round(self.lon, 6)
        name = re.sub(r'_+', '_', self.name)
        return f"Place:Name:{name}__Lat:{lat}__Lon:{lon}"

    @staticmethod
    def from_string(string):
        name, lat, lon = string.lstrip("Place:").split("__")
        name, lat, lon = name.lstrip("Name:"), float(lat.lstrip("Lat:")), float(lon.lstrip("Lon:"))
        return Place(name, lat, lon)

    def __eq__(self, other):
        return self.name == other.name and round(self.lat, 6) == round(other.lat, 6) and \
            round(self.lon, 6) == round(other.lon, 6)
