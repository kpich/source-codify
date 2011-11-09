
import sys

def split_file(filename):
    lines = open(filename, 'r').readlines()
    A,B,C = split_into_thirds(lines)
    write_file(filename + '.split1', A + B)
    write_file(filename + '.split2', B + C)
    write_file(filename + '.split3', A + C)

def split_into_thirds(lines):
    N = len(lines) / 3
    return lines[:N], lines[N:2*N], lines[2*N:]

def write_file(filename, lines):
    f = open(filename, 'w')
    for line in lines:
        f.write(line)
    f.close()

if __name__ == '__main__':
    split_file(sys.argv[1])
