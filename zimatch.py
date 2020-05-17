#!/usr/bin/env python3


import sys
from pathlib import Path


def build_dict(txt, excludes=' ，。[]\n\r'):
    '''returns a dict of hanzi to the lines that contain it. example:
        {
            '工': {'宮車其寫，秀工寺射。', '吾車既工，吾馬既同。'},
            '求': {'大求又是', '麀鹿速速，君子之求。'},
            '楊': {'何以苞之，維楊及柳。'},
        }
    '''
    excludes_set = set(excludes)
    d = {}
    for line in txt.splitlines():
        for ch in line:
            if ch in excludes_set:
                continue
            d[ch] = d.get(ch, set())
            d[ch].add(line)
    return d


def find_contiguous(txt, d, excludes=' ，。[]\n\r'):
    '''find strings that contain chars in d or excludes and
    yield (matching_count, window)

    * matching_count is how many chars are matched using d
    * window is a list [i, j] that indicates the start and end of the matching string

    example:

        find_contiguous('知魚之樂。', zi_dict)
        => 3, [1, 4]
        meaning the window is '知魚之樂。'[1:4] which is '魚之樂' which contains 3 matching chars

        find_contiguous('知魚之樂。魚之樂。', zi_dict)
        => 6, [1, 8]
        meaning the window is '知魚之樂。魚之樂。'[1:8] which is '魚之樂。魚之樂' which contains 6 matching chars (and 1 excluded char)
    '''
    txt_len = len(txt)
    matching_count, window = 0, []
    for i in range(txt_len + 1):
        ch = txt[i] if i < txt_len else 'sentinel' # a sentinel will make sure the last window is always yielded
        if ch in d:
            matching_count += 1
            if not window:
                window = [i, i + 1]
            else:
                window[1] = i + 1
        elif ch in excludes:
            continue
        else:
            if window:
                yield matching_count, window
                matching_count, window = 0, []


def match_n_or_more(txt, n, d, nonmatch_color='\033[0;37m', match_color='\033[0;32m'):
    '''returns a colored string if at least n contiguous chars can be found in d'''
    k = 0 # start position of non-matching string
    output = ''
    for matching_count, window in find_contiguous(txt, d):
        if matching_count < n:
            continue
        i, j = window
        output += '%s%s%s%s\033[0m' % (nonmatch_color, txt[k:i], match_color, txt[i:j])
        k = j # j is the end of the matching string, thus the start of non-matching string
    if output:
        output += '%s%s\033[0m' % (nonmatch_color, txt[k:])
    return output


def print_usage():
    bin_name = sys.argv[0]
    print('''usage:
        %s file_for_dict_building file_to_search N
''' % bin_name)


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print_usage()
        exit(1)

    filename_for_dict_building = sys.argv[1]
    file_for_dict_building = Path(filename_for_dict_building)
    if not file_for_dict_building.is_file():
        print('%s is not a valid file' % filename_for_dict_building)
        print_usage()
        exit(2)

    text_for_dict_building = file_for_dict_building.read_text()

    zi_dict = build_dict(text_for_dict_building)

    if '--debug' in sys.argv:
        for k, v in zi_dict.items():
            print(k, ':', v)

        for k, window in find_contiguous('知魚之樂。', zi_dict):
            assert(k == 3 and window == [1, 4])

        for k, window in find_contiguous('知魚之樂。魚之樂。', zi_dict):
            assert(k == 6 and window == [1, 8])

        print('-' * 80)

        print(match_n_or_more('維其有之，', 3, zi_dict))
        print(match_n_or_more('是以似之。', 1, zi_dict))
        print(match_n_or_more('知魚之樂。', 2, zi_dict))

        exit(0)

    filename_to_search = sys.argv[2]
    file_to_search = Path(filename_to_search)
    if not file_to_search.is_file():
        print('%s is not a valid file' % filename_to_search)
        print_usage()
        exit(2)

    text_to_search = file_to_search.read_text()

    n = int(sys.argv[3])

    for line in text_to_search.splitlines():
        m = match_n_or_more(line, n, zi_dict)
        if not m:
            continue # skip the line if no match at all
        print(m)
