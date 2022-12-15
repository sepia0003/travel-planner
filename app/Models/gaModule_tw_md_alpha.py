# run docker:osrm-backend first
import requests
import polyline
import folium
import random

class Node:
    def __init__(self, lon=None, lat=None, util=None, stay=None, open=None ,close=None): # stay, open, close should be in min
        self.lon = lon
        self.lat = lat
        self.util = util
        self.stay = stay
        self.open = open
        self.close = close
        self.alpha = 1

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

    def getalpha(self):
        return self.alpha

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

    def delnode(self, value):
        self.storage.remove(value)      #remove는 리스트의 인덱스로 찾아서 지우는게 아니라 리스트의 밸류로 찾아서 지우는것이다.

    def storagesize(self):
        return len(self.storage)


class Tour:
    def __init__(self, nodestorage, portion): #false가 평소에 쓰는것 , 특별히 true일때는 초기화할때나 특별한경우
        self.nodestorage = nodestorage
        self.tour = []                  # tour = [visitnode1(obj), visitnode2(obj), ...]
        self.fitness = 0.0              # fitness would be value which indicates how well "the tour" fits
        self.tourutil = 0
        self.tourtwmiss = 0
        self.tourdistance = 0
        self.portion = portion
        if not self.portion:
            for i in range(0, self.nodestorage.storagesize()):          #ns:Tour에서는 처음에 객체생성시 인수로받아온nodestorage안의 노드개수만큼공간만들고 시작
                self.tour.append(None)

    # def __len__(self):                  # len()함수
    #     return len(self.tour)

    # def __setitem__(self, key, value):  # tour[key] = value 메소드
    #     self.tour[key] = value
    
    # def __getitem__(self, index):       # tour[key] 호출 메소드
    #     return self.tour[index]         # __~~__ 같은 매직메소드는 get,set,del,len(겟셋끼들은)이 있다. 하지만 리스트 조작이랑 헷갈려서 굳이 안쓰기로 결정  
                                          # 참고로 index는 key의 일종이다.

    def getnode(self, index):
        return self.tour[index]

    def setnode(self, index, value):
        self.tour[index] = value
        self.fitness = 0.0
        self.tourutil = 0
        self.tourtwmiss = 0
        self.tourdistance = 0

    def delnode(self, value):
        self.tour.remove(value)
        self.fitness = 0.0
        self.tourutil = 0
        self.tourtwmiss = 0
        self.tourdistance = 0

    def toursize(self):
        return len(self.tour)

    def inittour(self):
        for i in range(0, self.nodestorage.storagesize()):      #ns:해당객체에 저장된 ns의 사이즈만큼의 투어를 만드는역할
            self.setnode(i, self.nodestorage.getnode(i))
        random.shuffle(self.tour)
    
    def getfitness(self):                                     
        if self.fitness == 0:
            self.fitness = self.gettourutil() - self.gettourtwmiss() - self.gettourdistance()         # the evaluation function of the problem
        return self.fitness

    def gettourutil(self):
        if self.tourutil == 0:
            allutil = 0
            currenttime = self.getnode(0).getopen()
            for i in range(0, self.toursize()):
                frompoint = self.getnode(i)
                topoint = None
                if i+1 < self.toursize():
                    topoint = self.getnode(i+1)
                else:
                    topoint = self.getnode(0)
                if frompoint.getopen() <= currenttime <= frompoint.getclose():
                    allutil += frompoint.getutil()
                    currenttime += frompoint.getstay()
                    currenttime += frompoint.timeTo(topoint)
                else:
                    currenttime += frompoint.timeTo(topoint)
            if self.getnode(0).getopen() <= currenttime <= self.getnode(0).getclose() and not self.portion:
                allutil += self.getnode(0).getutil()
            else:
                pass
            self.tourutil = allutil
        return self.tourutil

    def gettourtwmiss(self):
        if self.tourtwmiss == 0:
            alltwmiss = 0
            currenttime = self.getnode(0).getopen() #min
            for i in range(0, self.toursize()):
                frompoint = self.getnode(i)
                topoint = None
                if i+1 < self.toursize():
                    topoint = self.getnode(i+1)
                else:
                    topoint = self.getnode(0)
                if frompoint.getopen() <= currenttime <= frompoint.getclose():
                    currenttime += frompoint.getstay()
                    currenttime += frompoint.timeTo(topoint)
                else:
                    alltwmiss += frompoint.getalpha() * min(abs(currenttime - frompoint.getopen()), abs(currenttime - frompoint.getclose()))
                    currenttime += frompoint.timeTo(topoint)
            if self.getnode(0).getopen() <= currenttime <= self.getnode(0).getclose():
                pass
            elif not self.portion:
                alltwmiss += self.getnode(0).getalpha() * min(abs(currenttime - self.getnode(0).getopen()), abs(currenttime - self.getnode(0).getclose()))
            self.tourtwmiss = alltwmiss    
        return self.tourtwmiss

    def gettourdistance(self):
        if self.tourdistance == 0:
            alldistance = 0
            for i in range(0, self.toursize()):
                frompoint = self.getnode(i)
                topoint = None
                if i+1 < self.toursize():
                    topoint = self.getnode(i+1)
                else:
                    topoint = self.getnode(0)                   # in this project, we regard a route as a closed route. we come back to start point.
                alldistance += frompoint.distanceTo(topoint)
            if self.portion:
                alldistance -= frompoint.distanceTo(topoint)
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
                newtour = Tour(nodestorage, False)             #ns:population에서는 단순히 맨처음population일때 해당pop으로서 쓰일 랜덤순서의투어들을 만드는역할 
                newtour.inittour()
                self.settour(i, newtour)
        
    # def __setitem__(self, key, value):
    #     self.tours[key] = value

    # def __getitem__(self, index):
    #     return self.tours[index]
    
    def gettour(self, index):
        return self.tours[index]

    def settour(self, index, tour):
        self.tours[index] = tour

    def getmostfittour(self):
        mostfittour = self.tours[0]
        
        for i in range(self.populationsize()):
            if mostfittour.getfitness() <= self.gettour(i).getfitness():
                mostfittour = self.gettour(i)

        return mostfittour

    def populationsize(self):
        return len(self.tours)


class GeneticAlgo:
    def __init__(self, nodestorage, mutationrate=0.05, parentcandsize=5, elitism=True):
        self.nodestorage = nodestorage
        self.mutationrate = mutationrate
        self.parentcandsize = parentcandsize
        self.elitism = elitism

    def evolvepopulation(self, oldpopulation):
        self.cleanup(oldpopulation)

        newpopulation = Population(self.nodestorage, oldpopulation.populationsize(), False)

        elitismoffset = 0
        if self.elitism:
            newpopulation.settour(0, oldpopulation.getmostfittour())
            elitismoffset = 1

        for i in range(elitismoffset, oldpopulation.populationsize()):
            parent1 = self.makecandselectone(oldpopulation)
            parent2 = self.makecandselectone(oldpopulation)
            child = self.crossover(parent1, parent2)
            newpopulation.settour(i, child)

        for i in range(elitismoffset, oldpopulation.populationsize()):
            self.mutate(newpopulation.gettour(i))
        
        return newpopulation

    def cleanup(self, oldpopulation):
        alphaupnodes = []
        for i in range(0, oldpopulation.populationsize()):
            temptour = oldpopulation.gettour(i)
            currenttime = temptour.getnode(0).getopen() #pop을 구성하는 각 투어에서 맨앞에노드의open시간
            for j in range(0, temptour.toursize()):
                frompoint = temptour.getnode(i)
                topoint = None
                if i+1 < temptour.toursize():
                    topoint = temptour.getnode(i+1)
                else:
                    topoint = temptour.getnode(0)
                if frompoint.getopen() <= currenttime <= frompoint.getclose(): #tw안이면
                    currenttime += frompoint.getstay()
                    currenttime += frompoint.timeTo(topoint)
                else: #tw밖이면
                    if frompoint not in alphaupnodes:
                        alphaupnodes.append(frompoint)
                    currenttime += frompoint.timeTo(topoint)
            if temptour.getnode(0).getopen() <= currenttime <= temptour.getnode(0).getclose():
                pass #처음시작위치로 돌아왔을때 tw내부일때
            else: #tw밖일때
                if temptour.getnode(0) not in alphaupnodes:
                    alphaupnodes.append(temptour.getnode(0))
        for ele in alphaupnodes:
            ele.alpha += 1
        
        bannodes = []
        worstnum = 50
        for i in range(0, self.nodestorage.storagesize()):
            tempnode = self.nodestorage.getnode(i)
            if (tempnode.getalpha() >= worstnum) and (tempnode not in bannodes):
                bannodes.append(tempnode)
        for ele in bannodes:    
            self.nodestorage.delnode(ele)
            for i in range(0, oldpopulation.populationsize()):
                oldpopulation.gettour(i).delnode(ele)

        for i in range(0, oldpopulation.populationsize()):
            _ = oldpopulation.gettour(i).getfitness()

    def makecandselectone(self, oldpopulation):
        temppopulation = Population(self.nodestorage, self.parentcandsize, False)

        for i in range(0, self.parentcandsize):         # randomly select 5 parentcand on previous population, and regard them as temppopulation, and get mostfit parent on it.
            randpopidx = int(random.random() * oldpopulation.populationsize())
            temppopulation.settour(i, oldpopulation.gettour(randpopidx)) # temppopulation can be like [tour5, tour5, tour2, tour1, tour8]

        selectedtour = temppopulation.getmostfittour()
        return selectedtour

    def crossover(self, parent1, parent2):      # parent1, parent2, child are all "tour"s
        child = Tour(self.nodestorage, False)

        # parent1내에서 부분구간을잡고 Tour객체를 부분투어로서 선언후, setnode로 그 부분구간의 노드를 하나씩 세트해준다. 
        # 그후 그 부분투어의 fitness를 레코드{}딕셔너리에 fitness : 해당부분투어객체 로 저장한다.
        # 이 작업을 모든 구간에 대해서 다 해본뒤 레코드에 전부 어팬드한다. 
        # 그후 keys로 가장 높은 fitness를 찾고 그fitness의 구간을 가져와서 패치로삼는다

        fitnessroutedict = {}
        for portionstart in range(0, parent1.toursize()):
            historynode = []
            for commondiff in range(0, parent1.toursize()):
                portionend = portionstart + commondiff
                if portionend >= parent1.toursize():
                    portionend -= parent1.tousize()
                historynode.append(parent1.getnode(portionend))
                route = Tour(self.nodestorage, True)
                route.tour = historynode
                routefitness = route.getfitness()
                fitnessroutedict[routefitness] = (portionstart, portionend) #portionstart,end는 parent1투어내부의 노드의인덱스
        
        maxfitness = max(fitnessroutedict.keys())
        parent1_patchinfo = fitnessroutedict[maxfitness]
        patchstart = parent1_patchinfo[0]
        patchend = parent1_patchinfo[1]
        if patchstart <= patchend:
            for i in range(patchstart, patchend+1):
                child.setnode(i, parent1.getnode(i))
        else:
            for i in range(patchstart, parent1.toursize()):
                child.setnode(i, parent1.getnode(i))
            for i in range(0, patchend+1):
                child.setnode(i, parent1.getnode(i))
        
        for i in range(0, parent2.toursize()):
            if not child.containing(parent2.getnode(i)):
                for j in range(0, parent2.toursize()):
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


if __name__ == '__main__':
    n_nodes = 10
    populationsize = 50
    n_generation = 100

    nodestorage = NodeStorage()

    # listing nodes
    nodestorage.addnode(Node(lon=139.741424, lat=35.699721, util=50, stay=90, open=480, close=1020)) # TUS 8~17(hour)
    nodestorage.addnode(Node(lon=139.728871, lat=35.661302, util=50, stay=90, open=480, close=1020)) # mori tower
    nodestorage.addnode(Node(lon=139.714924, lat=35.643925, util=50, stay=90, open=480, close=1020)) # ebisu
    nodestorage.addnode(Node(lon=139.701975, lat=35.682837, util=50, stay=90, open=480, close=1020)) # yoyogi
    nodestorage.addnode(Node(lon=139.719525, lat=35.680659, util=50, stay=90, open=480, close=1020)) # shinanomachi
    nodestorage.addnode(Node(lon=139.666109, lat=35.705378, util=50, stay=90, open=480, close=1020)) # nakano
    nodestorage.addnode(Node(lon=139.668144, lat=35.661516, util=50, stay=90, open=480, close=1020)) # shimokitazawa
    nodestorage.addnode(Node(lon=139.686511, lat=35.680789, util=50, stay=90, open=480, close=1020)) # gatsudai
    nodestorage.addnode(Node(lon=139.579722, lat=35.702351, util=50, stay=90, open=480, close=1020)) # kichijoji
    nodestorage.addnode(Node(lon=139.736571, lat=35.628930, util=50, stay=90, open=480, close=1020)) # shinagawa
    
    population = Population(nodestorage, populationsize=populationsize, init=True)
    geneticalgo = GeneticAlgo(nodestorage)

    # evolve
    for i in range(n_generation):
        population = geneticalgo.evolvepopulation(population)

    result = population.getmostfittour().tour # result = [node, node, node, node, ...]

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