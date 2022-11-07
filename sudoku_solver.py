import tkinter
from tkinter import filedialog as fd
import tkinter.messagebox

#CONFIG
TITLE = "SudokuSolver"
ICON = "icon.ico"
SIZE = "270x320"
COLOR = "black"

class Datagrid:

    def __init__(self) -> None:

        self.grid = [[GridValue((row, column), "_") for column in range(9)] for row in range(9)]

    def copy(self):

        new_grid = Datagrid()
        for x, row in enumerate(self.grid):
            for y, gridval in enumerate(row):
                num = gridval.get_final_value()
                if num == "":
                    num = "_"
                new_grid.grid[x][y] = GridValue((x,y), num)

        return new_grid
        
    def print(self) -> None:
        for index, line in enumerate(self.grid):
            sline = [str(num.value) for num in line]
            print(" | ".join(sline))

    def check_row(self, row_index: int) -> dict:

        missing_nums = {1, 2, 3, 4, 5, 6, 7, 8, 9}
        for spot in self.grid[row_index]:
            if spot.value in missing_nums:
                missing_nums.discard(spot.value)

        return missing_nums

    def check_column(self, column_index: int) -> dict:

        missing_nums = {1, 2, 3, 4, 5, 6, 7, 8, 9}
        for i in range(9):
            num = self.grid[i][column_index].value
            if num in missing_nums:
                missing_nums.discard(num)

        return missing_nums

    def check_square(self, index: tuple) -> dict:

        missing_nums = {1, 2, 3, 4, 5, 6, 7, 8, 9}
        square_index = get_square_index(index)
        square_list = get_indices_from_square_index(square_index)

        for c in square_list:
            num = self.grid[c[0]][c[1]].value
            if num in missing_nums:
                missing_nums.discard(num)
        
        return missing_nums

    def missing_mumbers(self, index: tuple) -> list:

        row_set = self.check_row(index[0])
        column_set = self.check_column(index[1])
        square_set = self.check_square(index)

        return list(row_set & column_set & square_set)

    def calculate_all(self) -> bool:
        """Iterates trough the grid, calculates the missing values. Returns true, if the grid is changed"""
        grid_changed = False
        for row in self.grid:
            for gridval in row:
                if gridval.is_final():
                    continue
                missing = self.missing_mumbers(gridval.get_position())
                if len(missing) == 1:
                    gridval.set_final_value(missing[0])
                    grid_changed = True
                else:
                    gridval.set_possible_values(missing)
        return grid_changed

    def is_solved(self) -> bool:
        """Returns True if the grid is solved"""

        for row in self.grid:
            for spot in row:
                if not spot.is_final():
                    return False
        if not self.is_grid_valid():
            return False
        return True

    def unsolved_positions(self) -> list:
        """Returns a list of unsolved positions in the grid
        """
        unsolved = []
        for row in self.grid:
            for spot in row:
                if not spot.is_final():
                    unsolved.append(spot.get_position())
        return sorted(unsolved, key= lambda x: len(self.grid[x[0]][x[1]].get_possible_values()))               

    def is_grid_valid(self) -> tuple:

        for row in self.grid:
            for gridval in row:
                if not gridval.is_final():
                    continue
                num = gridval.get_final_value()
                row_values = [self.grid[gridval.get_position()[0]][column].get_final_value() for column in range(9) if column != gridval.get_position()[1]]
                if num > 9 or num < 1:
                    return (False, gridval.get_position())
                if num in row_values:
                    return (False, gridval.get_position())
                column_values = [self.grid[row][gridval.get_position()[1]].get_final_value() for row in range(9) if row != gridval.get_position()[0]]
                if num in column_values:
                    return (False, gridval.get_position())
                square_values = [self.grid[row][column].get_final_value() for row, column in get_indices_from_square_index(get_square_index(gridval.get_position())) if gridval.get_position() != (row, column)]
                if num in square_values:
                    return (False, gridval.get_position())
        return (True, ())

    def is_grid_unsolvable(self) -> tuple:

        for row in self.grid:
            for gridval in row:
                if gridval.is_final():
                    continue
                if not gridval.get_possible_values():
                    return (True, gridval.get_position())
        return (False, ())

    def solve(self) -> None:

        while self.calculate_all():
            pass
    
def get_square_index(ind: tuple) -> tuple:

    column = (ind[1]+3)//3-1
    row = (ind[0]+3)//3-1
    return (row, column)

def get_indices_from_square_index(ind) -> list:

    indices = []
    for i in range(3):
        for j in range(3):
            indices.append((ind[0]*3+i, ind[1]*3+j))

    return indices

def file_reader(filename: str) -> list:
    output = []
    with open(filename, 'r') as file:
        for row, line in enumerate(file):
            output.append([num if num.isnumeric() else " " for num in line.strip().split(';')])
    file.close()
    return output    

class GridValue:

    def __init__(self, pos:tuple, num: int) -> None:

        self.position = pos
        if num == "_":
            self.empty = True
            self.closed = False
            self.value = ""
        else:
            self.value = num
            self.closed = True
            self.empty = False
            
        self.possible_values = []

    def get_final_value(self) -> int:

        return self.value

    def set_final_value(self, value: int)-> None:

        self.value = value
        self.closed = True

    def is_final(self) -> bool:

        return self.closed

    def set_possible_values(self, numlist: list) -> None:
        
        self.possible_values = numlist

    def get_possible_values(self) -> list:

        return self.possible_values

    def get_position(self) -> tuple:

        return self.position

    def __str__(self) -> str:

        return f"is_final(): {self.closed} pos: {self.position}, value:{self.value}, possible values:{self.possible_values}"

class Node:

    def __init__(self, nodelist: list, index: int, grid: Datagrid) -> None:

        self.index = index
        self.parent = None
        if index > 0:
            self.parent = nodelist.array[index-1]
        self.grid = grid
        self.n = -1
        self.child_grid = None
        
    def get_grid(self) -> Datagrid:
        return self.grid

    def solve(self) -> bool:
        self.n += 1
        self.child_grid = None
        solved_grid = self.grid.copy()
        solved_grid.solve()
        if solved_grid.is_solved():                                             #If the grid is solved, returns True
            self.grid = solved_grid
            return True
        if solved_grid.is_grid_unsolvable()[0]:                                 #If the grid is unsolvable, returns
            return False
        x, y = solved_grid.unsolved_positions()[0]                              #Selects an unsolved field on the grid, where the list of potential numbers is the shortest
        poss_nums = solved_grid.grid[x][y].get_possible_values()                #Gets the possible values for the selected field
        if len(poss_nums) < self.n+1:                                           #If all possible values were tested for the field, return false
            return False
        test_value = poss_nums[self.n]                                          #selects the n-th element from the list
        self.child_grid = solved_grid
        self.child_grid.grid[x][y].set_final_value(test_value)                  #inserts the value into the new grid
        return False

class NodeList:

    def __init__(self, grid: Datagrid) -> None:

        self.startgrid = grid
        self.array = []
        self.array.append(Node(self, len(self.array), self.startgrid))
        self.solved_grid = None

    def solve_sudoku(self) -> None:                                             #Recursive method to solve the grid
        try:
            current_node = self.array[-1]                                       #Last Node from the list
        except IndexError:
            self.solved_grid = self.startgrid
            tkinter.messagebox.showerror("Invalid table", "The game is unsolvable!")
            return                                          
        if current_node.solve():
            self.solved_grid = current_node.grid
            return 
        if current_node.child_grid == None:                                     #Steps back to the previous node and discards the current
            self.array.pop()
            self.solve_sudoku()
        else:
            self.array.append(Node(self, len(self.array), current_node.child_grid)) #Creates a new node
            self.solve_sudoku()

class App(tkinter.Tk):

    def __init__(self) -> None:
        super().__init__()
        self.geometry(SIZE)
        self.title(TITLE)
        self.resizable(False, False)
        self.configure(bg=COLOR)
        self.datagrid = Datagrid()
        self.iconbitmap(ICON)
        self.init_components()
        
    def init_components(self) -> None:

        menubar = tkinter.Menu(self)
        filemenu = tkinter.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=self.clear_table)
        filemenu.add_command(label="Open", command=self.load_file)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.config(menu=menubar)
        self.entry_list = [[tkinter.Entry(self, font =('Arial 16'), fg = 'black' , justify='center') for i in range(9)] for j in range(9)]
        for row, line in enumerate(self.entry_list):
            for column, field in enumerate(line):
                self.place_entry_field(row, column)
        self.solve_button = tkinter.Button(self, text="Solve", command= self.calculate, state= tkinter.DISABLED)
        self.solve_button.place(x=274/2-45, y=270, width = 92, height = 30)
        self.check_button = tkinter.Button(self, text="Validate", command= self.read_in)
        self.check_button.place(x=0, y=270, width = 92, height = 30)
        clear_file_button = tkinter.Button(self, text="Clear", command= self.clear_table)
        clear_file_button.place(x=274-90, y=270, width = 91, height = 30)
        
    def load_file(self) -> None:
        
        filename = fd.askopenfilename()
        input = file_reader(filename)
        self.entry_list = [[tkinter.Entry(self, font =('Arial 16'), fg = 'black' , justify='center') for i in range(9)] for j in range(9)]
        for row, line in enumerate(self.entry_list):
            for column, field in enumerate(line):
                self.place_entry_field(row, column)
                field.insert(1, input[row][column])

    def calculate(self) -> None:

        self.refresh_values()
        valid, position = self.datagrid.is_grid_valid()
        if not valid:
            self.check_values()
            return
        node_list = NodeList(self.datagrid)
        try:
            node_list.solve_sudoku()
        except RecursionError as e:
            print(e)
        self.datagrid = node_list.solved_grid
        self.refresh_values()
        self.solve_button['state'] = tkinter.DISABLED

    def read_in(self) -> None:
        for x, row in enumerate(self.entry_list):
            for y, field in enumerate(row):
                value = self.entry_list[x][y].get()
                if value.isnumeric():
                    value = int(value)
                else:
                    value = "_"
                self.datagrid.grid[x][y] = GridValue((x, y), value)
        self.check_values()

    def check_values(self) -> None:

        valid, position = self.datagrid.is_grid_valid()
        if valid:
            self.solve_button['state'] = tkinter.NORMAL
            self.check_button['state'] = tkinter.DISABLED
            self.check_button['text'] = "✓" 
            return
        x,y = position
        self.entry_list[x][y]= tkinter.Entry(self, font =('Arial 16'), fg = 'red', bg = 'yellow' , justify='center')
        self.place_entry_field(x, y)
        self.entry_list[x][y].insert(1, str(self.datagrid.grid[x][y].get_final_value()))

    def refresh_values(self) -> None:
        for x, row in enumerate(self.datagrid.grid):
            for y, gridval in enumerate(row):
                if self.entry_list[x][y].get() != str(gridval.value):
                    self.entry_list[x][y]= tkinter.Entry(self, font =('Arial 16'), fg = 'blue', justify='center')
                    self.place_entry_field(x, y)
                    self.entry_list[x][y].insert(1, str(gridval.value))

    def clear_table(self) -> None:
        self.datagrid = Datagrid()
        for x, row in enumerate(self.datagrid.grid):
            for y, gridval in enumerate(row):
                if self.entry_list[x][y].get() != str(gridval.value):
                    self.entry_list[x][y]= tkinter.Entry(self, font =('Arial 16'), fg = 'black', justify='center')
                    self.place_entry_field(x, y)
        self.check_button['state'] = tkinter.NORMAL
        self.check_button['text'] = "Validate"       
    
    def place_entry_field(self, x: int, y: int) -> None:

        separator_width = 2
        self.entry_list[x][y].place(x=y*30+(y//3)*separator_width, y=x*30+(x//3)*separator_width, width = 30, height = 30)

if __name__ == "__main__":

    app = App()
    app.mainloop()

    

