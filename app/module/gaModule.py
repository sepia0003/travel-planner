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

    def __setitem__(self, key, value):
        self.tour[key] = value
    
    def __getitem__(self, index):
        return self.tour[index]

    def gettourpoint(self, index):
        return self.tour[index]

    def settourpoint(self, key, value):
        self.tour[key] = value
        self.fitness = 0.0
        self.tourdistance = 0

    def toursize(self):
        return len(self.tour)

    def generatetour(self):
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


class pooloftours:
    def __init__(self, points, poolsize, init):
        self.tours = []
        for i in range(poolsize):
            self.tours.append(None)
        
        if init:
            for i in range(poolsize):
                newtour = tour(points)
                newtour.generatetour()
                self.savetour(i, newtour)
        
    def __setitem__(self, key, value):
        self.tours[key] = value

    def __getitem__(self, index):
        return self.tours[index]
    
    def savetour(self, index, tour):
        self.tours[index] = tour

    def gettour(self, index):
        return self.tours[index]

    def getmostfit(self):
        mostfit = self.tours[0]
        
        for i in range(self.poolsize):
            if mostfit.getfitness() <= self.gettour(i).getfitness():
                mostfit = self.gettour(i)

        return mostfit

    def poolsize(self):
        return len(self.tours)


class ga:
    def __init__(self, points, mutationrate=0.05, parentcandsize=5, elitism=True):
        self.points = points
        self.mutationrate = mutationrate
        self.parentcandsize = parentcandsize
        self.elitism = elitism

    def evolve(self, oldpool):
        newpool = pooloftours(self.points, oldpool.poolsize(), False)
        elitismoffset = 0
        if self.elitism:
            newpool.savetour(0, oldpool.getmostfit())
            elitismoffset = 1

        for i in range(elitismoffset, newpool.poolsize()):
            parent1 = self.candselect(oldpool)
            parent2 = self.candselect(oldpool)
            child = self.crossover(parent1, parent2)
            newpool.savetour(i, child)

        for i in range(elitismoffset, newpool.poolsize()):
            self.mutate(newpool.gettour(i))
        
        return newpool

    def crossover(self, parent1, parent2):
        child = tour(self.points)

        patchstart = int(random.random() * parent1.toursize())
        patchend = int(random.random() * parent1.toursize())

        for i in range(0, child.toursize()):
            if patchstart < patchend and patchstart < i and i < patchend:
                child.settourpoint(i, parent1.gettourpoint(i))
            elif patchstart > patchend:
                if not (i < patchstart and i > patchend):
                    child.settourpoint(i, parent1.gettourpoint(i))

        for i in range(0, parent2.toursize()):
            if not child.thistourcontains(parent2.gettourpoint(i)):
                for j in range(0, child.toursize()):
                    if child.gettourpoint(j) == None:
                        child.settourpoint(j, parent2.gettourpoint(i))
                        break
        
        return child

    def mutate(self, tour):
        for touridx1 in range(0, tour.toursize()):
            if random.random() < self.mutationrate:
                touridx2 = int(tour.toursize() * random.random())

                point1 = tour.gettourpoint(touridx1)
                point2 = tour.gettourpoint(touridx2)

                tour.settourpoint(touridx2, point1)
                tour.settourpoint(touridx1, point2)

    def candselect(self, pool):
        newpool = pool(self.points, self.parentcandsize, False)
        for i in range(0, self.parentcandsize):
            randomid = int(random.random() * pool.poolsize())
            newpool.savetour(i, pool.gettour(randomid))
        mostfit = newpool.getmostfit()
        return mostfit



