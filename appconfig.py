import platform

where = platform.uname().release.find("aws")

if where == -1:
    # Local
    config = {
        "host": "localhost",
        "database": "macro_meals_db",
        "user": "root",
        "password": "",
    }

else:
    #on Python Anywhere
    config = {
        "host": "Mohsin272.mysql.pythonanywhere-services.com",
        "database": "Mohsin272$macro_meals_db",
        "user": "Mohsin272",
        "password": "macromealsdbpassword",
    }  # pragma no cover
