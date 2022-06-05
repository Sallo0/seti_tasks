import sys

import requests
import time


def getUserId(user):
    try:
        return requests.get(user).text.split("money&target=mail")[1].split("&")[0]
    except IndexError:
        print("Не знаю такого")


def getOnlineFriendsIds(id, token):
    x = requests.get("https://api.vk.com/method/friends.getOnline?user_id=" + id + "&access_token=" + token + "&v=5.131").text.split(
        "[")
    ids = x[1].split("]")
    return ids[0].split(",")


def getFriendsIds(id, token):
    x = requests.get("https://api.vk.com/method/friends.get?user_id=" + id + "&access_token=" + token + "&v=5.131").text.split("[")
    ids = x[1].split("]")
    return ids[0].split(",")


def getFriendInfo(id, token):
    infoById = requests.get(
        "https://api.vk.com/method/users.get?user_id=" + id + "&access_token=" + token + "&v=5.131").text.split('"')
    return infoById[7] + " " + infoById[11]


if __name__ == "__main__":
    c = 0
    token = input("Введите токен: ")
    while True:
        userInput = input("Введите id пользователя или ссылку на Vk: ")

        if len(userInput.split("/")) > 1:
            user = getFriendInfo(getUserId(str(userInput)), token)
            userId = getUserId(str(userInput))
        else:
            user = getFriendInfo(str(userInput), token)
            userId = user

        print("Друзья онлайн у пользователя: " + str(user))

        try:
            for i in getOnlineFriendsIds(userId, token):
                if c == 10:
                    time.sleep(1)
                    c = 0
                else:
                    c += 1
                    print(getFriendInfo(i, token))

            print("\n")
        except IndexError:
            print("Профиль скрыт")
            continue


        print("Все друзья пользователя: " + str(user))
        for i in getFriendsIds(userId, token):
            if c == 10:
                time.sleep(1)
                c = 0
            else:
                c += 1
                print(getFriendInfo(i, token))

#b12a78c1cb8ac1c0c6e3871f7f01a00d4a9b61ce754f9c708e75f3a34c612820f42506a3a1fb5c554e2e0