import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import rc
rc('animation', html='jshtml')

def make_animation(imgs):
  """
  Makes an animation from a list of images
  Parameters
  ----------
  imgs: list of (height, width, 3) np arrays
    list of images
  Return
  -------
  ani: animation
  """
  fig, ax = plt.subplots()
  draw = []
  for i in range(len(imgs)):
    draw_i = ax.imshow(imgs[i])
    if i == 0:
      ax.imshow(imgs[0]) # Show an initial one first
    draw.append([draw_i])
  plt.close()
  ani = animation.ArtistAnimation(fig, draw, interval=200, blit=True,
                              repeat=False)
  return ani
