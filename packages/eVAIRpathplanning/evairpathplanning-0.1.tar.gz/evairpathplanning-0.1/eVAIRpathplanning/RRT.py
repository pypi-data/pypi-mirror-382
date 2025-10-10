import numpy as np
import random as rand

#collision check
def collision_free(p1, p2, map_matrix):

    x0, y0 = p1
    x1, y1 = p2

    steps = int(max(abs(x1 - x0), abs(y1 - y0)))
    for i in range(steps + 1):
        t = i / steps
        x = x0 + t * (x1 - x0)
        y = y0 + t * (y1 - y0)


        xi = int(round(x))
        yi = int(round(y))


        # Check for obstacle
        if map_matrix[xi, yi] == 1:
            return False

    return True

#finding path
def findpath(E, start):
    #converts E one for x11 and y11, another for x12, y12
    E = np.array(E)
    VE1 = (E[:,:,0])
    VE2 = (E[:,:,1])
    ipath = -1
    Vpath = [[VE2[ipath,0]], [VE2[ipath,1]]]

    start2 = [start[0], start[1]]

    #matches the x11 and y11 with a x12 and y12
    while VE1[ipath][0] != start2[0] and VE1[ipath][0] != start2[1]:
        ip = np.where(VE2 == VE1[ipath])
        iplen = range(len(ip[0]))
        for j in iplen:
            for k in iplen:
                print(ip)
                if ip[0][j] == ip[0][k] and j != k:
                    ipath = ip[0][j]
        Vpath[0].append(VE2[ipath,0])
        Vpath[1].append(VE2[ipath,1])
    Vpath[0].append(VE1[0,0])
    Vpath[1].append(VE1[0,1])

    return Vpath

def RRT13(map, start, goal):
    ### RRT ###
    #starting variables (counter and connect check)
    icntr = 0
    cnct = False
    #separate because it makes it easier to modify the map and RRT
    Qgoal = goal

    #G(V, E)
    #E = [[[x11,x12],[y11,y12]], [[x11,x12],[y11,y12]]]
    E = []
    #V = [[x1, x2...], [y1, y2...]]
    V = [[start[0]], [start[1]]]

    #While counter < lim and path isn't connected
    while icntr < 10000 and cnct == False:
        #Xnew  = RandomPosition()
        #[x1, y1]
        X = (rand.randrange(0, len(map), 1), rand.randrange(0, len(map[0]), 1))

        #if IsInObstacle(Xnew) == True:
            #continue
        Xvalid = True
        shapes1 = []

        xi = int(X[0])
        yi = int(X[1])

        #checks if there's already a point there 
        for i in range(len(V[0])):
            if xi == V[0][i]:
                if yi == V[1][i]:
                    Xvalid = False
        #checks if point is on 1
        if map[xi, yi] == 1:
            Xvalid = False

        if Xvalid == True:
            #Xnearest = Nearest(G(V,E),Xnew) //find nearest vertex
            #setting the nearest vertex as vertex 1
            Vnrst = (V[0][0], V[1][0])
            Vdist1 = ((V[0][0] - X[0])**2 + (V[1][0] - X[1])**2)**(1/2)
            #comparing the vertex distances to determine the closest vertex
            for i in range(len(V[0])):
                Vdist2 = ((V[0][i] - X[0])**2 + (V[1][i] - X[1])**2)**(1/2)
                if Vdist2 < Vdist1:
                    Vnrst = (V[0][i], V[1][i])
                    Vdist1 = Vdist2

            #Link = Chain(Xnew,Xnearest)
            #G.append(Link)
            #[[[x11,x12], [y11,y12]]
            #E.append([[Vnrst[0],X[0]], [Vnrst[1],X[1]]])
            #V[0].append(X[0])
            #V[1].append(X[1])
            if Xvalid and collision_free(Vnrst, X, map):
                E.append([[Vnrst[0], X[0]], [Vnrst[1], X[1]]])
                V[0].append(X[0])
                V[1].append(X[1])

                #if Xnew in Qgoal:
                    #Return G
                if X[0] >= Qgoal[0][0] and X[1] >= Qgoal[1][0]:
                    if X[0] <= Qgoal[0][1] and X[1] <= Qgoal[1][1]:
                        cnct = True

        #iteration
        icntr += 1

    ### RRT ###


    ### tracing the path ###
    Vpath = findpath(E, start)
    ### tracing the path ###

    return E, V, Vpath, icntr