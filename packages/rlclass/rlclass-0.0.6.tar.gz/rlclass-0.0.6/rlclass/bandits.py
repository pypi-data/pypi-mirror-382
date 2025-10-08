import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from matplotlib import rc

rc('animation', html='jshtml')
  
    
def animate(pi, mu, T, *other):
  """
  pi: policy
  mu: arm means
  T: horizon
  other: 
    Other parameters passed to pi
    pi(W, N, *other)
  """
  K = len(mu)
  N = np.zeros(K)
  W = np.zeros(K)

  # Define shapes and their representations
  shapes = {
      'circle': {'marker': 'o', 'color': 'red'},
      'triangle': {'marker': '^', 'color': 'green'},
      'square': {'marker': 's', 'color': 'blue'},
      'dollar': {'text': '$', 'color': 'gold'}
  }

  # Create a figure and axis
  fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 4))

  # Set the limits of the plot for slot machines
  ax1.set_xlim(-1, K)
  ax1.set_ylim(0, 1)

  # Remove the frame and ticks from the first axis
  ax1.axis('off')

  # Set the limits of the plot for the histogram of plays
  ax2.set_xlim(-1, K)
  ax2.set_ylim(0, T)

  # Create a bar plot for the histogram of plays and wins
  hist_bars_plays = ax2.bar(range(K), N, color='blue', edgecolor='black', linewidth=1.5, alpha=0.6, label='Plays')
  hist_bars_wins = ax2.bar(range(K), W, color='gold', edgecolor='black', linewidth=1.5, alpha=0.6, label='Wins')

  # Set the x-ticks and labels for the second axis
  ax2.set_xticks(range(K))
  ax2.set_xticklabels([f'Machine {i + 1}\n$\\mu_{i + 1} = {mu[i]:.2f}$' for i in range(K)])
  ax2.legend(loc='upper right')

  # Function to update the plot
  def update(timestep):
      ax1.clear()  # Clear the previous frame
      ax1.set_xlim(-1, K)
      ax1.set_ylim(0, 1)
      ax1.axis('off')

      # Determine if the selected machine results in a win
      machine_index = pi(W, N, *other)
      N[machine_index] += 1

      # Determine the outcome of the play
      if np.random.rand() < mu[machine_index]:
          # Win: all shapes are dollars
          shapes_displayed = ['dollar', 'dollar', 'dollar']
          W[machine_index] += 1
      else:
          # Lose: shapes can be any mix, including dollars, but not all dollars
          available_shapes = list(shapes.keys())
          while True:
              shapes_displayed = np.random.choice(available_shapes, size=3, replace=True)
              if not (shapes_displayed[0] == 'dollar' and shapes_displayed[1] == 'dollar' and shapes_displayed[2] == 'dollar'):
                  break

      # Update the histogram of plays and wins
      for rect_plays, rect_wins, h_plays, h_wins in zip(hist_bars_plays, hist_bars_wins, N, W):
          rect_plays.set_height(h_plays)
          rect_wins.set_height(h_wins)

      # Display shapes on the selected machine, side by side with space
      for i, shape in enumerate(shapes_displayed):
          shape_info = shapes[shape]
          if shape == 'dollar':
              ax1.text(machine_index + (i - 1) * 0.2, 0.7, shape_info['text'], color=shape_info['color'], ha='center', va='center', fontsize=20)
          else:
              ax1.plot(machine_index + (i - 1) * 0.2, 0.7, marker=shape_info['marker'], color=shape_info['color'], markersize=20)

      # Set the title to the current timestep
      ax1.set_title(f'Timestep {timestep + 1}', fontsize=16, fontweight='bold')
      ax2.set_title('Histogram of Plays and Wins', fontsize=16, fontweight='bold')

  # Create the animation with a dynamic interval
  def init():
      # Initialize the animation with a slow interval
      return []

  plt.close()

  # Create the animation
  ani = animation.FuncAnimation(fig, update, init_func=init, frames=T, repeat=False)
  return ani
