import math
import random
import bisect

import pygame
import os
import config
import operator

from structure import Node, findMST, costMST, makeGraph
class BaseSprite(pygame.sprite.Sprite):
    images = dict()

    def __init__(self, x, y, file_name, transparent_color=None, wid=config.SPRITE_SIZE, hei=config.SPRITE_SIZE):
        pygame.sprite.Sprite.__init__(self)
        if file_name in BaseSprite.images:
            self.image = BaseSprite.images[file_name]
        else:
            self.image = pygame.image.load(os.path.join(config.IMG_FOLDER, file_name)).convert()
            self.image = pygame.transform.scale(self.image, (wid, hei))
            BaseSprite.images[file_name] = self.image
        # making the image transparent (if needed)
        if transparent_color:
            self.image.set_colorkey(transparent_color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


class Surface(BaseSprite):
    def __init__(self):
        super(Surface, self).__init__(0, 0, 'terrain.png', None, config.WIDTH, config.HEIGHT)


class Coin(BaseSprite):
    def __init__(self, x, y, ident):
        self.ident = ident
        super(Coin, self).__init__(x, y, 'coin.png', config.DARK_GREEN)

    def get_ident(self):
        return self.ident

    def position(self):
        return self.rect.x, self.rect.y

    def draw(self, screen):
        text = config.COIN_FONT.render(f'{self.ident}', True, config.BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


class CollectedCoin(BaseSprite):
    def __init__(self, coin):
        self.ident = coin.ident
        super(CollectedCoin, self).__init__(coin.rect.x, coin.rect.y, 'collected_coin.png', config.DARK_GREEN)

    def draw(self, screen):
        text = config.COIN_FONT.render(f'{self.ident}', True, config.RED)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


class Agent(BaseSprite):
    def __init__(self, x, y, file_name):
        super(Agent, self).__init__(x, y, file_name, config.DARK_GREEN)
        self.x = self.rect.x
        self.y = self.rect.y
        self.step = None
        self.travelling = False
        self.destinationX = 0
        self.destinationY = 0

    def set_destination(self, x, y):
        self.destinationX = x
        self.destinationY = y
        self.step = [self.destinationX - self.x, self.destinationY - self.y]
        magnitude = math.sqrt(self.step[0] ** 2 + self.step[1] ** 2)
        self.step[0] /= magnitude
        self.step[1] /= magnitude
        self.step[0] *= config.TRAVEL_SPEED
        self.step[1] *= config.TRAVEL_SPEED
        self.travelling = True

    def move_one_step(self):
        if not self.travelling:
            return
        self.x += self.step[0]
        self.y += self.step[1]
        self.rect.x = self.x
        self.rect.y = self.y
        if abs(self.x - self.destinationX) < abs(self.step[0]) and abs(self.y - self.destinationY) < abs(self.step[1]):
            self.rect.x = self.destinationX
            self.rect.y = self.destinationY
            self.x = self.destinationX
            self.y = self.destinationY
            self.travelling = False

    def is_travelling(self):
        return self.travelling

    def place_to(self, position):
        self.x = self.destinationX = self.rect.x = position[0]
        self.y = self.destinationX = self.rect.y = position[1]

    # coin_distance - cost matrix
    # return value - list of coin identifiers (containing 0 as first and last element, as well)
    def get_agent_path(self, coin_distance):
        pass


class ExampleAgent(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        path = [i for i in range(1, len(coin_distance))]
        random.shuffle(path)
        return [0] + path + [0]

class Jocke(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        root = Node(None, [0])
        root.toVisit = [i for i in range(1, len(coin_distance))]
        queue = [root]
        minCost = math.inf
        minPath = []

        while len(queue):
            node = queue.pop(0)

            for coin in node.toVisit:
                child = Node(node, node.path + [coin])
                child.toVisit = [i for i in node.toVisit if i != coin]
                child.cost = node.cost + coin_distance[child.path[-1]][child.path[-2]]
                queue.append(child)

            if len(node.toVisit) == 0:
                #node.path.append(0)
                node.cost += coin_distance[node.path[-1]][0]
                if(node.cost < minCost):
                    minCost = node.cost
                    minPath = node.path

        return minPath + [0]


class Aki(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        toVisit = [i for i in range(1, len(coin_distance))]
        path = [0]
        while len(toVisit):
            currCoin = path[-1]
            nextCoin = -1
            minCost = math.inf
            for i in range(len(coin_distance[currCoin])):
                if minCost > coin_distance[currCoin][i] and i in toVisit:
                    minCost = coin_distance[currCoin][i]
                    nextCoin = i
            path.append(nextCoin)
            toVisit.remove(nextCoin)
        path.append(0)
        return path

class Uki(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        root = Node(None, [0])
        root.toVisit = [i for i in range(1, len(coin_distance))]
        nodes = len(coin_distance)*-1
        queue = [root]
        path = []
        while len(queue):
            node = queue.pop(0)
            #print(node.path, "cost: ", node.cost)
            if len(node.toVisit) == 0:
                path = node.path
                break

            for coin in node.toVisit:
                child = Node(node, node.path + [coin])
                child.toVisit = [i for i in node.toVisit if i != coin]
                child.cost = node.cost + coin_distance[child.path[-1]][child.path[-2]]
                child.len = node.len - 1
                child.lastCoin = coin
                queue.append(child)
                if child.len == nodes:
                    child.cost += coin_distance[child.path[-1]][0]


            queue.sort(key=operator.attrgetter('cost', 'len', 'lastCoin'))


        path.append(0)
        return path

class Micko(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):

        root = Node(None, [0])
        root.toVisit = [i for i in range(1, len(coin_distance))]
        #mst = findMST(coin_distance)

        queue = [root]
        path = []
        while len(queue):
            node = queue.pop(0)

            price = costMST(findMST(makeGraph(coin_distance, [i for i in node.path if i != 0])))

            if len(node.toVisit) == 0:
                path = node.path
                break

            for coin in node.toVisit:
                child = Node(node, node.path + [coin])
                child.toVisit = [i for i in node.toVisit if i != coin]
                child.cost = node.cost + coin_distance[child.path[-1]][child.path[-2]]
                child.price = child.cost + price
                child.len = node.len - 1
                child.lastCoin = coin
                queue.append(child)
            queue.sort(key=operator.attrgetter('price', 'len', 'lastCoin'))


        path.append(0)
        return path