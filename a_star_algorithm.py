class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.position = (x, y)
        self.parent = None
        self.g = 0
        self.h = 0
        self.f = 0

def a_star(grid, start, end):
    open_list = []
    closed_list = []

    start_node = Node(start[0], start[1])
    end_node = Node(end[0], end[1])

    open_list.append(start_node)

    while open_list:
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        open_list.pop(current_index)
        closed_list.append(current_node)

        if current_node.position == end_node.position:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1]

        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            node_position = (current_node.x + new_position[0], current_node.y + new_position[1])

            if (
                node_position[0] > (len(grid) - 1)
                or node_position[0] < 0
                or node_position[1] > (len(grid[len(grid) - 1]) - 1)
                or node_position[1] < 0
            ):
                continue

            if grid[node_position[0]][node_position[1]] != 0:
                continue

            new_node = Node(node_position[0], node_position[1])
            children.append(new_node)

        for child in children:
            if child in closed_list:
                continue

            child.g = current_node.g + 1
            child.h = ((child.x - end_node.x) ** 2) + ((child.y - end_node.y) ** 2)
            child.f = child.g + child.h

            if len([open_node for open_node in open_list if child.position == open_node.position and child.g > open_node.g]) > 0:
                continue

            open_list.append(child)

    return None
