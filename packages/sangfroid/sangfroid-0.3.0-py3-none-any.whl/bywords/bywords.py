from bs4 import BeautifulSoup
import sangfroid
import os
import glob
import re
import collections
import math
import re
import logging
import functools

logger = logging.getLogger('bywords')
LOGGING_FORMAT = '%(time)10s %(layer)10s %(str)s'

WHITESPACE = re.compile('([ \t\n]+)')
NOTHING = re.compile('()')

NON_WORD_LETTERS = re.compile('[^a-z0-9 ]') # FIXME not very i18n-friendly

PREFIX = 'bywords-'

bywords_groups = None

@functools.total_ordering
class WordTiming:
    def __init__(self, text, item):
        self.text = text
        self.item = item
        self.time = 0

    def __lt__(self, other):
        return self.time<other.time

    def __eq__(self, other):
        return self.time==other.time

    def __str__(self):
        return LOGGING_FORMAT % {
            'time': '%0.02g' % (self.time,),
            'layer': self.item,
            'str': self.text,
            }

    __repr__ = __str__

class BywordsGroup:
    def __init__(self, group):
        self.group = group

        self.texts = [
                (self.tidy_string(item.desc), item,)
                for item in
                list(reversed(group.find_all('text')))
                ]

        self.full_text = ' '.join(
                [s[0] for s in self.texts])

    @classmethod
    def tidy_string(self, n):
        return NON_WORD_LETTERS.sub('', n.lower())

    def matches(self, s, duration, start=0,
                letter_at_a_time = False,
                ):

        word_timings = []

        if letter_at_a_time:
            splitting_re = NOTHING
        else:
            splitting_re = WHITESPACE

        if s!=self.full_text:
            return None

        for _, item in self.texts:
            item['text'].is_animated = False

            words = [w for w in splitting_re.split(item.desc)
                     if w!=''
                     ]

            i = 0
            while words:
                word = words.pop(0)

                i += len(word)

                word_timings.append(
                        WordTiming(
                            text = item.desc[:i],
                            item = item,
                            ))

                if words and words[0].strip()=='':
                    i += len(words.pop(0))

            s = s[len(item.desc):]

        total_letters = sum([len(w.text) for w in word_timings])
        ms_per_letter = duration/total_letters

        time = start
        for w in word_timings:
            w.time = time/1000
            time += len(w.text)*ms_per_letter

        return word_timings

    def __str__(self):
        return self.group.desc

    __repr__ = __str__

    def __lt__(self, other):
        return str(self) < str(other)

    def __eq__(self, other):
        return str(self) < str(other)

class Bywords:
    def __init__(self, srt, sif,
                 letter_at_a_time = False,
                 ):
        self.srt = srt
        self.sif = sif

        self.no_matches = []

        self.lines = [
                (
                    line.start.ordinal,
                    line.duration.ordinal,
                    BywordsGroup.tidy_string(line.text),
                    )
                for line in srt
                ]

        self.groups = sorted([
            BywordsGroup(group)
            for group in self.sif.find_all(sangfroid.layer.Group)
            if group.desc is not None
            and group.desc.lower().startswith('bywords')
            ])

        result = {}
        found = None

        for start, duration, text in self.lines:
            for group in self.groups:
                found = group.matches(text,
                                      duration,
                                      start,
                                      letter_at_a_time,
                                 )
                if found:
                    break
            if found:
                for word in found:
                    result[word.time] = word
            else:
                self.no_matches.append(text)

        self.words = sorted(list(result.values()))

    def dump_findings_to_logger(self):
        logger.info("\n\n=== Source timings ===\n")

        logger.info("---  %12s %s", "Time (s)", "Normalised text")
        for start, duration, text in self.lines:
            logger.info("    %12s %s", start/1000, text)

        logger.info("\n\n=== Source layers ===\n")

        logger.info("---  Normalised text")
        for group in self.groups:
            logger.info("   %s", group.full_text)

        logger.info("\n\n=== Matches ===\n")

        logger.info(LOGGING_FORMAT % {
            'time': 'At time (s)',
            'layer': 'on layer',
            'str': 'set string',
            })
        if self.words:
            for word_timing in self.words:
                logger.info("    %s", word_timing)

        else:
            logger.info("There were no matches.")

        logger.info("\n\n=== Unmatched ===\n")

        if self.no_matches:
            for line in self.no_matches:
                logger.info("    %s", line)
        else:
            logger.info("Everything was matched.")

    def __iter__(self):
        return iter(self.words)
