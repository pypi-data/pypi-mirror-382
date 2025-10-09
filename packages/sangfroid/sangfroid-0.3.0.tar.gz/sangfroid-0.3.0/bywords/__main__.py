import argparse
import pysrt
import os
import sys
import logging
import sangfroid
from bywords.adjust import adjust

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger('bywords')

def main():
    parser = argparse.ArgumentParser(
            description='make words appear in time with subtitles')
    parser.add_argument(
            'sif', type=str,
            help='name of the .sif animation file')
    parser.add_argument(
            'srt', type=str, nargs='?',
            help='name of the .srt subtitles file')
    parser.add_argument(
            '--letter', '-l', action='store_true',
            help="letter at a time (rather than word at a time)")
    parser.add_argument(
            '--verbose', '-v', action='count', default=0,
            help="print what's being done")
    args = parser.parse_args()

    if args.srt is None:
        srt_filename = os.path.splitext(args.sif)[0]+'.srt'
    else:
        srt_filename = args.srt

    if args.verbose>1:
        logger.setLevel(logging.DEBUG)
    elif args.verbose==1:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARNING)

    srt = pysrt.open(srt_filename)
    animation = sangfroid.Animation(args.sif)
    logger.debug("Loaded animation and timings.")

    adjust(srt, animation,
           letter_at_a_time = args.letter,
           )

    logger.debug("Saving...")
    animation.save(args.sif)
    logger.info("Done.")

if __name__=='__main__':
    main()
