import numpy as np
import collections
import heapq


class GridGraph:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def neighbors(self, position):
        neighbors = []

        # West
        if(position[0]-1 >= 0):
            neighbors.append((position[0]-1, position[1]))
        # North
        if(position[1]+1 < self.height):
            neighbors.append((position[0], position[1]+1))
        # East
        if(position[0]+1 < self.width):
            neighbors.append((position[0]+1, position[1]))
        # South
        if(position[1]-1 >= 0):
            neighbors.append((position[0], position[1]-1))

        return neighbors

    def cost(self, current, next):
        return 1

    def heuristic(self, a, b) -> float:
        (x1, y1) = a
        (x2, y2) = b
        return abs(x1 - x2) + abs(y1 - y2)
        # return np.linalg.norm(np.array(a)-np.array(b))

    def a_star_search(self, graph, start, goal):
        print("goal: ", goal)
        print("start: ", start)
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0

        while frontier:
            current = heapq.heappop(frontier)[1]

            if current == goal:
                break

            for next in graph.neighbors(current):
                new_cost = cost_so_far[current] + graph.cost(current, next)
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(next, goal)
                    heapq.heappush(frontier, (priority, next))
                    came_from[next] = current

        return came_from, cost_so_far

    def draw_tile(self, graph, id, style):
        r = " . "
        if 'number' in style and id in style['number']:
            r = " %-2d" % style['number'][id]
        if 'point_to' in style and style['point_to'].get(id, None) is not None:
            (x1, y1) = id
            (x2, y2) = style['point_to'][id]
            if x2 == x1 + 1:
                r = " < "
            if x2 == x1 - 1:
                r = " > "
            if y2 == y1 + 1:
                r = " ^ "
            if y2 == y1 - 1:
                r = " v "
        if 'path' in style and id in style['path']:
            r = " @ "
        if 'start' in style and id == style['start']:
            r = " A "
        if 'goal' in style and id == style['goal']:
            r = " Z "
        return r

    def draw_grid(self, graph, **style):
        print("___" * graph.width)
        for y in range(graph.height):
            for x in range(graph.width):
                print("%s" % self.draw_tile(graph, (x, y), style), end="")
            print()
        print("~~~" * graph.width)

    def breadth_first_search(self, graph, start, goal):
        frontier = collections.deque()
        frontier.append(start)
        came_from = {}
        came_from[start] = None

        while frontier:
            current = frontier.popleft()

            if current == goal:
                break

            for next in graph.neighbors(current):
                if next not in came_from:
                    frontier.append(next)
                    came_from[next] = current

        return came_from

    def dijkstra_search(self, graph, start, goal):
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {}
        cost_so_far = {}  # closed
        came_from[start] = None
        cost_so_far[start] = 0

        while frontier:
            current = heapq.heappop(frontier)[1]

            if current == goal:
                break

            for next in graph.neighbors(current):
                new_cost = cost_so_far[current] + graph.cost(current, next)
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost
                    heapq.heappush(frontier, (priority, next))
                    came_from[next] = current

        return came_from, cost_so_far

    def reconstruct_path(self, came_from, start, goal):
        current = goal
        path = []
        while current != start:
            path.append(current)
            current = came_from[current]
        path.append(start)  # optional
        path.reverse()  # optional
        return path

# Just for Debugging
# if __name__ == "__main__":
#     width = 10
#     height = 10

#     graph = GridGraph(width, height)

#     print(graph.neighbors([8, 9]))

#     start = (4, 0)
#     goal = (1, 3)

#     print("######### W szerz #############")
#     res = graph.breadth_first_search(graph, start, goal)
#     graph.draw_grid(graph, point_to=res, start=start, goal=goal)

#     print("######### Djikstra #############")
#     came_from, cost_so_far = graph.dijkstra_search(graph, start, goal)
#     graph.draw_grid(graph, point_to=came_from, start=start, goal=goal)
#     graph.draw_grid(graph, path=graph.reconstruct_path(came_from, start=start,
#                                                        goal=goal))

#     print("######### A* #############")
#     came_from, cost_so_far = graph.a_star_search(graph, start, goal)
#     graph.draw_grid(graph, point_to=came_from, start=start, goal=goal)
#     graph.draw_grid(graph, path=graph.reconstruct_path(came_from, start=start,
#                                                        goal=goal))
#     print(graph.reconstruct_path(came_from, start=start, goal=goal))
