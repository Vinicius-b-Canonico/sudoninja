import random
import copy
import math
import os
import shutil

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

def generate_sudoku(block_size=3, cells_to_remove=40, verbose=False, premade_blocks=None, is_multi_sudoku=False):
    """
    Generates a Sudoku puzzle and its corresponding solution.

    This function creates either a standard Sudoku puzzle or a complex multi-sudoku puzzle based on the parameters.
    It supports injecting pre-defined blocks into the grid (for corner embedding or special cases) and can be used
    both for independent puzzles and as part of a larger composite puzzle (e.g., multi-sudoku).

    Parameters:
    -----------
    block_size : int, optional (default=3)
        The size of a single block (sub-grid) in the puzzle. A block_size of 3 generates a standard 9x9 grid.

    cells_to_remove : int, optional (default=40)
        The number of cells to remove from the completed grid in order to form the final puzzle. 
        This controls the puzzle’s difficulty.

    verbose : bool, optional (default=False)
        If True, enables verbose logging of the generation process.

    premade_blocks : dict, optional (default=None) (only applied if not multi sudoku for now, but can 100% be improved by a ninja)
        A dictionary specifying pre-filled blocks to be embedded into the puzzle before generation.
        The keys are (block_row, block_col) positions (0-indexed), and the values are 2D lists representing 
        full sub-grids (e.g., 3x3 if block_size=3) to place at those locations.

        Example:
        --------
        premade_blocks = {
            (0, 0): [
                [5, 0, 0],
                [0, 7, 0],
                [0, 0, 1]
            ]
        }

    is_multi_sudoku : bool, optional (default=False)
        If True, generates a full multi-sudoku puzzle layout instead of a single 9x9 grid. 
        Delegates puzzle creation to `create_multi_sudoku`.

    Returns:
    --------
    tuple of (puzzle, solution):
        - puzzle : list of lists
            The generated Sudoku puzzle with some numbers removed.
        - solution : list of lists
            The complete solution for the generated puzzle.

    Notes:
    ------
    - If `is_multi_sudoku=True`, the function ignores `premade_blocks` and returns a combined multi-grid directly.
    - The internal validity of the puzzle is preserved during removal of cells, ensuring the puzzle remains solvable.

    Example Usage:
    --------------
    puzzle, solution = generate_sudoku(
        block_size=3,
        cells_to_remove=40,
        verbose=True,
        premade_blocks={
            (0, 0): [
                [5, 0, 0],
                [0, 7, 0],
                [0, 0, 1]
            ]
        }
    )
    print("Puzzle:")
    print_grid(puzzle)
    print("Solution:")
    print_grid(solution)
    """
    if is_multi_sudoku:
        return create_multi_sudoku(block_size=block_size,cells_to_remove=cells_to_remove,verbose=verbose)
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
    """
    Creates a multi-sudoku puzzle composed of five interconnected Sudoku grids.

    This function generates a complex puzzle structure where four smaller sudoku puzzles
    are placed in the corners (top-left, top-right, bottom-left, bottom-right), and a central
    sudoku puzzle sits in the middle. These five grids are partially linked through shared blocks:
    - The corner puzzles each include one pre-filled 3x3 block taken from the central puzzle's solution.
    - These shared blocks ensure interdependence between the five grids, creating a unique and challenging puzzle layout.

    Parameters:
    -----------
    block_size : int, optional (default=3)
        The size of a single block in each sudoku grid. A value of 3 produces standard 9x9 sudoku puzzles.

    cells_to_remove : int, optional (default=40)
        The number of cells to remove from each generated puzzle, controlling the difficulty level.

    verbose : bool, optional (default=False)
        If True, enables verbose output from the puzzle generation process for debugging or inspection.

    Returns:
    --------
    combined : list of lists
        A 2D grid representing the full multi-sudoku layout with five interlinked puzzles.
        The combined layout is larger than a standard sudoku grid and follows this structure:

            [ TL |     | TR ]
            [     |  C  |    ]
            [ BL |     | BR ]

        Each grid is filled independently but includes one 3x3 block from the central solution
        to maintain coherence between the puzzles.

    Example:
    --------
    multi_grid = create_multi_sudoku(block_size=3, cells_to_remove=45)
    print_grid(multi_grid, block_size=3, is_multi_sudoku=True)
    """
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

def print_grid(grid, block_size, is_multi_sudoku=False):
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

def save_grid_to_file(grid, block_size, filename="combined_grid.txt", is_multi_sudoku=False, overwrite_existing: bool = False):
    """
    Saves a formatted grid to a text file, auto-creating folders and appending '.txt' if missing.

    This function takes a grid (list of lists), formats it in a structured way, and writes it to a text file.
    It divides the grid into blocks of size `block_size` by `block_size`, and optionally adds extra spacing for 
    multi-sudoku layouts (i.e., concatenated or composite sudoku grids).

    Enhancements:
    -------------
    - If the `filename` includes directories that don't exist, they will be created automatically.
    - If the `filename` does not include a file extension, `.txt` is appended automatically.

    Formatting Rules:
    -----------------
    - Values equal to `0` are shown as a dot (`.`).
    - Values equal to `"X"` (case-insensitive) are shown as `XX`.
    - All other values are shown padded to two characters (e.g., ` 7`, `10`).
    - Horizontal lines (`+---+---+...`) separate block rows.
    - Vertical bars (`|`) separate block columns.

    Parameters:
    -----------
    grid : list of list
        The 2D list representing the grid. Each element is a number, zero, or a special character like `"X"`.

    block_size : int
        Size of one block in the grid. For example, `block_size=3` is used for standard 9x9 Sudoku.

    filename : str, optional (default="combined_grid.txt")
        Name (and optional path) of the file where the grid will be saved.

    is_multi_sudoku : bool, optional (default=False)
        If set to True, assumes the grid is a multi-sudoku (composed of multiple sudoku blocks) and adjusts the formatting accordingly.

    overwrite_existing : bool, optional (default=False)
        If True, will overwrite the file if it already exists.
        If False, will automatically rename the file to avoid overwriting,
        using the format: "filename_previous_1.txt", "filename_previous_2.txt", etc.

    Example:
    --------
    grid = [
        [1, 2, 3, 0],
        [4, 5, 6, 0],
        [7, 8, 9, 'X'],
        [0, 0, 0, 0]
    ]
    save_grid_to_file(grid, 3, "saves/output_grid", is_multi_sudoku=True)

    Output:
    -------
    A file will be created with the formatted grid content.
    The absolute path of the saved file will be printed to the console.
    """
    if not os.path.splitext(filename)[1]:
        filename += ".txt"

    # 🔧 Ensure the folder path exists before writing
    if os.path.dirname(filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)

    # Handle file backup logic
    if not overwrite_existing and os.path.exists(filename):
        base, ext = os.path.splitext(filename)
        i = 1
        backup_filename = f"{base}_previous_{i}{ext}"
        while os.path.exists(backup_filename):
            i += 1
            backup_filename = f"{base}_previous_{i}{ext}"
        shutil.move(filename, backup_filename)
        
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


# === Example Usage ===
# These are runnable examples when executing this script directly.
# They demonstrate usage of core functions like generate_sudoku, save_grid_to_file, and print_grid.
# also, i dont enforce uniqueness in solutions, as most sudoku generation engines seem to do.
# this makes it way simpler and for my use is not a problem, but feel free to PR if you can code it!
if __name__ == "__main__":
    # Block size:
    # - 3 => 9x9 Sudoku
    # - 4 => 16x16 Sudoku
    # - 5 => 25x25 Sudoku (may be unstable)
    # - Block sizes <3 not fully tested
    block_size = 3
    cells_to_remove = 50  # Difficulty setting: more cells removed = harder puzzle
    #remenber need at least 17 numbers seeable to find a solution
    verbose = False

    # Toggle between single-grid and multi-grid Sudoku
    testing_multi_sudoku = False

    if testing_multi_sudoku:
        grid = create_multi_sudoku(block_size=block_size, cells_to_remove=cells_to_remove, verbose=verbose)
        save_grid_to_file(grid, block_size, filename="examples/multi_grid.txt", is_multi_sudoku=True)
        print_grid(grid=grid, block_size=block_size, is_multi_sudoku=True)

    else:
        # === Standard Puzzle ===
        puzzle, solution = generate_sudoku(
            block_size=block_size,
            cells_to_remove=cells_to_remove,
            verbose=verbose
        )
        print("\nGenerated Standard Sudoku Puzzle:")
        print_grid(puzzle, block_size=block_size)
        save_grid_to_file(puzzle, block_size, filename="examples/standard_grid.txt")

        print("\nSolution:")
        print_grid(solution, block_size=block_size)

        # === 9x9 with Premade Block ===
        #this premade blocks were mainly made as a way to allow for the multi-sudoku, but they do allow for
        #some further customization if anyone cares to. by doing this, you can send blocks of prechoosen numbers
        # to be part of the final solution, with 0 being cells to put a random number in, 
        # and 1-9 being the actual numbers.
        # the cordinate pairs are for the blocks of 3X3 or 4X4 depending on the block_size 
        #
        # this whole system can eventually be improved to:
        #                allow for forcing cells to be open in the puzzle state.
        #                allow for customization at the cell level
        #
        # Uncomment to test
        premade9x9 = {
            (0, 0): [
                [5, 0, 0],
                [0, 7, 0],
                [0, 0, 1]
            ]
        }
        puzzle2, solution2 = generate_sudoku(
            block_size=3,
            cells_to_remove=40,
            verbose=verbose,
            premade_blocks=premade9x9
        )
        print("\nGenerated 9x9 Puzzle with Premade Block:")
        print(premade9x9)
        print_grid(puzzle2,block_size=3)
        print("Solution:")
        print_grid(solution2,block_size=3)

        # === 16x16 with Premade Block ===
        # Uncomment to test
        # premade16x16 = {
        #     (0, 0): [
        #         [ 1,  2,  0,  0],
        #         [ 0,  0,  5,  6],
        #         [ 0,  9, 10,  0],
        #         [13,  0,  0, 16]
        #     ]
        # }
        # puzzle3, solution3 = generate_sudoku(
        #     block_size=4,
        #     cells_to_remove=40,
        #     verbose=verbose,
        #     premade_blocks=premade16x16
        # )
        # print("\nGenerated 16x16 Puzzle with Premade Block:")
        # print(premade16x16)
        # print_grid(puzzle3,block_size=4)
        # print("Solution:")
        # print_grid(solution3,block_size=4)












# Example usage:

# # === Usage Examples ===
# #need to clean this up when i can, feel free to anyone
# if __name__ == "__main__":
#     # Choose 3 for classic, 4 for 16x16, 5 for 25x25, etc.
#     # block size of 5 and above doesnt seem to be very stable.
#     # havent tested with 2 or 1 either, no idea whatd happen lol

#     block_size = 3          # 4x4 blocks = 16x16 grid
#     cells_to_remove = 50   # Adjust based on difficulty
#     verbose = False          # Enable debugging output
#     testing_multi_sudoku = True
#     if testing_multi_sudoku:
#         game = create_multi_sudoku(block_size=block_size,cells_to_remove=40, verbose=False)
#         save_grid_to_file(game, block_size,filename="my_grid.txt",is_multi_sudoku=True)
#         print_grid(grid=game,block_size=block_size,is_multi_sudoku=True)
#     else:
#         puzzle1, solution1 = generate_sudoku(block_size=block_size, cells_to_remove=cells_to_remove, verbose=verbose)
#         print("\nGenerated Puzzle 1 :")
#         print_grid(puzzle1, block_size=3,is_multi_sudoku=False)
#         save_grid_to_file(puzzle1, block_size,filename="my_grid.txt",is_multi_sudoku=False)

#         print("Solution 1 :")
#         print_grid(solution1, block_size=3, is_multi_sudoku=False)
#         # premade9X9 = {
#         #     (0, 0): [
#         #         [5, 0, 0],
#         #         [0, 7, 0],
#         #         [0, 0, 1]
#         #     ]
#         # }
#         # puzzle2, solution2 = generate_sudoku(
#         #     block_size=3,
#         #     cells_to_remove=40,
#         #     verbose=verbose,
#         #     premade_blocks=premade9X9
#         # )
#         # print("\nGenerated 9X9 Puzzle with premade block :")
#         # print(premade9X9)
#         # print_grid(puzzle2)
#         # print("Solution 9X9 Puzzle with premade block :")
#         # print_grid(solution2)
#         # premade16X16 = {
#         #     (0, 0): [
#         #         [ 1,  2,  0,  0],
#         #         [ 0,  0,  5,  6],
#         #         [ 0,  9, 10,  0],
#         #         [13,  0,  0, 16],
#         #     ]
#         # }
#         # puzzle3, solution3 = generate_sudoku(
#         #     block_size=4,
#         #     cells_to_remove=40,
#         #     verbose=verbose,
#         #     premade_blocks=premade16X16
#         # )
#         # print("\nGenerated 16X16 Puzzle with premade block :")
#         # print(premade16X16)
#         # print_grid(puzzle3)
#         # print("Solution 16X16 Puzzle with premade block  :")
#         # print_grid(solution3)



   
