import platform

where = platform.uname().release.find("aws")

if where == -1:
    # Local
    config = {
        "host": "localhost",
        "database": "macro_meals_db",
        "user": "root",
        "password": "macro_meals_password",
    }

else:
    #on Python Anywhere
    config = {
        "host": "C00250220.mysql.pythonanywhere-services.com",
        "database": "Mohsin272$macro_meals_db",
        "user": "Mohsin272",
        "password": "macromealsdbpassword",
    }  # pragma no cover
