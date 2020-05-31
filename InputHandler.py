from enum import Enum


class PointType(Enum):
    STARTING = 1
    END = 2
    INTERSECTION = 3
    UPPER_CIRCLE_START = 4
    LOWER_CIRCLE_END = 5
    OUT_OF_RANGE = 6


class Point:
    def __init__(self,x, y, p_type, line1=None, line2=None):
        self.x = x
        self.y = y
        self.p_type = p_type
        self.line1 = line1
        self.line2 = line2

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
    def __init__(self, x, y, r):
        self.center_x = x
        self.center_y = y
        self.radius = r

    def center(self):
        return self.center_x, self.center_y


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