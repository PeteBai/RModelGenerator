import random
import os
import uuid
import time
import graph as g

dirX = "C:\\Users\\surface\\OneDrive - CQU\\Project Sydney\\推荐系统数据生成a.61\\"

#依赖函数：为一个用户初始化一些艺术家
def generateArtists(pMaxArtists, artistsCount):
    allArtists = []
    seedArtists = []
    seedArtistsMax = random.randint(1, pMaxArtists)
    for i in range(0, artistsCount):
        allArtists.append(i+1)
    random.shuffle(allArtists)
    for i in range(0, seedArtistsMax):
        seedArtists.append(allArtists[0])
        allArtists.pop(0)
    allArtists.clear()
    return seedArtists

#依赖函数：以某一概率决定该项是否为1，否则为0
def percentControl(pPickPecrentage):
    controller = random.randint(1,100)
    if controller <= pPickPecrentage * 100:
        return True
    else:
        return False

#依赖函数：为一个艺术家生成一些标签
def generateAT(pMaxTag, tagCount):
    l = []
    c = []
    limit = random.randint(1,pMaxTag)
    for i in range(0, tagCount):
        c.append(i+1)
    random.shuffle(c)
    for i in range(0, limit):
        l.append(c[0])
        c.pop(0)
    c.clear()
    return l

#依赖函数：生成时间戳
def convertTime2(startYear, endYear):
    #maxLoop是系统最多要分配多少次不同标签
    YRS_IN_SEC = 31536000
    dts = str(startYear) + "-01-01 00:00:00"
    tss = time.mktime(time.strptime(dts, "%Y-%m-%d %H:%M:%S"))
    return (int(tss)+random.randint(0, (YRS_IN_SEC-1)*(endYear-startYear+1)))*1000


#用户-朋友
#该函数应先于其他生成函数执行！
#pMaxFriends - 每个人最多有多少朋友
#pUserCount - 用户数
def generateFriends(pMaxFriends, pUserCount):
    f = open(dirX+"User-Friends-temp.dat",'w+')
    for i in range(1, int(pUserCount)+1):
        users = list(range(1, pUserCount+1))
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
    nf = open(dirX+"gen\\user_friends.dat",'w+')
    nf.write("userID friendID\n")
    for i in range(1, int(pUserCount)+1):
        at = graph.adjacentTo(str(i))
        for k in at:
            nf.writelines(str(i)+" "+k+"\n")
    nf.close()
    return graph

#用户-艺术家-权重【参考用户-供应商-访问数】
#pMaxFriends - 每个人最多有多少朋友
#pMaxArtists - 每个人最多喜欢多少艺术家
#pPickPercentage - 艺术家在朋友间传播时保留的百分比
#pThreshold - 艺术家在朋友间传播的最多次数
#pMaxWeight - 一个用户对一位艺术家的最大权重
#pIsNegative - 权重是否允许出现负数
#pUserCount - 用户数
#pArtistsCount - 艺术家数
def generateUAW(pMaxFriends, pMaxArtists, pPickPecrentage, pThreshold, pMaxWeight, pIsNegative, pUserCount, pArtistsCount):
    g = generateFriends(pMaxFriends, pUserCount)
    m = list(range(0,pUserCount))
    threshold = [pThreshold] * pUserCount
    m[0] = generateArtists(pMaxArtists, pArtistsCount)
    for i in range(1, pUserCount+1):
        friends = g.adjacentTo(str(i))
        if m[i-1] == i-1:
            #我自己都没有东西,得给自己生成一些，然后再给朋友
            m[i-1] = generateArtists(pMaxArtists, pArtistsCount)
        #现在我有东西了
        #检查到没到阈值，没到才能继续传播
        if threshold[i-1] > 0:
            for j in friends:
                friendArtists = m[int(j)-1]
                if m[int(j)-1] == int(j)-1:
                    #说明朋友还没有东西，先生成一些
                    friendArtists = generateArtists(pMaxArtists, pArtistsCount)
                #然后，混入我传播的内容
                for k in m[i-1]:
                    if percentControl(pPickPecrentage) == True:
                        friendArtists.append(int(k))        
                #检查长度是否超过最大限制
                if len(friendArtists) > pMaxArtists:
                    random.shuffle(friendArtists)
                    cut = random.randint(1, pMaxArtists)
                    m[int(j)-1] = friendArtists[0:cut+1]
            #我自己的阈值减1
            threshold[i-1] -= 1
    #----------------接下来是生成点击量的逻辑-------------------
    v = []
    temp = {}
    allPeople = []
    for i in range(1, pUserCount+1):
        allPeople.append(str(i))
        for j in m[i-1]:
            #temp.append(random.randint(int(pMaxWeight/50), pMaxWeight))
            temp[j] = random.randint(int(pMaxWeight/50), pMaxWeight)
        v.append(temp)
        temp = {}
    allPeople = set(allPeople)
    divider = (0.1 if(pIsNegative == False) else 10)
    divider2 = int((1 if(pMaxWeight <= 1000) else pMaxWeight/1000))
    for i in range(1, pUserCount+1):
        friends = g.adjacentTo(str(i))
        #找出共同的店铺,访问采用int(j)-1
        for j in friends:
            intersection = set(m[int(j)-1]) & set(m[i-1])
            for k in intersection:
                v[int(j)-1][k] += random.randint(1, pMaxWeight * divider)
                v[i-1][k] += random.randint(1, pMaxWeight * divider)
        #对于不是访问朋友的共同的店铺-1
    
    #----------------点击量生成逻辑结束------------------------
    f = open(dirX+"gen\\user_artists.dat",'w+')
    f.write("userID artistID weight\n")
    for i in range(1, pUserCount+1):
        #center = random.randint(int(pMaxWeight/50), pMaxWeight)
        for j in m[i-1]:
            f.writelines(str(i)+" "+str(j)+" "+str(v[i-1][j])+"\n")
    f.close()
    threshold.clear()
    return (g, m)

#用户-标签【参考用户-类别，可以从UMCT中提取】
#用户-标签-艺术家-时间戳【就是UMCT】
#pMaxFriends - 每个人最多有多少朋友
#pMaxArtists - 每个人最多喜欢多少艺术家
#pPickPercentage - 艺术家在朋友间传播时保留的百分比
#pThreshold - 艺术家在朋友间传播的最多次数
#pMaxTag - 一个艺术家最多可以创造的歌曲类型
#pTagPercentage - 歌曲类型在艺术家中传播时保留的百分比
#pMaxWeight - 一个用户对一位艺术家的最大权重
#pStartYear - 产生时间戳的开始年份
#pEndYear - 产生时间戳的截至年份
#pIsNegative - 权重是否允许出现负数
#pUserCount - 用户数
#pArtistsCount - 艺术家数
#pTagCount - 标签总数
def generateUTAT(pMaxFriends, pMaxArtists, pPickPecrentage, pThreshold, pMaxTag, pTagPercentage, pMaxWeight, pStartYear, pEndYear, pIsNegative, pUserCount, pArtistsCount, pTagCount):
    (friendGraph, manuList) = generateUAW(pMaxFriends, pMaxArtists, pPickPecrentage, pThreshold, pMaxWeight, pIsNegative, pUserCount, pArtistsCount)
    c = []#c是供应商-类别列表
    umc = [-1] * pUserCount
    uct = [-1] * pUserCount#用户标签时间戳字典列表
    #创建所有制造商提供的各种标签
    for i in range(0, pArtistsCount):
        c.append(generateAT(pMaxTag, pTagCount))
    for i in range(0, pUserCount):
        #对每一个用户，检查其对应的标签集合是否为空
        if uct[i] == -1:
            #是空，按照顺序列表传播的方法生成
            singleManu = manuList[i]   
            sets = []
            for j in singleManu:
                sets.append(set(c[j-1]))
            t = list(sets[0])
            random.shuffle(t)
            mc = dict()
            singleC = []
            limit = random.randint(1, min(pMaxTag, len(t)))
            for j in range(0, limit):
                singleC.append(t[0])
                t.pop(0)
            mc[singleManu[0]] = singleC
            singleC = []
            for j in range(0, len(singleManu)-1):
                ands = sets[j] & sets[j+1]
                excepts = list(sets[j+1] - ands)
                for k in list(ands):
                    if percentControl(pTagPercentage) == True:
                        singleC.append(k)
                for k in excepts:
                    if percentControl(1-pTagPercentage) == True:
                        singleC.append(k)
                mc[singleManu[j+1]] = singleC
                singleC = []
            #现在我们拿到了该用户的供应商-类别字典
            umc[i] = mc
            singleC.clear()
            #现在不是空了，抽取标签集
            allUserTags = set()
            allUserTagTime = set()
            for value in umc[i].values():
                allUserTags = allUserTags | set(value)
            for tag in list(allUserTags):
                allUserTagTime.add((tag, convertTime2(pStartYear, pEndYear)))
            uct[i] = allUserTagTime
        friends = friendGraph.adjacentTo(str(i+1))
        for friend in friends:
            #拿到朋友的商店：
            friendManu = manuList[int(friend)-1]
            #拿到自己的标签-时间戳：
            myTagTime = dict(uct[i])
            myTag = set()
            #拿到自己的标签集
            for key in myTagTime:
                myTag.add(key)
            #拿到朋友选择的商店标签，在umc中
            friendChoice = umc[int(friend)-1]
            #如果朋友还没有选择，帮他选好
            if friendChoice == -1:
                newFriendChoice = dict()
                for j in friendManu:
                    #拿到朋友商店中的所有标签：
                    same = set(c[j-1]) & myTag
                    #建立该商店的标签列表
                    friendManuTag = []
                    for k in list(same):
                        if percentControl(pTagPercentage) == True:
                            friendManuTag.append(k)
                    diff = set(c[j-1]) - myTag
                    for k in list(diff):
                        if percentControl(pTagPercentage) == False:
                            friendManuTag.append(k)
                    newFriendChoice[j] = friendManuTag
                umc[int(friend)-1] = newFriendChoice
            #如果朋友选了，和他选的混在一起
            else:
                for key, value in friendChoice.items():
                    same = myTag & set(value)
                    diff = set(value) - myTag
                    for k in list(diff):
                        if percentControl(pTagPercentage) == True:
                            same.add(k)
                    friendChoice[key] = same
            #获取朋友的时间戳
            friendTime = dict()
            if uct[int(friend)-1] != -1:
                friendTime = dict(uct[int(friend)-1])
            newFriendTime = dict()
            friendChoice = umc[int(friend)-1]
            friendTagSet = set()
            #找出朋友所有的标签
            for value in friendChoice.values():
                friendTagSet = friendTagSet | set(value)
            for key in friendTagSet:
                if myTagTime.get(key) != None:#在我这里就用我的
                    newFriendTime[key] = myTagTime.get(key)
                    pass
                elif friendTime.get(key) != None:#在朋友那里但不在我这里
                    newFriendTime[key] = friendTime.get(key)
                else:
                    newFriendTime[key] = convertTime2(pStartYear, pEndYear)
            #uct[int(friend)-1] = tuple(newFriendTime)
            newFTimeTuple = []
            for key, value in newFriendTime.items():
                newFTimeTuple.append((key, value))
            uct[int(friend)-1] = newFTimeTuple
    f = open(dirX+"gen\\user_taggedartists-timestamps.dat",'w+')
    f2 = open(dirX+"gen\\user_tag_lastfm.dat",'w+')
    f2.write("userid tagid\n")
    for i in range(0, pUserCount):
        for j in uct[i]:
            f2.writelines(str(i+1)+" "+str(j[0])+"\n")
    f.write("userID artistID tagID timestamp\n")
    for i in range(0, pUserCount):
        #manuList, umc, uct
        for j in range(0, len(manuList[i])):
            for key, value in umc[i].items():
                for v in value:
                    for tu in uct[i]:
                        if tu[0] == v:
                            timestamp = tu[1]
                    f.writelines(str(i+1)+" "+str(key)+" "+str(v)+" "+str(timestamp)+"\n")
    f.close()
    f2.close()

#标签-用户数【从用户标签中反提取】
def generateTUn(pTagCount):
    f2 = open(dirX+"gen\\user_tag_lastfm.dat",'r')
    u = [0] * pTagCount
    for line in f2:
        if(line != "userid tagid\n"):
            u[int(line.split()[1])-1] += 1
    f2.close()
    f = open(dirX+"gen\\tag_usernum.dat",'w+')
    for i in range(0, pTagCount):
        f.writelines(str(i+1)+" "+str(u[i])+"\n")
    f.close()
        

if __name__ == "__main__":
    #generateUAW(10, 30, 0.9, 10, 20000, False, 300, 200)
    #generateUTAT(100, 30, 0.9, 10, 40, 0.97, 10000, 2017, 2019, False, 300, 200, 500)
    #generateTUn(500)
    artistsCount = int(input("请输入艺术家的数目："))
    tagCount = int(input("请输入歌曲类别数："))
    userCount = int(input("请输入用户数目："))
    pMaxTag = int(input("请输入一个艺术家最多能创作的歌曲类型数："))
    pMaxArtists = int(input("请输入一个用户最多收藏过多少艺术家："))
    pMaxWeight = int(input("请输入一个权重基准："))
    #pIsNegative = bool(input("请输入浏览次数是否允许负数，允许（True）会增大浏览次数差距，甚至会出现负数："))
    pMaxFriends = int(input("请输入一个用户的朋友数目基准："))
    pPickPercentage = float(input("请输入艺术家在朋友间传播时的保留百分比，以小数输入："))
    pThreshold = int(input("请输入艺术家在朋友间传播时的最高传播次数："))
    print("注意：在输入标签传播百分比时请保证在0.8以上，否则会出现许多用户出现空标签的情况。")
    pTagPercentage = float(input("请输入标签在艺术家间传递时的保留百分比，以小数输入："))
    print("下面产生时间戳。请输入时间戳开始、结束的年份。\n如2019开始，2020结束，程序将会产生从2019年年初到2020年年底共2年中产生时间戳")
    pStartYear = int(input("请输入时间戳开始的年份："))
    pEndYear = int(input("请输入时间戳结束的年份："))
    generateUTAT(pMaxFriends, pMaxArtists, pPickPercentage, pThreshold, pMaxTag, pTagPercentage, pMaxWeight, pStartYear, pEndYear, bool("false"), userCount, artistsCount, tagCount)
    generateTUn(tagCount)
