import re


def get_regex_from_found_info(info, is_education):
    patterns = [re.compile(r"\b" + info + r"\b", re.IGNORECASE)]
    if is_education:
        naming_position = info.find(" им. ")
        if naming_position > 0:
            shortened = info[0:naming_position]
            patterns.append(re.compile(r"\b" + shortened + r"\b", re.IGNORECASE))
        left_brace_position = info.find("(")
        right_brace_position = info.find(")")
        if left_brace_position > -1 and right_brace_position - left_brace_position > 0:
            shortened = info[0:left_brace_position - 1]
            patterns.append(re.compile(r"\b" + shortened + r"\b", re.IGNORECASE))
            braced = info[left_brace_position + 1:right_brace_position]
            former_position = braced.find("бывш. ")
            if former_position > -1:
                patterns.append(re.compile(r"\b" + braced[former_position + 6:] + r"\b", re.IGNORECASE))
            else:
                patterns.append(re.compile(r"\b" + braced + r"\b", re.IGNORECASE))
    return patterns


def get_regex_from_file(filename):
    patterns = []
    with open(filename, encoding='utf-8') as file:
        for line in file:
            patterns.append(re.compile(r"" + line.rstrip(), re.IGNORECASE))
    return patterns


def check_group(group_info, found_info, keywords, blacklist=None, allowed_activities=None):
    name = group_info["name"]
    status = group_info["status"]
    desc = group_info["description"]

    for pattern in found_info:
        if (re.search(pattern, name) is not None
                or re.search(pattern, status) is not None
                or re.search(pattern, desc) is not None):
            return True

    if allowed_activities is None or group_info["activity"] in allowed_activities:
        for keyword_pattern in keywords:
            if (re.search(keyword_pattern, name) is not None
                    or re.search(keyword_pattern, status) is not None
                    or re.search(keyword_pattern, desc) is not None):
                if blacklist is None:
                    return True
                else:
                    for blacklist_pattern in blacklist:
                        if (re.search(blacklist_pattern, name) is not None
                                or re.search(blacklist_pattern, status) is not None
                                or re.search(blacklist_pattern, desc) is not None):
                            return False
                    return True

    return False

