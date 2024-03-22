import sys
import cv2

class Polygon:
    def __init__(self, points):
        """
        points: a list of Points in clockwise order.
        """
        self.points = points

    @property
    def edges(self):
        edge_list = []
        for i,p in enumerate(self.points):
            p1 = p
            p2 = self.points[(i+1) % len(self.points)]
            edge_list.append((p1,p2))

        return edge_list
    
    @property
    def edges_as_tuples(self):
        return [(p1.to_tuple(), p2.to_tuple()) for p1, p2 in self.edges]
    
    @property
    def points_as_tuples(self):
        return [p.to_tuple() for p in self.points]
    
    def draw(self, frame, color=(0, 255, 0), thickness=2):
        for i in range(len(self.points)):
            p1 = self.points[i]
            p2 = self.points[(i+1) % len(self.points)]
            cv2.line(frame, p1.to_tuple(), p2.to_tuple(), color, thickness)

    # Ray casting algorithm to find if point inside polygon
    # http://www.philliplemons.com/posts/ray-casting-algorithm#:~:text=The%20algorithm%20starts%20with%20P,as%20seen%20in%20Figure%202.
    def contains(self, point):
        # _huge is used to act as infinity if we divide by 0
        _huge = sys.float_info.max
        # _eps is used to make sure points are not on the same line as vertexes
        _eps = 0.00001

        # We start on the outside of the polygon
        inside = False
        for edge in self.edges:
            # Make sure A is the lower point of the edge
            A, B = edge[0], edge[1]
            if A.y > B.y:
                A, B = B, A

            # Make sure point is not at same height as vertex
            if point.y == A.y or point.y == B.y:
                point.y += _eps

            if (point.y > B.y or point.y < A.y or point.x > max(A.x, B.x)):
                # The horizontal ray does not intersect with the edge
                continue

            if point.x < min(A.x, B.x): # The ray intersects with the edge
                inside = not inside
                continue

            try:
                m_edge = (B.y - A.y) / (B.x - A.x)
            except ZeroDivisionError:
                m_edge = _huge

            try:
                m_point = (point.y - A.y) / (point.x - A.x)
            except ZeroDivisionError:
                m_point = _huge

            if m_point >= m_edge:
                # The ray intersects with the edge
                inside = not inside
                continue

        return inside