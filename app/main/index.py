from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask import current_app as app

main = Blueprint('main', __name__, url_prefix='/')

@main.route('/main', methods=['GET'])
def index():
    testdata = 'TESTING string'
    return render_template('/main/index.html', testdatahtml=testdata)


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