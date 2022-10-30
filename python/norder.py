#def genNOrderPoly(C):
#    return (lambda a: lambda v, w = len(C)-1: a(a, v, w))(lambda s, j, x: C[x] if x==0 else C[x] * j ** x + s(s, j, x-1))
