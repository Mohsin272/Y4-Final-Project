        password = request.form.get("password")
        password = password.encode('utf-8')
        hashed_password = bcrypt.hashpw(password, salt)