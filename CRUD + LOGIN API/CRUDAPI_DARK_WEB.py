try:
    from flask import Flask, jsonify, request
    from pymongo import MongoClient
    from bson.json_util import dumps
    from bson.objectid import ObjectId
    import json
    from datetime import datetime
    import time
    import re
    import bcrypt
    import pyotp
    from bson import json_util
    from flask_socketio import SocketIO
    from flask_cors import CORS
except Exception as e:
    print("Some Modules are Missing :{}".format(e))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# database connection
def databaseConnection():
   CONNECTION_STRING = "mongodb+srv://emseccomandcenter:TUXnEN09VNM1drh3@cluster0.psiqanw.mongodb.net/?retryWrites=true&w=majority"
   client = MongoClient(CONNECTION_STRING)
   return client['darkWebAutomation']
db = databaseConnection()
# this database contain information about xpath
collection = db["websiteXPATH"]
# for login page
collection1 = db["portalLogin"]

# Validate the email address using a regex.
def is_email_address_valid(email):
    if not re.match("^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$", email):
        return False
    return True

# send otp for authentication
def send_otp_for_authentication(id,_secret_key):
    login_user = collection1.find({"_id":ObjectId(id)})
    totp = pyotp.TOTP(login_user[0]['secret key'])
    totp.now()
    return totp.verify(_secret_key)
    
# login
@app.route('/login', methods=['POST'])
def login():
    _email = request.json['email']
    _password = request.json['password']
    _secret_key = request.json['OTP']
	# check for user exist or not
    if collection1.count_documents({'email':_email})==0:
        return jsonify("User not exist")
    login_user = collection1.find({"email":_email})
    if login_user[0]['email'] == _email:
        # password matching
        if bcrypt.hashpw(_password.encode('utf-8'), login_user[0]['password']) == login_user[0]['password']:
            correct = send_otp_for_authentication(login_user[0]['_id'],_secret_key)
            if correct:
                return jsonify("Login Successfull")
            else:
                return jsonify("Login Failed")
        else:
            return jsonify("Wrong Password")
    else:
        return jsonify("User does not exist")

# display all users
@app.route('/allWebsite',methods=['GET'])
def users():
	users = collection.find()
	resp = dumps(users)
	return resp

# socket send data
@app.route('/sendData',methods=['POST'])
def sendData():
    data=request.json['data']
    socketio.emit('data',data)
    return jsonify({'result':'OK'})

# socket send log
@app.route('/sendLog',methods=['POST'])
def sendLog():
    data=request.json['msg']
    socketio.emit('log',data)
    return jsonify({'result':'OK'})

# GET , PUT and UPDATE Website
@app.route('/darkWebsite/<id>', methods=['GET','DELETE','PUT'])
def website(id):
    if request.method=='GET':
        try:
            data =collection.find_one({'_id':ObjectId(id)})
            user = dumps(data)
            return user
        except:
            resp = jsonify("No Content")
            resp.status_code = 204
            return resp

    if request.method=='DELETE':
        try:
		query = {"_id": ObjectId(id)}
		collection.delete_one(query)
		resp = jsonify("Field Deleted")
		resp.status_code = 410
		return resp
	except:
		resp = jsonify("Already Deleted")
		resp.status_code = 210
		return resp

    if request.method =='PUT':
        _name =request.json['name']
        _darkweb_url =request.json['darkweb_url'] 
        _iterator=request.json['iterator']
        _title_xpath=request.json['title_xpath']
        _body_xpath=request.json['body_xpath']
        _date_xpath=request.json['date_xpath']
        _scrollable=request.json['scrollable']
        _pagination = request.json['pagination']
        _is_nextbtn=request.json['is_nextbtn']
        _xpath_of_next_btn=request.json['xpath_of_next_btn']
        _xpath_of_pagination_container=request.json['xpath_of_pagination_container']
        _tag_name_of_pages=request.json['tag_name_of_pages']
        _clickable =request.json['clickable']
        _clickable_btn_xpath =request.json['clickable_btn_xpath']
        _waitTime =request.json['waitTime']
        _isSPA =request.json['isSPA']
        _isUrgent =request.json['isUrgent']
        
        dict = {}
        if(len(str(_name))>0):
            dict['name'] = _name
        if(len(str(_darkweb_url))>0):
            dict['darkweb_url'] = _darkweb_url 
        if(len(str(_iterator))>0):
            dict['iterator'] = _iterator
        if(len(str(_title_xpath))>0):
            dict['title_xpath'] = _title_xpath
        if(len(str(_body_xpath))>0):
            dict['body_xpath'] = _body_xpath
        if(len(str(_date_xpath))>0):
            dict['date_xpath'] = _date_xpath
        if(len(str(_scrollable))>0):
            dict['scrollable'] = _scrollable
        if(len(str(_pagination))>0):
            dict['pagination'] = _pagination
        if(len(str(_is_nextbtn))>0):
            dict['is_nextbtn'] = _is_nextbtn
        if(len(str(_xpath_of_next_btn))>0):
            dict['xpath_of_next_btn'] = _xpath_of_next_btn
        if(len(str(_xpath_of_pagination_container))>0):
            dict['xpath_of_pagination_container'] = _xpath_of_pagination_container
        if(len(str(_tag_name_of_pages))>0):
            dict['tag_name_of_pages'] = _tag_name_of_pages
        if(len(str(_clickable))>0):
            dict['clickable'] = _clickable
        if(len(str(_clickable_btn_xpath))>0):
            dict['clickable_btn_xpath'] = _clickable_btn_xpath
        if(len(str(_waitTime))>0):
            dict['waitTime'] = _waitTime
        if(len(str(_isSPA))>0):
            dict['isSPA'] = _isSPA
        if(len(str(_isUrgent))>0):
            dict['isUrgent'] = _isUrgent
        
        # update values in database
        collection.find_one_and_update({"_id":ObjectId(id)},{"$set":dict})
                
        resp = jsonify("Website updated")
        resp.status_code = 200
        return resp

# Add Website
@app.route('/darkWebsite', methods=['POST'])
def post():
    name =request.json['name']
    darkweb_url =request.json['darkweb_url'] 
    iterator=request.json['iterator']
    title_xpath=request.json['title_xpath']
    body_xpath=request.json['body_xpath']
    date_xpath=request.json['date_xpath']
    scrollable=request.json['scrollable']
    pagination = request.json['pagination']
    is_nextbtn=request.json['is_nextbtn']
    xpath_of_next_btn=request.json['xpath_of_next_btn']
    xpath_of_pagination_container=request.json['xpath_of_pagination_container']
    tag_name_of_pages=request.json['tag_name_of_pages']
    failed_count = 0
    clickable =request.json['clickable']
    clickable_btn_xpath =request.json['clickable_btn_xpath']
    waitTime =request.json['waitTime']
    status = "not started"
    isSPA =request.json['isSPA']
    time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    isUrgent = False
    
    if collection.count_documents({'darkweb_url':darkweb_url})>0:
        return jsonify("url Already exist.. Update the field if you need")
    if request.method == "POST":
        collection.insert_one({'name':name,'darkweb_url':darkweb_url,'iterator':iterator,'title_xpath':title_xpath,'body_xpath':body_xpath,'date_xpath':date_xpath,'scrollable':scrollable,'pagination':pagination,'is_nextbtn':is_nextbtn,'xpath_of_next_btn':xpath_of_next_btn,'xpath_of_pagination_container':xpath_of_pagination_container,'tag_name_of_pages':tag_name_of_pages,'failedCount':failed_count,'clickable':clickable,'clickable_btn_xpath':clickable_btn_xpath,'waitTime':waitTime,'status':status,'isSPA':isSPA,'time':time,'isUrgent':isUrgent})
        resp = jsonify("Website added successfully")
        resp.status_code = 200
        return resp
    else:
        return not_found()

# Error Handler
@app.errorhandler(404)
def not_found(error = None):
    message = {
        'status': 404,
        'message' : 'Not Found' + request.url
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp    

# main Function
if __name__=='__main__':
    app.run(debug=True)
