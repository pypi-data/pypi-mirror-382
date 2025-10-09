import assign_overload
import wrapt


class T(wrapt.ObjectProxy):        
    def _assign_(self, value, *annotation):
        print(f"called with {value}")
        self.__wrapped__ = value
        return self


class A:
    a = T(10)


def test1():
    global b
    #a, b = T(), T()
    print("here")
    b = c = d = T(10)
    b = 20
    print(b)
    print(type(b))


def test2():
    a = A()
    a.a = T(5)
    a.a = 30
    print(a.a)    
    del a.a
    print(a.a)

    
def main():
    test1()
    print()
    test2()


if assign_overload.patch_and_reload_module():
    main()
