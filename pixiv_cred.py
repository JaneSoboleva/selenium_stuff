from cryptography.fernet import Fernet


def saveLoginInfo(pixiv_l="", pixiv_p=""):
    key = Fernet.generate_key()
    f = Fernet(key)
    if pixiv_l != "":
        s_l = pixiv_l
    else:
        s_l = input('Pixiv email: ')
    if pixiv_p != "":
        s_p = pixiv_p
    else:
        s_p = input('Pixiv password: ')
    s_l = s_l + chr(13) + s_p
    bs_l = bytes(s_l, 'utf-8')
    token = f.encrypt(bs_l)

    fl = open("pixivlogin.", "wb")
    fl.write(token)
    fl.close()

    fk = open("key.", "wb")
    fk.write(key)
    fk.close()

    print("Login info saved.")


def loadLoginInfo():
    fl = open("pixivlogin.", "rb")
    token = fl.read()
    fl.close()

    fk = open("key.", "rb")
    key = fk.read()
    fk.close()

    f = Fernet(key)
    decr = f.decrypt(token)
    s_l, s_p = decr.decode('utf-8').split(chr(13))
    return [s_l, s_p]
