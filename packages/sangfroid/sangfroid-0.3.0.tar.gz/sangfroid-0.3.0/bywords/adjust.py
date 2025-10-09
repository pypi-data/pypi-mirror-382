import sangfroid
from bywords.bywords import Bywords
import logging

logger = logging.getLogger('bywords')

def set_constant_waypoint(tl, time, value):
    s = sangfroid.value.String(value)
    t = sangfroid.T(
            f"{time}s",
            ref = tl.parent.tag,
            )
    waypoint = sangfroid.value.Waypoint(
            time = t,
            value = s,
            before = 'constant',
            after = 'constant',
            )
    tl += waypoint

def adjust(subtitles, animation,
           letter_at_a_time = False,
           ):
    bw = Bywords(
            sif=animation,
            srt=subtitles,
            letter_at_a_time = letter_at_a_time,
            )

    if logger.level<logging.WARNING:
        bw.dump_findings_to_logger()

    for obj in set([o.item for o in bw]):
        obj.is_animated = True
        timeline = obj['text'].timeline

        set_constant_waypoint(timeline, 0, '')

        for word in bw:
            if word.item!=obj:
                continue

            seconds = f"{word.time/1000}s"

            set_constant_waypoint(timeline,
                                  word.time,
                                  word.text,
                                  )
