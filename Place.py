class Place:

    def __init__(self, name, lat, lon):
        self.name = name
        self.lat = lat
        self.lon = lon

    def __eq__(self, other):
        return self.name == other.name and round(self.lat, 6) == round(other.lat, 6) and \
            round(self.lon, 6) == round(other.lon, 6)
