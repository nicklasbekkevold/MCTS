from math import log, sqrt
from typing import Callable, Tuple

import parameters
from TreeNode import TreeNode
from world.simulated_world import SimulatedWorld

Policy = Callable[[Tuple[int, ...], Tuple[int, ...]], int]  # (s, valid_actions) -> a


class MCTS:

    player_sign = {
        1: 1,
        2: -1
    }

    def __init__(self, initial_state: Tuple[int, ...]) -> None:
        self.root = TreeNode(initial_state)
        self.action_space = parameters.NUMBER_OF_ACTIONS

    def update_root(self, action: int) -> None:
        self.root = self.root.children[action]
        self.root.parent = None

    def get_normalized_distribution(self) -> Tuple[float, ...]:
        # print(list(map(lambda node: node.visits, self.root.children.values())), "/", self.root.visits - 1)
        distribution = []
        for action in range(self.action_space):
            if action in self.root.children:
                distribution.append(float(self.root.children[action].visits) / float(self.root.visits - 1))
            else:
                distribution.append(0.0)
        return tuple(distribution)

    def tree_search(self, rootNode: TreeNode, world: SimulatedWorld) -> TreeNode:
        current_node = rootNode
        while not current_node.is_leaf:
            action = self.tree_policy(current_node)
            # print('UCT values', list(map(lambda key: (key, self.UCT(current_node.children[key])), current_node.children.keys())))
            # print(f'Node chosen {action}. For player {current_node.player_id}')
            _, _ = world.step(action)
            current_node = current_node.children[action]

        # Node is terminal state
        if world.is_final_state():
            current_node.set_terminal()
            return current_node

        # Node expansion
        if current_node.visits != 0:
            for action, legal in enumerate(world.get_legal_actions()):
                if bool(legal):
                    current_node.add_node(action, world.generate_state(action))
            current_node = list(current_node.children.values())[0]
        return current_node

    def do_rollout(self, leaf_node: TreeNode, default_policy: Policy, world: SimulatedWorld) -> int:
        if leaf_node.is_terminal:
            return world.get_winner_id()

        current_state = leaf_node.state
        while not world.is_final_state():
            legal_actions = world.get_legal_actions()
            action = default_policy(current_state, legal_actions)
            current_state, _ = world.step(action)
        return world.get_winner_id()

    def do_backpropagation(self, leaf_node: TreeNode, winner: int) -> None:
        current_node = leaf_node
        while current_node is not None:
            current_node.add_reward(winner)
            current_node.increment_visit_count()
            current_node = current_node.parent

    def tree_policy(self, node: TreeNode) -> int:
        """
        Choses an action based on the UCT score of that corresponding node
        """
        policy_func = max if node.player_id == 1 else min
        return policy_func(node.children.keys(), key=lambda key: self.UCT(node.children[key]))

    def UCT(self, child_node: TreeNode) -> float:
        c = -parameters.UCT_C if child_node.player_id == 1 else parameters.UCT_C
        return child_node.value + (c * sqrt(2 * log(child_node.parent.visits) / (child_node.visits + 1)))
