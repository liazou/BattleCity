# 场景类
import pygame
import random
import numpy as np

# 石头墙
class Brick(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.brick = pygame.image.load('images/scene/brick.png')
		self.rect = self.brick.get_rect()
		self.being = False


# 钢墙
class Iron(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.iron = pygame.image.load('images/scene/iron.png')
		self.rect = self.iron.get_rect()
		self.being = False


# 冰
class Ice(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.ice = pygame.image.load('images/scene/ice.png')
		self.rect = self.ice.get_rect()
		self.being = False


# 河流
class River(pygame.sprite.Sprite):
	def __init__(self, kind=None):
		pygame.sprite.Sprite.__init__(self)
		if kind is None:
			self.kind = random.randint(0, 1)
		self.rivers = ['images/scene/river1.png', 'images/scene/river2.png']
		self.river = pygame.image.load(self.rivers[self.kind])
		self.rect = self.river.get_rect()
		self.being = False


# 树
class Tree(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.tree = pygame.image.load('images/scene/tree.png')
		self.rect = self.tree.get_rect()
		self.being = False

# 地图
class Map():
	directions = [(0,1),(1,0),(0,0),(1,1)]
	home_locations = [
		(x, y) for x in range(10, 16) for y in range(22, 26) if (x,y) not in [
			(12, 24), (12, 25), (13, 24), (13, 25) # home center
		]
	]
	number_rows = 25
	number_cols = 20

	def __init__(self, stage):
		self.brickGroup = pygame.sprite.Group()
		self.ironGroup  = pygame.sprite.Group()
		self.iceGroup = pygame.sprite.Group()
		self.riverGroup = pygame.sprite.Group()
		self.treeGroup = pygame.sprite.Group()

		self.create_home()
		prev_object = None

		self.map_object_type = [[None] * self.number_cols for _ in range(self.number_rows)]

		for (i, j) in [(0, 12), (12, 12), (24, 12)]:
			# 上中下路初始为钢墙降低难度
			self.create_map_object(Iron, self.ironGroup, i, j)

		for i in range(0, self.number_rows, 2):
			for j in range(2, self.number_cols, 2):
				if self.map_object_type[i][j] != None:
					continue
				prev_object = self.generate_random_map_object(i, j, stage, prev_object)

	def generate_random_map_object(self, x, y, stage, prev_object):
		map_object_list = [
			(Brick, self.brickGroup),
			(Iron, self.ironGroup),
			(Tree, self.treeGroup),
			(Ice, self.iceGroup),
			(River, self.riverGroup),
			(None, None)
		]

		neighbor_objects = []
		if x == 0 and y == 0:
			neighbor_objects.append(None)
		else:
			if x > 0:
				neighbor_objects.append(self.map_object_type[x-1][y])
			if y > 0: 
				neighbor_objects.append(self.map_object_type[x][y-1])
			if x > 0 and y > 0:
				neighbor_objects.append(self.map_object_type[x-1][y-1])

		stage_factor = 0.01**stage
		object_markov_matrix = {
			Brick: [0.4, 0.1, 0.1, 0.1, 0.1, 0.2],
			Iron: [0.1, 0.25 * (1 - stage_factor), 0.1, 0.1, 0.1, 0.35 * (1 + stage_factor)],
			Tree: [0.1, 0.1, 0.3, 0.1, 0.1, 0.3],
			Ice: [0.1, 0.1, 0.1, 0.3, 0.05, 0.3],
			River: [0.1, 0.1, 0.1, 0.1, 0.2 * (1 - stage_factor), 0.4 * (1 + stage_factor)],
			None: [0.35, 0.1, 0.1, 0.1, 0.1, 0.25],
		}

		neighbor_object_prob = [object_markov_matrix[obj] for obj in neighbor_objects]

		sample_object, objectGroup = random.choices(
			map_object_list, 
			# weights=object_markov_matrix[prev_object]
			weights=np.mean(neighbor_object_prob, axis=0)
		)[0]

		if sample_object:
			self.create_map_object(sample_object, objectGroup, x, y)
		
		return sample_object

	def create_map_object(self, initial_object, objectGroup, x, y):
		self.map_object_type[x][y] = initial_object
		for dx, dy in self.directions:
			object = initial_object()
			# if x + dx < self.number_rows and y + dy < self.number_cols:
			# 	self.map_object_type[x+dx][y+dy] = initial_object
			object.rect.left, object.rect.top = 3 + (x + dx) * 24, 3 + (y + dy) * 24
			object.being = True
			objectGroup.add(object)

	def create_home(self):
		for x, y in self.home_locations:
			self.brick = Brick()
			self.brick.rect.left, self.brick.rect.top = 3 + x * 24, 3 + y * 24
			self.brick.being = True
			self.brickGroup.add(self.brick)
	
	def protect_home(self):
		for x, y in self.home_locations:
			self.iron = Iron()
			self.iron.rect.left, self.iron.rect.top = 3 + x * 24, 3 + y * 24
			self.iron.being = True
			self.ironGroup.add(self.iron)
	
	def remove_home_protection(self):
		# 消除钢墙
		for each in self.ironGroup:
			x = (each.rect.left - 3) // 24
			y = (each.rect.top - 3) // 24
			if (x, y) in self.home_locations:
				each.being = False
				self.ironGroup.remove(each)			