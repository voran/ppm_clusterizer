#!/usr/bin/python2
import random
import sys
import math

class KMeansUtils:
    @staticmethod
    def get_distance(point1, point2):
        xd = point2.x - point1.x
        yd = point2.y - point1.y
        zd = point2.z - point1.z
        return xd*xd + yd*yd + zd*zd


class Point:
    x = None
    y = None
    z = None

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class Cluster:
    location = None
    points = None
    point_set = None

    def __init__(self, location):
        self.location = location
        self.points = []
        self.point_set = set()

    def get_point_set(self):
        if len(self.point_set) == 0:
            self.point_set = set(self.points)
        return self.point_set

    def update_location(self):
        sum_x = 0
        sum_y = 0
        sum_z = 0

        for point in self.points:
            sum_x += point.x
            sum_y += point.y
            sum_z += point.z

        old_location = self.location
        self.location = Point(sum_x / len(self.points), sum_y / len(self.points), sum_z / len(self.points))
        return KMeansUtils.get_distance(old_location, self.location)



class KMeans:
    points = None
    clusters = None
    cluster_count = None
    min_displacement = None

    def __init__(self, rgb_array, cluster_count, max_displacement):
        self.cluster_count = cluster_count
        self.max_displacement = max_displacement
        self.clusters = []
        self.points = []

        for line in rgb_array:
            (x, y, z) = line
            self.points.append(Point(int(x), int(y), int(z)))


    def find_closest_cluster(self, point):
        min_distance = sys.maxint
        min_distance_cluster = None
        for cluster in self.clusters:
            distance = KMeansUtils.get_distance(cluster.location, point)

            if min_distance > distance:
                min_distance = distance
                min_distance_cluster = cluster

        min_distance_cluster.points.append(point)
        return min_distance

    def run(self):
        init_points = random.sample(self.points, self.cluster_count)

        self.clusters = []
        for point in init_points:
            self.clusters.append(Cluster(point))

        iteration = 1
        displacement = sys.maxint
        while displacement > self.max_displacement:
            for cluster in self.clusters:
                cluster = Cluster(cluster.location)

            for point in self.points:
                self.find_closest_cluster(point)

            displacement = 0
            for cluster in self.clusters:
                displacement += cluster.update_location()

            sys.stderr.write("Iteration %s: displacement: %s, max_displacement: %s\n" % (iteration, displacement, self.max_displacement))
            iteration += 1

        sys.stderr.write("kmeans terminated after %s iterations\n\n" % (iteration - 1))


if __name__ == "__main__":

    if len(sys.argv) < 3:
        sys.stderr.write("Example invocation: cat input.ppm | python2 %s <num_clusters> <min_displacement> > output.ppm\n" % sys.argv[0])
        sys.exit(1)

    sys.stderr.write("Loading input from stdin...\n")
    rgb_array = []
    line_num = 0
    for line in sys.stdin:
        if line_num == 0:
            file_type = line.rstrip('\n')
        if line_num == 2:
            (max_x, max_y) = line.rstrip('\n').split(" ")
        elif line_num == 3:
            max_value = line.rstrip('\n')
        elif line_num > 3:
            rgb_line = []
            value_num = 0

            for value in line.rstrip('\n').split(" "):
                if value_num > 0 and value_num % 3 == 0:
                    rgb_array.append(list(rgb_line))
                    rgb_line = []
                rgb_line.append(value)
                value_num += 1

        line_num += 1

    cluster_count = int(sys.argv[1])
    kmeans = KMeans(rgb_array, cluster_count, int(sys.argv[2]))
    sys.stderr.write("Points: %s\n" % len(rgb_array))
    sys.stderr.write("Clusters: %s\n\n" % cluster_count)

    sys.stderr.write("Running kmeans...\n")
    kmeans.run()

    sys.stderr.write("Writing output to stdout...\n")
    print file_type
    print "#Generated using %s" % sys.argv[0]
    print "%s %s" % (max_x, max_y)
    print max_value


    for point in kmeans.points:
        for cluster in kmeans.clusters:
            if point in cluster.get_point_set():
                print "%s %s %s" % (cluster.location.x, cluster.location.y, cluster.location.z)
                break
