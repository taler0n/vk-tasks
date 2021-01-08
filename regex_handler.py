import re


def get_regex_from_found_info(info):
    patterns = [re.compile(r"\b" + info + r"\b", re.IGNORECASE)]
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


def check_group(group_info, params):
    name = group_info["name"]
    status = ""
    desc = ""
    if group_info.get("status"):
        status = group_info["status"]
    if group_info.get("description"):
        desc = group_info["description"]

    for pattern in params["found_info"]:
        if (re.search(pattern, name) is not None
                or re.search(pattern, status) is not None
                or re.search(pattern, desc) is not None):
            return True

    keyword_count = 0
    blacklist_count = 0
    if (len(params["allowed_activities"]) == 0 or group_info.get("activity") is None
            or group_info["activity"] in params["allowed_activities"]):
        for keyword_pattern in params["keywords"]:
            if (re.search(keyword_pattern, name) is not None
                    or re.search(keyword_pattern, status) is not None
                    or re.search(keyword_pattern, desc) is not None):
                keyword_count += 1
        for blacklist_pattern in params["blacklist"]:
            if (re.search(blacklist_pattern, name) is not None
                    or re.search(blacklist_pattern, status) is not None
                    or re.search(blacklist_pattern, desc) is not None):
                blacklist_count += 1

    return keyword_count - blacklist_count > 0
