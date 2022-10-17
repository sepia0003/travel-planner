# run docker:osrm-backend first
import requests
import polyline
import folium
import random

class city:
    def __init__(self, lon=None, lat=None):
        self.lon = lon
        self.lat = lat

    def getlon(self):
        return self.lon
    
    def getlat(self):
        return self.lat

    def distanceTo(self, dest): #lon,lat ~ lon,lat
        url = "http://localhost:5000/route/v1/driving/{},{};{},{}?steps=true".format(self.getlon(), self.getlat(), dest.getlon(), dest.getlat())
        response = requests.get(url).json()

        distance = response["routes"][0]["distance"] # unit=M


class points:
    points = []                         # points = [city1(obj), city2(obj), ...]

    def addpoint(self, city):
        self.points.append(city)

    def getpoint(self, index):
        return self.points[index]

    def numofpoints(self):
        return len(self.points)

class tour:
    def __init__(self, points):
        self.points = points
        self.tour = []                  # tour = [visitcity1(obj), visitcity2(obj), ...]
        self.fitness = 0.0
        self.tourdistance = 0

    def __len__(self):
        return len(self.tour)
    
    def __getitem__(self, index):
        return self.tour[index]

    def __setitem__(self, key, value):
        self.tour[key] = value

    def gettourpoint(self, index):
        return self.tour[index]

    def settourpoint(self, key, value):
        self.tour[key] = value
        self.fitness = 0.0
        self.tourdistance = 0

    def toursize(self):
        return len(self.tour)

    def generateTour(self):
        for i in range(0, self.points.numofpoints()):
            self.settourpoint(i, self.points.getpoint(i))
        random.shuffle(self.tour)
    
    def getfitness(self):
        if self.fitness == 0:
            self.fitness = 1/float(self.gettourdistance())
        return self.fitness

    def gettourdistance(self):
        if self.tourdistance == 0:
            alldistance = 0
            for i in range(0, self.toursize()):
                frompoint = self.gettourpoint(i)
                topoint = None
                if i+1 < self.toursize():
                    topoint = self.gettourpoint(i+1)
                else:
                    topoint = self.gettourpoint(0)
                alldistance += frompoint.distanceTo(topoint)
            self.tourdistance = alldistance
        return self.tourdistance

    def thistourcontains(self, city):
        return city in self.tour