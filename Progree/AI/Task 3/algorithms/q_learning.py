"""
Tabular Q-Learning Reinforcement Learning Agent for Grid Navigation.
Learns state-action value table Q(s, a) using Bellman optimality equation with potential-based reward shaping:
Q(s, a) <- Q(s, a) + alpha * [Reward + gamma * max_a' Q(s', a') - Q(s, a)]
"""

import random
import time
import math
from typing import List, Tuple, Dict, Any, Generator, Optional, Set
from .base import (
    BaseSearchAlgorithm, SearchResult, StepLog,
    calculate_path_cost
)

ACTIONS_4 = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # Up, Right, Down, Left
ACTIONS_8 = [
    (-1, 0), (0, 1), (1, 0), (0, -1),
    (-1, -1), (-1, 1), (1, -1), (1, 1)
]

class QLearningAgent(BaseSearchAlgorithm):
    def __init__(
        self,
        alpha: float = 0.3,       # Learning rate
        gamma: float = 0.98,      # Discount factor
        epsilon: float = 0.6,     # Initial exploration rate
        epsilon_decay: float = 0.99,
        min_epsilon: float = 0.05,
        episodes: int = 400,
        max_steps_per_episode: int = 350
    ):
        super().__init__("Q-Learning Agent (RL)")
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon
        self.episodes = episodes
        self.max_steps_per_episode = max_steps_per_episode
        self.q_table: Dict[Tuple[int, int], List[float]] = {}
        self.episode_rewards: List[float] = []

    def _get_actions(self, allow_diagonal: bool) -> List[Tuple[int, int]]:
        return ACTIONS_8 if allow_diagonal else ACTIONS_4

    def _get_q(self, state: Tuple[int, int], num_actions: int) -> List[float]:
        if state not in self.q_table:
            # Optimistic or zero initialization
            self.q_table[state] = [0.0] * num_actions
        return self.q_table[state]

    def _choose_action(self, state: Tuple[int, int], actions: List[Tuple[int, int]], eps: float) -> int:
        if random.random() < eps:
            return random.randint(0, len(actions) - 1)
        q_vals = self._get_q(state, len(actions))
        max_q = max(q_vals)
        best_indices = [i for i, val in enumerate(q_vals) if abs(val - max_q) < 1e-7]
        return random.choice(best_indices)

    def _heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def search(self, grid: Any, allow_diagonal: bool = False, **kwargs) -> SearchResult:
        start_time = time.perf_counter_ns()
        start = grid.start
        goal = grid.goal
        total_walkable = grid.total_walkable_cells
        actions = self._get_actions(allow_diagonal)
        num_actions = len(actions)

        self.q_table.clear()
        self.episode_rewards.clear()
        explored_nodes: Set[Tuple[int, int]] = {start}
        eps = self.epsilon
        total_steps = 0

        for ep in range(self.episodes):
            curr = start
            ep_reward = 0.0

            for _ in range(self.max_steps_per_episode):
                total_steps += 1
                explored_nodes.add(curr)

                if curr == goal:
                    break

                a_idx = self._choose_action(curr, actions, eps)
                dr, dc = actions[a_idx]
                next_state = (curr[0] + dr, curr[1] + dc)

                # Base reward + potential-based reward shaping
                if not grid.in_bounds(next_state[0], next_state[1]) or not grid.is_walkable(next_state[0], next_state[1]):
                    reward = -15.0
                    next_state = curr
                elif next_state == goal:
                    reward = 200.0
                else:
                    move_cost = grid.get_move_cost(curr, next_state)
                    # Heuristic progress shaping bonus: encourages moving toward goal
                    dist_curr = self._heuristic(curr, goal)
                    dist_next = self._heuristic(next_state, goal)
                    progress_bonus = (dist_curr - dist_next) * 2.0
                    reward = -1.0 * move_cost + progress_bonus

                ep_reward += reward

                # Bellman Update
                old_q = self._get_q(curr, num_actions)[a_idx]
                next_max_q = max(self._get_q(next_state, num_actions))
                target = reward + self.gamma * next_max_q
                self.q_table[curr][a_idx] = old_q + self.alpha * (target - old_q)

                curr = next_state

            self.episode_rewards.append(ep_reward)
            eps = max(self.min_epsilon, eps * self.epsilon_decay)

        # Extract greedy optimal path from learned Q-table
        path = [start]
        curr = start
        visited_in_path = {start}
        success = False

        for _ in range(self.max_steps_per_episode):
            if curr == goal:
                success = True
                break
            q_vals = self._get_q(curr, num_actions)
            best_idx = int(max(range(num_actions), key=lambda i: q_vals[i]))
            dr, dc = actions[best_idx]
            next_state = (curr[0] + dr, curr[1] + dc)

            if not grid.is_walkable(next_state[0], next_state[1]) or next_state in visited_in_path:
                break

            visited_in_path.add(next_state)
            path.append(next_state)
            curr = next_state
            if curr == goal:
                success = True
                break

        if not success:
            path = []

        elapsed_ms = (time.perf_counter_ns() - start_time) / 1e6
        path_cost = calculate_path_cost(grid, path) if success else 0.0
        expanded_count = len(explored_nodes)
        density = expanded_count / total_walkable if total_walkable > 0 else 0.0

        return SearchResult(
            algorithm_name=self.name,
            success=success,
            path=path,
            path_cost=path_cost,
            step_count=total_steps,
            expanded_nodes_count=expanded_count,
            expanded_density=density,
            runtime_ms=elapsed_ms,
            peak_frontier=num_actions,
            explored_nodes=explored_nodes,
            metadata={
                "episodes_trained": self.episodes,
                "final_epsilon": round(eps, 4),
                "avg_reward_last_50": sum(self.episode_rewards[-50:]) / max(1, len(self.episode_rewards[-50:])),
                "reward_history": self.episode_rewards
            }
        )

    def step_generator(self, grid: Any, allow_diagonal: bool = False, **kwargs) -> Generator[Dict[str, Any], None, SearchResult]:
        start_time = time.perf_counter_ns()
        start = grid.start
        goal = grid.goal
        total_walkable = grid.total_walkable_cells
        actions = self._get_actions(allow_diagonal)
        num_actions = len(actions)

        self.q_table.clear()
        self.episode_rewards.clear()
        explored_nodes: Set[Tuple[int, int]] = {start}
        eps = self.epsilon
        total_steps = 0

        yield {"type": "init", "open": [start], "closed": [], "current": start}

        for ep in range(self.episodes):
            curr = start
            ep_reward = 0.0
            ep_path = [start]

            for step_idx in range(self.max_steps_per_episode):
                total_steps += 1
                explored_nodes.add(curr)

                if curr == goal:
                    break

                a_idx = self._choose_action(curr, actions, eps)
                dr, dc = actions[a_idx]
                next_state = (curr[0] + dr, curr[1] + dc)

                if not grid.in_bounds(next_state[0], next_state[1]) or not grid.is_walkable(next_state[0], next_state[1]):
                    reward = -15.0
                    next_state = curr
                elif next_state == goal:
                    reward = 200.0
                else:
                    move_cost = grid.get_move_cost(curr, next_state)
                    dist_curr = self._heuristic(curr, goal)
                    dist_next = self._heuristic(next_state, goal)
                    progress_bonus = (dist_curr - dist_next) * 2.0
                    reward = -1.0 * move_cost + progress_bonus

                ep_reward += reward
                old_q = self._get_q(curr, num_actions)[a_idx]
                next_max_q = max(self._get_q(next_state, num_actions))
                target = reward + self.gamma * next_max_q
                self.q_table[curr][a_idx] = old_q + self.alpha * (target - old_q)

                curr = next_state
                ep_path.append(curr)

            self.episode_rewards.append(ep_reward)
            eps = max(self.min_epsilon, eps * self.epsilon_decay)

            if (ep + 1) % max(1, self.episodes // 30) == 0 or ep == self.episodes - 1:
                yield {
                    "type": "step",
                    "current": curr,
                    "open": ep_path[-10:],
                    "closed": list(explored_nodes),
                    "steps": total_steps,
                    "episode": ep + 1,
                    "epsilon": eps,
                    "reward": ep_reward,
                    "q_table_size": len(self.q_table)
                }

        # Greedy path rollout
        path = [start]
        curr = start
        visited_in_path = {start}
        success = False

        for _ in range(self.max_steps_per_episode):
            if curr == goal:
                success = True
                break
            q_vals = self._get_q(curr, num_actions)
            best_idx = int(max(range(num_actions), key=lambda i: q_vals[i]))
            dr, dc = actions[best_idx]
            next_state = (curr[0] + dr, curr[1] + dc)

            if not grid.is_walkable(next_state[0], next_state[1]) or next_state in visited_in_path:
                break

            visited_in_path.add(next_state)
            path.append(next_state)
            curr = next_state
            if curr == goal:
                success = True
                break

        if not success:
            path = []

        elapsed_ms = (time.perf_counter_ns() - start_time) / 1e6
        path_cost = calculate_path_cost(grid, path) if success else 0.0
        expanded_count = len(explored_nodes)
        density = expanded_count / total_walkable if total_walkable > 0 else 0.0

        result = SearchResult(
            algorithm_name=self.name,
            success=success,
            path=path,
            path_cost=path_cost,
            step_count=total_steps,
            expanded_nodes_count=expanded_count,
            expanded_density=density,
            runtime_ms=elapsed_ms,
            peak_frontier=num_actions,
            explored_nodes=explored_nodes,
            metadata={
                "episodes_trained": self.episodes,
                "final_epsilon": round(eps, 4),
                "avg_reward_last_50": sum(self.episode_rewards[-50:]) / max(1, len(self.episode_rewards[-50:])),
                "reward_history": self.episode_rewards
            }
        )
        yield {"type": "complete", "result": result, "path": path}
        return result
