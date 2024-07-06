from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Tuple, Set, List

# Enum for Command Types
class CommandType(Enum):
    FORWARD = 'F'
    ROTATE_RIGHT = 'R'
    ROTATE_LEFT = 'L'

# Enum for Directions, stored in order of directions
class Direction(Enum): 
    NORTH = 'N'
    EAST = 'E'
    SOUTH = 'S'
    WEST = 'W'

# Command Interface
class Command(ABC):
    def __init__(self, car):
        self.car = car

    @abstractmethod
    def execute(self, simulation_map):
        pass

# Forward Command
class Forward(Command):
    def execute(self, simulation_map):
        if self.car.collided:
            return
        new_position = self.car.get_next_position()
        if simulation_map.check_if_out_of_boundaries(new_position):
            return
        simulation_map.move(self.car, new_position)


# RotateRight Command
class RotateRight(Command):
    def execute(self, simulation_map):
        if self.car.collided:
            return
        self.car.rotate_right()

# RotateLeft Command
class RotateLeft(Command):
    def execute(self, simulation_map):
        if self.car.collided:
            return
        self.car.rotate_left()

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Rectangle:
    def __init__(self, position: Point, width, height):
        self.position = position
        self.width = width
        self.height = height

# Entity Abstract Class
class Entity(ABC):
    def __init__(self, entity_id):
        self.id = entity_id

# Vehicle Interface
class Vehicle(Entity, ABC):
    def __init__(self, name, x, y, direction: Direction, length=1, width=1):
        super().__init__(name)
        self.name = name
        self.x = x
        self.y = y
        self.direction = direction
        self.length = length
        self.width = width
        self.collided = False
        self.last_step = 0

    def update_collided(self):
        self.collided = True

    def set_last_step(self, step):
        self.last_step = step

    def update_position(self, new_x, new_y):
        self.x = new_x
        self.y = new_y

    def get_position(self):
        return self.x, self.y
    
    def get_next_position(self, distance=1):
        if self.direction == Direction.NORTH.value:
            return self.x, self.y + distance
        elif self.direction == Direction.SOUTH.value:
            return self.x, self.y - distance
        elif self.direction == Direction.EAST.value:
            return self.x + distance, self.y
        elif self.direction == Direction.WEST.value:
            return self.x - distance, self.y

    def move(self, distance=1):
        if self.direction == Direction.NORTH.value:
            self.y += distance
        elif self.direction == Direction.SOUTH.value:
            self.y -= distance
        elif self.direction == Direction.EAST.value:
            self.x += distance
        elif self.direction == Direction.WEST.value:
            self.x -= distance

    def rotate_right(self):
        directions = [d.value for d in Direction]
        current_index = directions.index(self.direction)
        self.direction = directions[(current_index + 1) % len(directions)]

    def rotate_left(self):
        directions = [d.value for d in Direction]
        current_index = directions.index(self.direction)
        self.direction = directions[(current_index - 1) % len(directions)]

# Car Class
class Car(Vehicle):

    def __init__(self, name, x, y, direction):
        super().__init__(name, x, y, direction)

    # def get_next_position(self):
    #     if self.direction == Direction.NORTH.value:
    #         return self.x, self.y + 1
    #     elif self.direction == Direction.SOUTH.value:
    #         return self.x, self.y - 1
    #     elif self.direction == Direction.EAST.value:
    #         return self.x + 1, self.y
    #     elif self.direction == Direction.WEST.value:
    #         return self.x - 1, self.y

    # def rotate_right(self):
    #     directions = [d.value for d in Direction]
    #     current_index = directions.index(self.direction)
    #     self.direction = directions[(current_index + 1) % len(directions)]

    # def rotate_left(self):
    #     directions = [d.value for d in Direction]
    #     current_index = directions.index(self.direction)
        # self.direction = directions[(current_index - 1) % len(directions)]

# Map Class
class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.coord_to_entity_set: Dict[Tuple[int, int], Set[Entity]] = {}

    def get_coord_to_entity_set(self):
        return self.coord_to_entity_set

    def get_position_of(self, entity):
        for coord, entities in self.coord_to_entity_set.items():
            if entity in entities:
                return coord
        return None

    def move(self, entity, new_coord):
        old_coord = self.get_position_of(entity)
        if old_coord:
            self.coord_to_entity_set[old_coord].remove(entity)
        if new_coord not in self.coord_to_entity_set:
            self.coord_to_entity_set[new_coord] = set()
        self.coord_to_entity_set[new_coord].add(entity)
        
        entity.update_position(*new_coord)

    def check_if_out_of_boundaries(self, coord):
        x, y = coord
        return not (0 <= x < self.width and 0 <= y < self.height)

    def check_collisions(self):
        collision_detected = False
        for coord, entities in self.coord_to_entity_set.items():
            if len(entities) > 1:
                collision_detected = True
                for entity in entities:
                    if isinstance(entity, Car):
                        entity.update_collided()
        return collision_detected

# CommandCreator Class
class CommandCreator:
    @staticmethod
    def create(car, command_str):
        if command_str == CommandType.FORWARD.value:
            return Forward(car)
        elif command_str == CommandType.ROTATE_RIGHT.value:
            return RotateRight(car)
        elif command_str == CommandType.ROTATE_LEFT.value:
            return RotateLeft(car)

# Step Class
class Step:
    def __init__(self, step_id):
        self.step_id = step_id
        self.commands: List[Command] = []

    def add_command(self, command):
        self.commands.append(command)

    def run(self, simulation_map):
        for command in self.commands:
            command.execute(simulation_map)

# Simulatable Interface
class Simulatable(ABC):
    @abstractmethod
    def run(self):
        pass

# Simulator Class
class Simulator(Simulatable):
    def __init__(self):
        self.steps = []

    def run(self, simulation_map):
        for step_id, step in enumerate(self.steps):
            for command in step.commands:
                car = command.car
                if not car.collided:
                    command.execute(simulation_map)
                    car.set_last_step(step_id)
                    if simulation_map.check_collisions():
                        for coord, cars in simulation_map.get_coord_to_entity_set().items():
                            for c in cars:
                                if c.collided and not c.last_step:
                                    c.set_last_step(step_id)
    
def main():
    print("Welcome to Auto Driving Car Simulation!")

    # Function to get valid integer input for width and height
    def get_valid_field_dimensions():
        while True:
            try:
                input_str = input("Please enter the width and height of the simulation field in x y format: ").strip()
                parts = input_str.split()
                if len(parts) != 2:
                    raise ValueError("Please enter exactly two integers separated by a space.")
                width, height = parts
                if not width.isdigit() or not height.isdigit():
                    raise ValueError("Both width and height must be integers.")
                width, height = int(width), int(height)
                if width <= 0 or height <= 0:
                    raise ValueError("Dimensions must be positive integers.")
                return width, height
            except ValueError as ve:
                print(f"Invalid input: {ve}. Please enter again.")

    width, height = get_valid_field_dimensions()
    simulation_map = Map(width, height)
    print(f"You have created a field of {width} x {height}\n")
    simulator = Simulator()

    while True:
        print("Please choose from the following options:\n[1] Add a car to field\n[2] Run simulation")
        choice = input().strip()

        if choice == '1':
            while True:
                car_name = input("Please enter the name of the car: ").strip()
                if any(car.name == car_name for cars in simulation_map.get_coord_to_entity_set().values() for car in cars):
                    print(f"A car with the name {car_name} already exists. Please enter a unique name.")
                else:
                    break

            while True:
                try:
                    initial_position = input(f"Please enter initial position of car {car_name} in x y Direction format: ").strip().split()
                    if len(initial_position) != 3:
                        raise ValueError("Please enter exactly three values: x y Direction")
                    x, y = initial_position[0], initial_position[1]
                    direction = initial_position[2].upper()
                    if not x.isdigit() or not y.isdigit():
                        raise ValueError("Both x and y must be integers")
                    x, y = int(x), int(y)
                    if direction not in [d.value for d in Direction]:
                        raise ValueError(f"Invalid direction. Please enter one of {[d.value for d in Direction]}.")
                    if simulation_map.check_if_out_of_boundaries((x, y)):
                        raise ValueError("Initial position is out of boundaries. Please enter a valid position")
                    if any(car.x == x and car.y == y for cars in simulation_map.get_coord_to_entity_set().values() for car in cars):
                        raise ValueError("A car already exists at this position. Please enter a different position")
                    break
                except ValueError as ve:
                    print(f"Invalid input: {ve}. Please enter again.")

            car = Car(car_name, x, y, direction)
            simulation_map.move(car, (x, y))

            while True:
                try:
                    commands = input(f"Please enter the commands for car {car_name}: ").strip().upper()
                    if not all(c in [ct.value for ct in CommandType] for c in commands):
                        raise ValueError(f"Commands must only contain {[ct.value for ct in CommandType]}")
                    break
                except ValueError as ve:
                    print(f"Invalid input: {ve}. Please enter again.")

            for step_id, command_str in enumerate(commands):
                command = CommandCreator.create(car, command_str)
                if step_id >= len(simulator.steps):
                    simulator.steps.append(Step(step_id))
                simulator.steps[step_id].add_command(command)

            print("Your current list of cars are:\n")
            for coord, cars in simulation_map.get_coord_to_entity_set().items():
                for car in cars:
                    print(f"- {car.name}, ({car.x},{car.y}) {car.direction}, {commands}\n")
        elif choice == '2':
            print("Your current list of cars are:\n")
            for coord, cars in simulation_map.get_coord_to_entity_set().items():
                for car in cars:
                    print(f"-{car.name}, ({car.x},{car.y}) {car.direction}, {commands}\n")
            simulator.run(simulation_map)
            print("After simulation, the result is:")
            for coord, cars in simulation_map.get_coord_to_entity_set().items():
                for car in cars:
                    if car.collided:
                        affected_cars = ', '.join([affected_car.name for affected_car in simulation_map.get_coord_to_entity_set()[coord] if affected_car != car])
                        print(f"- {car.name}, collides with {affected_cars} at {coord} at step {car.last_step + 1}")
                    else:
                        print(f"- {car.name}, ({car.x},{car.y}) {car.direction}")

            while True:
                try:
                    print("Please choose from the following options:\n[1] Start over\n[2] Exit")
                    choice = input().strip()
                    if choice == '1':
                        main()
                    elif choice == '2':
                        print("Thank you for running the simulation. Goodbye!")
                        return
                    else:
                        raise ValueError("Invalid choice. Please enter 1 or 2.")
                except ValueError as ve:
                    print(f"Invalid input: {ve}. Please enter again.")
        else:
            print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()
