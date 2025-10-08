from collections import namedtuple
import os

class Graph:
  def __init__(self, payload):
    self.points = []
    for p in payload.get('points', []):
      point = namedtuple('Point', iter(p.keys()))(**p)
      self.points.append(point)
    
    self.axes = []
    for ax in payload.get('axes', []):
      axis = namedtuple('Axis', iter(ax.keys()))(**ax)
      self.axes.append(axis)
    
    self.limits = []
    for l in payload.get('limits', []):
      limit = namedtuple('Limit', iter(l.keys()))(**l)
      self.limits.append(limit)
      
    self.lines = []
    for ln in payload.get('lines', []):
      line = namedtuple('Line', iter(ln.keys()))(**ln)
      self.lines.append(line)
 
    self.grids = []
    for ln in payload.get('grids', []):
      grid = namedtuple('Grid', iter(ln.keys()))(**ln)
      self.grids.append(grid)

  def __str__(self):
    outStr = os.linesep + "Points:" + os.linesep
    outStr = outStr + os.linesep.join(["  {},{}".format(p.x, p.y) for p in self.points])
    outStr = outStr + os.linesep + "Axes (High/Low):" + os.linesep
    outStr = outStr + os.linesep.join(["  [{}, {}]".format(p.high, p.low) for p in self.axes])
    outStr = outStr + os.linesep + "Lines:" + os.linesep
    outStr = outStr + os.linesep.join(["  Points in segment: {}".format(len(p.segments)) for p in self.lines])
    if self.limits:
      outStr = outStr + os.linesep + "Limits:" + os.linesep
      outStr = outStr + os.linesep.join(["  name={},value={},axis={}".format(p.name, p.value, p.axis) for p in self.limits])

    return outStr
