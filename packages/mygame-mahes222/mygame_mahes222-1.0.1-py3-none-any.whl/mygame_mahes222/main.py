class Board:

    def __init__(self, size):
        self.size = size
        self.grid = [['- ' for _ in range(size)] for _ in range(size)]
        self.position = [size - 1] * size

    def printgrid(self):
        for row in self.grid:
            visual = ""
            for cell in row:
                visual += cell
            print(visual)


    def fillcolor(self, column, color):
        current_col = column
        for i in range(len(color)):
            if self.position[current_col - 1] < 0:
                return False

            row = self.position[current_col - 1]
            self.grid[row][current_col - 1] = color[i] + " "
            self.position[current_col - 1] -= 1
            current_col = (current_col % self.size) + 1
        self.find_matches()
        return True

    def find_matches(self):
        directions = [
            [(0, 1), (0, -1)],
            [(1, 0), (-1, 0)],
            [(1, 1), (-1, -1)],
            [(1, -1), (-1, 1)]
        ]

        matches = []

        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] == "- ":
                    continue

                for drow in directions:
                    cells = [(r, c)]
                    for dr, dc in drow:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.size and 0 <= nc < self.size and self.grid[nr][nc] == self.grid[r][c]:
                            cells.append((nr, nc))

                    if len(cells) >= 3:
                        matches.append(cells)
        if not matches:
                return
        for match in matches:
            for (r, c) in match:
                self.grid[r][c] = "- "
        self.apply_gravity()
        self.find_matches()


    def apply_gravity(self):
        for c in range(self.size):
            stack = [self.grid[r][c] for r in range(self.size) if self.grid[r][c] != "- "]
            self.position[c] = self.size - 1 -len(stack)
            for r in range(self.size - 1, -1, -1):
                if stack:
                    self.grid[r][c] = stack.pop()
                else:
                    self.grid[r][c] = "- "



def main():
    try:
        size = int(input("Enter the size of the Box: "))
        g = Board(size)
        while True:
            column = int(input("Enter the column: "))
            color = input("Enter the color: ")
            if g.fillcolor(column, color):
                g.printgrid()
            else:
                print("Column filled.")
                break
    except ValueError:
        print("Enter a valid number for size")

if __name__ == "__main__":
    main()
