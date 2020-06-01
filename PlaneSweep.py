from InputHandler import PlaneSweepInput, Point, PointType
import InputHandler
import heapq

epsilon = 0.001


class SweepLineStatus:
    def __init__(self):
        self.sweepline = 0
        self.tree = SortedList(key=lambda line_seg: line_seg.value_at_x(self.sweepline))

    def index_in_tree(self, line):
        for i in range(len(self.tree)):
            if self.tree[i].is_equal(line):
                return i
        return -1

    def swap_order(self, index1, index2, line1, line2):
        del self.tree[index1]
        del self.tree[index2]
        self.sweepline += epsilon
        self.tree.add(line1)
        self.tree.add(line2)

    def _binary_append(self, line):
        self.tree.append(line)
        self.tree.sort(key=lambda x: x.value_at_x(self.sweepline))  # TODO: Optimize

    def swap_cwc_intersection(self, circle1, circle2):
        if circle1.y > circle2.y:
            up_circle = circle1
            low_circle = circle2
        else:
            up_circle = circle2
            low_circle = circle1

        low_half_circle_index = self.tree.index(up_circle.lower_circle)
        up_half_circle_index = self.tree.index(low_circle.upper_circle)

        self.tree[low_half_circle_index], self.tree[up_half_circle_index] = self.tree[up_half_circle_index], self.tree[low_half_circle_index]



    def delete_circle_report_intersection(self, circle, sweepline):
        self.sweepline = sweepline
        intersections = []
        upper_circle_index = self.tree.index(circle.upper_circle)
        lower_circle_index = self.tree.index(circle.lower_circle)
        if upper_circle_index - lower_circle_index != 1:
            raise Exception("Circles are adjacent in the Sweepline status")
        try:
            upper_obj = self.tree[upper_circle_index+1]
            lower_obj = self.tree[lower_circle_index-1]
            if type(upper_obj) is InputHandler.LineSegment and type(lower_obj) is InputHandler.LineSegment:
                intersection = upper_obj.compute_intersection(lower_obj)
                if intersection.x > sweepline and intersection.p_type == PointType.INTERSECTION:
                    intersections.append(intersection)
            elif type(upper_obj) is InputHandler.LineSegment and type(lower_obj) is InputHandler.HalfCircle:
                circle_intersection1, circle_intersection2 = lower_obj.parent.compute_intersection_line(upper_obj)
                intersections.append(circle_intersection1)
                intersections.append(circle_intersection2)
            elif type(upper_obj) is InputHandler.HalfCircle and type(lower_obj) is InputHandler.LineSegment:
                circle_intersection1, circle_intersection2 = upper_obj.parent.compute_intersection_line(lower_obj)
                intersections.append(circle_intersection1)
                intersections.append(circle_intersection2)
            else:
                circle_intersection1, circle_intersection2 = upper_obj.parent.compute_intersection_circle(lower_obj)
                intersections.append(circle_intersection1)
                intersections.append(circle_intersection2)
        except IndexError:
            return intersections

    def add_circle_report_intersection(self, circle, sweepline):
        self.sweepline = sweepline
        intersections = []
        self._binary_append(circle.upper_circle)
        self._binary_append(circle.lower_circle)
        upper_circle_index = self.tree.index(circle.upper_circle)
        lower_circle_index = self.tree.index(circle.lower_circle)
        if upper_circle_index < lower_circle_index:
            self.tree[upper_circle_index], self.tree[lower_circle_index] = self.tree[lower_circle_index], self.tree[upper_circle_index]
            upper_circle_index, lower_circle_index = lower_circle_index, upper_circle_index
        try:
            obj_above = self.tree[upper_circle_index+1]
            if type(obj_above) is InputHandler.LineSegment:
                intersection1, intersection2 = circle.compute_intersection_line(obj_above)
                intersections.append(intersection1)
                intersections.append(intersection2)
            else:
                circle_intersection1, circle_intersection2 = circle.compute_intersection_circle(obj_above.parent)
                intersections.append(circle_intersection1)
                intersections.append(circle_intersection2)
        except IndexError:
            pass
        try:
            obj_below = self.tree[lower_circle_index-1]
            if type(obj_below) is InputHandler.LineSegment:
                intersection1, intersection2 = circle.compute_intersection_line(obj_below)
                intersections.append(intersection1)
                intersections.append(intersection2)
            else:
                circle_intersection1, circle_intersection2 = circle.compute_intersection_circle(obj_below.parent)
                intersections.append(circle_intersection1)
                intersections.append(circle_intersection2)
        except IndexError:
            pass
        return intersections

    def add_and_report_intersection(self, line, sweepline):
        self.sweepline = sweepline
        # Add a new line segment and report the s and s' which are adjacent to the new line
        self._binary_append(line)
        line_index = self.tree.index(line)
        intersections = []

        # In between the tree so check both above and below
        if 0 < line_index < len(self.tree)-1:
            adj_obj = self.tree[line_index+1]

            # Object below is a line segment
            if type(adj_obj) is InputHandler.LineSegment:
                intersection1 = line.compute_intersection(adj_obj)
                if intersection1.p_type == PointType.OUT_OF_RANGE:
                    intersection1 = None
                intersections.append(intersection1)

            # Object below is a Half Circle
            else:
                circle_intersection1, circle_intersection2 = adj_obj.parent.compute_intersection_line(line)
                intersections.append(circle_intersection1)
                intersections.append(circle_intersection2)

            # Object above is a line segment
            adj_obj = self.tree[line_index-1]
            if type(adj_obj) is InputHandler.LineSegment:
                intersection2 = line.compute_intersection(adj_obj)
                if intersection2.p_type == PointType.OUT_OF_RANGE:
                    intersection2 = None
                intersections.append(intersection2)

            # Object above is a Half Circle
            else:
                circle_intersection1, circle_intersection2 = adj_obj.parent.compute_intersection_line(line)
                intersections.append(circle_intersection1)
                intersections.append(circle_intersection2)

            return intersections

        # Added event is the top most event
        elif line_index == 0:
            object_below = self.tree[line_index + 1]
            if type(object_below) is InputHandler.LineSegment:
                try:
                    intersection = line.compute_intersection(self.tree[line_index+1])
                except IndexError:
                    intersections.append(None)
                    return intersections

                if intersection.x > sweepline and intersection.p_type == PointType.INTERSECTION:
                    intersections.append(intersection)

            # Object below is Half Circle
            else:
                circle_intersection1, circle_intersection2 = object_below.parent.compute_intersection_line(line)
                intersections.append(circle_intersection1)
                intersections.append(circle_intersection2)

        else:
            object_above = self.tree[line_index + 1]
            if type(object_above) is InputHandler.LineSegment:
                try:
                    intersection = line.compute_intersection(self.tree[line_index-1])
                except IndexError:
                    intersections.append(None)
                    return intersections
                if intersection.x > sweepline and intersection.p_type == PointType.INTERSECTION:
                    intersections.append(intersection)
                    return intersections

        return intersections

    def delete_and_report_intersection(self, line, sweepline):
        self.sweepline = sweepline
        result = None
        if len(self.tree) == 0:
            return None, None
        line_index = self.tree.index(line)
        if 0 < line_index < len(self.tree)-1:
            obj_above = self.tree[line_index - 1]
            obj_below = self.tree[line_index + 1]
            if type(obj_above) is InputHandler.LineSegment and type(obj_below) is InputHandler.LineSegment:
                intersection = self.tree[line_index - 1].compute_intersection(self.tree[line_index + 1])
                if intersection.x > sweepline and intersection.p_type == PointType.INTERSECTION:
                    result =  intersection, None
                else:
                    result = None, None
            elif type(obj_above) is InputHandler.LineSegment and type(obj_below) is InputHandler.HalfCircle:
                circle_intersection1, circle_intersection2 = obj_below.parent.compute_intersection_line(obj_above)
                result = circle_intersection1, circle_intersection2
            elif type(obj_above) is InputHandler.HalfCircle and type(obj_below) is InputHandler.LineSegment:
                circle_intersection1, circle_intersection2 = obj_above.parent.compute_intersection_line(obj_below)
                result = circle_intersection1, circle_intersection2
            # Both are circles
            else:
                # Check if they are the same circle
                obj_above = self.tree[line_index - 1]
                obj_below = self.tree[line_index + 1]
                if obj_above.parent.is_same(obj_below.parent):
                    result = None, None
                else:
                    circle_intersection1, circle_intersection2 = obj_below.parent.compute_intersection_circle(obj_above.parent)
                    result = circle_intersection1, circle_intersection2
        else:
            result = None, None
        del self.tree[line_index]
        return result

    def swap_and_report_intersection(self, line1, line2, sweepline):
        self.sweepline = sweepline
        # Swap the order of l1 and l2 and report s adj to l1 and s' adj to l2
        index1 = self.tree.index(line1)
        index2 = self.tree.index(line2)
        intersections = []
        if abs(index1-index2) != 1:
            raise Exception("Invalid line segments to swap. They are not adjacent in the tree.")
        # self.tree[index1], self.tree[index2] = self.tree[index2], self.tree[index1]
        self.swap_order(index1, index2, line1, line2)
        if index1 > index2:
            try:
                obj_below = self.tree[index1+1]
                if type(obj_below) is InputHandler.LineSegment:
                    intersection1 = line2.compute_intersection(obj_below)
                    if intersection1 is not None:
                        intersection1 = None if (intersection1.p_type == PointType.OUT_OF_RANGE or intersection1.x < sweepline) \
                            else intersection1
                    intersections.append(intersection1)
                else:
                    circle_intersection1, circle_intersection2 = obj_below.parent.compute_intersection_line(line2)
                    intersections.append(circle_intersection1)
                    intersections.append(circle_intersection2)
            except IndexError:
                intersection1 = None
                intersections.append(intersection1)
            try:
                obj_above = self.tree[index2 - 1]
                if type(obj_above) is InputHandler.LineSegment:
                    intersection2 = line1.compute_intersection(obj_above)
                    if intersection2 is not None:
                        intersection2 = None if (intersection2.p_type == PointType.OUT_OF_RANGE or intersection2.x < sweepline) \
                            else intersection2
                    intersections.append(intersection2)
                else:
                    circle_intersection1, circle_intersection2 = obj_above.parent.compute_intersection_line(line1)
                    intersections.append(circle_intersection1)
                    intersections.append(circle_intersection2)

            except IndexError:
                intersection2 = None
                intersections.append(intersection2)
        else:
            try:
                obj_above= self.tree[index1-1]
                if type(obj_above) is InputHandler.LineSegment:
                    intersection1 = line2.compute_intersection(obj_above)
                    if intersection1 is not None:
                        intersection1 = None if (intersection1.p_type == PointType.OUT_OF_RANGE or intersection1.x < sweepline) \
                            else intersection1
                    intersections.append(intersection1)
                else:
                    circle_intersection1, circle_intersection2 = obj_above.parent.compute_intersection_line(line2)
                    intersections.append(circle_intersection1)
                    intersections.append(circle_intersection2)
            except IndexError:
                intersection1 = None
                intersections.append(intersection1)
            try:
                obj_below= self.tree[index2 + 1]
                if type(obj_below) is InputHandler.LineSegment:
                    intersection2 = line1.compute_intersection(obj_below)
                    if intersection2 is not None:
                        intersection2 = None if (intersection2.p_type == PointType.OUT_OF_RANGE or intersection2.x < sweepline) \
                            else intersection2
                    intersections.append(intersection2)
                else:
                    circle_intersection1, circle_intersection2 = obj_below.parent.compute_intersection_line(line1)
                    intersections.append(circle_intersection1)
                    intersections.append(circle_intersection2)

            except IndexError:
                intersection2 = None
                intersections.append(intersection2)

        return intersections


class EventsQueue:
    def __init__(self):
        self.h = []

    def init_heap(self, values):
        self.clear()
        for point in values:
            if type(point) is not Point:
                raise TypeError("Invalid input type, input is not of the type InputHandler.Point")
            self.h.append((point.x, id(point), point))
        heapq.heapify(self.h)

    def push(self, val):
        if val is None:
            # Do nothing
            return
        if type(val) is not Point:
            raise TypeError("Invalid input type, input is not of the type InputHandler.Point")
        heapq.heappush(self.h, (val.x, id(val), val))

    def pop(self):
        """Assuming that no two points have the same x-coordinate"""
        return heapq.heappop(self.h)

    def next_unique_pop(self, prev):
        """
        Pops a point from the PQ not equal to the prev. *Assuming no to events have the same x-coordinate.
        :param prev: Previous point
        :return: If there is a unique point [True, point.x, point]
                Else return [False, None, None]
        """
        if self.size() == 0:
            return False, None, None
        elif prev is None:
            top, _, point = self.pop()
            return (True, top, point)
        else:
            top, _, point = self.pop()
            while top == prev.x and point.p_type == prev.p_type and self.size() > 0:
                top, _, point = self.pop()
            return (False, None, None) if top == prev.x and point.p_type == prev.p_type else (True, top, point)

    def clear(self):
        self.h = []

    def size(self):
        return len(self.h)


class PlaneSweep:
    def __init__(self, plane_sweep_input):
        if type(plane_sweep_input) is not PlaneSweepInput:
            raise Exception("Invalid Input Type")
        self.q = EventsQueue()
        self.q.init_heap(plane_sweep_input.all_points())
        self.sweepline_status = SweepLineStatus()
        self.intersections = []

    def _process_event(self, event):
        sweepline = event.x
        if event.p_type == PointType.STARTING:
            # Add line to SweepLineStatus
            # Compute intersections
            # Add intersections to EventsQueue if right of L
            intersections = self.sweepline_status.add_and_report_intersection(event.line1, sweepline)
            [self.q.push(intersection) for intersection in intersections]

        elif event.p_type == PointType.END:
            # Delete line from SweepLineStatus
            # Compute intersections for s and s'
            # Add intersections to EventsQueue if right of L
            intersection = self.sweepline_status.delete_and_report_intersection(event.line1, sweepline)

            self.q.push(intersection)
        elif event.p_type == PointType.INTERSECTION:
            # Swap Intersecting lines
            # Generate new events based on swap
            # Add new events to the heap
            intersections = self.sweepline_status.swap_and_report_intersection(event.line1, event.line2, sweepline)
            [self.q.push(intersection) for intersection in intersections]

        elif event.p_type == PointType.CIRCLE_START:
            # Insert two arcs into status
            # Check for intersections with their neighbours
            # if its a Circle -> Intersection of circle with circle
            # if its a line -> Intersection of circle with line
            intersections = self.sweepline_status.add_circle_report_intersection(event.circle1, sweepline)
            [self.q.push(intersection) for intersection in intersections]

        elif event.p_type == PointType.CIRCLE_END:
            # Remove both the arcs from SLS
            # Check for intersection
            intersections = self.sweepline_status.delete_circle_report_intersection(event.circle1)
            [self.q.push(intersection) for intersection in intersections]

        elif event.p_type == PointType.C_w_C_INTERSECTION:
            # Swap the upper half of lower circle with the lower half of upper circle
            # Check for intersections
            # Add new events to heap
            pass

        elif event.p_type == PointType.C_w_L_INTERSECTION:
            # Check if the event if for upper half or lower half
            # Swap the order of line and that half in the sweepline status.
            # Check for intersection
            # Add new events to heap
            pass

        else:
            raise Exception("Got an out of bound point in the sweepline status")

    def run(self):
        prev = None
        while self.q.size() > 0:
            valid, next_x, next_point = self.q.next_unique_pop(prev)
            if not valid:
                continue
            if next_point.p_type == PointType.INTERSECTION:
                self.intersections.append(next_point)
            self._process_event(next_point)
            prev = next_point

        return self.intersections


if __name__ == "__main__":
    psw_input = InputHandler.get_input()
    planesweep = PlaneSweep(psw_input)
    intersections = planesweep.run()
    print(len(intersections))

