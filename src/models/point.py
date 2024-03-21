class Point:
  def __init__(self, x, y):
      """
      A point specified by (x,y) coordinates in the cartesian plane
      """
      self.x = x
      self.y = y

  def to_tuple(self):
      ''' Returns the point as a tuple '''
      return (int(self.x), int(self.y))