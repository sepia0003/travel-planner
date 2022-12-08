from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask import current_app as app
from ..Models.dbModule import Database

bp = Blueprint('main', __name__, url_prefix='/')
db = Database()
try: db.maketable("locationtable")
except: pass

@bp.route('/', methods=['GET'])
def main():
    return render_template('index.html')

@bp.route('/inputing', methods=['POST'])
def inputing():
    try:
        if request.form["resetflag"] == "초기화":
            db.resetlocationlist()
            destlist = db.getlocationlist() #get은 [[1row의values], [2row의values]]
        return render_template('index.html', destlist=destlist)
    except:
        db.addlocation(tuple(request.form.values())) #튜플형태로 반환해줘야함
        destlist = db.getlocationlist()
        return render_template('index.html', destlist=destlist)




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