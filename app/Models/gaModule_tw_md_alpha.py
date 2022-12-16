# run docker:osrm-backend first
import requests
import polyline
import folium
import random

class Node:
    def __init__(self, lon=None, lat=None, util=None, stay=None, open=None ,close=None, alpha=1, name=None): # stay, open, close should be in min
        self.lon = lon
        self.lat = lat
        self.util = util
        self.stay = stay
        self.open = open
        self.close = close
        self.alpha = alpha
        self.name = name

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
    
    def getname(self):
        return self.name

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

    # __~~__ 같은 매직메소드는 get,set,del,len(겟셋들은)이 있다. 하지만 리스트 조작이랑 헷갈려서 굳이 안쓰기로 결정
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
            # print('투어의길이:', len(self.tour))      #테스트
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
                allutil += self.getnode(0).getutil()    #돌아왔을때도 효용을 얻게해서 효용의 높은곳에서 시작하는 가능성이 높아지도록
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
    def __init__(self, nodestorage, worstnum, mutationrate=0.05, parentcandsize=5, elitism=True):
        self.nodestorage = nodestorage
        self.mutationrate = mutationrate
        self.parentcandsize = parentcandsize
        self.elitism = elitism
        self.worstnum = worstnum

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
        #oldpopulation의 tour1~tour6전부순회 해보보면서 tw에 안맞는 노드가 있다면 badstackofnodes에 스택을 추가해나간다 
        #(각노드는 투어에서 한번밖에 등장하지 않으므로 한노드의 스택의 최대값은 populationsize가 된다)
        #그렇게 badstackofnodes가 만들어졌다면 populationsize/2 보다 많은 투어에서 tw를위반한 노드의 알파를 1씩증가시킨다
        badstackofnodes = {} #노드:빈도 순으로 작성
        for i in range(0, oldpopulation.populationsize()):
            temptour = oldpopulation.gettour(i)
            currenttime = temptour.getnode(0).getopen() #pop을 구성하는 각 투어에서 맨앞에노드의open시간
            for j in range(0, temptour.toursize()):
                frompoint = temptour.getnode(j)
                topoint = None
                if j+1 < temptour.toursize():
                    topoint = temptour.getnode(j+1)
                else:
                    topoint = temptour.getnode(0)
                if frompoint.getopen() <= currenttime <= frompoint.getclose(): #tw안이면
                    currenttime += frompoint.getstay()
                    currenttime += frompoint.timeTo(topoint)
                else: #tw밖이면
                    if frompoint not in badstackofnodes:
                        badstackofnodes[frompoint] = 1
                    else:
                        badstackofnodes[frompoint] += 1
                    currenttime += frompoint.timeTo(topoint)
            if temptour.getnode(0).getopen() <= currenttime <= temptour.getnode(0).getclose():
                pass #처음시작위치로 돌아왔을때 tw내부일때
            else: #tw밖일때
                if temptour.getnode(0) not in badstackofnodes:
                    badstackofnodes[temptour.getnode(0)] = 1
                else:
                    badstackofnodes[temptour.getnode(0)] += 1
        for ele in badstackofnodes.keys():
            if badstackofnodes[ele] > oldpopulation.populationsize()/2:
                ele.alpha += 1
        
        #GA객체만들때 입력한 최악수를 넘어가는 알파를 가진 노드를 nodestorage에서도, tour1~tour6에서도 삭제
        bannodes = []
        for i in range(0, self.nodestorage.storagesize()):
            tempnode = self.nodestorage.getnode(i)
            if (tempnode.getalpha() >= self.worstnum) and (tempnode not in bannodes):
                bannodes.append(tempnode)
        for ele in bannodes:    
            self.nodestorage.delnode(ele)
            for i in range(0, oldpopulation.populationsize()):
                oldpopulation.gettour(i).delnode(ele)

        #삭제된후의tour1~tour6에 대해 각각 피트니스 갱신
        for i in range(0, oldpopulation.populationsize()):
            _ = oldpopulation.gettour(i).getfitness()

    def makecandselectone(self, oldpopulation):
        #중복을 허락해서 oldpopulation에서 요소를 미리정한후보사이즈만큼 뽑아옴 그중에서 가장 피트니스높은것을 선택하는 작업
        temppopulation = Population(self.nodestorage, self.parentcandsize, False)

        for i in range(0, self.parentcandsize):         # randomly select 5 parentcand on previous population, and regard them as temppopulation, and get mostfit parent on it.
            randpopidx = int(random.random() * oldpopulation.populationsize())
            temppopulation.settour(i, oldpopulation.gettour(randpopidx)) # temppopulation can be like [tour5, tour5, tour2, tour1, tour8]

        selectedtour = temppopulation.getmostfittour()
        return selectedtour

    def crossover(self, parent1, parent2):      # parent1, parent2, child are all "tour"s
        child = Tour(self.nodestorage, False)

        #parent1이라는 하나의 투어 내부에서 가능한 모든 루트(시작점에돌아오지않는경로)를 스택앤캐치방식으로 잡고
        #해당 루트의 시작노드,끝노드의 인덱스를key로 피트니스값을value로 하는 딕셔너리로서 저장 
        routefitnessdict = {}
        for portionstart in range(0, parent1.toursize()):
            historynode = []
            for commondiff in range(0, parent1.toursize()):
                portionend = portionstart + commondiff
                if portionend >= parent1.toursize():
                    portionend -= parent1.toursize()
                historynode.append(parent1.getnode(portionend))
                route = Tour(self.nodestorage, True)
                route.tour = historynode
                fitnessofroute = route.getfitness()
                routefitnessdict[(portionstart, portionend)] = fitnessofroute #portionstart,end는 parent1투어내부의 노드의인덱스
        
        #그 딕셔너리에서 가장 피트니스가높은 루트를 parent1에서 가져온다.
        #그 루트의 시작노드, 끝노드의 인덱스가 오름차순이면 child에 그인덱스대로 복붙하고
        #내림차순이면 일단 시작노드의 인덱스부터 끝인덱스까지 child에 복붙하고 0인덱스부터 끝노드의 인덱스까지 child에 복붙
        maxfitness = max(routefitnessdict.values())
        temprecord = []
        for ele in routefitnessdict.keys():
            if routefitnessdict[ele] == maxfitness:
                temprecord.append(ele)
        tempidx = int(len(temprecord) * random.random())
        parent1_patchinfo = temprecord[tempidx]
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
        
        #그리고 child의 남은 None부분에 parent2에서 순서교차로 가져옴
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
                #random.random()은 0이상 1미만의 분수를 반환한다. 1이절대 될수없으므로 toursize를 곱해주고 int()로 소수점이하를 버리면 인덱스가 된다.

                node1 = tour.getnode(touridx1)
                node2 = tour.getnode(touridx2)

                tour.setnode(touridx2, node1)
                tour.setnode(touridx1, node2)


def inspectvalidity(sometour):
    flag = 1 #1은 valid하다는의미 
    currenttime = sometour.getnode(0).getopen() #min
    for i in range(0, sometour.toursize()):
        frompoint = sometour.getnode(i)
        topoint = None
        if i+1 < sometour.toursize():
            topoint = sometour.getnode(i+1)
        else:
            topoint = sometour.getnode(0)
        if frompoint.getopen() <= currenttime <= frompoint.getclose():
            currenttime += frompoint.getstay()
            currenttime += frompoint.timeTo(topoint)
        else:
            flag = 0
            currenttime += frompoint.timeTo(topoint)
    if sometour.getnode(0).getopen() <= currenttime <= sometour.getnode(0).getclose():
        pass
    else:
        flag = 0
    
    if flag == 1:
        validity = 'Valid!'
    else:
        validity = 'Fail!'
    
    print(validity)

def inspecttimeTo(sometour):
    for i in range(0, sometour.toursize()):
        frompoint = sometour.getnode(i)
        topoint = None
        if i+1 < sometour.toursize():
            topoint = sometour.getnode(i+1)
        else:
            topoint = sometour.getnode(0)
        print("{} ~ {} : ".format(frompoint.getname(), topoint.getname()), "{}".format(frompoint.timeTo(topoint)))
    


if __name__ == '__main__':
    # testenv
    n_nodes = 10
    populationsize = 50
    n_generation = 700
    worstnum = 100

    # testnodes
    # 주의, util이 너무 커버리면 그노드가 있는 투어의 fitness를구할때 twmiss나 distance의 마이너스값이 없는것이나 마찬가지가됨
    # 결국 tw나 거리도 고려하지않고 오로지 투어의 util만을 가지고 투어들끼리의 비교를하게됨
    tus =           Node(lon=139.741424, lat=35.699721, util=1, stay=5, open=184, close=185, name='tus')
    moritower =     Node(lon=139.728871, lat=35.661302, util=5, stay=5, open=404, close=405, name='moritower')
    ebisu =         Node(lon=139.714924, lat=35.643925, util=2, stay=5, open=354, close=355, name='ebisu')
    yoyogi =        Node(lon=139.701975, lat=35.682837, util=3, stay=5, open=888, close=889, name='yoyogi')
    shinanomachi =  Node(lon=139.719525, lat=35.680659, util=5, stay=5, open=121, close=122, name='shinanomachi')
    nakano =        Node(lon=139.666109, lat=35.705378, util=10, stay=5, open=0, close=1043, name='nakano')
    shimokitazawa = Node(lon=139.668144, lat=35.661516, util=3, stay=5, open=971, close=972, name='shimokitazawa')
    hatsudai =      Node(lon=139.686511, lat=35.680789, util=6, stay=5, open=69, close=70, name='hatsudai')
    kichijoji =     Node(lon=139.579722, lat=35.702351, util=5, stay=5, open=680, close=681, name='kichijoji')
    shinagawa =     Node(lon=139.736571, lat=35.628930, util=10, stay=5, open=297, close=298, name='shinagawa')

    nodestorage = NodeStorage()
    nodestorage.addnode(tus)
    nodestorage.addnode(moritower)
    nodestorage.addnode(ebisu) 
    nodestorage.addnode(yoyogi)
    nodestorage.addnode(shinanomachi) 
    nodestorage.addnode(nakano) 
    nodestorage.addnode(shimokitazawa) 
    nodestorage.addnode(hatsudai)
    nodestorage.addnode(kichijoji)
    nodestorage.addnode(shinagawa)
    mapframenodestorage = NodeStorage()
    mapframenodestorage.storage = nodestorage.storage.copy()

    # ask inspection of timeTo before evolution
    print("you want to inspect timeTo of your custom tour?")
    answer = input()
    if answer == 'y':
        temptour = Tour(nodestorage, False)
        temptour.setnode(0, nakano)
        temptour.setnode(1, hatsudai)
        temptour.setnode(2, shinanomachi)
        temptour.setnode(3, tus)
        temptour.setnode(4, shinagawa)
        temptour.setnode(5, ebisu)
        temptour.setnode(6, moritower)
        temptour.setnode(7, kichijoji)
        temptour.setnode(8, yoyogi)
        temptour.setnode(9, shimokitazawa)
        inspecttimeTo(temptour)
        exit()
    else:
        pass

    # makepopulation, geneticalgo obj for evolution
    population = Population(nodestorage, populationsize=populationsize, init=True)
    geneticalgo = GeneticAlgo(nodestorage, worstnum)

    # evolution
    for i in range(n_generation):
        population = geneticalgo.evolvepopulation(population)
        for j in nodestorage.storage:       #테스트
            print(j.getalpha(), end='/')    #테스트
        print('\n')                         #테스트

    # get result from latest population
    result = population.getmostfittour()
    result_justlist = population.getmostfittour().tour # result = [node, node, node, node, ...]

    # inspect validity of result
    inspectvalidity(result)


    # 노드의 개수가 많아지면 제네레이션도 많아져야하나?
    # 그럼 많아질때 worstnum도 증가시켜야하나?
    # 노드개수 고정시켰을때에 대해서인데, 다양한 효용의 투어가 나오는데 여러개 해봐서 그중 좋은 투어를 반환하도록해야할까
    

    # make a map with result
    import matplotlib.pyplot as plt

    original_lonlist = []
    original_latlist = []
    for i in mapframenodestorage.storage:
        original_lonlist.append(i.getlon())
        original_latlist.append(i.getlat())
    plt.scatter(original_lonlist, original_latlist)
    plt.xlim([min(original_lonlist) - 0.001, max(original_lonlist) + 0.001])
    plt.ylim([min(original_latlist) - 0.001, max(original_latlist) + 0.001])
    
    lonlist = []
    latlist = []
    for i in result_justlist:
        lonlist.append(i.getlon())
        latlist.append(i.getlat())
    for i in range(0, len(result_justlist)):    
        if i+1<len(result_justlist):
            plt.plot([lonlist[i], lonlist[i+1]], [latlist[i], latlist[i+1]], color="blue")
            plt.text(lonlist[i], latlist[i], '{}'.format(i))
        else:
            plt.plot([lonlist[i], lonlist[0]], [latlist[i], latlist[0]], color='red')
            plt.text(lonlist[i], latlist[i], '{}'.format(i))

    resultutil = 0
    for i in result.tour:
        resultutil += i.getutil()
    resultutil += result.tour[0].getutil()
    plt.text(139.60, 35.64, '{}'.format(resultutil))

    plt.savefig('map(gaModlue_tw_md_alpha).png')

    

    # make map with this result
    # lonlist = []
    # latlist = []
    # latlonlist = []
    # for i in result:
    #     lonlist.append(i.getlon())
    #     latlist.append(i.getlat())
    #     latlonlist.append((i.getlat(), i.getlon()))

    # map = folium.Map(location=[sum(latlist)/10, sum(lonlist)/10], zoom_start=13)

    # for i in range(n_nodes):
    #     if i != n_nodes-1:
    #         url = "http://localhost:5000/route/v1/driving/{},{};{},{}".format(lonlist[i], latlist[i], lonlist[i+1], latlist[i+1])
    #         response = requests.get(url).json()
    #         geometry = response["routes"][0]["geometry"]
    #         route = polyline.decode(geometry)
    #         folium.PolyLine(route, weight=8, color='blue', opacity=0.6).add_to(map)
    #     else:
    #         url = "http://localhost:5000/route/v1/driving/{},{};{},{}".format(lonlist[i], latlist[i], lonlist[0], latlist[0])
    #         response = requests.get(url).json()
    #         geometry = response["routes"][0]["geometry"]
    #         route = polyline.decode(geometry)
    #         folium.PolyLine(route, weight=8, color='red', opacity=0.6).add_to(map)
    
    # for i in range(n_nodes):
    #     folium.Marker(location=latlonlist[i], icon=folium.Icon(icon='play', color='green')).add_to(map)

    

    # map.save('gamap2.html')
