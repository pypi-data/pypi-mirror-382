import numpy as np
import gymnasium

def make_reward_function_transition_matrix(env):
  """
  Build reward function and transition function

  Parameters
  ----------
  env: Environment

  Return
  -------
  reward: np array of shape (n_actions, n_states)
   reward[a, s] return the reward obtained after playing action a in state s
  transition: np array of shape (n_actions, n_states, n_states)
   transition[a, s, s2] returns the probability of transitionning to s2 if playing action a in state s
  """
  n_states = env.observation_space.n
  n_actions = env.action_space.n
  reward = np.zeros((n_actions, n_states))
  transition = np.zeros((n_actions, n_states, n_states))
  for s in range(n_states):
    for a in range(n_actions):
      for (proba, s2, r, term) in env.unwrapped.P[s][a]:
        reward[a, s] += r * proba
        transition[a, s, s2] += proba
  return reward, transition

def q_pi(R, P, gamma, pi):
  """
  Compute the state-action value function of pi (in closed form)

  Parameters
  ----------
  R: np array of shape (n_actions, n_states)
   R[a, s] return the reward obtained after playing action a in state s
  P: np array of shape (n_actions, n_states, n_states)
   P[a, s, s2] returns the probability of transitionning to s2 if playing action a in state s
  gamma: float
    Discounting parameter (between 0 and 1)
  pi: np array of size (n_actions, n_states)
    Policy to evaluate
  Return
  ------
  q_pi: np array of size n_states, n_actions
    State action value of pi
  """
  n_actions, n_states = R.shape
  Rpi = np.zeros(n_states)
  Ppi = np.zeros((n_states, n_states))
  I = np.eye(n_states)
  for s in range(n_states):
    Rpi[s] = np.sum([R[a, s] * pi[a, s] for a in range(n_actions)])
    Ppi[s] = np.sum([P[a, s, :] * pi[a, s] for a in range(n_actions)], axis=0)
  v_pi = np.linalg.pinv(I - gamma * Ppi).dot(Rpi)
  qpi = np.zeros((n_states, n_actions))
  for s in range(n_states):
    for a in range(n_actions):
      qpi[s, a] = R[a, s] + gamma * P[a, s, :].dot(v_pi)
  return qpi

def policy_iteration(env, n_iterations, gamma, R=None, P=None):
  """
  Perform policy iteration
  Parameters
  ----------
  env: Environment
    The environment
  n_iteration: int
    Number of iterations to perform
  gamma: float
    Discount parameter
  Return
  ------
  pi: np array of size n_actions, n_states
    Policy that associates to a state action pair a probability
  """
  n_states = env.observation_space.n
  n_actions = env.action_space.n
  if R is None or P is None:
    R, P = make_reward_function_transition_matrix(env)
  q = np.zeros((n_states, n_actions))
  for _ in range(n_iterations):
    pi = np.zeros((n_actions, n_states))
    for s in range(n_states):
      pi[np.argmax(q[s]), s] = 1
    q = q_pi(R, P, gamma, pi)
  return pi

def compute_vpi(env, pi, gamma):
    """Compute the state value function of policy pi

    Args:
        env (Environment): _description_
        pi (np array of size (n_actions, n_states)): policy
        gamma (float): discount factor
    
    Returns:
        np array of size (n_states): value function
    """
    n_states = env.observation_space.n
    n_actions = env.action_space.n
    R, P = make_reward_function_transition_matrix(env)
    Rpi = np.zeros(n_states)
    Ppi = np.zeros((n_states, n_states))
    I = np.eye(n_states)
    for s in range(n_states):
        Rpi[s] = np.sum([R[a, s] * pi[a, s] for a in range(n_actions)])
        Ppi[s] = np.sum([P[a, s, :] * pi[a, s] for a in range(n_actions)], axis=0)
    v_pi = np.linalg.pinv(I - gamma * Ppi).dot(Rpi)
    return v_pi

def compute_qpi(env, pi, gamma):
    """Compute the state-action value function of policy pi

    Args:
        env (Environment): _description_
        pi (np array of size (n_actions, n_states)): policy
        gamma (float): discount factor
    
    Returns:
        np array of size (n_states, n_actions): state-action value function
    """
    n_states = env.observation_space.n
    n_actions = env.action_space.n
    R, P = make_reward_function_transition_matrix(env)
    return q_pi(R, P, gamma, pi)
    


def simulated_env(pos):
  """
  Creates an environment with a custom starting position.

  Parameters
  ----------

  pos: int
    Index of startin position

  Return
  ------

  env: Environement or None (if starting is not F)
    The environment with the custom starting position

  starting: int
    "H": Startin on a H
    "F": Starting on a F
    "G": Starting on a G

  """
  map = [list("FFFF"), list("FHFH"), list("FFFH"), list("HFFG")]
  if map[pos // 4][pos % 4] == "H" or map[pos // 4][pos % 4] == "G":
    return None, map[pos // 4][pos % 4]
  map[pos // 4][pos % 4] = "S"
  map = ["".join(m) for m in map]
  senv = gymnasium.make('FrozenLake-v1', render_mode="rgb_array", desc=map, is_slippery=False)
  return senv, "F"
