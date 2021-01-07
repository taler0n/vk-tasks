import json

import vk_api
import common
import regex_handler


def main():
    user_ids = common.get_list("users.txt", True)
    session = common.get_session("credentials.txt")
    api = session.get_api()
    tools = vk_api.VkTools(session)
    output = {}
    edu_params = get_edu_params()
    career_params = get_career_params()

    for user_id in user_ids:
        print("user_id: %s" % user_id)
        career = get_career(api, user_id)
        schools = get_schools(api, user_id)
        universities = get_universities(api, user_id)

        print("\tworks")
        common.print_dict_tabulated(career, "work_name")
        print("\teducation")
        common.print_dict_tabulated(schools, "education_name")
        common.print_dict_tabulated(universities, "education_name")

        get_found_career_info(career_params, career)
        get_found_edu_info(edu_params, schools, universities)
        groups = tools.get_all_iter("groups.get", 1000, {"user_id": user_id})
        indexed_groups = index_groups(api, groups, career_params, edu_params)
        print("\tgroups")
        common.print_dict_tabulated(indexed_groups, "group_id")

        user_info = {
            "works": career,
            "education": schools.update(universities),
            "groups": indexed_groups
        }
        output[user_id] = user_info

        clear_params(edu_params, career_params)

    with open("output.txt", "w", encoding='utf-8') as file:
        json.dump(output, file, default=str, ensure_ascii=False)


def get_edu_params():
    return {
        "found_info": [],
        "keywords": regex_handler.get_regex_from_file("keywords_edu.txt"),
        "blacklist": regex_handler.get_regex_from_file("blacklist_edu.txt"),
        "allowed_activities": common.get_list("allowed_activities_edu.txt", False)}


def get_career_params():
    return {
        "found_info": [],
        "found_groups": [],
        "keywords": regex_handler.get_regex_from_file("keywords_career.txt"),
        "blacklist": [],
        "allowed_activities": []}


def get_schools(api, user_id):
    schools_name = {}
    user_info = api.users.get(user_ids=user_id, fields="schools")
    if user_info[0].get("schools") is None:
        return schools_name

    for school in user_info[0]["schools"]:
        school_id = school["id"]
        schools_name[school_id] = dict.fromkeys(["info", "dt_start", "dt_end", "type"])
        school_info = {}
        if school.get("country") is not None:
            school_info["country"] = school["country"]
        if school.get("city") is not None:
            school_info["city"] = school["city"]
        if school.get("name") is not None:
            school_info["name"] = school["name"]

        schools_name[school_id]["info"] = school_info
        if school.get("year_from") is not None:
            schools_name[school_id]["dt_start"] = school["year_from"]
        if school.get("year_to") is not None:
            schools_name[school_id]["dt_end"] = school["year_to"]
        elif school.get("year_graduated") is not None:
            schools_name[school_id]["dt_end"] = school["year_graduated"]
        if school.get("type_str") is not None:
            schools_name[school_id]["type"] = school["type_str"]
        else:
            schools_name[school_id]["type"] = "SCHOOL"

    return schools_name


def get_universities(api, user_id):
    universities_name = {}
    user_info = api.users.get(user_ids=user_id, fields="universities")
    if user_info[0].get("universities") is None:
        return universities_name

    for university in user_info[0]["universities"]:
        university_id = university["id"]
        universities_name[university_id] = dict.fromkeys(["info", "dt_start", "dt_end", "type"])
        university_info = {}
        if university.get("country") is not None:
            university_info["country"] = university["country"]
        if university.get("city") is not None:
            university_info["city"] = university["city"]
        if university.get("name") is not None:
            university_info["name"] = university["name"]
        if university.get("faculty") is not None:
            university_info["faculty"] = university["faculty"]
        if university.get("faculty_name") is not None:
            university_info["faculty_name"] = university["faculty_name"]
        if university.get("chair") is not None:
            university_info["chair"] = university["chair"]
        if university.get("chair_name") is not None:
            university_info["chair_name"] = university["chair_name"]
        if university.get("education_form") is not None:
            university_info["education_form"] = university["education_form"]
        if university.get("education_status") is not None:
            university_info["education_status"] = university["education_status"]

        universities_name[university_id]["info"] = university_info
        if university.get("graduation") is not None:
            universities_name[university_id]["dt_end"] = university["graduation"]
        universities_name[university_id]["type"] = "UNIVERSITY"

    return universities_name


def get_career(api, user_id):
    career_name = {}
    user_info = api.users.get(user_ids=user_id, fields="career")
    if user_info[0].get("career") is None:
        return career_name

    for career in user_info[0]["career"]:
        if career.get("group_id") is not None:
            career_id = career["group_id"]
        else:
            career_id = career["company"]
        career_name[career_id] = dict.fromkeys(["info", "dt_start", "dt_end"])
        career_info = {}
        if career.get("company") is not None:
            career_info["company"] = career["company"]
        if career.get("country_id") is not None:
            career_info["country_id"] = career["country_id"]
        if career.get("city_id") is not None:
            career_info["city_id"] = career["city_id"]
        if career.get("position") is not None:
            career_info["position"] = career["position"]

        career_name[career_id]["info"] = career_info
        if career.get("from") is not None:
            career_name[career_id]["dt_start"] = career["from"]
        if career.get("until") is not None:
            career_name[career_id]["dt_end"] = career["until"]

    return career_name


def get_found_edu_info(edu_params, schools, universities):
    for key in schools.keys():
        edu_params["found_info"] += regex_handler.get_regex_from_found_info(schools[key]["info"]["name"], True)
    for key in universities.keys():
        edu_params["found_info"] += regex_handler.get_regex_from_found_info(universities[key]["info"]["name"], True)


def get_found_career_info(career_params, career):
    for key in career.keys():
        if career[key]["info"].get("company") is None:
            career_params["found_groups"].append(key)
        else:
            career_params["found_info"] += \
                regex_handler.get_regex_from_found_info(career[key]["info"]["company"], False)
    if len(career_params["found_groups"]) > 0 or len(career_params["found_info"]) > 0:
        career_params["keywords"] = []


def index_groups(api, groups, career_params, edu_params):
    indexed_groups = {}
    for group_id in groups:
        group_info = api.groups.getById(group_id=group_id, fields=["status", "description"])[0]
        if group_info["type"] != "event":
            tags = []
            if regex_handler.check_group(group_info, edu_params):
                indexed_groups[group_id] = {"name": group_info["name"], "tags": tags}
                tags.append("EDUCATION")
            if group_id in career_params["found_groups"] or regex_handler.check_group(group_info, career_params):
                indexed_groups[group_id] = {"name": group_info["name"], "tags": tags}
                tags.append("WORK")

    return indexed_groups


def clear_params(edu_params, career_params):
    edu_params["found_info"] = []
    career_params["found_info"] = []
    career_params["found_groups"] = []
    career_params["keywords"] = regex_handler.get_regex_from_file("keywords_career.txt")


main()
