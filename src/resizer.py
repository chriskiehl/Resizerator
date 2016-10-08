'''
Simple, dumb, and quick destructive image resizing
'''

import glob
import os
import sys
import time
from functools import partial
from itertools import imap, islice

from PIL import Image
from gooey import Gooey, GooeyParser

# PyInstaller multiprocessing recipe patch
# https://github.com/pyinstaller/pyinstaller/wiki/Recipe-Multiprocessing
try:
    if sys.platform.startswith('win'):
        import multiprocessing.popen_spawn_win32 as forking
    else:
        import multiprocessing.popen_fork as forking
except ImportError:
    import multiprocessing.forking as forking

if sys.platform.startswith('win'):
    # First define a modified version of Popen.
    class _Popen(forking.Popen):
        def __init__(self, *args, **kw):
            if hasattr(sys, 'frozen'):
                # We have to set original _MEIPASS2 value from sys._MEIPASS
                # to get --onefile mode working.
                os.putenv('_MEIPASS2', sys._MEIPASS)
            try:
                super(_Popen, self).__init__(*args, **kw)
            finally:
                if hasattr(sys, 'frozen'):
                    # On some platforms (e.g. AIX) 'os.unsetenv()' is not
                    # available. In those cases we cannot delete the variable
                    # but only set it to the empty string. The bootloader
                    # can handle this case.
                    if hasattr(os, 'unsetenv'):
                        os.unsetenv('_MEIPASS2')
                    else:
                        os.putenv('_MEIPASS2', '')
    # Second override 'Popen' class with our modified version.
    forking.Popen = _Popen
# end patch

import multiprocessing



@Gooey
def main():
    parser = GooeyParser(
        description='Resizes odd dimensions to a known "good" aspect ratio')

    parser.add_argument(
        'directory',
        help='Directory with the images to resize',
        widget='DirChooser')

    parser.add_argument(
        'pattern',
        help='File pattern to match',
        default='*.jpeg')

    parser.add_argument(
        '--width',
        help='Resize images to this width',
        default=864,
        type=int)

    parser.add_argument(
        '--height',
        help='Resize images to this height',
        default=540,
        type=int)

    parser.add_argument(
        '-c', '--cores',
        help='number of cores to use (default is all available)',
        default=str(multiprocessing.cpu_count()),
        choices=map(str, range(1, multiprocessing.cpu_count() + 1)))

    args = parser.parse_args()

    if not os.path.exists(args.directory):
        print 'Unable to locate supplied directory :('
        sys.exit()

    abs_path = partial(os.path.join, args.directory)
    picklable_payload = lambda path: (path, args.width, args.height)

    absolute_paths = imap(abs_path, glob.glob1(args.directory, args.pattern))
    payload = imap(picklable_payload, absolute_paths)

    start = time.time()
    pool = multiprocessing.Pool(int(args.cores))
    pool.imap_unordered(resize_and_save, payload)
    pool.close()
    pool.join()

    print('time taken: ', time.time() - start)


def resize_and_save(arg_tuple):
    path, width, height = arg_tuple
    print 'converting: {}'.format(os.path.split(path)[-1])
    im = Image.open(path)
    im2 = im.resize((width, height))
    im2.save(path)

if __name__ == '__main__':
    multiprocessing.freeze_support()
    nonbuffered_stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    sys.stdout = nonbuffered_stdout
    main()
