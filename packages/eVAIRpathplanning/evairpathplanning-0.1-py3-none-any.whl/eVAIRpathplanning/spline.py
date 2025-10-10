import numpy as np

#only divide the ends of the edges rather than the whole thing
def pathdivider(Vpath):
    newVpath = [[], []]
    xn = Vpath[0]
    yn = Vpath[1]

    for i in range(len(xn) - 1):
        length2 = ((xn[i] - xn[i+1])**2 + (yn[i] - yn[i+1])**2)**(1/2)
        if length2 > 40:
            xpt, ypt = xn[i], yn[i]
            newVpath[1].append(xpt)
            newVpath[0].append(ypt)
            n = int(length2/40)
            dx = (xn[i] - xn[i+1])/(n + 1)
            dy = (yn[i] - yn[i+1])/(n + 1)
            for j in range(n):
                xpt, ypt = xpt-dx, ypt-dy
                newVpath[1].append(xpt)
                newVpath[0].append(ypt)
        else:
            xpt, ypt = xn[i], yn[i]
            newVpath[1].append(xpt)
            newVpath[0].append(ypt)

    ypt, xpt = xn[-1], yn[-1]
    newVpath[0].append(xpt)
    newVpath[1].append(xpt)

    n =  np.array(newVpath)
    newVpath = np.flip(newVpath)
    return newVpath


def bspline(Vpath, res):
    blen = len(Vpath[0])
    #Belezier curve

    #path points
    tpts = np.linspace(0, 1, res)
    Cxpts = []
    Cypts = []

    #pascal's traingle (for Px constants)
    pas1 = [1,1]
    for i in range(blen - 2):
        pas2 = [1]
        for i in range(len(pas1)-1):
            pas2.append(pas1[i]+pas1[i+1])
        pas2.append(1)
        pas1 = pas2

    #Px and Py uses point P_i and an equation to create the Bezier curve, C
    for t in tpts:
        Cx = 0
        Cy = 0
        for i in range(blen):
            n = blen - 1

            Px = Vpath[0][i]*pas1[i]*((1-t)**(n - i))*(t**i)
            Cx += Px
            Py = Vpath[1][i]*pas1[i]*(1-t)**(n - i)*t**i
            Cy += Py

        Cxpts.append(Cx)
        Cypts.append(Cy)

    return Cxpts, Cypts


def bspline2(Vpath, gapsize, res):
    newVpath = [[], []]
    #Vpathx's and y's
    xn = Vpath[0]
    yn = Vpath[1]

    #slicing the edges evenly
    for i in range(len(xn) - 1):
        length2 = ((xn[i] - xn[i+1])**2 + (yn[i] - yn[i+1])**2)**(1/2)
        if length2 >= gapsize * 2:
            xpt, ypt = xn[i], yn[i]
            newVpath[1].append(xpt)
            newVpath[0].append(ypt)
            n = int(length2/gapsize)
            dx = (xn[i] - xn[i+1])/(n + 1)
            dy = (yn[i] - yn[i+1])/(n + 1)
            for j in range(n):
                xpt, ypt = xpt-dx, ypt-dy
                newVpath[1].append(xpt)
                newVpath[0].append(ypt)
        else:
            xpt, ypt = xn[i], yn[i]
            newVpath[1].append(xpt)
            newVpath[0].append(ypt)

    xpt, ypt = xn[-1], yn[-1]
    newVpath[0].append(xpt)
    newVpath[1].append(xpt)

    n =  np.array(newVpath)
    newVpath = np.flip(newVpath)
    Vpath = newVpath

    blen = len(Vpath[0])
    #Belezier curve

    #path points
    tpts = np.linspace(0, 1, res)
    Cxpts = []
    Cypts = []

    #pascal's traingle (for Px constants)
    pas1 = [1,1]
    for i in range(blen - 2):
        pas2 = [1]
        for i in range(len(pas1)-1):
            pas2.append(pas1[i]+pas1[i+1])
        pas2.append(1)
        pas1 = pas2

    #Px and Py uses point P_i and an equation to create the Bezier curve, C
    for t in tpts:
        Cx = 0
        Cy = 0
        for i in range(blen):
            n = blen - 1

            Px = Vpath[0][i]*pas1[i]*((1-t)**(n - i))*(t**i)
            Cx += Px
            Py = Vpath[1][i]*pas1[i]*(1-t)**(n - i)*t**i
            Cy += Py

        Cxpts.append(Cx)
        Cypts.append(Cy)

    return Cxpts, Cypts, Vpath


#gapsize = distane between each point
#num = number of points on each end
def bspline3(Vpath, gapsize, num, res):
    newVpath = [[], []]
    #Vpathx's and y's
    xn = Vpath[0]
    yn = Vpath[1]

    #slicing the edges only at the ends
    for i in range(len(xn) - 1):
        length2 = ((xn[i] - xn[i+1])**2 + (yn[i] - yn[i+1])**2)**(1/2)
        if length2 > gapsize*num:
            xpt1, ypt1 = xn[i], yn[i]
            xpt2, ypt2 = xn[i+1], yn[i+1]
            newVpath[1].append(xpt)
            newVpath[0].append(ypt)

            dy = gapsize*(ypt2-ypt1)/(((xpt2-xpt1)**2+(ypt2-ypt1)**2)**(1/2))
            dx = gapsize*(xpt2-xpt1)/(((xpt2-xpt1)**2+(ypt2-ypt1)**2)**(1/2))

            for j in range(num):
                xpt, ypt = xpt1-gapsize, ypt1-gapsize
                newVpath[1].append(xpt)
                newVpath[0].append(ypt)
            for j in range(num):
                xpt, ypt = xpt2+gapsize, ypt2+gapsize
                newVpath[1].append(xpt2)
                newVpath[0].append(ypt2)
        else:
            xpt1, ypt1 = xn[i], yn[i]
            newVpath[1].append(xpt1)
            newVpath[0].append(ypt1)

    xpt1, ypt1 = xn[-1], yn[-1]
    newVpath[0].append(xpt1)
    newVpath[1].append(xpt1)

    n =  np.array(newVpath)
    newVpath = np.flip(newVpath)
    Vpath = newVpath

    blen = len(Vpath[0])
    #Belezier curve

    #path points
    tpts = np.linspace(0, 1, res)
    Cxpts = []
    Cypts = []

    #pascal's traingle (for Px constants)
    pas1 = [1,1]
    for i in range(blen - 2):
        pas2 = [1]
        for i in range(len(pas1)-1):
            pas2.append(pas1[i]+pas1[i+1])
        pas2.append(1)
        pas1 = pas2

    #Px and Py uses point P_i and an equation to create the Bezier curve, C
    for t in tpts:
        Cx = 0
        Cy = 0
        for i in range(blen):
            n = blen - 1

            Px = Vpath[0][i]*pas1[i]*((1-t)**(n - i))*(t**i)
            Cx += Px
            Py = Vpath[1][i]*pas1[i]*(1-t)**(n - i)*t**i
            Cy += Py

        Cxpts.append(Cx)
        Cypts.append(Cy)

    return Cxpts, Cypts, Vpath

def weightedbspline(Vpath, gapsize, res, obpts):
    #slicing the edges evenly

    newVpath = [[], []]
    #Vpathx's and y's
    xn = Vpath[0]
    yn = Vpath[1]

    for i in range(len(xn) - 1):
        length2 = ((xn[i] - xn[i+1])**2 + (yn[i] - yn[i+1])**2)**(1/2)
        if length2 >= gapsize * 2:
            xpt, ypt = xn[i], yn[i]
            newVpath[1].append(xpt)
            newVpath[0].append(ypt)
            n = int(length2/gapsize)
            dx = (xn[i] - xn[i+1])/(n + 1)
            dy = (yn[i] - yn[i+1])/(n + 1)
            for j in range(n):
                xpt, ypt = xpt-dx, ypt-dy
                newVpath[1].append(xpt)
                newVpath[0].append(ypt)
        else:
            xpt, ypt = xn[i], yn[i]
            newVpath[1].append(xpt)
            newVpath[0].append(ypt)

    xpt, ypt = xn[-1], yn[-1]
    newVpath[0].append(xpt)
    newVpath[1].append(xpt)

    n =  np.array(newVpath)
    newVpath = np.flip(newVpath)
    Vpath = newVpath

    #Belezier curve
    blen = len(Vpath[0])

    #path points
    tpts = np.linspace(0, 1, res)
    Cxpts = []
    Cypts = []

    #weights
    Ws = []

    #weights based on point length
    for i in range(blen):
        Wlen = ((Vpath[0][i] - obpts[0][0])**2 + (Vpath[1][i] - obpts[1][0])**2)
        for j in range(1, len(obpts[0])):
            Wlen1 = ((Vpath[0][i] - obpts[0][j])**2 + (Vpath[1][i] - obpts[1][j])**2)
            if Wlen1 < Wlen:
                Wlen = Wlen1

        W = (1/Wlen)**2
        Ws.append(W)

    #pascal's traingle (for Px constants)
    pas1 = [1,1]
    for i in range(blen - 2):
        pas2 = [1]
        for i in range(len(pas1)-1):
            pas2.append(pas1[i]+pas1[i+1])
        pas2.append(1)
        pas1 = pas2

    #Px and Py uses point P_i and an equation to create the Bezier curve, C
    for t in tpts:
        Cxn = 0
        Cyn = 0
        Cxd = 0
        Cyd = 0
        for i in range(blen):
            n = blen - 1

            bxW = (pas1[i]*((1-t)**(n - i))*(t**i))*Ws[i]
            Cxn += bxW*Vpath[0][i]
            Cxd += bxW

            byW = (pas1[i]*((1-t)**(n - i))*(t**i))*Ws[i]
            Cyn += byW*Vpath[1][i]
            Cyd += byW

        Cx = Cxn/Cxd
        Cy = Cyn/Cyd
        Cxpts.append(Cx)
        Cypts.append(Cy)

    return Cxpts, Cypts, Vpath