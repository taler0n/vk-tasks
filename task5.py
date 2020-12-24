import vk_api
import common


def main():
    user_ids = common.get_user_ids("users.txt")
    session = common.get_session("credentials.txt")
    api = session.get_api()
    tools = vk_api.VkTools(session)


main()