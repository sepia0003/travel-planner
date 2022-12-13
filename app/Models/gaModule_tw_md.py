# run docker:osrm-backend first
import requests
import polyline
import folium
import random

class Node:
    def __init__(self, lon=None, lat=None, util=None, stay=None, open=None ,close=None): # open, close should be in min
        self.lon = lon
        self.lat = lat
        self.util = util
        self.stay = stay
        self.open = open
        self.close = close

    def getlon(self):
        return self.lon
    
    def getlat(self):
        return self.lat

    def getutil(self):
        return self.util

    def getstay(self):
        return self.stay

    def getopen(self):
        return self.open

    def getclose(self):
        return self.close

    def distanceTo(self, dest): #lon,lat ~ lon,lat, we use manhattan distance for brief test.
        distance = 0            #unit = °, we don't use min'sec" only degree.
        distance += abs(self.getlon() - dest.getlon())
        distance += abs(self.getlat() - dest.getlat())
        return distance

    def timeTo(self, dest):
        walkspeed = 0.00070125  #unit = °/min = 0.002805°/4min (walkspeed of a normal person)
        distance = self.distanceTo(dest)
        time = distance / walkspeed 
        return time


class NodeStorage:
    storage = []                         # storage = [node1(obj), node2(obj), ...]

    def addnode(self, node):
        self.storage.append(node)

    def getnode(self, index):
        return self.storage[index]

    def storagesize(self):
        return len(self.storage)


class Tour:
    def __init__(self, nodestorage):
        self.nodestorage = nodestorage
        self.tour = []                  # tour = [visitnode1(obj), visitnode2(obj), ...]
        self.fitness = 0.0              # fitness would be value which indicates how well "the tour" fits
        self.tourdistance = 0
        for i in range(0, self.nodestorage.storagesize()):
            self.tour.append(None)

    def __len__(self):
        return len(self.tour)

    def __setitem__(self, key, value):
        self.tour[key] = value
    
    def __getitem__(self, index):
        return self.tour[index]

    def getnode(self, index):
        return self.tour[index]

    def setnode(self, key, value):
        self.tour[key] = value
        self.fitness = 0.0
        self.tourdistance = 0

    def toursize(self):
        return len(self.tour)

    def generatetour(self):
        for i in range(0, self.nodestorage.storagesize()):
            self.setnode(i, self.nodestorage.getnode(i))
        random.shuffle(self.tour)
    
    def getfitness(self):
        if self.fitness == 0:
            self.fitness = 1/float(self.gettourdistance())
        return self.fitness

    def gettourdistance(self):
        if self.tourdistance == 0:
            alldistance = 0
            for i in range(0, self.toursize()):
                frompoint = self.getnode(i)
                topoint = None
                if i+1 < self.toursize():
                    topoint = self.getnode(i+1)
                else:
                    topoint = self.getnode(0)
                alldistance += frompoint.distanceTo(topoint)
            self.tourdistance = alldistance
        return self.tourdistance

    def containing(self, node):
        return node in self.tour


class Population:
    def __init__(self, nodestorage, populationsize, init):
        self.tours = []
        for i in range(0, populationsize):
            self.tours.append(None)
        
        if init:
            for i in range(0, populationsize):
                newtour = Tour(nodestorage)
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
        
        for i in range(self.populationsize()):
            if mostfit.getfitness() <= self.gettour(i).getfitness():
                mostfit = self.gettour(i)

        return mostfit

    def populationsize(self):
        return len(self.tours)


class GeneticAlgo:
    def __init__(self, nodestorage, mutationrate=0.05, parentcandsize=5, elitism=True):
        self.nodestorage = nodestorage
        self.mutationrate = mutationrate
        self.parentcandsize = parentcandsize
        self.elitism = elitism

    def evolvepopulation(self, oldpopulation):
        newpopulation = Population(self.nodestorage, oldpopulation.populationsize(), False)

        elitismoffset = 0
        if self.elitism:
            newpopulation.savetour(0, oldpopulation.getmostfit())
            elitismoffset = 1

        for i in range(elitismoffset, newpopulation.populationsize()):
            parent1 = self.selectmostfittour(oldpopulation)
            parent2 = self.selectmostfittour(oldpopulation)
            child = self.crossover(parent1, parent2)
            newpopulation.savetour(i, child)

        for i in range(elitismoffset, newpopulation.populationsize()):
            self.mutate(newpopulation.gettour(i))
        
        return newpopulation

    def crossover(self, parent1, parent2):      # parent1, parent2, child are all "tour"s
        child = Tour(self.nodestorage)

        patchstart = int(random.random() * parent1.toursize())
        patchend = int(random.random() * parent1.toursize())

        for i in range(0, child.toursize()):    # randomly select patchstart, patchend, and mix tour timelines on that basis
            if patchstart < patchend and patchstart < i and i < patchend:
                child.setnode(i, parent1.getnode(i))
            elif patchstart > patchend:
                if not (i < patchstart and i > patchend):
                    child.setnode(i, parent1.getnode(i))

        for i in range(0, parent2.toursize()):
            if not child.containing(parent2.getnode(i)):
                for j in range(0, child.toursize()):
                    if child.getnode(j) == None:
                        child.setnode(j, parent2.getnode(i))
                        break
        
        return child

    def mutate(self, tour):
        for touridx1 in range(0, tour.toursize()):
            if random.random() < self.mutationrate:     # with a little probablility, exchange nodes in the tour
                touridx2 = int(tour.toursize() * random.random())

                node1 = tour.getnode(touridx1)
                node2 = tour.getnode(touridx2)

                tour.setnode(touridx2, node1)
                tour.setnode(touridx1, node2)

    def selectmostfittour(self, somepopulation):
        temppopulation = Population(self.nodestorage, self.parentcandsize, False)

        for i in range(0, self.parentcandsize):         # randomly select 5 parentcand on previous population, and regard them as temppopulation, and get mostfit parent on it.
            randpopidx = int(random.random() * somepopulation.populationsize())
            temppopulation.savetour(i, somepopulation.gettour(randpopidx)) # temppopulation can be like [tour5, tour5, tour2, tour1, tour8]

        mostfittour = temppopulation.getmostfit()
        return mostfittour



if __name__ == '__main__':
    n_nodes = 10
    populationsize = 50
    n_generation = 100

    nodestorage = NodeStorage()

    # listing nodes
    nodestorage.addnode(Node(lon=139.741424, lat=35.699721)) # TUS
    nodestorage.addnode(Node(lon=139.728871, lat=35.661302)) # mori tower
    nodestorage.addnode(Node(lon=139.714924, lat=35.643925)) # ebisu
    nodestorage.addnode(Node(lon=139.701975, lat=35.682837)) # yoyogi
    nodestorage.addnode(Node(lon=139.719525, lat=35.680659)) # shinanomachi
    nodestorage.addnode(Node(lon=139.666109, lat=35.705378)) # nakano
    nodestorage.addnode(Node(lon=139.668144, lat=35.661516)) # shimokitazawa
    nodestorage.addnode(Node(lon=139.686511, lat=35.680789)) # gatsudai
    nodestorage.addnode(Node(lon=139.579722, lat=35.702351)) # kichijoji
    nodestorage.addnode(Node(lon=139.736571, lat=35.628930)) # shinagawa
    
    population = Population(nodestorage, populationsize=populationsize, init=True)
    geneticalgo = GeneticAlgo(nodestorage)

    # evolve
    for i in range(n_generation):
        population = geneticalgo.evolvepopulation(population)

    result = population.getmostfit().tour # result = [node, node, node, node, ...]

    # make map with this result
    lonlist = []
    latlist = []
    latlonlist = []
    for i in result:
        lonlist.append(i.getlon())
        latlist.append(i.getlat())
        latlonlist.append((i.getlat(), i.getlon()))

    map = folium.Map(location=[sum(latlist)/10, sum(lonlist)/10], zoom_start=13)

    for i in range(n_nodes):
        if i != n_nodes-1:
            url = "http://localhost:5000/route/v1/driving/{},{};{},{}".format(lonlist[i], latlist[i], lonlist[i+1], latlist[i+1])
            response = requests.get(url).json()
            geometry = response["routes"][0]["geometry"]
            route = polyline.decode(geometry)
            folium.PolyLine(route, weight=8, color='blue', opacity=0.6).add_to(map)
        else:
            url = "http://localhost:5000/route/v1/driving/{},{};{},{}".format(lonlist[i], latlist[i], lonlist[0], latlist[0])
            response = requests.get(url).json()
            geometry = response["routes"][0]["geometry"]
            route = polyline.decode(geometry)
            folium.PolyLine(route, weight=8, color='red', opacity=0.6).add_to(map)
    
    for i in range(n_nodes):
        folium.Marker(location=latlonlist[i], icon=folium.Icon(icon='play', color='green')).add_to(map)

    

    map.save('gamap2.html')




    # 1. 거리일정하게 유지한뒤 time window에 안맞는 루트 삭제
    # 2. 거리를 풀어준뒤 time window에 안맞으면 패널티 부과해서 유전알고리즘
    # 3. 거리와 시간 둘다 유전알고리즘 적용