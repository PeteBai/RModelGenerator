import random
import os
import uuid
import time
import graph as g

categoryCount = 0
manufactureCount = 0
userCount = 0

dirX = "C:\\Users\\surface\\Desktop\\Project Sydney\\电商数据生成a.3\\"

def generateData(rows, cols, pLabels, pFileName, pIsSerried, pIsUUID):
    #print(random.randint(1, 100))
    f = open(str(pFileName)+".dat",'w+')
    f.write(pLabels)
    f.write("\n")
    if(pIsSerried == True):
        for r in range(0, rows):
            for c in range(0, cols-1):
                if(c == 0):
                    f.writelines(str(r+1)+" ")
                else:
                    #这里写入非最后一列的、带序列的内容
                    pass
            f.write(str(uuid.uuid1()))
            f.write("\n")
    else:
        reqA = []
        reqB = []
        for c in range(0, cols):
            reqA.append(input("请输入第"+str(c+1)+"列的起使值："))
            reqB.append(input("请输入第"+str(c+1)+"列的结束值："))
        for r in range(0, rows):
            for c in range(0, cols-1):
                f.writelines(str(random.randint(int(reqA[c]), int(reqB[c])))+" ")
            f.write(str(random.randint(int(reqA[cols-1]), int(reqB[cols-1]))))
            f.write("\n")
    f.close()
        
#
#电子商务
#商品类别
#销售商【一个销售商对应数个类别】
#用户-销售商-权重
#用户-朋友
#用户-销售商-商品类别

def generateCategory():
    fileName = "Categories"
    label = "categoryId name"
    #num = input("请输入商品类别数：")
    #categoryCount = int(num)
    generateData(int(categoryCount), 2, label, fileName, True, True)

def generateManufacture():
    fileName = "Manufacture"
    label = "manufactureId name"
    #num = input("请输入制造商类别数：")
    #manufactureCount = int(num)
    generateData(int(manufactureCount), 2, label, fileName, True, True)

#用户-供应商-商品类别
#每个供应商随机与m个商品类别产生联系
#建立二维数组：【供应商1，供应商2.。。】，供应商1：【类别1，类别2.。。】
#每个用户随机选择n个商供应商，从每个供应商里面选取k（不定）个类别

#03-13-17:28 added timestamp
#用户时间戳特性：长度为13位，最后跟4-6个0不等
#对于一个用户的所有记录，应该有很多相同的时间戳
#这个用户的时间戳波动应该保证在一个较短的长度内
#获得开始-结束的时间，获得变化程度
#在这段给定的时间内，随机获取n个时间点【list】，对所有事件随机分配

def convertTime(startYear, endYear, minLoop, maxLoop):
    #maxLoop是系统最多要分配多少次不同标签
    YRS_IN_SEC = 31536000
    dts = str(startYear) + "-01-01 00:00:00"
    tss = time.mktime(time.strptime(dts, "%Y-%m-%d %H:%M:%S"))
    dte = str(endYear) + "-12-31 23:59:59"
    tse = time.mktime(time.strptime(dte, "%Y-%m-%d %H:%M:%S"))
    res = []
    ml = random.randint(minLoop, maxLoop)
    for i in range(0, ml):
        res.append((int(tss)+random.randint(0, (YRS_IN_SEC-1)*(endYear-startYear+1)))*1000)
    return res

#03-14-15：52
#每个用户维护一个list，里面是他访问的所有店铺。再为每个用户生成随即上限值
#读入图，选择1号用户作为起点，随机生成0~【最多用户访问的店铺数】之内个商家，保存到列表
#设置一个传播门槛，即一个用户最多传播多少次
#现在这个用户向他所有的朋友传播这个列表，随机选取其中60%的店铺（这个复制标准可变）
#这个用户每传播一次门槛-1，到0就停止传播
#朋友收到列表，在不超过随机上限的前提下将其加入自己的列表
#一个节点在达到随机上限时停止接受新店铺，在门槛降为0时停止传播自己的店铺列表

def percentControl(pPickPecrentage):
    controller = random.randint(1,100)
    if controller <= pPickPecrentage * 100:
        return True
    else:
        return False

def generateManu(pMaxManu):
    allManu = []
    seedManu = []
    seedManuMax = random.randint(1,pMaxManu)
    for i in range(0, manufactureCount):
        allManu.append(i+1)
    random.shuffle(allManu)
    for i in range(0, seedManuMax):
        seedManu.append(allManu[0])
        allManu.pop(0)
    allManu.clear()
    return seedManu


#03-18-19：40
#好友和店铺的浏览次数之间的联系关系：
#对于一对好友来说，会有共同访问的店铺列表
#计算两个好友对共同访问的店铺访问数之和m和共同访问的店铺的总访问数之和n
#依次计算本人和其他所有不是好友的人共同访问的店铺访问数之和m1和共同访问的店铺的总访问数之和n1
#m/n应该大于大部分的m1/n1

#03-19-15：31
# m是每个用户选择的商店，对每个店铺-用户都要随机生成一个访问量
# 对每个用户：
# 针对每一个好友关系，找到它们两个的共同访问商店，给这些商店加上某个数
# 针对每个非好友关系，找到两个的共同访问商店，给这些商店减去某个数

def generateUMV2(pMaxFriends, pMaxManu, pPickPecrentage, pThreshold, pMaxViewCount, pIsNegative):
    g = generateFriends(pMaxFriends)
    m = list(range(0,userCount))
    threshold = [pThreshold] * userCount
    m[0] = generateManu(pMaxManu)
    for i in range(1, userCount+1):
        friends = g.adjacentTo(str(i))
        if m[i-1] == i-1:
            #我自己都没有东西,得给自己生成一些，然后再给朋友
            m[i-1] = generateManu(pMaxManu)
        #现在我有东西了
        #检查到没到阈值，没到才能继续传播
        if threshold[i-1] > 0:
            for j in friends:
                friendManu = m[int(j)-1]
                if m[int(j)-1] == int(j)-1:
                    #说明朋友还没有东西，先生成一些
                    friendManu = generateManu(pMaxManu)
                #然后，混入我传播的内容
                for k in m[i-1]:
                    if percentControl(pPickPecrentage) == True:
                        friendManu.append(int(k))        
                #检查长度是否超过最大限制
                if len(friendManu) > pMaxManu:
                    random.shuffle(friendManu)
                    cut = random.randint(1, pMaxManu)
                    m[int(j)-1] = friendManu[0:cut+1]
            #我自己的阈值减1
            threshold[i-1] -= 1
    #----------------接下来是生成点击量的逻辑-------------------
    v = []
    temp = {}
    allPeople = []
    for i in range(1, userCount+1):
        allPeople.append(str(i))
        for j in m[i-1]:
            #temp.append(random.randint(int(pMaxViewCount/50), pMaxViewCount))
            temp[j] = random.randint(int(pMaxViewCount/50), pMaxViewCount)
        v.append(temp)
        temp = {}
    allPeople = set(allPeople)
    divider = (0.1 if(pIsNegative == False) else 10)
    for i in range(1, userCount+1):
        friends = g.adjacentTo(str(i))
        #找出共同的店铺,访问采用int(j)-1
        for j in friends:
            intersection = set(m[int(j)-1]) & set(m[i-1])
            for k in intersection:
                v[int(j)-1][k] += random.randint(1, pMaxViewCount * divider)
                v[i-1][k] += random.randint(1, pMaxViewCount * divider)
        #对于不是朋友的 共同访问的店铺-1
        if pIsNegative == True:
            notFriend = list(allPeople - set(friends))
            for j in notFriend:
                intersection = set(m[int(j)-1]) & set(m[i-1])
                for k in intersection:
                    v[int(j)-1][k] -= random.randint(1, pMaxViewCount/10)
                    v[i-1][k] -= random.randint(1, pMaxViewCount/10)
    
    #----------------点击量生成逻辑结束------------------------
    f = open(dirX+"gen\\User-Manu-ViewCount.dat",'w+')
    f.write("userID manufactureID viewCount\n")
    for i in range(1, userCount+1):
        #center = random.randint(int(pMaxViewCount/50), pMaxViewCount)
        for j in m[i-1]:
            f.writelines(str(i)+" "+str(j)+" "+str(v[i-1][j])+"\n")
    f.close()
    threshold.clear()
    return m

#03-14-20:55
# 目前朋友选择的商家有一定的相似性
# 维护一个list，里面是每个商家所销售的所有标签
# 对于第一个人，随机初始化他选的第一个商家的一些标签
# 读出他选的其他商家，将这些商家里的所有标签与初始标签做交集
# 在交集中选出一定比例的标签，再与不在交集中的一些标签做混合
# 这是新的所选标签，依次向下传播

def generateMC(pMaxCate):
    c = []
    limit = random.randint(1,pMaxCate)
    for i in range(0, pMaxCate):
        c.append(i+1)
    random.shuffle(c)
    for i in range(0, limit):
        c.append(c[0])
    return c


def generateUMCT2(pMaxFriends, pMaxManu, pPickPecrentage, pThreshold, pMaxCate, pTagPercentage, pMaxViewCount, pStartYear, pEndYear, pMinLoop, pMaxLoop, pIsNegative=False):
    manuList = generateUMV2(pMaxFriends, pMaxManu, pPickPecrentage, pThreshold, pMaxViewCount, pIsNegative)
    c = []
    f = open(dirX+"gen\\User-Manu-Cate-TimeStamp.dat",'w+')
    f.write("userId manufactureId categoryId timeStamp\n")
    #创建所有制造商提供的各种标签
    for i in range(0, manufactureCount):
        c.append(generateMC(pMaxCate))
    #对于每个人，都做上面的操作
    for i in range(0, userCount):
        singleManu = manuList[i]   
        sets = []
        for j in singleManu:
            sets.append(set(c[j-1]))
        limit = random.randint(1, pMaxCate)
        t = list(sets[0])
        random.shuffle(t)
        time = convertTime(pStartYear, pEndYear, pMinLoop, pMaxLoop)
        random.shuffle(time)
        for j in range(0, limit):
            f.writelines(str(i+1)+" "+str(singleManu[0])+" "+str(t[0])+" "+str(time[0])+"\n")
            t.pop(0)
        for j in range(0, len(singleManu)-1):
            ands = sets[j] & sets[j+1]
            excepts = list(sets[j+1] - ands)
            for k in list(ands):
                if percentControl(pTagPercentage) == True:
                    random.shuffle(time)
                    f.writelines(str(i+1)+" "+str(singleManu[j+1])+" "+str(k)+" "+str(time[0])+"\n")
            for k in excepts:
                if percentControl(1-pTagPercentage) == True:
                    random.shuffle(time)
                    f.writelines(str(i+1)+" "+str(singleManu[j+1])+" "+str(k)+" "+str(time[0])+"\n")
    f.close()

#！！---注意：该函数已经不再使用！---
def generateUMCT(pMaxCate, pMaxManu, pMaxViewCount, pStartYear, pEndYear, pMinLoop, pMaxLoop):
    f = open("User-Manufacture-Category-TimeStamp.dat",'w+')
    f.write("userId manufactureId categoryId timeStamp\n")

    af = open("User-Manufacture-ViewCount.dat",'w+')
    af.write("userId manufactureId ViewCount\n")

    #num = input("请输入用户数：")
    num = int(userCount)
    #build manufacture-category relationship
    m = []#m是运营商-类别二维数组
    c = []
    for i in range(0, manufactureCount):
        maxC = random.randint(1, pMaxCate)
        for j in range(0, maxC):
            #pMaxCat是一个供应商最多提供多少种商品
            c.append(random.randint(1, categoryCount))
        m.append(c)
        c=[]
    #user select manufacture
    for i in range(1,int(num)+1):
        maxM = random.randint(1, pMaxManu)
        #maxM是当前用户选择供应商的数目，pMaxManu是一个用户最多可以选择多少供应商。
        t = convertTime(pStartYear, pEndYear, pMinLoop, pMaxLoop)
        for j in range(0, maxM):#for each manufacture
            currManu = random.randint(1, manufactureCount)
            currViewCount = random.randint(1, pMaxViewCount)
            #03-13-17:28 原来是m[j-1]，有必要改为m[currManu]吗？
            for k in m[currManu-1]:#对每个供应商里的所有类别
                if(random.randint(0,1) == 1):
                    random.shuffle(t)
                    f.writelines(str(i)+" "+str(currManu)+" "+str(k)+" "+str(t[0])+"\n")
            #下面为顾客浏览的每个供应商随机赋浏览次数，最大为pMaxViewCount个
            af.writelines(str(i)+" "+str(currManu)+" "+str(currViewCount)+"\n")
    f.close()
    af.close()

#03-14-14:20
#两个好友应该多次浏览同一供应商\同一类别, 浏览次数相似
#两个好友购买的类别应该相近, 在同一家供应商购买的相同货物的类别应该占比较大

def generateFriends(pMaxFriends):
    #!!---该函数应先于其他生成函数执行！---
    f = open(dirX+"User-Friends-temp.dat",'w+')
    for i in range(1, int(userCount)+1):
        users = list(range(1, userCount+1))
        maxFriends = random.randint(1, pMaxFriends)
        #maxFriends是当前用户的朋友数
        users.remove(i)
        for j in range(0, maxFriends):
            random.shuffle(users)
            f.writelines(str(i)+" "+str(users[0])+"\n")
            users.pop(0)
    f.close()
    tempFile = dirX + "User-Friends-temp.dat"
    graph = g.Graph(tempFile)
    nf = open(dirX+"gen\\User-Friends.dat",'w+')
    nf.write("userId friendsID\n")
    for i in range(1, int(userCount)+1):
        at = graph.adjacentTo(str(i))
        for k in at:
            nf.writelines(str(i)+" "+k+"\n")
    nf.close()
    return graph





if __name__ == "__main__":
    manufactureCount = int(input("请输入供货商的数目："))
    categoryCount = int(input("请输入全网商品类别数："))
    userCount = int(input("请输入电商用户数目："))
    pMaxCate = int(input("请输入一个供应商最多能提供的商品类型数："))
    pMaxManu = int(input("请输入一个用户最多访问过多少店铺："))
    #03-14-22：25
    pMaxViewCount = int(input("请输入一个用户在同一个店铺的浏览次数基准："))
    #03-19-17:15
    pIsNegative = bool(input("请输入浏览次数是否允许负数，允许（True）会增大浏览次数差距，甚至会出现负数："))
    pMaxFriends = int(input("请输入一个用户的朋友数目基准："))
    pPickPercentage = float(input("请输入店铺在朋友间传播时的保留百分比，以小数输入："))
    pThreshold = int(input("请输入店铺在朋友间传播时的最高传播次数："))
    pTagPercentage = float(input("请输入标签在店铺间传递时的保留百分比，以小数输入："))
    print("下面产生时间戳。请输入时间戳开始、结束的年份。\n如2019开始，2020结束，程序将会产生从2019年年初到2020年年底共2年中产生时间戳")
    pStartYear = int(input("请输入时间戳开始的年份："))
    pEndYear = int(input("请输入时间戳结束的年份："))
    pMinLoop = int(input("请输入该用户时间戳变化的最小次数："))
    pMaxLoop = int(input("请输入该用户时间戳变化的最大次数："))
    generateCategory()
    generateManufacture()
    generateUMCT2(pMaxFriends, pMaxManu, pPickPercentage, pThreshold, pMaxCate, pTagPercentage, pMaxViewCount, pStartYear, pEndYear, pMinLoop, pMaxLoop, pIsNegative)

    # userCount = 500
    # # # #generateFriends(20)
    # manufactureCount = 20
    # # categoryCount = 5000
    # # # #generateUM(10, 10, 0.3, 9)
    # # generateUMCT2(10, 15, 0.6, 9, 20, 0.7, 1000, 2018, 2019, 3, 9)
    # generateUMV2(10, 10, 0.8, 7, 50, True)