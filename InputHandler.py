from cmath import sqrt
from enum import Enum
from shapely.geometry import LineString
from shapely.geometry import Point as ShapelyPoint


class PointType(Enum):
    STARTING = 1
    END = 2
    INTERSECTION = 3
    CIRCLE_START = 4
    CIRCLE_END = 5
    C_w_C_INTERSECTION = 6 # Circle with circle
    C_w_L_INTERSECTION = 7 # Circle with line
    OUT_OF_RANGE = 8


class Point:
    def __init__(self,x, y, p_type, line1=None, line2=None, circle1=None, circle2=None):
        self.x = x
        self.y = y
        self.p_type = p_type
        self.line1 = line1
        self.line2 = line2
        self.circle1 = circle1
        self.circle2 = circle2

    def coordinate(self):
        return self.x, self.y

    def toString(self):
        return "({}, {})".format(self.x, self.y)


class LineSegment:
    def __init__(self, m, c, t1, t2):
        """
        :param m: Slope
        :param c: Y-Intercept
        :param t1: Left endpoint of Line-segment
        :param t2: Right endpoint of Line-segment
        """
        self.slope = m
        self.y_intercept = c
        self.t1 = t1
        self.t2 = t2

    def value_at_x(self, x):
        return self.slope*x + self.y_intercept

    def start_point(self):
        return Point(self.t1, self.value_at_x(self.t1), PointType.STARTING, line1=self)

    def end_point(self):
        return Point(self.t2, self.value_at_x(self.t2), PointType.END, line1=self)

    def compute_intersection(self, line2):
        # x = (c2-c1)/(m1-m2)
        if type(line2) is not LineSegment:
            raise TypeError("Invalid input type, input is not of the type InputHandler.LineSegment")
        line1 = self
        if line1.slope - line2.slope == 0:
            return Point(float('inf'), float('inf'), PointType.OUT_OF_RANGE)
        x_inter = (line2.y_intercept - line1.y_intercept)/(line1.slope - line2.slope)
        if line1.t1 < x_inter < line1.t2 and line2.t1 < x_inter < line2.t2:
            return Point(x_inter, line1.value_at_x(x_inter), PointType.INTERSECTION, line1=self, line2=line2)
        return Point(x_inter, line1.value_at_x(x_inter), PointType.OUT_OF_RANGE)

    def is_equal(self, line2):
        line1 = self
        if line1.slope == line2.slope and line1.y_intercept == line2.y_intercept and line1.t1 == line2.t1 and line1.t2 == line2.t2:
            return True
        else:
            return False


class Circle:
    def __init__(self, x, y, r, upper_circle, lower_circle):
        self.center_x = x
        self.center_y = y
        self.upper_circle = upper_circle
        self.lower_circle = lower_circle
        self.radius = r

    def center(self):
        return self.center_x, self.center_y

    def value_at_x(self, x):
        b = 2*self.center_y
        a = self.center_x
        c = -(self.radius**2) + x**2 + a**2 - 2*a*x
        # TODO These can be complex numbers but ideally should not matter since the circle is always removed
        return (-b + sqrt(b**2 - 4*a*c))/2*a, (-b - sqrt(b**2 - 4*a*c))/2*a

    def compute_intersection_line(self, line):
        # TODO Tangency case
        p = ShapelyPoint(self.center_x, self.center_y)
        c = p.buffer(self.radius).boundary
        l = LineString([(0, line.value_at_x(0)), (10, line.value_at_x(10))])
        i = c.intersection(l)
        result = []
        try:
            i.geoms[0].coords[0], i.geoms[1].coords[0]
        except AttributeError:
            return None, None
        if line.t1 <= i.geoms[0].coords[0][0] <= line.t2:
            result.append(Point(i.geoms[0].coords[0][0], i.geoms[0].coords[0][1], PointType.C_w_L_INTERSECTION, circle1=self, line1=line))
        else:
            result.append(None)
        if line.t1 <= i.geoms[1].coords[0][0] <= line.t2:
            result.append(Point(i.geoms[1].coords[0][0], i.geoms[1].coords[0][1], PointType.C_w_L_INTERSECTION, circle1=self, line1=line))
        else:
            result.append(None)
        return result[0], result[1]

    def compute_intersection_circle(self, circle2):
        # TODO Tangency case
        p1 = ShapelyPoint(self.center_x, self.center_y)
        c1 = p1.buffer(self.radius).boundary
        p2 = ShapelyPoint(circle2.center_x, circle2.center_y)
        c2 = p2.buffer(circle2.radius).boundary
        i = c1.intersection(c2)
        try:
            i.geoms[0].coords[0], i.geoms[1].coords[0]
        except AttributeError:
            # Check Tangency
            return Point(float('inf'), float('inf'), PointType.OUT_OF_RANGE), Point(float('inf'), float('inf'), PointType.OUT_OF_RANGE)
        p1 = Point( i.geoms[0].coords[0][0],  i.geoms[0].coords[0][1], PointType.C_w_C_INTERSECTION, circle1=self, circle2= circle2)
        p2 = Point( i.geoms[1].coords[0][0],  i.geoms[1].coords[0][1], PointType.C_w_C_INTERSECTION, circle1=self, circle2= circle2)

        return p1, p2

    def is_same(self, circle2):
        circle1 = self
        if circle1.center_x == circle2.center_x and circle1.center_y == circle2.center_y and circle1.radius == circle2.radius:
            return True
        else:
            return False

    def intersects_upper(self, point):
        if point.y > self.center_y:
            return True
        else:
            return False



class CircleHalf(Enum):
    UPPER = 1
    LOWER = 2


class HalfCircle:
    def __init__(self, parent_circle, half):
        self.parent = parent_circle
        self.half = half


class PlaneSweepInput:
    def __init__(self, line_segments, circles):
        self.line_segments = line_segments
        self.circles = circles

    def all_points(self):
        endpoints = []
        for line in self.line_segments:
            endpoints.append(line.start_point())
            endpoints.append(line.end_point())
        return endpoints


def get_input(filename = "input.txt"):
    line_segments = []
    circles = []
    file = open(filename)
    try:
        number_of_entries = int(file.readline())
    except ValueError as e:
        print("Invalid input file. Expected Integer in the first line")
        raise Exception(e)

    for i in range(int(number_of_entries)):
        coordinates = file.readline().split(" ")
        if len(coordinates) == 4:
            # Line Segment y = mx + c [t1, t2]
            [m, c, t1, t2] = [float(coordinates[0]), float(coordinates[1]), float(coordinates[2]), float(coordinates[3])]
            current_segment = LineSegment(m,c,t1,t2)
            line_segments.append(current_segment)
        elif len(coordinates) == 3:
            # Circle with c_x c_y and radius
            [c_x, c_y, r] = [float(coordinates[0]), float(coordinates[1]), float(coordinates[2])]
            current_circle = Circle(c_x, c_y, r)
            circles.append(current_circle)

    plane_sweep_inputs = PlaneSweepInput(line_segments, circles)
    return plane_sweep_inputs


if __name__ == "__main__":
    a = get_input("input.txt")