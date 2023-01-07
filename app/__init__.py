from flask import Flask

app = Flask(__name__)

from .Controllers.main import bp

app.register_blueprint(bp)








#현재패키지의 main이란 폴더에서 index라는 모듈을 실행하고 만들어진 main이란놈을 main으로서 가져옴
#main은 필요한정보가 모두 html에 렌더링되어서 만들어진 개성적인 웹페이지 1장 그자체

#그놈을 app이라는 플라스크 서버에 먹여주고 완료