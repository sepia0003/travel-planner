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
    starttime = 0

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
            currenttime = self.nodestorage.starttime
            for i in range(0, self.toursize()):
                frompoint = self.getnode(i)
                topoint = None
                if i+1 < self.toursize():
                    topoint = self.getnode(i+1)
                else:
                    topoint = self.getnode(0)  
                if frompoint.getstay() <= frompoint.getclose()-frompoint.getopen():
                    if currenttime < frompoint.getopen():
                        currenttime += frompoint.timeTo(topoint)    #작은스테이윈도우가 왼쪽에 있을땐, 기다리지 않고 그냥 지나치고 다음노드로
                    elif frompoint.getclose() < currenttime+frompoint.getstay():
                        currenttime += frompoint.timeTo(topoint)    #작은스테이윈도우가 오른쪽에 있을땐, 당연히 그냥 지나치고 다음노드로
                    else:
                        currenttime += frompoint.getstay()
                        allutil += frompoint.getutil()              #작은스테이윈도우가 타임윈도우안에있을땐, 체류하고 유틸얻고 다음노드로
                        currenttime += frompoint.timeTo(topoint)
                else:
                    currenttime += frompoint.timeTo(topoint)        #큰스테이윈도우이면 당연히 그냥 지나치고 다음노드로
            if not self.portion:
                if self.getnode(0).getstay() <= self.getnode(0).getclose()-self.getnode(0).getopen():
                    if currenttime < self.getnode(0).getopen():
                        pass       
                    elif self.getnode(0).getclose() < currenttime+self.getnode(0).getstay():
                        pass                                        #이전루프에서는 frompoint에 대해 조사후 다음노드까지의 이동시간을 구했다.
                    else:                                           #하지만 이전루프에서 from이마지막인덱스의 노드이고 to가처음인덱스의노드일때, to까지의이동시간까지만구하고
                        allutil += self.getnode(0).getutil()        #to의노드에 도착했을때 to의노드의tw에 맞는지 안맞는지 체크를 안했다.
                else:                                               #그래서 한번더 to노드 즉,처음노드만 따로 한번더 검증
                    pass                                            #돌아왔을때에도 util을 주는이유는 집으로 정할노드보다 더 투어에서 돌아와도 여유있을 tw를 가진 노드가 있을경우
            self.tourutil = allutil                                 #집의 util을 그 노드보다 크게 줘서 집으로 돌아오게끔 하기위해
        return self.tourutil                                        #(돌아올노드는 1.tw가 투어에서 돌아와도 열려있을만큼 넓음 2.유틸이많음 의 우선순위로 결정됨)

    def gettourtwmiss(self):
        if self.tourtwmiss == 0:
            alltwmiss = 0
            currenttime = self.nodestorage.starttime
            for i in range(0, self.toursize()):
                frompoint = self.getnode(i)
                topoint = None
                if i+1 < self.toursize():
                    topoint = self.getnode(i+1)
                else:
                    topoint = self.getnode(0)
                if frompoint.getstay() <= frompoint.getclose()-frompoint.getopen():
                    if currenttime < frompoint.getopen():
                        tempmiss = frompoint.getopen() - currenttime        #주의, miss는 단지 시간차이만 나타내는것이고, twmiss는 거기에 알파를 곱해준값이다.
                        alltwmiss += tempmiss * frompoint.getalpha()
                        currenttime += frompoint.timeTo(topoint)
                    elif frompoint.getclose() < currenttime+frompoint.getstay():
                        tempmiss = currenttime+frompoint.getstay() - frompoint.getclose()
                        alltwmiss += tempmiss * frompoint.getalpha()
                        currenttime += frompoint.timeTo(topoint)
                    else:
                        currenttime += frompoint.getstay()
                        currenttime += frompoint.timeTo(topoint)
                else:
                    tempmiss = max(abs(currenttime - frompoint.getopen()), abs(currenttime+frompoint.getstay() - frompoint.getclose()))
                    alltwmiss += tempmiss * frompoint.getalpha()
                    currenttime += frompoint.timeTo(topoint)
            if not self.portion:
                if self.getnode(0).getstay() <= self.getnode(0).getclose()-self.getnode(0).getopen():
                    if currenttime < self.getnode(0).getopen():
                        tempmiss = self.getnode(0).getopen() - currenttime
                        alltwmiss += tempmiss * self.getnode(0).getalpha()
                    elif self.getnode(0).getclose() < currenttime+self.getnode(0).getstay():
                        tempmiss = currenttime+self.getnode(0).getstay() - self.getnode(0).getclose()
                        alltwmiss += tempmiss * self.getnode(0).getalpha()
                    else:
                        pass
                else:
                    tempmiss = max(abs(currenttime - self.getnode(0).getopen()), abs(currenttime+self.getnode(0).getstay() - self.getnode(0).getclose()))
                    alltwmiss += tempmiss * self.getnode(0).getalpha()
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
        #(각노드는 투어에서 한번밖에 등장하지 않으므로 한노드의 스택의 최대값은 populationsize가 된다. 0인덱스의 노드일지라도 1번만 세도록 함)
        #그렇게 badstackofnodes가 만들어졌다면 populationsize/2 보다 많은 투어에서 tw를위반한 노드의 알파를 1씩증가시킨다
        badstackofnodes = {} #노드:빈도 순으로 작성
        for ele in self.nodestorage.storage:
            badstackofnodes[ele] = 0 # 스택을 0으로 초기화
        for i in range(0, oldpopulation.populationsize()):      #주의, populationsize는 해당population안에 들어가있는 tour의 개수이다.
            temptour = oldpopulation.gettour(i)
            currenttime = self.nodestorage.starttime
            alreadystacked = []
            for j in range(0, temptour.toursize()):             #주의, toursize는 해당 tour안에 들어가있는 node의 개수이다.
                frompoint = temptour.getnode(j)
                topoint = None
                if j+1 < temptour.toursize():
                    topoint = temptour.getnode(j+1)
                else:
                    topoint = temptour.getnode(0)
                if frompoint.getstay() <= frompoint.getclose()-frompoint.getopen():
                    if currenttime < frompoint.getopen():
                        badstackofnodes[frompoint] += 1
                        alreadystacked.append(frompoint)
                        currenttime += frompoint.timeTo(topoint)
                    elif frompoint.getclose() < currenttime+frompoint.getstay():
                        badstackofnodes[frompoint] += 1
                        alreadystacked.append(frompoint)
                        currenttime += frompoint.timeTo(topoint)
                    else:
                        currenttime += frompoint.getstay()
                        currenttime += frompoint.timeTo(topoint)
                else:
                    badstackofnodes[frompoint] += 1
                    alreadystacked.append(frompoint)
                    currenttime += frompoint.timeTo(topoint)
            if temptour.getnode(0) not in alreadystacked:
                if temptour.getnode(0).getstay() <= temptour.getnode(0).getclose()-temptour.getnode(0).getopen():
                    if currenttime < temptour.getnode(0).getopen():
                        badstackofnodes[temptour.getnode(0)] += 1
                    elif temptour.getnode(0).getclose() < currenttime+temptour.getnode(0).getstay():
                        badstackofnodes[temptour.getnode(0)] += 1
                    else:
                        pass
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
        #그 루트의 시작노드, 끝노드의 인덱스가 오름차순이면 child의 맨앞에서부터 채워나가고
        #내림차순이면 일단 시작노드의 인덱스부터 끝인덱스까지 child에 맨앞에서부터 채워나가고 0인덱스부터 끝노드의 인덱스까지 그뒤로 채워나감
        #(절대 있는 parent1의 노드인덱스위치 그대로 복붙하면 안된다. 그 인덱스위치 그대로 끝날때까지 고정이 되어버리기 때문)
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
                child.setnode(i-patchstart, parent1.getnode(i))
        else:
            for i in range(patchstart, parent1.toursize()):
                child.setnode(i-patchstart, parent1.getnode(i))
            for i in range(0, patchend+1):
                child.setnode(i+parent1.toursize()-patchstart, parent1.getnode(i))
        
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


def inspecttour(sometour, starttime):
    flag = 1 #1은 valid하다는의미
    currenttime = starttime
    print('시작시간:', currenttime)
    print('')
    for i in range(0, sometour.toursize()):
        frompoint = sometour.getnode(i)
        topoint = None
        if i+1 < sometour.toursize():
            topoint = sometour.getnode(i+1)
        else:
            topoint = sometour.getnode(0)
        if frompoint.getstay() <= frompoint.getclose()-frompoint.getopen():
            if currenttime < frompoint.getopen():
                flag = 0
                print('[{}]를 방문했으나 tw가 안맞았음({})'.format(frompoint.getname(), currenttime))
                currenttime += frompoint.timeTo(topoint)
                print('{}({})'.format(frompoint.timeTo(topoint), currenttime))
            elif frompoint.getclose() < currenttime+frompoint.getstay():
                flag = 0
                print('[{}]를 방문했으나 tw가 안맞았음({})'.format(frompoint.getname(), currenttime))
                currenttime += frompoint.timeTo(topoint)
                print('{}({})'.format(frompoint.timeTo(topoint), currenttime))
            else:
                currenttime += frompoint.getstay()
                print('[{}]\t {}분 체류({})'.format(frompoint.getname(), frompoint.getstay(), currenttime))
                currenttime += frompoint.timeTo(topoint)
                print('{}({})'.format(frompoint.timeTo(topoint), currenttime))
        else:
            flag = 0
            print('[{}]를 방문했으나 tw가 안맞았음({})'.format(frompoint.getname(), currenttime))
            currenttime += frompoint.timeTo(topoint)
            print('{}({})'.format(frompoint.timeTo(topoint), currenttime))
    if sometour.getnode(0).getstay() <= sometour.getnode(0).getclose()-sometour.getnode(0).getopen():
        if currenttime < sometour.getnode(0).getopen():
            flag = 0
            print('[{}]를 방문했으나 tw가 안맞았음({})'.format(sometour.getnode(0).getname(), currenttime))
        elif sometour.getnode(0).getclose() < currenttime+sometour.getnode(0).getstay():
            flag = 0
            print('[{}]를 방문했으나 tw가 안맞았음({})'.format(sometour.getnode(0).getname(), currenttime))
        else:
            currenttime += sometour.getnode(0).getstay()
            print('[{}]\t {}분 체류({})'.format(sometour.getnode(0).getname(), sometour.getnode(0).getstay(), currenttime))
    else:
        flag = 0
        print('[{}]를 방문했으나 tw가 안맞았음({})'.format(sometour.getnode(0).getname(), currenttime))
    print('')
    print('종료시간:', currenttime)
    print('총소요시간:', currenttime - starttime)

    if flag == 1:
        validity = 'Valid!'
    else:
        validity = 'Fail!'
    print(validity)


if __name__ == '__main__':
    # testenv
    n_nodes = 10
    populationsize = 50
    n_generation = 1000
    worstnum = 500
    starttime = 480

    # testnodes
    tus =           Node(lon=139.741424, lat=35.699721, util=100, stay=90, open=480, close=840, name='tus')
    moritower =     Node(lon=139.728871, lat=35.661302, util=1, stay=30, open=0, close=10000, name='moritower')
    ebisu =         Node(lon=139.714924, lat=35.643925, util=40, stay=30, open=720, close=840, name='ebisu')
    yoyogi =        Node(lon=139.701975, lat=35.682837, util=100, stay=60, open=1200, close=1440, name='yoyogi')
    shinanomachi =  Node(lon=139.719525, lat=35.680659, util=30, stay=10, open=480, close=660, name='shinanomachi')
    nakano =        Node(lon=139.666109, lat=35.705378, util=100, stay=120, open=660, close=1200, name='nakano')
    shimokitazawa = Node(lon=139.668144, lat=35.661516, util=300, stay=30, open=1200, close=1440, name='shimokitazawa')
    hatsudai =      Node(lon=139.686511, lat=35.680789, util=50, stay=60, open=300, close=600, name='hatsudai')
    kichijoji =     Node(lon=139.579722, lat=35.702351, util=1000, stay=0, open=720, close=1080, name='kichijoji')
    shinagawa =     Node(lon=139.736571, lat=35.628930, util=700, stay=10, open=480, close=600, name='shinagawa')

    nodestorage = NodeStorage()
    nodestorage.starttime = starttime
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
        inspecttour(temptour, starttime)
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

    # inspect result
    inspecttour(result, starttime)


    # 노드의 개수가 많아지면 제네레이션도 많아져야하나?
    # 그럼 많아질때 worstnum도 증가시켜야하나?
    # 노드개수 고정시켰을때에 대해서인데, 다양한 효용의 투어가 나오는데 여러개 해봐서 그중 좋은 투어를 반환하도록해야할까
    # 뭔가 하나 노드가 특출나게 이상하면 alpha의 증가 속도가 덩달아 커지는 느낌
    # 전체제네레이션수의/4 로 최악수를 잡으면될듯?
    

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
