import typeguard
from typed_everywhere import Typed
import typed_everywhere


class A:
    a = Typed(10)


class B:
    def __add__(self, other):
        return B()


def test1():
    global b
    print("here")
    b = c = d = Typed(10)
    b = 20
    print(b)
    print(type(b))

def test2():
    a = A()
    a.a = Typed(5)
    a.a = 30
    print(a.a)
    del a.a
    print(a.a)

def test3():
    a = Typed(B())
    print(a)
    a += 1
    print(a)

@typeguard.typechecked
def test4(a: Typed[list[int]]):
    pass
    
def main():
    test1()
    print()
    test2()
    print()
    test3()
    test4(Typed([1,2,3]))

if typed_everywhere.patch_and_reload_module():
    main()
