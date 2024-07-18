class User:
    def __init__(self, jwttoken={}, username="NULL", password="NULL", is_user=False, uinfo={},verified=False,last_login=0.0):
        self.jwttoken = jwttoken
        self.username = username
        self.password = password
        self.is_user = is_user
        self.uinfo = uinfo
        self.verified=verified
        self.last_login=last_login
        # self.response_handler=response_handler

    def reset(self):
        self.jwttoken = {}
        self.username = "NULL"
        self.password = "NULL"
        self.is_user = False
        self.uinfo = {}
        self.verified=False
        self.last_login=0.0

    def set_username_value(self, value):
        self.username = value

    def get_username_value(self):
        return self.username

    def set_password_value(self, value):
        self.password = value

    def get_password_value(self):
        return self.password

    def set_jwttoken_value(self, value):
        self.jwttoken = value

    def get_jwttoken_value(self):
        return self.jwttoken

    def set_user_info_value(self, value):
        self.uinfo = value

    def get_user_info_value(self):
        return self.uinfo

    def set_is_user(self, value):
        self.is_user = value

    def get_is_user(self):
        return self.is_user
    
    def set_is_authenticated(self,value):
        self.verified=value

    def get_is_authenticated(self):
        return self.verified
    
    def set_last_login(self,value):
        self.last_login=value

    def get_last_login(self):
        return self.last_login
    # def set_response_handler(self, value):
    #     self.response_handler = value

    # def get_response_handler(self):
    #     return self.response_handler
