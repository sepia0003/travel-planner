from app import app

app.run(host='0.0.0.0', port=80)


# 모듈 = 스크립트 = .py파일
# import 모듈 // 그리고 사용할때는 모듈.변수, 모듈.함수() 로사용
# from 모듈 import 변수, 함수 // 바로 변수, 함수()를 "모듈."없이 사용가능

# __name__변수는 현재 실행중인 모듈이름이 저장
# import로 가져오면 가져온즉시 그 모듈이 실행이되므로 
# import시 __name__변수가 해당 모듈명이됨, 그리고 끝까지 실행다되면 __main__으로 돌아옴
# __main__이란 내가 run버튼을 누른 바로 그 모듈을 의미함

# __init__.py가 있는 폴더 = 패키지
# __init__.py 모듈은 속한 폴더를 패키지로 만들어 주고
# 해당 패키지가 import 되거나 from되었을때 바로 실행되어 초기화해준다
# import 패키지.모듈 // 그리고 사용할때는 패키지.모듈.변수, 패키지.모듈.함수() 로사용
# from 패키지.모듈 import 변수, 함수 // 바로 변수, 함수()를 "패키지.모듈."없이 사용가능
# 만약 패키지안에 하위패키지가 또있을때 import 패키지.하위패키지.모듈 처럼 .으로 내려가면됨

# 패키지에 있는 모듈을 import하면 가져온즉시 실행되고
# 실행중에 __name__변수가 해당패키지.모듈 이됨, 그리고 끝까지 실행이다끝나면 __main__으로 돌아옴

# --패키지내에서 __init__.py 조작법--
# from . import 패키지내의모듈 // .은 현재 __init__.py가 있는 패키지를 의미하고
# 그 패키지에서 모듈을 가져올수도 있음
# 그러면 패키지밖에서 이 패키지를 import해올때 __init__.py가 실행될테고 
# 그때 __init__.py에서 지정해준 모듈도 연쇄적으로 import됨
# from .패키지내의모듈 import 함수, 변수 // __init__.py 가있는 패키지내의모듈내의 함수,변수를 가져옴
# from .패키지내의모듈 import * // __init__.py 가있는 패키지내의모듈내의 모든 함수,변수를 가져옴
# __all__ = ['*로가져올함수','*로가져올변수'] // 이렇게 지정하면 *로 가져올 함수, 변수를 한정할수있음 지정안하면 모든 함수,변수를 가져옴
# 만약 __init__.py가있는 패키지내의하위패키지내의모듈내의함수,변수를 가져오려면 from .패키지내의하위패키지.모듈 import 함수, 변수 처럼 .으로 내려가면됨
# 만약 하위패키지가 2개이상이고 하위패키지내의모듈에서 다른 하위패키지내의모듈을 가져오려면 from ..(현재하위패키지의 현재패키지의)목표하위패키지 import 목표모듈
