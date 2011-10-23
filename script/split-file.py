import sys

NUM_LINES_IN_NEW_FILES = 20

def main(filename):
    lines = open(filename, 'r').readlines()
    filenum = 0
    curfile = open('%s.%d' % (filename, filenum), 'w')
    for i,line in enumerate(lines):
        if i > 0 and i % NUM_LINES_IN_NEW_FILES == 0:
            curfile.close()
            filenum += 1
            curfile = open('%s.%d' % (filename, filenum), 'w')
        curfile.write(line)
        i += 1
    curfile.close()

if __name__ == '__main__':
    main(sys.argv[1])
