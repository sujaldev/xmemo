import math


def match(keywords, text):
    if keywords.lower() == text.lower():
        return True
    return False


def are_similar(str1, str2):
    if match(str1, str2):
        return True
    if str1.lower() in str2.lower():
        return True

    str1_list = str1.lower().split(" ")
    str2_list = str2.lower().split(" ")
    match_count = 0
    max_len_diff = 10
    min_match_diff = 70
    if abs(len(str1_list) - len(str2_list)) <= math.ceil(max_len_diff * len(str2_list) / 100):
        for word in str1_list:
            if word in str2_list:
                match_count += 1
        if math.ceil(match_count * 100 / len(str2_list)) >= min_match_diff:
            return True
    return False
