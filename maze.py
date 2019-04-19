from random import randrange, shuffle, choice

aisle_base = '''\
 A                       B
  A                     B
   A                   B
CCCCADDDDDDDDDDDDDDDDDBEEEE
    |H               I|
    | H             I |
    |  H           I  |
    |JJJHKKKKKKKKKILLL|
    |   OP       QO   |
    |   ORPSSSSSQTO   |
    |   O W     W O   |
    |   O W     W O   |
    |   O W     W O   |
    |   O W     W O   |
    |   ORUSSSSSVTO   |
    |   OU       VO   |
    |JJJMKKKKKKKKKNLLL|
    |  M           N  |
    | M             N |
    |M               N|
CCCCFDDDDDDDDDDDDDDDDDGEEEE
   F                   G
  F                     G
 F                       G'''

passable = {
    'front': {
        'right': 0,
        'left': 1,
        'center': 1
    },
    'middle': {
        'right': 1,
        'left': 0,
        'center': 1
    },
    'back': {
        'right': 0,
        'left': 0,
        'center': 0,
    }
}
def ailse_from_passable_info(passable):
    #print(passable)
    aisle = aisle_base
    for key, flg_dict in passable.items():
        wall_u, wall_b, side = flg_dict['right'] and '  -' or r'/\ '
        a,b,c = (ord(i) for i in {'front':'BGE','middle':'INL','back':'QVT'}[key])
        aisle = aisle.translate(
             {a: wall_u, b: wall_b, c: side},
        )
        wall_u, wall_b, side = flg_dict['left'] and '  -' or r'\/ '
        a,b,c = (ord(i) for i in {'front':'AFC','middle':'HMJ','back':'PUR'}[key])
        aisle = aisle.translate(
             {a: wall_u, b: wall_b, c: side},
        )
        if flg_dict['center']:
            aisle = aisle.translate(
                {
                    'front': {ord('D'): ' ', ord('O'): '|'},
                    'middle': {ord('K'): ' ', ord('W'): '|'},
                    'back': {ord('S'): ' '}
                }[key]
            )
            continue
        aisle = aisle.translate(
            {
                'front': {**{i:' ' for i in range(ord('H'),ord('W')+1)},ord('D'):'-'},
                'middle': {**{i:' ' for i in range(ord('P'),ord('W')+1)},ord('K'):'-'},
                'back': {ord('S'):'-'}
            }[key]
        )
        break
    return aisle

def make_maze(size):
    p_size=size+1
    directs = [-1,p_size,-p_size,1] #←↓↑→
    if not(type(size) is int and size%2*size//5):
        raise ValueError(f'Invalid size:{size}')
    maze = [1]*(size*p_size)
    start = (p_size)*(randrange(size//2)*2+1) +randrange(size//2)*2+2
    def dig(s_pos):
        maze[s_pos]=0
        shuffle(directs)
        for direct in directs:
          p1,p2,p3 = (s_pos+direct*j for j in (1,2,3))
          if all(0<i<len(maze) and i%(p_size)*maze[i] for i in (p1,p2,p3)):
            maze[p1]=maze[p2]=0
            return p2
        return choice(
            [i for i,v in enumerate(maze)
            if (v-1)*((i//(p_size))*(i%(p_size)+1))%2
        ])
    C = (size-3)*(size-1)//2+(size-2)
    while maze.count(0) < C:
        start=dig(start)
    return maze
    
class Maze:
    def __init__(self, size):
        self.size = size
        self.maze = make_maze(size)
        self.current_coord = [0,0]
        self.current_ang = 1
        self.mapped_index_set = {1,2,3}
        self.mapping()
    
    @property
    def current_index(self):
        return self.coord_to_index(self.current_coord)
    
    def coord_to_index(self, coord):
        #print(coord)
        x,y = coord
        if x<0:
            x=-1
        elif x>self.size-3:
            x = self.size-2
        if y<0:
            y=-1
        elif y>self.size-3:
            y = self.size-2
    
        index = 2+x+(y+1)*(self.size+1)
        if index<0:
            index = 0
        elif index > self.size*(self.size+1):
            index = self.size*(self.size+1)-1
        return index
        
    @property
    def current_cell(self):
        return self.maze[self.current_index]
    
    def move_forward(self, step=1):
        if not step:
            return
        for _ in range(step):
            old_coord = self.current_coord[:]
            self.current_coord[self.current_ang%2] += self.current_ang<2 or -1
            c = self.current_coord[self.current_ang%2]
            if 0<= c<self.size-2 and not self.current_cell:
                continue
            break
        else:
            self.mapping()
            return 
        self.current_coord = old_coord
        self.mapping()
        
    
    def turn_r(self):
        self.current_ang = (self.current_ang+1)%4
        self.mapping()
        
    def turn_l(self):
        self.current_ang = (self.current_ang-1)%4
        self.mapping()
    
    def get_full_map(self):
        maze = self.maze[:]
        maze[self.current_index] = 2
        size = self.size
        return '\n'.join(''.join(('◼️','◻️️',('▶️','🔽','◀️','🔼')[self.current_ang])[x] for x in maze[1+(1+size)*y:(1+size)*(y+1)])for y in range(size))
        
    def mapping(self):
        self.mapped_index_set.add(self.current_index)
        passable = self.get_forward_3block()
        fst_index_list, *index_list_list = self.get_forward_3block_index_list_list()
        self.mapped_index_set.update(fst_index_list)
        for key,block_index_list in zip(('front', 'middle'),index_list_list):
            center = block_index_list.pop()
            self.mapped_index_set.update(block_index_list)
            if not passable[key]['center']:
                break
            self.mapped_index_set.add(center)
    
    def get_mapped(self):
        maze = self.maze[:]
        size = self.size
        for i in self.mapped_index_set:
            maze[i] += 3
        maze[self.current_index] = 2
        
        return '\n'.join(
            ''.join(
                (
                    '🚫','🚫',
                    ('▶️','🔽','◀️','🔼')[self.current_ang],
                    '◼️','◻️️'
                )[x] for x in maze[1+(1+size)*y:(1+size)*(y+1)]
            )
            for y in range(size)
        )
        
    def get_forward_3block_index_list_list(self):
        x,y = self.current_coord
        if self.current_ang is 0:
            index_list_list = [
                [self.coord_to_index((x+i+(not j),y+j)) for j in [1,-1,0]]
                for i in [0,1,2]
            ]
        elif self.current_ang is 2:
            index_list_list = [
                [self.coord_to_index((x-i-(not j),y-j)) for j in [1,-1,0]]
                for i in [0,1,2]
            ]
        elif self.current_ang is 1:
            index_list_list = [
                [self.coord_to_index((x+j,y+i+(not j))) for j in [-1,1,0]]
                for i in [0,1,2]
            ]
        elif self.current_ang is 3:
            index_list_list = [
                [self.coord_to_index((x-j,y-i-(not j))) for j in [-1,1,0]]
                for i in [0,1,2]
            ]
        return index_list_list
    
    def get_forward_3block(self):
        block_index_list_list = self.get_forward_3block_index_list_list()
        passable = {
            key1: {
                key2: not self.maze[index]
                for key2,index in zip(('right','left','center'),block_index_list)
            }
            for key1, block_index_list in zip(('front','middle','back'),block_index_list_list)
        }
        return passable
    
    def get_aisle_aa(self):
        passable = self.get_forward_3block()
        aisle = ailse_from_passable_info(passable)
        return aisle

