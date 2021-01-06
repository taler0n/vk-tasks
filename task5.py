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

    for user_id in user_ids:
        print("user_id: %s" % user_id)
        career = get_career(api, user_id)
        schools = get_schools(api, user_id)
        universities = get_universities(api, user_id)
        print("\tworks")
        for key in career.keys():
            print("\t\twork_name: %s" % key)
            for item in career[key].items():
                print("\t\t\t%s:" % item[0], "%s" % item[1])
        print("\teducation")
        for key in schools.keys():
            print("\t\teducation_name: %s" % key)
            for item in schools[key].items():
                print("\t\t\t%s:" % item[0], "%s" % item[1])
        for key in universities.keys():
            print("\t\teducation_name: %s" % key)
            for item in universities[key].items():
                print("\t\t\t%s:" % item[0], "%s" % item[1])

        indexed_groups = {}
        groups = tools.get_all_iter("groups.get", 1000, {"user_id": user_id})

        found_info_career = []
        found_groups_career = []
        for key in career.keys():
            if career[key]["info"].get("company") is None:
                found_groups_career.append(key)
            else:
                found_info_career += regex_handler.get_regex_from_found_info(career[key]["info"]["company"], False)
        found_info_edu = []
        for key in schools.keys():
            found_info_edu += regex_handler.get_regex_from_found_info(schools[key]["info"]["name"], True)
        for key in universities.keys():
            found_info_edu += regex_handler.get_regex_from_found_info(universities[key]["info"]["name"], True)

        keywords_career = regex_handler.get_regex_from_file("keywords_career.txt")
        allowed_activities_edu = common.get_list("allowed_activities_edu.txt", False)
        keywords_edu = regex_handler.get_regex_from_file("keywords_edu.txt")
        blacklist_edu = regex_handler.get_regex_from_file("blacklist_edu.txt")

        for group_id in groups:
            group_info = api.groups.getById(group_id=group_id, fields=["status", "description"])[0]
            if regex_handler.check_group(
                    group_info, found_info_edu, keywords_edu, blacklist_edu, allowed_activities_edu):
                indexed_groups[group_id] = {"name": group_info["name"], "tags": "[EDUCATION]"}
                continue
            if (group_id in found_groups_career
                    or regex_handler.check_group(group_info, found_info_career, keywords_career)):
                indexed_groups[group_id] = {"name": group_info["name"], "tags": "[WORK]"}

        user_info = {
            "works": career,
            "education": schools.update(universities),
            "groups": indexed_groups
        }
        print("\tgroups")
        for key in indexed_groups.keys():
            print("\t\tgroup_id: %s" % key)
            for item in indexed_groups[key].items():
                print("\t\t\t%s:" % item[0], "%s" % item[1])
        output[user_id] = user_info

    with open("output.txt", "w") as file:
        json.dump(output, file, default=str)


def get_schools(api, user_id):
    schools_name = {}
    schools = api.users.get(user_ids=user_id, fields="schools")

    for school in schools[0]["schools"]:
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
    universities = api.users.get(user_ids=user_id, fields="universities")

    for university in universities[0]["universities"]:
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


main()
