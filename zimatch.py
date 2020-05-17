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


def split_into_phrases(txt, wanted_phrase_len, ending_chars='\n\r', excludes=' 　，。[]\n\r'):
    '''yields phrases of wanted length as well as the line that contains it

    example:
        for phrase, line in split_into_phrases('關關雎鳩，在河之洲。\n窈窕淑女，君子好逑。\n', 5):
            print(phrase, '<', line)

        =>  關關雎鳩，在 < 關關雎鳩，在河之洲。
            關雎鳩，在河 < 關關雎鳩，在河之洲。
            雎鳩，在河之 < 關關雎鳩，在河之洲。
            鳩，在河之洲 < 關關雎鳩，在河之洲。
            窈窕淑女，君 < 窈窕淑女，君子好逑。
            窕淑女，君子 < 窈窕淑女，君子好逑。
            淑女，君子好 < 窈窕淑女，君子好逑。
            女，君子好逑 < 窈窕淑女，君子好逑。
    '''
    assert(set(ending_chars) < set(excludes))

    txt_len = len(txt)
    ending_char_set = set(ending_chars)
    excludes_set = set(excludes)
    last_ending_char_pos = -1

    for i in range(txt_len):
        if txt[i] in ending_char_set:
            last_ending_char_pos = i
            continue

        if txt[i] in excludes_set:
            continue

        j = i
        phrase_len = 0

        while j < txt_len and phrase_len < wanted_phrase_len:
            if txt[j] in ending_char_set:
                break
            if txt[j] not in excludes_set:
                phrase_len += 1
            j += 1

        if phrase_len == wanted_phrase_len:
            phrase = txt[i:j]
            while j < txt_len and txt[j] not in ending_char_set:
                j += 1
            line = txt[(last_ending_char_pos + 1):j]
            yield phrase, line


def find_chars_in_dict(phrase, d, excludes=' ，。[]\n\r'):
    '''returns a tuple of boolean and set

    * the boolean indicates if all chars in phrase are found in d
    * the set contains found chars, regardless all is found or not

    examples:

        find_chars_in_dict('右之右之，君子有之。', zi_dict)
        => (True, {'右', '之', '有', '子', '君'})

        print(find_chars_in_dict('維其有之，是以似之。', zi_dict))
        => (False, {'維', '以', '其', '有', '之', '是'})
    '''
    excludes_set = set(excludes)
    found = set()
    ok = True
    for ch in phrase:
        if ch in excludes_set:
            continue
        if ch in d:
            found.add(ch)
        else:
            ok = False
    return ok, found


def match_n(txt, n, d):
    '''finds n contiguous chars in txt where all chars can be found in d'''
    match_dict = {}
    for phrase, line in split_into_phrases(txt, n, ending_chars='\n\r', excludes=' ，。[]\n\r'):
        ok, found = find_chars_in_dict(phrase, d)
        if ok:
            match_dict[phrase] = match_dict.get(phrase, set()) | set([line])
    return match_dict


def print_matches(match_dict):
    '''print matches returned from match_n()'''
    for phrase, lines in match_dict.items():
        for line in lines:
            i = line.find(phrase)
            assert(i >= 0)  # must have found it
            end_of_phrase = i + len(phrase)
            print('\033[37m%s\033[0;32m%s\033[0;37m%s\033[0m' % (line[:i], line[i:end_of_phrase], line[end_of_phrase:]))


def is_debugging():
    return len(sys.argv) == 2 and sys.argv[1] == '--debug'


def print_dict(d):
    for k, v in d.items():
        print(k, ':', v)


def print_usage():
    bin_name = sys.argv[0]
    print('''usage:
        %s file_for_dict_building file_to_search N
''' % bin_name)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print_usage()
        exit(1)

    filename_for_dict_building = sys.argv[1]
    file_for_dict_building = Path(filename_for_dict_building)
    if not file_for_dict_building.is_file():
        print('%s is not a valid file' % filename_for_dict_building)
        print_usage()
        exit(2)

    filename_to_search = sys.argv[2]
    file_to_search = Path(filename_to_search)
    if not file_to_search.is_file():
        print('%s is not a valid file' % filename_to_search)
        print_usage()
        exit(2)

    text_for_dict_building = file_for_dict_building.read_text()
    text_to_search = file_to_search.read_text()

    n = int(sys.argv[3])

    zi_dict = build_dict(text_for_dict_building)

    if is_debugging():
        print_dict(zi_dict)

        print('-' * 80)

        for phrase, line in split_into_phrases('關關雎鳩，在河之洲。\n窈窕淑女，君子好逑。\n', 5):
            print(phrase, '<', line)

        print('-' * 80)

        print(find_chars_in_dict('維其有之，', zi_dict))
        print(find_chars_in_dict('是以似之。', zi_dict))

        exit(0)

    print_matches(match_n(text_to_search, n, zi_dict))
