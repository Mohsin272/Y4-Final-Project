import platform

where = platform.uname().release.find("aws")

if where == -1:
    # Local
    config = {
        "host": "127.0.0.1",
        "database": "macro_meals_db",
        "user":"root",
        "password":""
    }

# else:
    # on Python Anywhere
    # config = {
    #     "host": "C00250220.mysql.pythonanywhere-services.com",
    #     "database": "C00250220$default",
    #     "user": "C00250220",
    #     "password": "commentspassword",
    # }  # pragma no cover
