#-----------------------------------------------------------------------
# graph.py
# 图的数据结构，以邻接表的方式存储结点
#-----------------------------------------------------------------------
 
import sys
import stdio
from instream import InStream    #标准输入或文件输入统一类
import os
 
#-----------------------------------------------------------------------
 
class Graph:
    # 构造函数，通过按边方式构造图，文件每行形如"a1 a2"添加结点，边上的两个结点默认用空格字符作为分隔符
    def __init__(self, filename=None, delimiter=None):
        self._e = 0
        self._adj = dict()
        self.lpath = []
        if filename is not None:
            instream = InStream(filename)
            while instream.hasNextLine():
                line = instream.readLine()
                names = line.split(delimiter)
                for i in range(1, len(names)):
                    self.addEdge(names[0], names[i])
    # 通过按边添加结点的方式构造图
    def addEdge(self, v, w):
        if not self.hasVertex(v): self._adj[v] = set()
        if not self.hasVertex(w): self._adj[w] = set()
        if not self.hasEdge(v, w):
            self._e += 1
            self._adj[v].add(w)
            self._adj[w].add(v)
    #代返回结点v的所有邻结点
    def adjacentTo(self, v):
        ret = []
        for i in iter(self._adj[v]):
            ret.append(i)
        return ret
    
    # 返回所有结点
    def vertices(self):
        return iter(self._adj)
    
    # 如果含有v结点，返回True，否则False
    def hasVertex(self, v):
        return v in self._adj
    
    # 结点v,w间如果有边直连，返回True，否则False
    def hasEdge(self, v, w):
        return w in self._adj[v]
    
    # 返回结点总数
    def countV(self):
        return len(self._adj)
    
    # 返回边总数
    def countE(self):
        return self._e
    
    # 返回v结点的度
    def degree(self, v):
        return len(self._adj[v])
    #打印列表l
    def print_path(self, l):
        for x in l:
            print("%s -> "%x, end='')
        print("\n", end='')
    #打印从结点s到t的所有简单路径
    def allpath(self, s, t):
        self.lpath += [s]
        if(s==t):
            self.print_path(self.lpath)
        else:
            for v in self.adjacentTo(str(s)):
               if(v not in self.lpath): 
                    self.allpath(v, t)
            self.lpath.pop()
    
    # 重构打印类示例的函数
    def __str__(self):
        s = ''
        for v in self.vertices():
            s += v + '  '
            for w in self.adjacentTo(v):
                s += w + ' '
            s += '\n'
        return s
 
#-----------------------------------------------------------------------
 
def main():
    #file = sys.argv[1]
    file = "C:\\Users\\surface\\Desktop\\Project Sydney\\电商数据生成a.2\\graph\\User-Friends.dat"
    graph = Graph(file)
    #stdio.writeln(graph)
    print("all path:")
    graph.adjacentTo('5')
    


 
if __name__ == '__main__':
    main()

#版权声明：本文为CSDN博主「william_djj」的原创文章，遵循 CC 4.0 BY-SA 版权协议，转载请附上原文出处链接及本声明。
#原文链接：https://blog.csdn.net/william_djj/article/details/88619268