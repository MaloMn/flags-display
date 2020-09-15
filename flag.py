from PIL import Image, ImageDraw
import os
import math
import numpy as np
import random


def check_height(flags_list):
    h = flags_list[0].size[1]
    for f in flags_list[1:]:
        if h != f.size[1]:
            raise ImportError("Images of flags must all be the same height.")


def place_flag(center, size):
    """
    Returns four coordinates of the corners of the flag centered on center.
    They are in clockwise order starting by the top right-hand corner.
    :param center: center of the flag
    :param size: (width, height)
    :return:
    """
    return [(center[0] + size[0]/2, center[1] + size[1]/2), (center[0] + size[0]/2, center[1] - size[1]/2),
            (center[0] - size[0]/2, center[1] - size[1]/2), (center[0] - size[0]/2, center[1] + size[1]/2)]


def is_point_in_circle(r, p):
    """
    Tells if a point p is contained in the circle centered in (0, 0) of radius r
    :param r: radius
    :param p: point
    :return: boolean
    """
    return r >= math.hypot(*p)


def generate_possible_positions(points, flagsize, debug=False):
    # Finding the envelope
    # points = envelope(points)
    # Finding the top and bottom points
    south = max([max([b[1] for b in c]) for c in points])
    north = min([min([b[1] for b in c]) for c in points])
    extremes = [(0, north - flagsize[1]/2), (0, south + flagsize[1]/2)]

    # Finding the other points
    # Finding vertical segments of each flag
    segments = []
    for p in points:
        segments.append([p[0], p[1]])
        segments.append([p[3], p[2]])

    # Finding their middle vertical point
    middle_points = []
    segments = [(a[0][0], (a[0][1] + a[1][1])/2) for a in segments]
    y_positions = sorted(list(set([a[1] for a in segments])), reverse=True)

    for y in y_positions:
        # Find point sharing that origin
        p = list(filter(lambda a: a[1] == y, segments))
        p.sort(key=lambda a: a[0])
        middle_points.append(p[0])
        middle_points.append(p[-1])

    # Displace middles according to flag width
    for j in range(len(middle_points)):
        sign = np.sign(middle_points[j][0])
        middle_points[j] = (middle_points[j][0] + sign*flagsize[0]/2, middle_points[j][1])

    # out = extremes + middle_points
    random.shuffle(middle_points)
    random.shuffle(extremes)
    return middle_points + extremes


def upper_left_corner(coord):
    x = min([a[0] for a in coord])
    y = min([a[1] for a in coord])
    return x, y


def make_flag_display(flags, filename, im_format, debug=False):
    flags = flags.copy()
    # Initiate output array
    output = []
    # Shuffle the flags
    random.shuffle(flags)
    # Making sure that they have all the same height
    check_height(flags)

    first_flag = flags[0]
    flags.pop(0)

    radius = math.hypot(first_flag.size[0]/2, first_flag.size[1]/2)
    coordinates = [place_flag((0, 0), first_flag.size)]
    output.append([first_flag, upper_left_corner(coordinates[0])])

    # Main loop
    while len(flags) > 0:
        i = 0
        while i < len(flags):
            for p in generate_possible_positions(coordinates, flags[i].size):
                potential_coord = place_flag(p, flags[i].size)
                is_possible = [is_point_in_circle(radius, pc) for pc in potential_coord]
                if False not in is_possible:
                    coordinates.append(potential_coord)

                    # print('COORDINATES AFTER ADDING THE FLAG: ', coordinates)
                    output.append([flags[i], upper_left_corner(potential_coord)])
                    flags.pop(i)
                    i = 0

                    if debug:
                        img = Image.new('RGB', (int(radius)*2, int(radius)*2), color=0)
                        for flag, position in output:
                            img.paste(flag, (int(position[0]) + int(radius), int(position[1]) + int(radius)))

                        draw = ImageDraw.Draw(img)
                        pts_out = generate_possible_positions(coordinates, flags[i].size)
                        pts_out = [(a[0] + int(radius), a[1] + int(radius)) for a in pts_out]
                        for pts in pts_out:
                            draw.ellipse((pts[0] - 10, pts[1] - 10, pts[0] + 10, pts[1] + 10), fill=(255, 0, 0), outline=(0, 0, 0))

                        img.save("output_{}.png".format(len(output)), "PNG")
                    break
            i += 1
        radius += 50
        if debug:
            print(radius)

    # Displaying the flags
    radius = int(radius)
    img = Image.new('RGB', (radius*2, radius*2), color=0)
    for flag, position in output:
        img.paste(flag, (int(position[0]) + radius, int(position[1]) + radius))

    img.save(filename, im_format)


if __name__ == "__main__":
    # Gathering the flag images
    folder = "flags/"
    paths = os.listdir(folder)
    flag_list = [Image.open(folder + p) for p in paths]
    for z in range(10):
        make_flag_display(flag_list, "output_" + str(z) + ".png", "PNG")
        print(z)
