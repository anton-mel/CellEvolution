# Developed by Anton Melnychuk          March 1st 2024
# For ASTR 330 Class                    Yale University

# GUI Visualization
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# Imports
import pygame
import random
import math
import os

import Life
import Constants
from tools import parse_video


class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.light = 0
        self.occupied = None
        self.energy_level = 0
        self.organic_level = 0
    
    def set_living_cell(self, life) -> None:
        self.occupied = life

    def kill_life(self) -> None:
        ''' Transfer Life Energy to the Cell '''

        if self.occupied:
            self.organic_level += 0.001
            self.energy_level += 0.001
            self.occupied = None

    def check_position(self) -> object:
        return {self.x, self.y}
    

    # Options for the Video Visualisation
    # SOIL, ENERGY, COLOR

    def draw_color(self, surface) -> None:
        ''' Draws the Cell & Life by COLOR '''

        if self.occupied:
            if isinstance(self.occupied, Life.Leaf):

                # Draw Instance of the Leaf

                if self.occupied.direction % 2 == 0:
                    pygame.draw.ellipse(surface, self.occupied.color,
                        (self.x + Constants.CELL_SIZE // 4, self.y, Constants.CELL_SIZE // 2, Constants.CELL_SIZE * 1.05), 0)
                else:
                    pygame.draw.ellipse(surface, self.occupied.color,
                        (self.x, self.y + Constants.CELL_SIZE // 4, Constants.CELL_SIZE * 1.05, Constants.CELL_SIZE // 2), 0)
                    
            elif isinstance(self.occupied, Life.Root) or isinstance(self.occupied, Life.Radio):

                offset = Constants.CELL_SIZE // 2
                pygame.draw.circle(surface, self.occupied.color,
                    (self.x + offset, self.y + offset), Constants.CELL_SIZE // 2, 0)
                
            elif isinstance(self.occupied, Life.Newborn):

                offset = Constants.CELL_SIZE // 2
                pygame.draw.circle(surface, self.occupied.color,
                    (self.x + offset, self.y + offset), Constants.CELL_SIZE // 2, 1)
                
            elif isinstance(self.occupied, Life.Pipe):

                # Draw Instance of the Pipe

                pipe_size = Constants.CELL_SIZE // 2
                offset = (Constants.CELL_SIZE - pipe_size) // 2

                if self.occupied.direction % 2 == 0:
                    pygame.draw.rect(
                        surface, self.occupied.color, 
                        (self.x + offset, self.y + offset, pipe_size // 4, Constants.CELL_SIZE), 0)
                else: 
                    pygame.draw.rect(
                        surface, self.occupied.color, 
                        (self.x + offset, self.y + offset, Constants.CELL_SIZE, pipe_size // 4), 0)
        else:

            if self.organic_level > Constants.ORGANIC_THRESHOLD:
                pygame.draw.rect(
                    surface, Constants.ORGANIC_TOXIC,
                    (self.x, self.y, Constants.CELL_SIZE, Constants.CELL_SIZE), 0)
            if self.energy_level > Constants.ENERGY_THRESHOLD:
                pygame.draw.rect(
                    surface, Constants.ENERGIC_TOXIC,
                    (self.x, self.y, Constants.CELL_SIZE, Constants.CELL_SIZE), 0)
    
    def draw_soil(self, surface) -> None:
        ''' Draws the Cell by SOIL energy '''

        organic_level_clipped = min(max(self.organic_level, 0), 1)
        color_value = int(255 * (1 - organic_level_clipped))
        color = (color_value, color_value, color_value)

        pygame.draw.rect(surface, color, (self.x, self.y, Constants.CELL_SIZE, Constants.CELL_SIZE))
                
    def draw_energy(self, surface) -> None:
        ''' Draws the Cell by ENERGY left '''

        energy_color = self.calculate_energy_color()
        pygame.draw.rect(surface, energy_color, (self.x, self.y, Constants.CELL_SIZE, Constants.CELL_SIZE))

    # Helper Functions

    def calculate_energy_color(self) -> tuple:
        ''' Calculate energy color based on organic level '''

        energy_level = self.organic_level
        if energy_level < 0.5:
            # Low energy: from yellow to red
            r, g, b = 255, int(energy_level * 2 * 255), 0
        else:
            # High energy: from green to yellow
            r, g, b= int((1 - energy_level) * 2 * 255), 255, 0

        return (r, g, b)

        
class Sector:
    def __init__(self, **kwargs):
        self.cells = self.create_cells()

        self.display_type = None
        self.day_counter = 0
        self.light_global = 0

        # For faster cell access
        self.reading_x = 0
        self.reading_y = 0

        # Gather all energy to a dictionary
        self.gathered_energy = [0] * FAMILIES_COUNT

        self.generate_borders()
        self.generate_life(**kwargs)

    def save_energy(self, family_idx, energy) -> None:
        self.gathered_energy[family_idx] += energy


    # Functions for One-time Definition

    def create_cells(self) -> list:
        ''' Define Cells on GRID Defition '''

        cells = []
        for x in range(0, SECTOR_SIZE_X, Constants.CELL_SIZE):
            for y in range(0, SECTOR_SIZE_Y, Constants.CELL_SIZE):
                cell = Cell(x, y)
                cell.energy_level = random.uniform(0, 0.8)
                cell.organic_level = random.uniform(0, 0.8)

                cells.append(cell)

        return cells
    
    def generate_life(self, **kwargs) -> None:
        ''' Pull Life into Cells '''

        for family_idx in range(FAMILIES_COUNT):
            random_cell = random.choice(self.cells)
            
            # Keep searching for a valid to live cell
            while random_cell.occupied is not None and \
                  random_cell.organic_level != 1:
                random_cell = random.choice(self.cells)

            # Random / User DNA Life
            dna = Life.DNA()
            if not kwargs.items():
                dna.generate_random()
            else: 
                dna = Life.DNA(**kwargs)
            life = Life.Newborn(family_idx, dna)

            # Grant Parent Child to Access Cell X-Y Coords
            life.set_gridpos_function(random_cell.check_position)
            life.define_color()

            random_cell.set_living_cell(life)
    
    def generate_borders(self) -> None:
        ''' Generate toxic borders to keep evolution within families
            for a bit before letting them attack others '''

        for row_idx in range(0, SECTOR_SIZE_X, Constants.CELL_SIZE):
            for col_idx in range(0, SECTOR_SIZE_Y, Constants.CELL_SIZE):
                padding = SECTOR_BORDER * Constants.CELL_SIZE
                idx_flat = (row_idx // Constants.CELL_SIZE) * (SECTOR_SIZE_Y // Constants.CELL_SIZE) + (col_idx // Constants.CELL_SIZE)
                cell = self.cells[idx_flat]

                if (cell.x < padding or
                    cell.x > (SECTOR_SIZE_X - padding) - Constants.CELL_SIZE or
                    cell.y < padding or
                    cell.y > (SECTOR_SIZE_Y - padding) - Constants.CELL_SIZE):
                        
                        self.cells[idx_flat].organic_level = 1
        
        middlex_idx = SECTOR_SIZE_X // Constants.CELL_SIZE // 2
        middley_idx = SECTOR_SIZE_Y // Constants.CELL_SIZE // 2

        border_thickness = SECTOR_BORDER // 2
    
        for row_idx in range(middlex_idx * Constants.CELL_SIZE - border_thickness * Constants.CELL_SIZE, (middlex_idx + 1) * Constants.CELL_SIZE + border_thickness * Constants.CELL_SIZE):
            for col_idx in range(0, SECTOR_SIZE_Y, Constants.CELL_SIZE):
                idx_flat = (row_idx // Constants.CELL_SIZE) * (SECTOR_SIZE_Y // Constants.CELL_SIZE) + (col_idx // Constants.CELL_SIZE)
                self.cells[idx_flat].organic_level = 1
                
        for col_idx in range(middley_idx * Constants.CELL_SIZE - border_thickness * Constants.CELL_SIZE, (middley_idx + 1) * Constants.CELL_SIZE + border_thickness * Constants.CELL_SIZE):
            for row_idx in range(0, SECTOR_SIZE_X, Constants.CELL_SIZE):
                idx_flat = (row_idx // Constants.CELL_SIZE) * (SECTOR_SIZE_Y // Constants.CELL_SIZE) + (col_idx // Constants.CELL_SIZE)
                self.cells[idx_flat].organic_level = 1


    # Helper Functions

    def move_and_wrap(self, x, y, direction) -> int:
        ''' Wrap Map Around by Given Coordinates and a Shift '''

        if direction == 1:    # Moving Left
            x -= Constants.CELL_SIZE
        elif direction == 2:  # Moving Above
            y -= Constants.CELL_SIZE
        elif direction == 3:  # Moving Right
            x += Constants.CELL_SIZE
        elif direction == 4:  # Moving Bottom
            y += Constants.CELL_SIZE

        # Wrap around

        if x < 0:
            x = SECTOR_SIZE_X - Constants.CELL_SIZE
        elif x >= SECTOR_SIZE_X:
            x = 0
        if y < 0:
            y = SECTOR_SIZE_Y - Constants.CELL_SIZE
        elif y >= SECTOR_SIZE_Y:
            y = 0

        return x, y


    # Private Functions for the Life Cells

    def update_next(self, direction, life, family_idx) -> Life:
        ''' Newborn private function for reproduction '''

        x, y = self.move_and_wrap(self.reading_x, self.reading_y, direction)
        neighbor_cell = self.get_cell_at(x, y)

        if neighbor_cell:

            # Prevent the colonies that are the same type eat each other

            if (neighbor_cell.occupied and neighbor_cell.occupied.family_idx == family_idx):
                return None

            # We can eat all kind of cells except the Roots and the Wood
            
            if neighbor_cell.occupied and (isinstance(neighbor_cell.occupied, Life.Root) or isinstance(neighbor_cell.occupied, Life.Pipe)):
                return None
            
            # We can build on energy toxic cell if not Radio Cell

            if neighbor_cell.energy_level > Constants.ENERGY_THRESHOLD and not isinstance(life, Life.Radio):
                return None
            
            # We can build on soil toxic cell if not Root Cell

            if neighbor_cell.organic_level > Constants.ORGANIC_THRESHOLD and not isinstance(life, Life.Root):
                return None

            # Eat Cell if Needed

            neighbor_cell.kill_life()
            curr_cell = self.get_cell_at(self.reading_x, self.reading_y)
            curr_cell.organic_level += 0.001 
            curr_cell.energy_level += 0.02

            neighbor_cell.set_living_cell(life)

            return neighbor_cell
    
    # Leaf
        
    def get_light_energy(self) -> None:
        curr_cell = self.get_cell_at(self.reading_x, self.reading_y)

        # If two leaf are next to each other => 0 energy

        for DIR in Constants.DIRECTIONS:
            x, y = self.move_and_wrap(self.reading_x, self.reading_y, DIR)
            next_cell = self.get_cell_at(x, y)

            if next_cell and isinstance(next_cell.occupied, Life.Leaf):
                self.save_energy(next_cell.occupied.family_idx, 0)
                self.save_energy(curr_cell.occupied.family_idx, 0)

        if curr_cell and isinstance(curr_cell.occupied, Life.Leaf):
            self.save_energy(curr_cell.occupied.family_idx, self.light_global)

    # Root
            
    def get_soil_energy(self) -> None:
        curr_cell = self.get_cell_at(self.reading_x, self.reading_y)

        if curr_cell and curr_cell.occupied:
            curr_cell.organic_level = curr_cell.organic_level * 0.7
            energy = curr_cell.organic_level * 0.3

            self.save_energy(curr_cell.occupied.family_idx, energy)

    # Radio
            
    def get_radio_energy(self) -> None:
        curr_cell = self.get_cell_at(self.reading_x, self.reading_y)

        if curr_cell and curr_cell.occupied:
            curr_cell.energy_level = curr_cell.energy_level * 0.7
            energy = curr_cell.energy_level * 0.3

            self.save_energy(curr_cell.occupied.family_idx, energy)
    

    # Helper Functions

    def update_daynight(self) -> None:
        ''' Use a cosine function to simulate day-night cycle (0.3-1 energy range) '''

        lower_bound, upper_bound = 0.3, 1
        scaled_value = (0.5 * math.cos(math.radians(self.day_counter)) + 0.5) * (upper_bound - lower_bound) + lower_bound
        self.light_global = scaled_value
        self.day_counter += 3

    def draw(self, surface):

        if self.display_type == "color":
            for cell in self.cells:
                cell.draw_color(surface)

        elif self.display_type == "soil":
            for cell in self.cells:
                cell.draw_soil(surface)

        elif self.display_type == "energy":
            for cell in self.cells:
                cell.draw_energy(surface)

    def get_cell_at(self, x, y):
        ''' Search for Cell in Shuffled Set '''

        for cell in self.cells:
            if cell.x == x and cell.y == y:
                return cell
            
        return None
    
    def check_occupied(self, x, y, shift, idx):
        xt, yt = self.move_and_wrap(x, y, shift)
        check_life = self.get_cell_at(xt, yt).occupied

        if check_life and \
            (check_life.family_idx == idx or \
             isinstance(check_life, Life.Root or \
             isinstance(check_life, Life.Pipe))):
            
            return True
        
        return False


    # To keep Canvas Clean

    def remove_tail(self, curr_cell, visited=set()):
        ''' On Cell Removal, Delete the Rest '''

        # Check for cycles
        if curr_cell in visited:
            return 
        visited.add(curr_cell)
        
        self.reading_x = curr_cell.x
        self.reading_y = curr_cell.y
        
        life = curr_cell.occupied
        back_dir = (life.direction + 1) % 4 + 1
        left_dir = 4 if back_dir == 1 else back_dir - 1
        right_dir = 1 if back_dir == 4 else back_dir + 1

        directions = [left_dir, back_dir, right_dir]
        for dir in directions:
            x, y = self.move_and_wrap(self.reading_x, self.reading_y, dir)
            neighbor = self.get_cell_at(x, y)

            if not neighbor: return
            life_next = neighbor.occupied
            if life_next and life_next.family_idx == life.family_idx:
                self.remove_tail(neighbor, visited)
                neighbor.occupied = None
 

    def step(self):
        ''' Executes One Step of the Cell Life Cycle '''
        self.update_daynight()

        # Remove Cell Ordering
        # To Simulate Randomness
        # In the Execution

        random.shuffle(self.cells)
        
        for cell in self.cells:
            self.reading_x = cell.x
            self.reading_y = cell.y

            life = cell.occupied

            if life: # execute
                if life.execute():
                    self.remove_tail(cell)
                    continue
                life.age += 1

                # Reasons to eliminate the cell
                if life.age > life.lifelen:
                    self.remove_tail(cell)
                    cell.occupied = None

                if (not isinstance(life, Life.Root) and \
                cell.organic_level > Constants.ORGANIC_THRESHOLD) or \
                (not isinstance(life, Life.Radio) and \
                cell.energy_level > Constants.ENERGY_THRESHOLD):
                    self.remove_tail(cell)
                    cell.occupied = None
            
            # The energy level in ground
            # aims to a default values
                    
            if cell.energy_level > 0.3:
                cell.energy_level -= 0.005
            elif cell.energy_level < 0.2:
                cell.energy_level += 0.005

        # Provide NewBorn Cells Gathered Energy 
        # And clean the uneccesary pipes
                
        for cell in self.cells:
            self.reading_x = cell.x
            self.reading_y = cell.y

            life = cell.occupied
            if life: # if any cell
                if isinstance(life, Life.Newborn):
                    life.energy_level += self.gathered_energy[life.family_idx]
                    self.gathered_energy[life.family_idx] = 0
                    if life.energy_level < Constants.REPROD_MIN:
                        cell.occupied = None


def main(**kwargs):
    ''' Define OS Global Variables and GUI/Tk User Windows '''

    global FODLER_PATH, TICK, FAMILIES_COUNT, SECTOR_SIZE_X, SECTOR_SIZE_Y, SECTOR_BORDER, DISPLAY
    
    # Update constants with user kwargs values
    TICK = kwargs.get('tick', 300)
    FODLER_PATH = kwargs.get('folder_path', './output')
    FAMILIES_COUNT = kwargs.get('families_count', 4)
    SECTOR_SIZE_X = kwargs.get('sector_size_x', 800)
    SECTOR_SIZE_Y = kwargs.get('sector_size_y', 800)
    SECTOR_BORDER = kwargs.get('sector_border', 0)
    DISPLAY = kwargs.get('display_type', "color")

    pygame.init()
    screen = pygame.display.set_mode((SECTOR_SIZE_X, SECTOR_SIZE_Y))
    pygame.display.set_caption("Evolution Game")

    grid_display = Sector(**kwargs)
    grid_display.display_type = DISPLAY

    # Grant Private Access to grid (encapsulation) to Cells
    # Instead of Prodiding whole Grid access to all Cells

    Life.Life.set_gridcheck_function(grid_display.check_occupied)
    Life.Newborn.set_private_function(grid_display.update_next)
    Life.Leaf.set_private_function(grid_display.get_light_energy)
    Life.Root.set_private_function(grid_display.get_soil_energy)
    Life.Radio.set_private_function(grid_display.get_radio_energy)

    clock = pygame.time.Clock()

    if not os.path.exists(FODLER_PATH):
        os.makedirs(FODLER_PATH)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
         
        # Save the Screen to the Folder
                
        filename = str(grid_display.day_counter).zfill(8) + ".png"
        pygame.image.save(screen, os.path.join(FODLER_PATH, filename))

        # Clear Screen

        screen.fill(Constants.BG)
        grid_display.step()
        
        # Execute Life Step and Display

        grid_display.draw(screen)

        pygame.display.flip()
        clock.tick(TICK)

        # Save Images in the Range

        if grid_display.day_counter > Constants.FINISH:
            break

    pygame.quit()
    folder_path = kwargs.get('folder_path', './output')
    parse_video.combine_images_to_video(folder_path, folder_path+"_video.mp4")

    
# User GUI Window

class DNADialog:
    ''' User Dialog Window Class '''

    def __init__(self, master):
        self.master = master
        self.master.title("ASTR 330 - Game of Life")

        title_label = tk.Label(master, text="Cell Evolution Game", font=("Arial", 24, "bold"), anchor="w", compound=tk.LEFT, fg="white")
        title_label.grid(row=0, column=0, columnspan=4, padx=20, pady=(20, 0), sticky="w")
        subtitle_label = tk.Label(master, text="Developed by Anton Melnychuk © 2024", font=("Arial", 12), anchor="w", fg="gray")
        subtitle_label.grid(row=1, column=0, columnspan=4, padx=20, pady=(0, 20), sticky="w")

        default_values = {
            "mutation_rate": "0.5",
            "rotate_skills": "0.5",
            "rotate_rate": "0.5",
            "radio_rate": "0.5",
            "root_rate": "0.5",
            "leaf_rate": "0.5",
            "newb_rate": "0.5",
            "folder_path": "output",
            "tick": "300",
            "families_count": "20",
            "sector_size_x": "880",
            "sector_size_y": "880",
            "sector_border": "0",
        }

        entries = [
            ("Cell Mutation Rate (0-1):", "mutation_rate"),
            ("Cell Rotate Skills (0-1):", "rotate_skills"),
            ("Cell Rotate Rate (0-1):", "rotate_rate"),
            ("Cell Radio Rate (0-1):", "radio_rate"),
            ("Cell Root Rate (0-1):", "root_rate"),
            ("Cell Leaf Rate (0-1):", "leaf_rate"),
            ("Cell Newborn Rate (0-1):", "newb_rate")
        ]
        
        for idx, (label_text, entry_name) in enumerate(entries):
            label = tk.Label(master, text=label_text, anchor="w")
            label.grid(row=idx+2, column=0, padx=20, pady=5, sticky="w")

            range_slider = ttk.Scale(master, from_=0, to=1, length=200, orient="horizontal")
            range_slider.grid(row=idx+2, column=1, padx=20, pady=5)
            setattr(self, f"{entry_name}_slider", range_slider)
            range_slider.set(0.5)

        # Additional fields and display type buttons
            
        additional_fields = [
            ("Folder Path:", "folder_path"),
            ("Tick (Iteration Speed):", "tick"),
            ("Families Count:", "families_count"),
            ("Sector Size X:", "sector_size_x"),
            ("Sector Size Y:", "sector_size_y"),
            ("Sector Border:", "sector_border"),
            ("Display Type:", "display_type"),
        ]

        for idx, (label_text, entry_name) in enumerate(additional_fields):
            label = tk.Label(master, text=label_text, anchor="w")
            label.grid(row=idx+2, column=2, padx=20, pady=5, sticky="w")

            if entry_name == "display_type":
                display_type_frame = ttk.Frame(master)
                display_type_frame.grid(row=idx+2, column=3, padx=20, pady=5, sticky="w")
                
                self.display_type_var = tk.StringVar()
                self.display_type_var.set("color")

                color_button = ttk.Radiobutton(display_type_frame, text="Color", variable=self.display_type_var, value="color", compound=tk.LEFT)
                color_button.grid(row=0, column=0, padx=(0, 7), pady=2, sticky="w")

                energy_button = ttk.Radiobutton(display_type_frame, text="Energy", variable=self.display_type_var, value="energy", compound=tk.LEFT)
                energy_button.grid(row=0, column=1, padx=(7, 7), pady=2, sticky="w")

                soil_button = ttk.Radiobutton(display_type_frame, text="Soil", variable=self.display_type_var, value="soild", compound=tk.LEFT)
                soil_button.grid(row=0, column=2, padx=(7, 0), pady=2, sticky="w")

            else:
                entry = ttk.Entry(master)
                entry.insert(0, default_values.get(entry_name, ""))
                entry.grid(row=idx+2, column=3, padx=20, pady=5)
                setattr(self, f"{entry_name}_entry", entry)
    
        self.instructions_button = ttk.Button(master, text="Read Instructions", command=self.show_instructions, style="Custom.TButton")
        self.instructions_button.grid(row=idx+3, column=2, columnspan=3, padx=(0, 130), pady=(20, 20), sticky="e")

        style = ttk.Style()
        style.configure("Custom.TButton", foreground="white")
        self.submit_button = ttk.Button(master, text="Play", command=self.submit, style="Custom.TButton")
        self.submit_button.grid(row=idx+3, column=3, columnspan=1, pady=(20, 20), sticky="e", padx=20)

    def show_instructions(self):
        pass

    def submit(self):
        try:
            mutation_rate = float(self.mutation_rate_slider.get())
            rotate_skills = float(self.rotate_skills_slider.get())
            rotate_rate = float(self.rotate_rate_slider.get())
            radio_rate = float(self.radio_rate_slider.get())
            root_rate = float(self.root_rate_slider.get())
            leaf_rate = float(self.leaf_rate_slider.get())
            newb_rate = float(self.newb_rate_slider.get())
            folder_path = self.folder_path_entry.get()
            tick = int(self.tick_entry.get())
            families_count = int(self.families_count_entry.get())
            sector_size_x = int(self.sector_size_x_entry.get())
            sector_size_y = int(self.sector_size_y_entry.get())
            sector_border = int(self.sector_border_entry.get())
            display_type = self.display_type_var.get()
            
            kwargs = {
                'mutation_rate': mutation_rate,
                'rotate_skills': rotate_skills,
                'rotate_rate': rotate_rate,
                'radio_rate': radio_rate,
                'root_rate': root_rate,
                'leaf_rate': leaf_rate,
                'newb_rate': newb_rate,
                'folder_path': folder_path,
                'tick': tick,
                'families_count': families_count,
                'sector_size_x': sector_size_x,
                'sector_size_y': sector_size_y,
                'sector_border': sector_border,
                'display_type': display_type
            }

            self.master.destroy()
            main(**kwargs)

        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please enter numeric values.")

def launch_dna_dialog():
    ''' General Properties and Definition of the User Window '''

    root = tk.Tk()
    root.resizable(False, False)
    DNADialog(root)

    root.mainloop()


if __name__ == "__main__":
    launch_dna_dialog()
