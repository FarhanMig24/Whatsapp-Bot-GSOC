class Patient:
    def __init__(self, demo_jwttoken={}, pextid="NULL", is_patient=False, psearchinfo={}, pinfo={},verified=False,last_login=0.0):
        self.demo_jwttoken = demo_jwttoken
        self.pextid = pextid
        self.is_patient = is_patient
        self.psearchinfo = psearchinfo
        self.pinfo = pinfo
        self.verified = verified
        self.last_login=last_login


    def reset(self):
        self.demo_jwttoken={}
        self.pextid="NULL"
        self.is_patient=False
        self.psearchinfo={}
        self.pinfo={}
        self.verified=False
        self.last_login=0.0
        
    def set_demo_jwttoken_value(self, value):
        self.demo_jwttoken = value

    def get_demo_jwttoken_value(self):
        return self.demo_jwttoken

    def set_is_patient(self, value):
        self.is_patient = value

    def get_is_patient(self):
        return self.is_patient

    def set_patient_search_info_value(self, value):
        self.psearchinfo = value

    def get_patient_search_info_value(self):
        return self.psearchinfo

    def set_patient_info_value(self, value):
        self.pinfo = value

    def get_patient_info_value(self):
        return self.pinfo

    def set_patient_ext_id(self, value):
        self.pextid = value

    def get_patient_ext_id(self):
        return self.pextid
    
    def set_is_authenticated(self,value):
        self.verified=value

    def get_is_authenticated(self):
        return self.verified
    
    def set_last_login(self,value):
        self.last_login=value

    def get_last_login(self):
        return self.last_login
    

