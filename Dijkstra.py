import pygame
import sys
import random
import threading
import time

# 初始化 Pygame
pygame.init()

class Dijkstra:
    def __init__(self):
        
        self.initialize()
        self.level = 3
        self.width = 1200
        self.hight = 800
        self.grid_size = 20
        self.rows = self.hight // self.grid_size
        self.columns = self.width // self.grid_size

        # 创建窗口
        self.screen = pygame.display.set_mode((self.width, self.hight))
        pygame.display.set_caption("Dijkstra")

        # 定义颜色
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.blue = (0, 0, 255)
        self.green = (0, 255, 0)
        self.red = (255, 0, 0)
        self.yellow = (255, 255, 0)
        self.orange = (255, 165, 0)
        self.pink = (255, 0, 255)

        # 创建一个表示网格的二维数组
        self.grid = [[self.white for _ in range(self.width // self.grid_size)] for _ in range(self.hight // self.grid_size)]
        self.add_obstacles(self.level)
        self.thread1 = threading.Thread(target=self.work)
        self.thread1.start()

    def initialize(self):
        self.order = 1
        self.running = True
        self.distance_list = []    # [["13","12",15]]  ， 13: 表示行， 12表示列，15表示距离
        self.closed_list = []  # [{"13":"12"}] ，     13: 表示行， 12表示列
        self.father_list = [] # [["13","12","13", "15"]] ， 13为行，12为列， 后面两个为父节点的坐标
        self.start = []
        self.end = []
    
    def find_neighbors(self, node, distance): # ["13","12",15]
        
        # 获取当前node的距离
        # distance =self.get_distance(node)

        if distance == None:
            print("distance is None")
            return False

        # 字符格式 转成int 格式  “12” -->1 2
        row = int(node[0]) # 行
        col = int(node[1]) # 列
        neighbors = []     # 保存临时的相邻方格, [["x","y", g ]]
        obstacles = []     # 保存相邻方格中的障碍物 [["x", "y"]]

        """
            查看该索引相邻的8个点, x 为可通行方格， o为障碍物
            x  x  o
            o  s  x
            x  x  x
        """

        for i in range(row -1, row + 2):
            if i < 0 or i >= self.rows: # 说明超出了 行的边界
                continue
            for j in range(col -1, col + 2):
                if j < 0 or j >= self.columns:
                    continue
                if i == row and j == col:
                    continue
            
                if self.is_in_close_list(i, j):
                    continue
                
                if self.is_obstacle(i, j):
                    obstacles.append([str(i) , str(j)])
                    continue

                # 左上角， 右下角， 左下角， 右上角
                if (i < row and j < col) or (i > row and j > col) or (i > row and j < col) or (i < row and j > col):
                    neighbor = [str(i) , str(j), distance + 14]
                    neighbors.append(neighbor)
                else:
                    neighbor = [str(i) , str(j), distance + 10]
                    neighbors.append(neighbor)

        indices_to_remove = []
        # # 遍历障碍物
        for obstacle in obstacles:
            if (int(obstacle[0]) == row -1) and (int(obstacle[1]) == col):   # 障碍物在该点的正上方, 把左上角，右上角方格剔除
                for j in [col -1, col +1]:
                    # 遍历相邻点
                    for index in range(len(neighbors)):
                        if obstacle[0] == neighbors[index][0] and str(j) == neighbors[index][1]:
                            indices_to_remove.append(index)
                            
            elif (int(obstacle[0]) == row +1) and (int(obstacle[1]) == col): # 障碍物在该点的正下方， 把左右两侧的方格剔除
                for j in [col -1, col +1]:
                    # 遍历相邻点
                    for index in range(len(neighbors)):
                        if obstacle[0] == neighbors[index][0] and str(j) == neighbors[index][1]:
                            indices_to_remove.append(index)
                            
            elif (int(obstacle[0]) == row) and (int(obstacle[1]) == col -1): # 障碍物在该点的左侧， 左上角和左下角方格剔除
                for i in [row -1, row +1]:
                    # 遍历相邻点
                    for index in range(len(neighbors)):
                        if str(i) == neighbors[index][0] and  obstacle[1] == neighbors[index][1]:
                            indices_to_remove.append(index)
                           
            elif (int(obstacle[0]) == row) and (int(obstacle[1]) == col +1): # 障碍物在该点的右侧， 右上角和右下角方格剔除
                for i in [row -1, row +1]:
                    # 遍历相邻点
                    for index in range(len(neighbors)):
                        if str(i) == neighbors[index][0] and  obstacle[1] == neighbors[index][1]:
                            indices_to_remove.append(index)
                           
        indices_to_remove = list(set(indices_to_remove))
        for index in reversed(indices_to_remove):
            del neighbors[index]    
                
        # 遍历周围的方格
        for index in neighbors:
            result, distance, num = self.is_in_distance_list(index)
            if result: # 已存在, 判断是否有更小的距离值
                if index[2] < distance:
                    # 更新距离值以及父节点，
                    self.distance_list[num][2] = index[2]
                    self.set_father_list(index, node)
            else: 
                # 添加到distance_list中， 并设置距离值和父节点
                self.add_in_distance_list(index)
                self.set_father_list(index, node)
                self.rendering_grid(index) # 渲染方格
                #time.sleep(0.005)
       
        # 对distance_list 重新排序
        self.distance_list = sorted(self.distance_list, key=lambda x: x[2])
        return False, None
    
    def add_obstacles(self, level):
        if level == 1:
            self.generate_circle_obstacles()
        elif level == 2:
            self.generate_two_simple_obstacles()
        elif level == 3:
            self.generate_obstacles()
        elif level == 4:
            self.generate_one_simple_obstacles()
            
    def generate_circle_obstacles(self):
        for i in range(20,40):
            self.grid[10][i] = self.black
            self.grid[20][i] = self.black
        
        for i in range(10,20):
            self.grid[i][20] = self.black
            self.grid[i][39] = self.black
    
    def generate_two_simple_obstacles(self):
        for i in range(10,20):
            self.grid[i][20] = self.black
            self.grid[i][39] = self.black
    
    def generate_one_simple_obstacles(self):
        for i in range(10,20):
            self.grid[i][30] = self.black
            
    def is_in_close_list(self, x, y): #[{"13":"12"}]
        for dictionary in self.closed_list:
            for key, value in dictionary.items():
                if key == str(x) and value == str(y):
                    return True
        return False
    
    def is_in_distance_list(self, index):
        for i in range(len(self.distance_list)):
            if self.distance_list[i][0] == index[0] and self.distance_list[i][1] == index[1]:
                distance = self.distance_list[i][2]
                return True, distance, i # 返回true和距离值,和当前索引
        return False , None, None
    
    def rendering_grid(self, index):
        x = int(index[0])
        y = int(index[1])
        if x != self.end[0] or y != self.end[1]:  # 不对终点渲染
            self.grid[x][y] = self.pink

    def get_str_index(self, index):
        return [str(index[0]),str(index[1])]
    
    def add_in_distance_list(self, index):
        self.distance_list.append(index)
    
    def set_father_list(self, sun, father):
        for i in range(len(self.father_list)):
            if self.father_list[i][0] == sun[0] and self.father_list[i][1] == sun[1]:
                self.father_list[i][2] = father[0]
                self.father_list[i][3] = father[1]
                return
       
        self.father_list.append([sun[0], sun[1], father[0], father[1]])

    def find_paths(self, start):
        str_start  = self.get_str_index(start)

        # 起点的起点距离值设置为零
        str_start.append(0)                  
        self.distance_list.append(str_start)

        while len(self.distance_list) > 0:
            tem_dic = {}
            current_node = self.distance_list.pop(0)

            # 是否找到目标点
            if self.is_goal(current_node):
                self.rendering_path(current_node)
                return True
            
            tem_dic[current_node[0]] = current_node[1]
            self.closed_list.append(tem_dic)   

            # 查找相邻的点，将该点的索引
            self.find_neighbors(current_node, current_node[2])  
            
        return False
    
    def get_lasted_index(self):
        for i in range(len(self.distance_list)):
            if i == len(self.distance_list) - 1:
                return i
            elif self.distance_list[i][2] != self.distance_list[i+1][2]:
                return i 

    def rendering_path(self, node):
        while True:
            for item in self.father_list:
                if item[0] == node[0] and item[1] == node[1]:
                    node.clear()
                    node.append(item[2])
                    node.append(item[3])

                    # 起点
                    if node[0] == str(self.start[0]) and node[1] == str(self.start[1]): 
                        return
                    else:
                       self.grid[int(node[0])][int(node[1])] = self.green
                    break

    def work(self):
        while(self.running):
            while(self.order <= 2 and self.running):

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        return 
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        
                        x, y = event.pos
                        grid_x = x // self.grid_size # 列
                        grid_y = y // self.grid_size # 行

                        if self.is_obstacle(grid_y, grid_x):
                            print("障碍物，请重新选择")
                            continue

                        if self.order == 1:
                            self.start.append(grid_y)
                            self.start.append(grid_x)
                            self.grid[grid_y][grid_x] = self.blue
                        elif self.order == 2:
                            self.end.append(grid_y)
                            self.end.append(grid_x)
                            self.grid[grid_y][grid_x] = self.orange
                        # 更改对应栅格的颜色为蓝色
                        
                        self.order +=1

            if self.order == 3:
                result = self.find_paths(self.start)
                if result:
                    print("成功找到路径")
                else:
                    print("无法找到路径")

                jump = False
                while not jump:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            return 
                        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:   
                            self.grid = [[self.white for _ in range(self.width // self.grid_size)] for _ in range(self.hight // self.grid_size)]
                            self.add_obstacles(self.level)
                            self.initialize()
                            jump = True
    
    def is_obstacle(self, x, y):
        return self.grid[x][y] == self.black
    
    def is_goal(self,index):
        return int(index[0]) == self.end[0] and int(index[1]) == self.end[1]

    def draw_grid(self):
        # 根据二维数组绘制方格颜色
        for i, row in enumerate(self.grid):
            for j, color in enumerate(row):
                rect = pygame.Rect(j * self.grid_size, i * self.grid_size, self.grid_size, self.grid_size)
                pygame.draw.rect(self.screen, color, rect)

        # 绘制栅格线
        for x in range(0, self.width, self.grid_size):
            pygame.draw.line(self.screen, self.black, (x, 0), (x, self.hight))
        for y in range(0, self.hight, self.grid_size):
            pygame.draw.line(self.screen, self.black, (0, y), (self.width, y))

    def generate_obstacles(self):
        num_obstacles = 150
        for i in range(num_obstacles):
            obstacle = (random.randint(0, self.rows-1), random.randint(0, self.columns-1))
            self.grid[obstacle[0]][obstacle[1]] = self.black

    def loop(self):
        # 主循环
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 
                
            # 重新绘制栅格
            self.draw_grid()
            # 刷新显示
            pygame.display.flip()

if __name__ == "__main__":
    a_star = Dijkstra()
    a_star.loop()
