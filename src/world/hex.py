from __future__ import annotations

from collections import deque
from typing import List, Optional, Set, Tuple

import parameters
# from visualize import Visualize
from world.simulated_world import SimulatedWorld

# class Peg:

#     def __init__(self) -> None:
#         self.connect_pegs = set(self)

#     def connect(self, otherPeg: Peg):
#         self.connect_pegs.union(otherPeg.connect_pegs)
#         return self.connect_pegs


class Hex(SimulatedWorld):

    opposite_player = {
        1: 2,
        2: 1,
    }

    def __init__(self, state: Optional[Tuple[int, ...]] = None):
        self.__size: int = parameters.SIZE
        self.__length = self.__size ** 2

        self.__modified_list = {
            1: [False for _ in range(self.__size)],
            2: [False for _ in range(self.__size)]
        }
        self.__ending_indices = {
            1: set([self.__length - (i + 1) for i in range(self.__size)]),
            2: set([self.__size * (i + 1) - 1 for i in range(self.__size)]),
        }

        if state is None:
            self.reset()
        else:
            self.__player_id, self.__board = state[0], list(state[1:])

    def reset(self, state: Optional[Tuple[int, ...]] = None) -> Tuple[int, ...]:
        if state is None:
            self.__player_id = 1
            self.__board = [0 for _ in range(self.__length)]
        else:
            self.__player_id, self.__board = state[0], list(state[1:])
        return self.__get_state()

    def get_legal_actions(self) -> Tuple[int, ...]:
        return tuple(1 if i == 0 else 0 for i in self.__board)

    def generate_child_states(self) -> Tuple[Tuple[int, ...], ...]:
        child_states = []
        for i in self.get_legal_actions():
            child_states += self.generate_state(i)
        return tuple(child_states)

    def generate_state(self, action: int) -> Tuple[int, ...]:
        next_board = list(self.__board)
        next_board[action] = self.__player_id
        return (Hex.opposite_player[self.__player_id], *next_board)

    def is_final_state(self) -> bool:
        """
        Checks whether the opposite player has won the game.
        """
        opposite_player = Hex.opposite_player[self.__player_id]
        if sum(self.__modified_list[opposite_player]) < self.__size:  # Does the player have the sufficient amount of pegs along its axis?
            return False

        # Sufficient amount of pegs, check for path using BFS
        visited_cells = set()
        for i in range(self.__size):
            index = i if opposite_player == 1 else i * self.__size
            if self.__board[index] == opposite_player and index not in visited_cells:

                # BFS
                visited_cells.add(index)
                queue = deque()
                queue.append(index)
                while len(queue) > 0:
                    current_cell = queue.popleft()
                    for neighbour in self.__get_filled_neighbours(current_cell, opposite_player):
                        if neighbour not in visited_cells and neighbour not in queue:
                            queue.append(neighbour)
                            if neighbour in self.__ending_indices[opposite_player]:
                                return True
                    visited_cells.add(current_cell)
        return False

    def step(self, action: int) -> Tuple[Tuple[int, ...], int]:
        assert 0 <= action < self.__size ** 2, 'Illegal action, index out of range'
        assert self.__board[action] == 0, 'Illegal action, cell is occupied'

        self.__board[action] = self.__player_id
        self.__modified_list[self.__player_id][self.__player_axis(action)] = True  # Used to speed up winning condition check
        self.__player_id = Hex.opposite_player[self.__player_id]
        return self.__get_state(), 0

    def __get_state(self) -> Tuple[int, ...]:
        return (self.__player_id, *self.__board)

    def __player_axis(self, action: int) -> int:
        if (self.__player_id == 1):
            return action % self.__size
        return action // self.__size

    def __coordinates_to_index(self, coordinates: Tuple[int, int]) -> int:
        return (coordinates[0] * self.__size) + coordinates[1]

    def __get_filled_neighbours(self, index: int, player_id: int) -> Set[int]:
        def is_cell_neighbour(cell: int) -> bool:
            if not (0 <= cell < self.__length):
                return False
            if abs((cell % self.__size) - (index % self.__size)) > 1:
                return False
            if self.__board[cell] != player_id:
                return False
            return True

        return set(filter(is_cell_neighbour, self.__get_neighbouring_indices(index)))

    def __get_neighbouring_indices(self, index: int) -> Set[int]:
        return {
            index - self.__size,
            index + self.__size,
            index + 1,
            index - 1,
            index - self.__size + 1,
            index + self.__size - 1
        }

    def __draw_board(self, action: int) -> None:
        pass
        # Visualize.draw_board(self, self.__board, action)
