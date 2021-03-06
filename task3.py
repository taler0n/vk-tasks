from datetime import datetime
import json
import vk_api
import common


def main():
    user_ids = common.get_list("users.txt", True)
    session = common.get_session("credentials.txt")
    api = session.get_api()
    tools = vk_api.VkTools(session)
    time_period = 7
    output = {}

    for user_id in user_ids:
        print("user %s:" % user_id)
        groups_info = get_groups_info(api, tools, user_id, time_period)
        friends_info = get_friends_info(api, tools, user_id, time_period)

        print("\n")
        print("\tgroups")
        common.print_dict_tabulated(groups_info, "post_id")
        print("\tfriends")
        common.print_dict_tabulated(friends_info, "post_id")

        user_info = {
            "groups": groups_info,
            "friends": friends_info
        }
        output[user_id] = user_info
    with open("output.txt", "w", encoding='utf-8') as file:
        json.dump(output, file, default=str, ensure_ascii=False)


def get_groups_info(api, tools, user_id, time_period):
    groups = tools.get_all_iter("groups.get", 1000, {"user_id": user_id})
    groups_info = {}

    for group_id in groups:
        print("group %s" % group_id)
        keep_reading = True
        request_count = 0
        while keep_reading:
            try:
                posts = api.wall.get(owner_id=-group_id, count=100, offset=request_count * 100)
            except vk_api.ApiError:
                break

            if len(posts["items"]) == 0:
                break
            request_count += 1
            for post in posts["items"]:
                post_date = datetime.utcfromtimestamp(post["date"])
                if (datetime.today() - post_date).days > time_period and post.get("is_pinned") is None:
                    keep_reading = False
                    break
                like_check = api.likes.isLiked(user_id=user_id, type="post", owner_id=-group_id, item_id=post["id"])
                if like_check["liked"] == 1:
                    post_info = {"group": group_id, "text": post["text"], "date": post_date.date()}
                    groups_info[post["id"]] = post_info

    return groups_info


def get_friends_info(api, tools, user_id, time_period):
    friends = tools.get_all_iter("friends.get", 5000, {"user_id": user_id})
    friends_info = {}

    for friend_id in friends:
        print("friend %s" % friend_id)
        keep_reading = True
        request_count = 0
        while keep_reading:
            try:
                posts = api.wall.get(owner_id=friend_id, count=100, offset=request_count * 100)
            except vk_api.ApiError:
                break

            if len(posts["items"]) == 0:
                break
            request_count += 1
            for post in posts["items"]:
                post_date = datetime.utcfromtimestamp(post["date"])
                if (datetime.today() - post_date).days > time_period and post.get("is_pinned") is None:
                    keep_reading = False
                    break
                like_check = api.likes.isLiked(user_id=user_id, type="post", owner_id=friend_id, item_id=post["id"])
                if like_check["liked"] == 1:
                    post_info = {"user": friend_id, "text": post["text"], "date": post_date.date()}
                    friends_info[post["id"]] = post_info

    return friends_info


main()
