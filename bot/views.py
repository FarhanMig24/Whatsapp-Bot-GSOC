from django.shortcuts import render
from twilio.rest import Client
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import requests
import json
import re
from urllib.parse import quote
import time


from django.views.decorators.csrf import csrf_exempt
from bot.users_schema.Patient import Patient
from bot.users_schema.User import User
from bot.Response import Response_Handler


LOGIN_EXPIRATION_TIME=15


account_sid = 'AC19d32cc92a35f05f4c4af29e45a58884'
auth_token = '860272559073fa7797a3d400c8ebc636'
client = Client(account_sid, auth_token)


handler = Response_Handler(0)
user = User()
patient = Patient()


#ENTRY POINT

@csrf_exempt
def bot(request):

    # print(request.POST)
    # data = JSONParser().parse(request)
    # print(data)
    message = request.POST.get('Body', '')
    sender_name = request.POST.get('ProfileName', '')
    sender_no = request.POST.get('From', '')
    
    print("Received Message:", message)
    print("Sender Name:", sender_name)
    print("Sender Number:", sender_no)
    
    handle_message(message,sender_name,sender_no)
    
    return HttpResponse()


## MESSAGE ROUTER

def handle_message(message, sender_name, sender_no):

    actions = {
        0:    lambda: send_first_message(sender_name, sender_no,message),
        1:    lambda: decide_userorpatient(sender_name, sender_no,message),


        102:  lambda: get_username(sender_name,sender_no,message),
        103:  lambda: get_password(sender_name,sender_no,message),
        104:  lambda: user_services(sender_name,sender_no),
        

        202:  lambda: get_dateofbirth(sender_name,sender_no,message),
        203:  lambda: get_patient_info_single(sender_name,sender_no,message),
        204:  lambda: patient_services(sender_name,sender_no,message),

        2041: lambda: get_patientrecords(sender_name,sender_no,message),
        # 2042: lambda: get_patientmedications(sender_name,sender_no,message),
        # 2043: lambda: get_patientprocedures(sender_name,sender_no,message),


        # 20411: lambda: get_patientpersonalinfo(sender_name,sender_no,message),
        # 20412: lambda: get_patientmedicalstatus(sender_name,sender_no,message),


        -1:   lambda: send_default_message(sender_no),
        -2:   lambda: send_relogin_message(sender_no)

    }

    print("Card No: {}".format(handler.get_response_handler()))
    if user.get_is_user() == True:
        print("yes")
        if user.get_is_authenticated() == True and (time.time() - user.get_last_login() > LOGIN_EXPIRATION_TIME*60):
            print("yes")
            user.reset()
            handler.set_response_handler(-2)
        else:
            user.set_last_login(time.time())
    if patient.get_is_patient() == True:
        if patient.get_is_authenticated() == True and (time.time() - patient.get_last_login() > LOGIN_EXPIRATION_TIME*60):
            patient.reset()
            handler.set_response_handler(-2)
        else:
            patient.set_last_login((time.time()))

    if message.lower() == "/reset":

        user.reset()
        patient.reset()
        handler.set_response_handler(0)

        send_first_message(sender_name, sender_no,"hi")
    else:
        actions[handler.get_response_handler()]()


## STARTING MESSAGE

def send_first_message(sender_name, sender_no,message):
    
    if message.lower() != "hi":
        send_default_message(sender_no)
    else:
        if user.get_is_authenticated()==False and patient.get_is_authenticated()==False:
            send_hi_message(sender_name,sender_no)
            handler.set_response_handler(1)
        else:
            if user.get_is_authenticated()==True:
                print_user_services_menu(sender_no)
                handler.set_response_handler(102)
            elif patient.get_is_authenticated()==True:
                print_patient_services_menu(sender_no)
                handler.set_response_handler(202)


## USER OR PATIENT RECOGNITION

def decide_userorpatient(sender_name, sender_no,message):

    if "patient" in message.lower():
        patient.set_is_patient(True)
        user.set_is_user(False)
        send_message(sender_no,'Please enter date of birth in YYYY-MM-DD format to continue.')
        handler.set_response_handler(202)
    elif "staff" in message.lower():
        patient.set_is_patient(False)
        user.set_is_user(True)
        send_message(sender_no,'Please enter your username to login.')
        handler.set_response_handler(102)
    else:
        handler.set_response_handler(0)
        send_default_message(sender_no)


## USER INFO

def get_username(sender_name,sender_no,message):
    user.set_username_value(message)
    handler.set_response_handler(103)
    send_message(sender_no,'Please enter your password now for authentication.')
    
def get_password(sender_name,sender_no,message):
    user.set_password_value(message)
    api_status=user_login_api_call()
    if api_status == -1:
        send_message(sender_no,'Server Error.\nTry Later')
    elif api_status == 401:
        handler.set_response_handler(102)
        send_message(sender_no,'The credentials you have entered are invalid.\nPlease enter correct username to restart authentication process.')

    elif api_status!= 200:
        handler.set_response_handler(102)
        send_message(sender_no,'Wrong API Call.Try Later')
    else:
        api_status_user=get_user_info_api(user.get_jwttoken_value()['access'])
        if api_status_user == -1:
            send_message(sender_no,'Server Error.\nTry Later')
        elif api_status_user != 200:
            send_message(sender_no,'Wrong API Call.\nTry Later')
        else:
            if 'whatsapp:+911234567891' != 'whatsapp:'+user.get_user_info_value()['phone_number']:  #change lhs of this condition to sender_no later.
                send_message(sender_no,'The given username is registered with a different phone number.\nPlease try with the username registered with this phone number.')
                handler.set_response_handler(102)
            else:
                send_message(sender_no,'You have succesfully authenticated as a user(staff).')
                handler.set_response_handler(104)
                user.set_is_authenticated(True)
                user_services(sender_name,sender_no)

def user_services(sender_name,sender_no):
    print_user_services_menu(sender_no)

## PATIENT INFO


def get_dateofbirth(sender_name,sender_no,message):

    if(re.match(r'^\d{4}-\d{2}-\d{2}$',message)):
        if re.match(r'^(19[2-9]\d|20[0-9][0-9])-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$',message):

            user.set_username_value('devdistrictadmin')
            user.set_password_value('Coronasafe@123')

            api_status=user_login_api_call()

            if api_status == -1:
                send_message(sender_no,'Server Error.\nTry Later')
            elif api_status != 200:
                send_message(sender_no,'Wrong API Call.\nTry Later')

            api_status_patient_info=search_patient_api(message,sender_no.split(':')[1],patient.get_demo_jwttoken_value()['access']) #2005-10-16 #+919987455444

            if api_status_patient_info == -1:
                send_message(sender_no,'Server Error.\nTry Later')
            elif api_status_patient_info != 200:
                send_message(sender_no,'Wrong API Call.\nTry Later')
            else:
                if patient.get_patient_search_info_value()['count'] == 1:
                    send_message(sender_no,'You have succesfully authenticated as a patient.')
                    patient.set_is_authenticated(True)
                    print_patient_services_menu(sender_no)
                    patient.set_patient_info_value(patient.get_patient_search_info_value()['results'][0])
                    patient.set_patient_ext_id(patient.get_patient_search_info_value()['results'][0]['patient_id'])
                    handler.set_response_handler(204)

                elif patient.get_patient_search_info_value()['count'] > 1:
                    send_message(sender_no,'Multple patient records exists.\nPlease enter patient name as entered earlier to find the record you are looking for.')
                    handler.set_response_handler(203)

                    # To be implemented check with name and accordingly filter

                else:
                    handler.set_response_handler(202)
                    send_message(sender_no,'No such patient exists. Please enter correct date of birth of the patient registered with this phone number.')

        else:
            handler.set_response_handler(202)
            send_message(sender_no,'The date of birth you have entered has invalid value.Please re-enter the date of birth')
    else:
        handler.set_response_handler(202)
        send_message('The date of birth you have entered has incorrect format.Please re-enter the date of birth in correct format.')

def get_patient_info_single(sender_name,sender_no,message):
    found_patient = "NULL"
    results=patient.get_patient_search_info_value()['results']
    for pat in results:
        if pat['name'].lower() == message.lower():
            found_patient = pat
            send_message(sender_no,'You have succesfully authenticated as a patient.')
            print_patient_services_menu(sender_no)
            patient.set_is_authenticated(True)
            patient.set_patient_info_value(patient.get_patient_search_info_value()['results'][0])
            patient.set_patient_ext_id(patient.get_patient_search_info_value()['results'][0]['patient_id'])
            handler.set_response_handler(204)
            break  # Exit the loop once a match is found

    if found_patient=="NULL":
        handler.set_response_handler(203)
        send_message(sender_no,'The name you have entered isn\'t present in the available records.Please enter correct name.')

        
    #PATIENT SERVICES

def patient_services(sender_name,sender_no,message):
    if message == "1":
        handler.set_response_handler(2041)
        print_patient_records_menu(sender_no)
    elif message == "2":
        handler.set_response_handler(2042)
    elif message == "3":
        handler.set_response_handler(2043)
    else:
        send_message(sender_no,'Invalid input provided.Please enter suitable number to access information')
        print_patient_services_menu(sender_no)
        handler.set_response_handler(204)


def get_patientrecords(sender_name,sender_no,message):
    patient_full_info=patient_info_api(patient.get_demo_jwttoken_value()['access'])
    if message == "1":
        handler.set_response_handler(204)
        get_patientpersonalinfo(sender_name,sender_no,patient_full_info)
        print_patient_services_menu(sender_no)
    elif message == "2":
        handler.set_response_handler(204)
        get_patientmedicalstatus(sender_name,sender_no,patient_full_info)
        print_patient_services_menu(sender_no)
    elif message == "3":
        handler.set_response_handler(204)
        #Need to use the last_consultation key for extracting.
    elif message == "4":
        handler.set_response_handler(204)
        get_patientfacilitydetails(sender_name,sender_no,patient_full_info)
        print_patient_services_menu(sender_no)
    else:
        send_message(sender_no,'Invalid input provided.Please enter suitable number to access information')
        print_patient_records_menu(sender_no)
        handler.set_response_handler(2041)
    


def get_patientpersonalinfo(sender_name,sender_no,patient_full_info):
    gender = "Male" if patient_full_info['gender'] == 1 else ("Female" if patient_full_info['gender'] == 2 else "Other")
    send_message(sender_no,f'Name:{patient_full_info['name']}\nAge:{patient_full_info['age']}\nGender:{gender}\nPhone Number:{patient_full_info['phone_number']}\nAddress:{patient_full_info['address']}\nDate of birth:{patient_full_info['date_of_birth']}\nNationality:{patient_full_info['nationality']}\nBlood Group:{patient_full_info['blood_group']}\n')

def get_patientmedicalstatus(sender_name,sender_no,patient_full_info):
    send_message(sender_no,f'Disease Status:{patient_full_info['disease_status']}\nAllergies:{patient_full_info['allergies']}\nPresent Health:{patient_full_info['present_health']}\nSARI:{patient_full_info['has_SARI']}\nAntenatal Status:{patient_full_info['is_antenatal']}\nVaccine Taken:{patient_full_info['is_vaccinated']}\nVaccine Name:{patient_full_info['vaccine_name']}\nNo of doses:{patient_full_info['number_of_doses']}\nCOVID Status:{patient_full_info['is_declared_positive']}\n')

def get_patientfacilitydetails(sender_name,sender_no,patient_full_info):
    send_message(sender_no,f'Facility Name:{patient_full_info['facility_object']['name']}\nFacility Address:{patient_full_info['facility_object']['address']}\nFacility Pincode:{patient_full_info['facility_object']['pincode']}\nFacility Contact No.:{patient_full_info['facility_object']['phone_number']}\nCurrent Patient Count:{patient_full_info['facility_object']['patient_count']}\nCurrent Bed Count:{patient_full_info['facility_object']['bed_count']}\n')





## HELPER FUNCTIONS
    
    
def print_user_services_menu(sender_no):
    client.messages.create(
        from_='whatsapp:+14155238886',
        body='User Services Menu:\n\n1.Show my schedules.\n2.Show asset status\n3.Show inventory data\n\n\nPlease enter the correct number according to your need.',
        to=sender_no
    )

def print_patient_services_menu(sender_no):
    client.messages.create(
        from_='whatsapp:+14155238886',
        body='Patient Services Menu:\n\n1.Show patient\'s records\n2.Show patient\'s current medications\n3.Show patient\'s procedures\n\n\nPlease enter the correct number according to your need.',
        to=sender_no
    )

def print_patient_records_menu(sender_no):
    client.messages.create(
        from_='whatsapp:+14155238886',
        body='Patient Records Menu:\n\n1.Show patient\'s personal information\n2.Show patient\'s current medical status.\n3.Show patient\'s medical history.\n4.Show patient\'s facility details.\n\n\nPlease enter the correct number according to your need.',
        to=sender_no
    )

def send_hi_message(sender_name,sender_no):
    client.messages.create(
        from_='whatsapp:+14155238886',
        body='Hi {}. This is the official Whatsapp bot for Open HealthCare Network.\nPlease enter whether you are a staff or a patient.'.format(sender_name),
        to=sender_no
    )

def send_message(sender_no,message):
    client.messages.create(
        from_='whatsapp:+14155238886',
        body=message,
        to=sender_no
    )

def send_default_message(sender_no):
    client.messages.create(
        from_='whatsapp:+14155238886',
        body='Sorry, I couldn\'t understand your message. Please enter Hi to get started with the OHCN Whatsapp Bot.',
        to=sender_no
    )

def send_relogin_message(sender_no):
   client.messages.create(
        from_='whatsapp:+14155238886',
        body=f'The last message has surpassed since {LOGIN_EXPIRATION_TIME} minutes.\nYou need to re-login to use the service once again\nEnter Hi to get started.',
        to=sender_no
    ) 

## API CALLS

def user_login_api_call():

    url = "http://localhost:9000/api/v1/auth/login/"

    payload = {
        "username": user.get_username_value(),
        "password": user.get_password_value()
    }
    print(payload)
    payload_json = json.dumps(payload)

    try:
        response = requests.post(url, data=payload_json, headers={"Content-Type": "application/json"})

        print(response.status_code)
        # print(payload_json)

        if response.status_code == 200:
            
            if user.get_is_user() == True:
                # print("user")
                user.set_jwttoken_value(response.json())
            elif patient.get_is_patient() == True:
                # print("patient")
                patient.set_demo_jwttoken_value(response.json())
            return response.status_code

        else:
            print("error")
            return response.status_code
        
    except requests.exceptions.RequestException as e:
        print("Error making API call:", e)
        return -1



def get_user_info_api(authorization_token):

    url = f'http://localhost:9000/api/v1/users/{user.get_username_value()}/'

    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer {}'.format(authorization_token)
    }
    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            user.set_user_info_value(response.json())
        else:
            print("Error:", response.status_code)
            print("Response Body:", response.text)
        return response.status_code
     
    except requests.exceptions.RequestException as e:
        print("Error making API call:", e)
        return -1
    


def search_patient_api(date_of_birth, ph_no,authorization_token):
   
    encoded_date_of_birth = quote(date_of_birth)   #Encoding parameters
    encoded_ph_no = quote(ph_no)
    print(encoded_date_of_birth)
    print(encoded_ph_no)

    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer {}'.format(authorization_token)
    }

    url = f"http://localhost:9000/api/v1/patient/search/?date_of_birth={encoded_date_of_birth}&phone_number={encoded_ph_no}" #date_of_birth={encoded_date_of_birth}&

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            patient.set_patient_search_info_value(response.json())
            print(patient.get_patient_search_info_value())
            return response.status_code
        else:
            print("Error: Failed to fetch patient information.")
            return response.status_code
    except requests.exceptions.RequestException as e:
        print("Error making API call:", e)
        return -1



def patient_info_api(authorization_token):
    url = f'http://localhost:9000/api/v1/patient/{patient.get_patient_ext_id()}/'

    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer {}'.format(authorization_token)
    }
    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            print("Error:", response.status_code)
            print("Response Body:", response.text)
            return None

    except requests.exceptions.RequestException as e:
        print("Error making API call:", e)
        return None


