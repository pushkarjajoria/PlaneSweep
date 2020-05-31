from InputHandler import PlaneSweepInput, Point, PointType
import InputHandler
import heapq
from sortedcontainers import SortedList


class SweepLineStatus:
    def __init__(self):
        pass


class SweepLineStatusList:
    def __init__(self):
        self.sweepline = 0
        self.tree = []

    def add_and_report_intersection(self, line, sweepline):
        self.sweepline = sweepline
        # Add a new line segment and report the s and s' which are adjacent to the new line
        self.tree.append(line)
        self.tree.sort(key=lambda x: x.value_at_x(sweepline)) # TODO: Check
        line_index = self.tree.index(line)
        if 0 < line_index < len(self.tree)-1:
            intersection1 = line.compute_intersection(self.tree[line_index+1])
            if intersection1.p_type == PointType.OUT_OF_RANGE:
                intersection1 = None
            intersection2 = line.compute_intersection(self.tree[line_index-1])
            if intersection2.p_type == PointType.OUT_OF_RANGE:
                intersection2 = None
            return intersection1, intersection2
        elif line_index == 0:
            try:
                intersection = line.compute_intersection(self.tree[line_index+1])
            except IndexError:
                return None, None
            return (intersection, None) if (intersection.x > sweepline and intersection.p_type == PointType.INTERSECTION)\
                else (None, None)
        else:
            try:
                intersection = line.compute_intersection(self.tree[line_index-1])
            except IndexError:
                intersection = None
            return (intersection, None) if (intersection.x > sweepline and intersection.p_type == PointType.INTERSECTION)\
                       else (None, None)

    def delete_and_report_intersection(self, line, sweepline):
        self.sweepline = sweepline
        if len(self.tree) == 0:
            return None
        line_index = self.tree.index(line)
        if 0 < line_index < len(self.tree)-1:
            intersection = self.tree[line_index - 1].compute_intersection(self.tree[line_index + 1])
            result = intersection if (intersection.x > sweepline and intersection.p_type == PointType.INTERSECTION) \
                else None
        else:
            result = None

        del self.tree[line_index]
        return result

    def swap_and_report_intersection(self, line1, line2, sweepline):
        self.sweepline = sweepline
        # Swap the order of l1 and l2 and report s adj to l1 and s' adj to l2
        index1 = self.tree.index(line1)
        index2 = self.tree.index(line2)
        if abs(index1-index2) != 1:
            raise Exception("Invalid line segments to swap. They are not adjacent in the tree.")
        self.tree[index1], self.tree[index2] = self.tree[index2], self.tree[index1]
        if index1 > index2:
            try:
                intersection1 = line2.compute_intersection(self.tree[index1+1])
                if intersection1 is not None:
                    intersection1 = None if (intersection1.p_type == PointType.OUT_OF_RANGE or intersection1.x < sweepline) \
                        else intersection1
            except IndexError:
                intersection1 = None
            try:
                intersection2 = line1.compute_intersection(self.tree[index2-1])
                if intersection2 is not None:
                    intersection2 = None if (intersection2.p_type == PointType.OUT_OF_RANGE or intersection2.x < sweepline) \
                        else intersection2

            except IndexError:
                intersection2 = None
        else:
            try:
                intersection1 = line2.compute_intersection(self.tree[index1-1])
                if intersection1 is not None:
                    intersection1 = None if (intersection1.p_type == PointType.OUT_OF_RANGE or intersection1.x < sweepline)\
                        else intersection1
            except IndexError:
                intersection1 = None
            try:
                intersection2 = line1.compute_intersection(self.tree[index2+1])
                if intersection2 is not None:
                    intersection2 = None if (intersection2.p_type == PointType.OUT_OF_RANGE or intersection2.x < sweepline)\
                        else intersection2
            except IndexError:
                intersection2 = None

        return intersection1, intersection2


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
        Pops a point from the PQ not equal to the prev
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
        self.sweepline_status = SweepLineStatusList()
        self.intersections = []

    def process_event(self, event):
        sweepline = event.x
        if event.p_type == PointType.STARTING:
            # Add line to SweepLineStatus
            # Compute intersections
            # Add intersections to EventsQueue if right of L
            intersection1, intersection2 = self.sweepline_status.add_and_report_intersection(event.line1, sweepline)

            # if intersection1 is not None and intersection1.p_type == PointType.INTERSECTION:
            #     self.intersections.append(intersection1)
            # if intersection2 is not None and intersection2.p_type == PointType.INTERSECTION:
            #     self.intersections.append(intersection2)

            self.q.push(intersection1)
            self.q.push(intersection2)

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
            intersection1, intersection2 = self.sweepline_status.swap_and_report_intersection(event.line1, event.line2, sweepline)

            self.q.push(intersection1)
            self.q.push(intersection2)
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
            self.process_event(next_point)
            prev = next_point

        return self.intersections


if __name__ == "__main__":
    psw_input = InputHandler.get_input()
    planesweep = PlaneSweep(psw_input)
    intersections = planesweep.run()
    print(len(intersections))

