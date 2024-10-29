#!/usr/bin/env python3

import sys
from os.path import join, isfile

def main(base_path):
    """
    Converts vertex, normal, and triangle data into an OBJ file format.

    Parameters:
        base_path (str): The base directory containing vertices.txt, normals.txt, and triangles.txt.

    Outputs:
        surface.obj file in the specified directory.
    """
    vertices_file = join(base_path, "vertices.txt")
    normals_file = join(base_path, "normals.txt")
    triangles_file = join(base_path, "triangles.txt")
    output_file = join(base_path, "surface.obj")

    # Check if normals file exists
    normals_exist = isfile(normals_file)

    # Reading vertices and triangles
    with open(vertices_file, "r") as vf, open(triangles_file, "r") as tf:
        vertices = [line.strip().split() for line in vf]
        triangles = [line.strip().split() for line in tf]

    # Read normals only if they exist
    if normals_exist:
        with open(normals_file, "r") as nf:
            normals = [line.strip().split() for line in nf]

    # Writing to OBJ format
    with open(output_file, "w") as of:
        # Write vertices
        for v in vertices:
            of.write(f"v {' '.join(v)}\n")

        # Write normals if available
        if normals_exist:
            for n in normals:
                of.write(f"vn {' '.join(n)}\n")

        # Write faces with or without normals
        for t in triangles:
            indices = [str(int(idx) + 1) for idx in t]
            if normals_exist:
                of.write(
                    f"f {indices[0]}//{indices[0]} {indices[1]}//{indices[1]} {indices[2]}//{indices[2]}\n"
                )
            else:
                of.write(f"f {indices[0]} {indices[1]} {indices[2]}\n")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python text2obj.py <base_path>")
    else:
        main(sys.argv[1])