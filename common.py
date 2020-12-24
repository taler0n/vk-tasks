import vk_api


def get_session(filename):
    with open(filename) as file:
        login = file.readline()
        password = file.readline()

    session = vk_api.VkApi(login, password)

    try:
        session.auth(token_only=True)
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    return session


def get_user_ids(filename):
    users = []
    with open(filename) as file:
        for line in file:
            users.append(int(line))

    return users
