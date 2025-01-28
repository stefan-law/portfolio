# Name: Stefan Law
# Course: CS325: Analysis of Algorithms
# Date: 11/14/2024

import heapq


def solve_puzzle(board: list[list[str]],
                 source: tuple[int, int],
                 destination: tuple[int, int]) -> tuple[list[tuple[int, int]], str] | None:
    """
    Utilizes BFS to determine one of the shortest routes through an m x n puzzle containing empty cells marked "-" and
    blocked cells marked "#" from the coordinates provided by source to the coordinates provided by destination. If no
    path is found, the function returns None. If the source and destination are the same, that cell coordinate is returned.
    :param board:
    :param source:
    :param destination:
    :return:
    """

    # Initialization
    pq = []  # Min-heap priority queue
    n = len(board)
    m = len(board[0])
    visited = [[(False, None) for col in range(m)] for row in range(n)]
    source_x = source[0]
    source_y = source[1]
    path = [(source_x, source_y)]
    heapq.heappush(pq, (0, source, path))
    visited[source_x][source_y] = (True, path, '')

    # Loop until pq is empty or we reach destination
    while pq:
        priority, (cell_x, cell_y), path = heapq.heappop(pq)
        # Check if we are at our destination
        if (cell_x, cell_y) == destination:
            return (visited[cell_x][cell_y][1], visited[cell_x][cell_y][2])



        # Process neighbors of current cell
        # Check up
        if cell_x - 1 >= 0 and not visited[cell_x-1][cell_y][0]:
            if board[cell_x-1][cell_y] != '#':
                # Push valid neighbor to queue and give it a path, mark as visited
                new_path = path.copy()
                new_path.append((cell_x - 1, cell_y))
                heapq.heappush(pq, (0, (cell_x - 1, cell_y), new_path))
                directions = visited[cell_x][cell_y][2][:]
                directions += 'U'
                visited[cell_x-1][cell_y] = (True, new_path, directions)
            else:
                visited[cell_x-1][cell_y] = (True, None)


        # Check down
        if cell_x + 1 < n and not visited[cell_x+1][cell_y][0]:
            if board[cell_x+1][cell_y] != '#':
                # Push valid neighbor to queue and give it a path, mark as visited
                new_path = path.copy()
                new_path.append((cell_x+1, cell_y))
                heapq.heappush(pq, (0,(cell_x+1, cell_y),new_path))
                directions = visited[cell_x][cell_y][2][:]
                directions += 'D'
                visited[cell_x+1][cell_y] = (True, new_path, directions)
            else:
                visited[cell_x+1][cell_y] = (True, None)

                # Check left
        if cell_y - 1 >= 0 and not visited[cell_x][cell_y-1][0]:
            if board[cell_x][cell_y-1] != '#':
                # Push valid neighbor to queue and give it a path, mark as visited
                new_path = path.copy()
                new_path.append((cell_x, cell_y-1))
                heapq.heappush(pq, (0, (cell_x, cell_y-1), new_path))
                directions = visited[cell_x][cell_y][2][:]
                directions += 'L'
                visited[cell_x][cell_y-1] = (True, new_path, directions)
            else:
                visited[cell_x][cell_y-1] = (True, None)

        # Check right
        if cell_y + 1 < m and not visited[cell_x][cell_y+1][0]:
            if board[cell_x][cell_y+1] != '#':
                # Push valid neighbor to queue and give it a path, mark as visited
                new_path = path.copy()
                new_path.append((cell_x, cell_y + 1))
                heapq.heappush(pq, (0, (cell_x, cell_y + 1), new_path))
                directions = visited[cell_x][cell_y][2][:]
                directions += 'R'
                visited[cell_x][cell_y+1] = (True, new_path, directions)
            else:
                visited[cell_x][cell_y+1] = (True, None)

    # pq is empty and no valid path was found
    return None

if __name__ == "__main__":
    puzzle = [
        ['-', '-', '-', '-', '-'],
        ['-', '-', '#', '-', '-'],
        ['-', '-', '-', '-', '-'],
        ['#', '-', '#', '#', '-'],
        ['-', '#', '-', '-', '-']
    ]
    print(solve_puzzle(puzzle, (0, 2), (2, 2)))
    print(solve_puzzle(puzzle, (0, 0), (4, 4)))
    print(solve_puzzle(puzzle, (0, 0), (4, 0)))
    print(solve_puzzle(puzzle, (0, 0), (0, 0)))
