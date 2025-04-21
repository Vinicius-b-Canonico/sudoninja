import random
import copy
import math
import os

def print_verbose(verbose, *args):
    if verbose:
        print(*args)

def is_safe(grid, row, col, num, block_size, verbose=False):
    grid_size = block_size * block_size

    # Row & column check
    for x in range(grid_size):
        if grid[row][x] == num or grid[x][col] == num:
            print_verbose(verbose, f"Conflict with number {num} at row {row} or col {col}")
            return False

    # Block check
    start_row = (row // block_size) * block_size
    start_col = (col // block_size) * block_size

    for i in range(block_size):
        for j in range(block_size):
            if grid[start_row + i][start_col + j] == num:
                print_verbose(verbose, f"Conflict with number {num} in block starting at {start_row},{start_col}")
                return False

    return True

def fill_grid(grid, block_size, verbose=False):
    grid_size = block_size * block_size

    for i in range(grid_size):
        for j in range(grid_size):
            if grid[i][j] == 0:
                numbers = list(range(1, grid_size + 1))
                random.shuffle(numbers)
                for num in numbers:
                    if is_safe(grid, i, j, num, block_size, verbose):
                        grid[i][j] = num
                        if fill_grid(grid, block_size, verbose):
                            return True
                        grid[i][j] = 0
                return False
    return True

def has_any_solution(grid, block_size, verbose=False):
    grid_size = block_size * block_size

    for i in range(grid_size):
        for j in range(grid_size):
            if grid[i][j] == 0:
                for num in range(1, grid_size + 1):
                    if is_safe(grid, i, j, num, block_size, verbose):
                        grid[i][j] = num
                        if has_any_solution(grid, block_size, verbose):
                            return True
                        grid[i][j] = 0
                return False
    return True

def remove_numbers_with_validity_check(grid, block_size, cells_to_remove, verbose=False):
    grid_size = block_size * block_size
    removed = 0
    attempts = 0
    max_attempts = cells_to_remove * 10

    while removed < cells_to_remove and attempts < max_attempts:
        row = random.randint(0, grid_size - 1)
        col = random.randint(0, grid_size - 1)

        if grid[row][col] != 0:
            backup = grid[row][col]
            grid[row][col] = 0
            print_verbose(verbose, f"Trying to remove cell ({row}, {col})")

            grid_copy = copy.deepcopy(grid)
            if has_any_solution(grid_copy, block_size, verbose):
                print_verbose(verbose, f"Cell ({row}, {col}) removed successfully.")
                removed += 1
            else:
                print_verbose(verbose, f"Removal of cell ({row}, {col}) made puzzle unsolvable. Reverting.")
                grid[row][col] = backup

            attempts += 1

    print_verbose(verbose, f"Removed {removed} cells after {attempts} attempts.")
    return grid

def generate_sudoku(block_size=3, cells_to_remove=40, verbose=False, premade_blocks=None):
    grid_size = block_size * block_size
    grid = [[0 for _ in range(grid_size)] for _ in range(grid_size)]
    print_verbose(verbose, f"Starting Sudoku generation with {grid_size}x{grid_size} grid.")

    # Apply premade blocks before generation
    if premade_blocks:
        apply_premade_blocks(grid, block_size, premade_blocks, verbose)

    if not fill_grid(grid, block_size, verbose):
        raise Exception("Failed to generate a complete Sudoku grid.")

    solution = copy.deepcopy(grid)
    puzzle = remove_numbers_with_validity_check(grid, block_size, cells_to_remove, verbose)
    return puzzle, solution

def apply_premade_blocks(grid, block_size, premade_blocks, verbose=False):

    for (block_row, block_col), block_data in premade_blocks.items():
        start_row = block_row * block_size
        start_col = block_col * block_size

        for i in range(block_size):
            for j in range(block_size):
                val = block_data[i][j]
                if val != 0:
                    r, c = start_row + i, start_col + j
                    if grid[r][c] != 0:
                        raise ValueError(f"Cell ({r},{c}) already set while applying premade block.")
                    if not is_safe(grid, r, c, val, block_size, verbose):
                        raise ValueError(f"Premade block value {val} at ({r},{c}) causes a conflict.")
                    grid[r][c] = val
                    print_verbose(verbose, f"Inserted premade value {val} at ({r},{c})")

    return grid


def extract_block(grid, block_size, block_row, block_col):
    """Extracts a block (as a 2D list) from a Sudoku grid."""
    return [
        [
            grid[block_row * block_size + i][block_col * block_size + j]
            for j in range(block_size)
        ]
        for i in range(block_size)
    ]

def create_multi_sudoku(block_size=3, cells_to_remove=40, verbose=False):

    # Step 1: Generate the central game
    central_puzzle, central_solution = generate_sudoku(block_size, cells_to_remove, verbose)

    # Step 2: Extract corner blocks from central solution to use in other games
    corner_blocks = {
        "TL": extract_block(central_solution, block_size, 0, 0),                          # Top-left
        "TR": extract_block(central_solution, block_size, 0, block_size - 1),            # Top-right
        "BL": extract_block(central_solution, block_size, block_size - 1, 0),            # Bottom-left
        "BR": extract_block(central_solution, block_size, block_size - 1, block_size - 1) # Bottom-right
    }

    # Step 3: Generate the four diagonal puzzles using these as premade blocks
    diagonal_puzzles = {}

    premade_positions = {
        "TL": (block_size - 1, block_size - 1),  # Bottom-right of TL game
        "TR": (block_size - 1, 0),              # Bottom-left of TR game
        "BL": (0, block_size - 1),              # Top-right of BL game
        "BR": (0, 0),                           # Top-left of BR game
    }

    for key in ["TL", "TR", "BL", "BR"]:
        premade_blocks = {
            premade_positions[key]: corner_blocks[key]
        }
        puzzle, _ = generate_sudoku(block_size, cells_to_remove, verbose, premade_blocks)
        diagonal_puzzles[key] = puzzle

    # # Step 4: Print all 5 games
    # print("CENTRAL PUZZLE:")
    # print_grid(central_puzzle)

    # print("TOP LEFT DIAGONAL:")
    # print_grid(diagonal_puzzles["TL"])

    # print("TOP RIGHT DIAGONAL:")
    # print_grid(diagonal_puzzles["TR"])

    # print("BOTTOM LEFT DIAGONAL:")
    # print_grid(diagonal_puzzles["BL"])

    # print("BOTTOM RIGHT DIAGONAL:")
    # print_grid(diagonal_puzzles["BR"])


    combined = combine_grids_with_center(diagonal_puzzles["TL"], diagonal_puzzles["TR"], diagonal_puzzles["BL"], diagonal_puzzles["BR"],center=central_puzzle, block_size=block_size)
    # print(combined)

    return combined

def combine_grids(top_left, top_right, bottom_left, bottom_right, block_size):
    grid_size = block_size * block_size
    filler_width = (block_size - 2) * block_size

    big_grid = []

    # --- Top half ---
    for i in range(grid_size):
        left_row = top_left[i]
        right_row = top_right[i]
        filler = ['X'] * filler_width
        big_grid.append(left_row + filler + right_row)

    # --- Filler rows ---
    filler_row = ['X'] * (grid_size * 2 + filler_width)
    for _ in range(filler_width):
        big_grid.append(filler_row[:])  # copy to avoid accidental reference sharing

    # --- Bottom half ---
    for i in range(grid_size):
        left_row = bottom_left[i]
        right_row = bottom_right[i]
        filler = ['X'] * filler_width
        big_grid.append(left_row + filler + right_row)

    return big_grid

def combine_grids_with_center(top_left, top_right, bottom_left, bottom_right, center, block_size):
    grid_size = block_size * block_size
    filler_width = (block_size - 2) * block_size
    total_size = grid_size * 2 + filler_width

    big_grid = []

    # --- Top half ---
    for i in range(grid_size):
        left_row = top_left[i]
        right_row = top_right[i]
        filler = ['X'] * filler_width
        big_grid.append(left_row + filler + right_row)

    # --- Filler rows ---
    filler_row = ['X'] * (grid_size * 2 + filler_width)
    for _ in range(filler_width):
        big_grid.append(filler_row[:])  # copy to avoid accidental reference sharing

    # --- Bottom half ---
    for i in range(grid_size):
        left_row = bottom_left[i]
        right_row = bottom_right[i]
        filler = ['X'] * filler_width
        big_grid.append(left_row + filler + right_row)

    # Step 2: Overlay the center grid
    start_row = (total_size - grid_size) // 2
    start_col = (total_size - grid_size) // 2

    for i in range(grid_size):
        for j in range(grid_size):
            val = center[i][j]
            prev_val = big_grid[start_row + i][start_col + j]
            if val != 0 or prev_val == "X":
                big_grid[start_row + i][start_col + j] = val

    return big_grid

#====================================THIS ARE OUTPUT FUNCTIONS =============================================

# I THINK THIS ONE BELOW IS DEPRECATED
def print_multi_sudoku(multi_sudoku_dict, block_size):
    grid_size = block_size * block_size
    empty_block = [["X" for _ in range(grid_size)] for _ in range(grid_size)]

    # Shorthand access
    TL = multi_sudoku_dict["TL"]
    TR = multi_sudoku_dict["TR"]
    BL = multi_sudoku_dict["BL"]
    BR = multi_sudoku_dict["BR"]
    CT = multi_sudoku_dict["central"]

    def get_row_section(grid, row_idx):
        return grid[row_idx] if grid is not None else ["X"] * grid_size

    def format_row(cells, block_size):
        row_str = ""
        for i, val in enumerate(cells):
            if i % block_size == 0:
                row_str += "|"
            row_str += f" {val:2}" if val != "X" and val != 0 else "  ."
        row_str += "|"
        return row_str

    def horizontal_separator(block_size, num_blocks=3):
        return "+" + "+".join(["-" * (3 * block_size)] * num_blocks) + "+"

    total_rows = grid_size * 3  # 3 blocks vertically: TL/CT/BL

    for row in range(total_rows):
        if row % block_size == 0:
            print(
                horizontal_separator(block_size, 7)
            )  # full width across all 7 blocks (3 left, 1 mid, 3 right)

        row_parts = []

        # Top block row
        if row < grid_size:
            # TL - Empty - TR
            row_parts.extend([
                format_row(get_row_section(TL, row), block_size),
                format_row(get_row_section(empty_block, row), block_size),
                format_row(get_row_section(TR, row), block_size),
            ])
        elif row < grid_size * 2:
            # Middle block row - BL, Central, BR
            central_row = row - grid_size
            row_parts.extend([
                format_row(get_row_section(BL, central_row), block_size),
                format_row(get_row_section(CT, central_row), block_size),
                format_row(get_row_section(BR, central_row), block_size),
            ])
        else:
            # Bottom block row - Empty
            lower_row = row - grid_size * 2
            row_parts.extend([
                format_row(get_row_section(empty_block, lower_row), block_size),
                format_row(get_row_section(empty_block, lower_row), block_size),
                format_row(get_row_section(empty_block, lower_row), block_size),
            ])

        # Combine the 3-part row visually into 7 blocks (some are empty)
        print("".join(row_parts[:1]) +  # TL/BL/empty
              "".join(row_parts[1:2]) +  # middle blank or CT
              "".join(row_parts[2:]))   # TR/BR/empty

    print(horizontal_separator(block_size, 7))

def print_grid(grid, block_size=None):
    grid_size = len(grid)
    if block_size is None:
        block_size = int(math.sqrt(grid_size))

    horizontal_line = "+" + "+".join(["-" * (3 * block_size)] * block_size) + "+"

    for i, row in enumerate(grid):
        if i % block_size == 0:
            print(horizontal_line)
        row_str = ""
        for j, val in enumerate(row):
            if j % block_size == 0:
                row_str += "|"
            row_str += f" {val:2}" if val != 0 else "  ."
        row_str += "|"
        print(row_str)
    print(horizontal_line)

def stable_new_print_grid(grid, block_size, is_multi_sudoku=False):
    """
    Prints a formatted grid to the console.

    This function takes a grid (list of lists), formats it in a structured way, and prints the content to the console.
    The grid will be divided into blocks of size `block_size` by `block_size`, with special formatting for the values:
    - Values that are `0` are displayed as a dot (`.`).
    - Values that are `"X"` are displayed as `XX`.
    - Other values are displayed normally, padded to a width of 2 characters for neatness.
    The grid will be wrapped in horizontal lines (`+---+---+...`) for visual clarity, and vertical bars (`|`) separate the blocks.

    Parameters:
    -----------
    grid : list of list
        The 2D list that represents the grid, where each element is either a number or a special character like `"X"`.
        Example:
        [
            [1, 2, 3, 0],
            [4, 5, 6, 0],
            [7, 8, 9, 'X'],
            [0, 0, 0, 0]
        ]
        
    block_size : int
        The size of the blocks in the grid. It determines how large each block is. 
        For example, `block_size=3` means a 9x9 grid.

    Example usage:
    --------------
    grid = [
        [1, 2, 3, 0],
        [4, 5, 6, 0],
        [7, 8, 9, 'X'],
        [0, 0, 0, 0]
    ]
    print_grid(grid, 3)
    
    This will print the grid in a nicely formatted structure to the console.

    Output:
    -------
    A formatted grid will be printed to the console with horizontal lines, vertical bars, and properly formatted values.
    """

    full_block_size = block_size
    if is_multi_sudoku:
        full_block_size = block_size * 2 + (block_size-2)

    horizontal_line = "+" + "+".join(["-" * (3 * block_size)] * full_block_size) + "+"

    # Print the grid to the console
    for i, row in enumerate(grid):
        if i % block_size == 0:
            print(horizontal_line)
        row_str = ""
        for j, val in enumerate(row):
            if j % block_size == 0:
                row_str += "|"
            if val == 0:
                row_str += "  ."
            elif isinstance(val, str) and val.upper() == "X":
                row_str += " XX"
            else:
                row_str += f" {val:2}"
        row_str += "|"
        print(row_str)
    print(horizontal_line)

def new_print_grid(grid, block_size, is_multi_sudoku=False):
    """
    Prints a formatted grid to the console.

    This function takes a grid (list of lists), formats it in a structured way, and prints the content to the console.
    The grid will be divided into blocks of size `block_size` by `block_size`, with special formatting for the values:
    - Values that are `0` are displayed as a dot (`.`).
    - Values that are `"X"` are displayed as `XX`.
    - Other values are displayed normally, padded to a width of 2 characters for neatness.
    The grid will be wrapped in horizontal lines (`+---+---+...`) for visual clarity, and vertical bars (`|`) separate the blocks.
    
    Additionally, if the `is_multi_sudoku` flag is set to `True`, the grid will be formatted for a multi-sudoku layout,
    where additional filler spaces are inserted to separate blocks for a larger grid. This is useful when working with
    multi-sudoku or larger puzzle structures that include multiple grids.

    Parameters:
    -----------
    grid : list of list
        The 2D list that represents the grid, where each element is either a number or a special character like `"X"`.
        Example:
        [
            [1, 2, 3, 0],
            [4, 5, 6, 0],
            [7, 8, 9, 'X'],
            [0, 0, 0, 0]
        ]
        
    block_size : int
        The size of the blocks in the grid. It determines how large each block is. 
        For example, `block_size=3` means a 9x9 grid.

    is_multi_sudoku : bool, optional (default=False)
        A flag to indicate if the grid is part of a multi-sudoku layout. If `True`, the grid will be formatted with additional
        filler spaces to separate the blocks for multi-sudoku puzzles. This is typically used for puzzles that have multiple
        grids (e.g., larger or concatenated sudoku grids).

    Example usage:
    --------------
    grid = [
        [1, 2, 3, 0],
        [4, 5, 6, 0],
        [7, 8, 9, 'X'],
        [0, 0, 0, 0]
    ]
    print_grid(grid, 3, is_multi_sudoku=True)
    
    This will print the grid in a nicely formatted structure to the console, with additional filler spaces if multi-sudoku.

    Output:
    -------
    A formatted grid will be printed to the console with horizontal lines, vertical bars, and properly formatted values.
    If `is_multi_sudoku` is `True`, the grid will include additional filler spaces between blocks for a multi-sudoku layout.
    """

    full_block_size = block_size
    if is_multi_sudoku:
        full_block_size = block_size * 2 + (block_size-2)

    horizontal_line = "+" + "+".join(["-" * (3 * block_size)] * full_block_size) + "+"

    # Print the grid to the console
    for i, row in enumerate(grid):
        if i % block_size == 0:
            print(horizontal_line)
        row_str = ""
        for j, val in enumerate(row):
            if j % block_size == 0:
                row_str += "|"
            if val == 0:
                row_str += "  ."
            elif isinstance(val, str) and val.upper() == "X":
                row_str += " XX"
            else:
                row_str += f" {val:2}"
        row_str += "|"
        print(row_str)
    print(horizontal_line)


def stable_save_grid_to_file(grid, block_size, filename="combined_grid.txt"):
    """
    Saves a formatted grid to a text file.

    This function takes a grid (list of lists), formats it in a structured way, and saves the content to a file.
    The grid will be divided into blocks of size `block_size` by `block_size`, with special formatting for the values:
    - Values that are `0` are displayed as a dot (`.`).
    - Values that are `"X"` are displayed as `XX`.
    - Other values are displayed normally, padded to a width of 2 characters for neatness.
    The grid will be wrapped in horizontal lines (`+---+---+...`) for visual clarity, and vertical bars (`|`) separate the blocks.

    Parameters:
    -----------
    grid : list of list
        The 2D list that represents the grid, where each element is either a number or a special character like `"X"`.
        Example:
        [
            [1, 2, 3, 0],
            [4, 5, 6, 0],
            [7, 8, 9, 'X'],
            [0, 0, 0, 0]
        ]
        
    block_size : int
        The size of the blocks in the grid. It determines how large each block is. 
        For example, `block_size=3` means a 9x9 grid.

    filename : str, optional, default="combined_grid.txt"
        The name of the file to save the grid to. If not provided, the default file name is `"combined_grid.txt"`.

    Example usage:
    --------------
    grid = [
        [1, 2, 3, 0],
        [4, 5, 6, 0],
        [7, 8, 9, 'X'],
        [0, 0, 0, 0]
    ]
    save_grid_to_file(grid, 3)
    
    This will create a file "combined_grid.txt" with the formatted grid content.

    Output:
    -------
    A file will be created with the grid saved in a formatted structure.
    Additionally, the absolute path of the saved file will be printed to the console.

    """
    full_block_size = block_size * 2 + (block_size-2)  # since grid is now 2x width and height
    horizontal_line = "+" + "+".join(["-" * (3 * block_size)] * full_block_size) + "+"

    with open(filename, "w") as f:
        for i, row in enumerate(grid):
            if i % block_size == 0:
                f.write(horizontal_line + "\n")
            row_str = ""
            for j, val in enumerate(row):
                if j % block_size == 0:
                    row_str += "|"
                if val == 0:
                    row_str += "  ."
                elif isinstance(val, str) and val.upper() == "X":
                    row_str += " XX"
                else:
                    row_str += f" {val:2}"
            row_str += "|"
            f.write(row_str + "\n")
        f.write(horizontal_line + "\n")


    print(f"✅ Grid saved to: {os.path.abspath(filename)}")

def save_grid_to_file(grid, block_size, filename="combined_grid.txt", is_multi_sudoku=False):
    """
    Saves a formatted grid to a text file.

    This function takes a grid (list of lists), formats it in a structured way, and writes it to a text file.
    It divides the grid into blocks of size `block_size` by `block_size`, and optionally adds extra spacing for 
    multi-sudoku layouts (i.e., concatenated or composite sudoku grids).

    The grid uses the following formatting rules:
    - Values equal to `0` are shown as a dot (`.`).
    - Values equal to `"X"` (case-insensitive) are shown as `XX`.
    - All other values are shown padded to two characters (e.g., ` 7`, `10`).
    - Horizontal lines (`+---+---+...`) separate block rows.
    - Vertical bars (`|`) separate block columns.

    If `is_multi_sudoku` is True, the formatting adjusts to fit multi-grid sudoku layouts.

    Parameters:
    -----------
    grid : list of list
        The 2D list representing the grid. Each element is a number, zero, or a special character like `"X"`.

    block_size : int
        Size of one block in the grid. For example, `block_size=3` is used for standard 9x9 Sudoku.

    filename : str, optional (default="combined_grid.txt")
        Name of the file where the grid will be saved.

    is_multi_sudoku : bool, optional (default=False)
        If set to True, assumes the grid is a multi-sudoku (composed of multiple sudoku blocks) and adjusts the formatting accordingly.

    Example:
    --------
    grid = [
        [1, 2, 3, 0],
        [4, 5, 6, 0],
        [7, 8, 9, 'X'],
        [0, 0, 0, 0]
    ]
    save_grid_to_file(grid, 3, "output.txt", is_multi_sudoku=True)

    Output:
    -------
    A file will be created with the formatted grid content.
    The absolute path of the saved file will be printed to the console.
    """
    full_block_size = block_size
    if is_multi_sudoku:
        full_block_size = block_size * 2 + (block_size - 2)

    horizontal_line = "+" + "+".join(["-" * (3 * block_size)] * full_block_size) + "+"

    with open(filename, "w") as f:
        for i, row in enumerate(grid):
            if i % block_size == 0:
                f.write(horizontal_line + "\n")
            row_str = ""
            for j, val in enumerate(row):
                if j % block_size == 0:
                    row_str += "|"
                if val == 0:
                    row_str += "  ."
                elif isinstance(val, str) and val.upper() == "X":
                    row_str += " XX"
                else:
                    row_str += f" {val:2}"
            row_str += "|"
            f.write(row_str + "\n")
        f.write(horizontal_line + "\n")

    print(f"✅ Grid saved to: {os.path.abspath(filename)}")

# Example usage:
# Assuming you have 4 grids of size 9x9 (block_size = 3)

# === Usage Examples ===
if __name__ == "__main__":
    # Choose 3 for classic, 4 for 16x16, 5 for 25x25, etc.
    block_size = 3          # 4x4 blocks = 16x16 grid
    cells_to_remove = 50   # Adjust based on difficulty
    verbose = False          # Enable debugging output
    testing_multi_sudoku = False
    if testing_multi_sudoku:
        game = create_multi_sudoku(block_size=block_size,cells_to_remove=40, verbose=False)
        save_grid_to_file(game, block_size,filename="my_grid.txt",is_multi_sudoku=True)
        new_print_grid(grid=game,block_size=block_size,is_multi_sudoku=True)
    else:
        puzzle1, solution1 = generate_sudoku(block_size=block_size, cells_to_remove=cells_to_remove, verbose=verbose)
        print("\nGenerated Puzzle 1 :")
        new_print_grid(puzzle1, block_size=3,is_multi_sudoku=False)
        save_grid_to_file(puzzle1, block_size,filename="my_grid.txt",is_multi_sudoku=False)

        print("Solution 1 :")
        print_grid(solution1)
        # premade9X9 = {
        #     (0, 0): [
        #         [5, 0, 0],
        #         [0, 7, 0],
        #         [0, 0, 1]
        #     ]
        # }
        # puzzle2, solution2 = generate_sudoku(
        #     block_size=3,
        #     cells_to_remove=40,
        #     verbose=verbose,
        #     premade_blocks=premade9X9
        # )
        # print("\nGenerated 9X9 Puzzle with premade block :")
        # print(premade9X9)
        # print_grid(puzzle2)
        # print("Solution 9X9 Puzzle with premade block :")
        # print_grid(solution2)
        # premade16X16 = {
        #     (0, 0): [
        #         [ 1,  2,  0,  0],
        #         [ 0,  0,  5,  6],
        #         [ 0,  9, 10,  0],
        #         [13,  0,  0, 16],
        #     ]
        # }
        # puzzle3, solution3 = generate_sudoku(
        #     block_size=4,
        #     cells_to_remove=40,
        #     verbose=verbose,
        #     premade_blocks=premade16X16
        # )
        # print("\nGenerated 16X16 Puzzle with premade block :")
        # print(premade16X16)
        # print_grid(puzzle3)
        # print("Solution 16X16 Puzzle with premade block  :")
        # print_grid(solution3)



   
