import vk_api


def get_session(filename):
    with open(filename, encoding='utf-8') as file:
        login = file.readline()
        password = file.readline()

    session = vk_api.VkApi(login, password)

    try:
        session.auth(token_only=True)
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    return session


def get_list(filename, convert_to_int):
    new_list = []
    with open(filename, encoding='utf-8') as file:
        for line in file:
            if convert_to_int:
                new_list.append(int(line))
            else:
                new_list.append(line.rstrip())
    return new_list


def print_dict_tabulated(dictionary, element_tag):
    for key in dictionary.keys():
        print("\t\t%s: " % element_tag, "%s" % key)
        for item in dictionary[key].items():
            print("\t\t\t%s: " % item[0], "%s" % item[1])
