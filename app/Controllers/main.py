from flask import Blueprint, request, render_template, flash, redirect, url_for, jsonify
from flask import current_app as app
from ..Models.dbModule import Database
from ..Models.gaModule_tw_md_alpha_wait import Node, NodeStorage, Tour, Population, GeneticAlgo, makemap
import matplotlib.pyplot as plt

bp = Blueprint('main', __name__, url_prefix='/')
db = Database()
try: db.maketable("locationtable")
except: pass

@bp.route('/', methods=['GET'])                 #GET은 서버의 값이나 상태를 바꾸지않고, POST는 바꾼다.
def main():
    return render_template('index.html')

@bp.route('/adding', methods=['POST'])
def adding():
    db.addlocation(tuple(request.get_json().values()))        #튜플형태로 반환해줘야함
    destlist = db.getlocationlist()                     #get은 [{1row의 key:val, ...}, {2row의 key:val, ...}]의 리스트
    tempdict = {'data': destlist}
    return jsonify(tempdict)                #jsonify(딕셔너리객체) 는 해당딕셔너리를 json화 시킨다음에 response 의 body에도 탑재해주고 headers도 "Content-Type": "application/json" 를 넣어준 객체를 반환한다.

@bp.route('/reset', methods=['POST'])
def reset():
    db.resetlocationlist()
    tempdict = {}
    tempdict['data'] = ''       #일단 리턴값으로 빈값을 리턴. 이렇게 작위적으로 리턴하지않는방법을 찾아보자
    return jsonify(tempdict)

@bp.route('/searching', methods=['GET'])
def searching():
    populationsize = 50
    n_generation = 2500
    worstnum = 500
    splittemp0 = request.args.get('starttime').split(':')
    starttime = int(splittemp0[0])*60 + int(splittemp0[1])

    destlist = db.getlocationlist() #[{row1에대한 field,val}, {row2에대한 field,val}, ...]

    nodestorage = NodeStorage()
    nodestorage.starttime = starttime
    for ele in destlist:
        splittemp1 = ele['open'].split(':')
        ele['open'] = int(splittemp1[0])*60 + int(splittemp1[1])
        splittemp2 = ele['close'].split(':')
        ele['close'] = int(splittemp2[0])*60 + int(splittemp2[1])
    for ele in destlist:
        nodestorage.addnode(Node(lon=float(ele['lon']), lat=float(ele['lat']), util=int(ele['util']), stay=int(ele['stay']), open=ele['open'], close=ele['close']))
    mapframenodestorage = NodeStorage()
    mapframenodestorage.storage = nodestorage.storage.copy()

    population = Population(nodestorage, populationsize=populationsize, init=True)
    geneticalgo = GeneticAlgo(nodestorage, worstnum)

    for i in range(n_generation):
        population = geneticalgo.evolvepopulation(population)
    
    resulttour = population.getmostfittour()

    makemap(mapframenodestorage, resulttour)

    htmlmapstr = open('resultmap.html', 'r').read().replace('<!DOCTYPE html>', '').replace('<head>', '').replace('</head>', '').replace('<body>', '').replace('</body>', '')
    tempdict = {'data': htmlmapstr}

    return jsonify(tempdict)

    #cwd에서 resultmap.html을 불러와서/ 불러온것을 json형식으로 변형한뒤/ jsonify로 리스폰스




#request.get_json()은 클라이언트가 post할때 body에 실어보낸 json을 딕셔너리객체로 바꿔주는 역할을 한다.
#즉, request.get_json()자체가 딕셔너리


#request.form은 html에서 input태그내의 name키에해당하는밸류, value키에해당하는밸류
#이 두가지 밸류를 각각 가져와서
#name키에해당하는밸류를 request.form내부의 하나의새로운키로
#value키에해당하는밸류를 그 새로만들어진키의 밸류로 각각대응시켜서
#request.form자체가 딕셔너리로서 기능하게된다.
#딕셔너리요소의 개수는 html안의 form태그안 맨처음부터 submit태그가 있는곳까지 가져간다.
#request.form이 딕셔너리로 기능하므로 당연히 .keys() .values() .items() 사용가능하다
#리턴값이 딕셔너리와 완전히 같은형식의 특별한 리스트로 나오게된다.
#list()로 겉의특별한[]를 평범한[]로 바꿔줄수있다. 혹은 tuple()로 ()로 바꿔줄수도있다.

#주의 html의 모든 밸류는 "~~"이었다 
#즉, name키에해당하는밸류도 str이고 value키에해당하는밸류도 str이다
#따라서 request.form내에 저장된 모든 키밸류들은 str이다.
#request.form["lon"]등으로 써야한다는것

#타입 <class 'werkzeug.datastructures.ImmutableMultiDict'>   
#내용 ImmutableMultiDict([('lon', '1232'), ('lan', '12321'), 
# ('util', '5678'), ('open', '11:03'), ('close', '02:03')])





# 보통 플라스크객체인 app에 route를 하는데 
# 여기서는 블루프린트객체인 bp에 route를 한뒤 이걸 app에 넘기는과정을함

# @란 데코레이터이다. 바로 아래에 입력된 함수a를 입력받아 
# 앞뒤에 추가 코드를 넣어 데코레이트○한것을 반환하는 역할을한다.
# def decorator(f):
#   def decorated():
#       print("앞추가코드")
#       f()
#       print("뒤추가코드")
#   return decorated
# 혹은
# class decorator:
#   def __init__(self, f):
#       self.f = f
#  
#   def __call__(self, *args, **kwargs):
#       print("앞추가코드")
#       self.f(*args, **kwargs)
#       print("뒤추가코드")
# 라고 만들수있다. 
# 클래스로 만들경우 아래함수a를 입력받을때 init되고, 앞뒤에추가 코드를 넣어 데코레이트○할때 call이된다.

# init은 객체만들때 실행되고, call은 메소드 지정없이 바로 사용될것을 써준다 (객체()로 바로 사용가능, 객체.사용하고싶은메소드() 가아니라)
# *args는 갯수제한없이 복수개의 인수 그자체를 의미, args는 그 복수개의 인수를 튜플화한것으로 해당함수에서 사용됨
# **kwargs는 갯수제한없이 복수개의 키=밸류 그자체를 의미, kwargs는 그 복수개의 인수를 딕셔너리화한것으로 해당함수에서 사용됨





# 이제 EC2에 도커를 설치후 컨테이너를 분리해 mysql, was+wsgi , apache 로 구성해줘야함