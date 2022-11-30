class test:
    def __init__(self):
        self.list = []
    
    def change(self, a):
        self.list.append(a)


obj = test()
obj.change(0)
obj.change(100)
obj.change(10000)
obj.change(10000000000)
obj.list.pop(2)
obj.list.pop(2)


testlist = [None, 1, 2, None, 3]

          #-10 -9 -8 -7 -6 -5 -4 -3 -2 -1
testlist2 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
int("1")
print(testlist2[10:11:1]) 
#리스트슬라이싱은 from:to:증순1 의미이고 기본증순1을 감순1로는 -1로따로써주면된다. 감순은 감순대로 요소순서가뒤바뀐다.
#from, to가 증순이아니면 슬라이싱되는게 없다. 마찬가지로 -1일땐 감순이아니면 슬라이싱되는게없다 
#그리고 from, to는 인덱스지칭이지 그숫자 자체대소에 의미가없다.

int("2")