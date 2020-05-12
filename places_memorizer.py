import telebot


def get_token():
    with open("token.tkn") as token_file:
        token = token_file.read()
    return token


if __name__ == "__main__":
    TOKEN = get_token()
    print(TOKEN)

