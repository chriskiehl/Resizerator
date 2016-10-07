import os
import glob
from functools import partial
from itertools import imap, islice
# from multiprocessing import cpu_count, Pool

import time

import sys
from PIL import Image
from gooey import Gooey, GooeyParser


@Gooey
def main():
    parser = GooeyParser(
        description='Resizes odd dimensions to a known "good" aspect ratio'
    )
    parser.add_argument(
        'directory',
        help='Directory with the images to resize',
        widget='DirChooser'
    )

    parser.add_argument(
        'pattern',
        help='File pattern to match',
        default='*.jpeg',
    )

    parser.add_argument(
        '--width',
        help='Resize images to this width',
        default=864,
        type=int
    )

    parser.add_argument(
        '--height',
        help='Resize images to this height',
        default=540,
        type=int
    )

    parser.add_argument(
        '-c', '--cores',
        help='number of cores to use (default is all available)',
        default=str(cpu_count()),
        choices=map(str, range(1, cpu_count() + 1)),
    )

    args = parser.parse_args()

    if not os.path.exists(args.directory):
        print 'Unable to locate supplied directory'
        sys.exit()

    abs_path = partial(os.path.join, args.directory)
    picklable_payload = lambda path: (path, args.width, args.height)

    absolute_paths = imap(abs_path, glob.glob1(args.directory, args.pattern))
    payload = imap(picklable_payload, absolute_paths)

    start = time.time()
    # pool = Pool(int(args.cores))
    # pool.imap_unordered(resize_and_save, payload, 1)
    map(resize_and_save, payload)
    # pool.close()
    # pool.join()
    print ('time taken: ', time.time() - start)


def resize_and_save(arg_tuple):
    path, width, height = arg_tuple
    print 'converting: {}'.format(os.path.split(path)[-1])
    im = Image.open(path)
    im2 = im.resize((width, height))
    im2.save(path)

if __name__ == '__main__':
    nonbuffered_stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    sys.stdout = nonbuffered_stdout
    main()
