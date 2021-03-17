from pymongo import MongoClient
from phe import paillier
from flask import Flask, request, render_template, redirect
import pickle
from flask_restful import Resource, Api
from flask_wtf import FlaskForm

app = Flask(__name__)
api = Api(app)

#load PUBLIC_KEY
public_key_file = open('publicKey', 'rb')
public_key = pickle.load(public_key_file)
public_key_file.close()

client = MongoClient('mongodb://20.198.81.2:27017/')
mydb = client['attendance_db']
rollnum_table = mydb["rollnum"]
enc_data_table = mydb["enc_data"]
attendance_table = mydb["attendance"]


@app.route('/delete', methods=['GET'])
def delete_all():
	attendance_table.delete_many({})
	enc_data_table.delete_many({})
	rollnum_table.delete_many({})
	return render_template('/viewtable.html',att_dict_list=[])

def eq_check(list1,list2,threshold):
	cnt = 0
	for i in range(len(list1)):
		if list1[i] == list2[i]:
			cnt = cnt + 1
	if cnt>int(threshold*len(list1)):
		return True
	else:
		return False

def conv_to_bin(string):
	return ''.join(format(ord(c),'08b') for c in string).replace('b','')

def create_db_entry(rollnum,enc_fproll):
	try:
		enc_fproll_entry_dict = {'_id':enc_fproll}
		res = enc_data_table.insert_one(enc_fproll_entry_dict)
		rollnum_entry_dict = {'_id':rollnum}
		res = rollnum_table.insert_one(rollnum_entry_dict)
		return True
	except Exception as e:
		print(e)
		return False

def get_all_rollnum():
	try:
		rollnumquery = rollnum_table.find({})
		rollnumlist = [elem['_id'] for elem in rollnumquery]
		return rollnumlist
	except Exception as e:
		print(e)
		return False


def get_all_enc_data():
	try:
		enc_data_query = enc_data_table.find({})
		enc_data_list = [elem['_id'] for elem in enc_data_query]
		enc_data_list = [i.strip('][').split(',') for i in enc_data_list]
		enc_data_list = [ [int(j) for j in i] for i in enc_data_list]
		return enc_data_list
	except Exception as e:
		print(e)
		return False

def get_attendance_record(rollnum="",date=""):
	try:
		if rollnum == "":
			if date == "":
				query = {}
			else:
				query = {'date':date}
		else:
			if date == "":
				query = {'rollnum':rollnum}
			else:
				query = {'rollnum':rollnum,'date':date}
		att_data_query = attendance_table.find(query)
		att_data_list = [{'rollnum':elem['rollnum'],'date':elem['date'],'time':elem['time']} for elem in att_data_query]
		"""enc_data_list = [i.strip('][').split(',') for i in enc_data_list]
		enc_data_list = [ [int(j) for j in i] for i in enc_data_list]
		return enc_data_list"""
		return att_data_list
	except Exception as e:
		print(e)
		return False

def attended(rollnum,date,time):
	try:
		entry_dict = {'rollnum':rollnum,'date':date,'time':time}
		res = attendance_table.insert_one(entry_dict)
	except Exception as e:
		print(e)
		return False

def check_similarity(enc_fp,rollnum_list,enc_data_list):
	if len(rollnum_list) == 0 or len(enc_data_list)==0 or len(enc_fp) == 0:
		return False, None
	for i in rollnum_list:
		enci = public_key.encrypt(int(conv_to_bin(i),2),r_value=999)
		enc_fp_obj = [paillier.EncryptedNumber(public_key,elem) for elem in enc_fp]
		candidate  = [enci+elem for elem in enc_fp_obj]
		candidate = [elem.ciphertext(False) for elem in candidate]
		for j in enc_data_list:
			print(j," - ",candidate)
			if eq_check(j,candidate,0.8):
				return True,i
		return False, None

class create_entry(Resource):
	def post(self):
		roll_num = request.form['rollnum']		
		enc_fproll = request.form['enc_fproll']
		print(roll_num)
		print(enc_fproll)
		status = create_db_entry(roll_num,enc_fproll)
		return {'status': status}

class verify(Resource):
	def post(self):
		enc_fp = request.form['enc_fp']
		enc_fp = enc_fp.strip('][').split(',')
		enc_fp = [int(i) for i in enc_fp]
		verify_date = request.form['verify_date']
		verify_time = request.form['verify_time']
		print(enc_fp)
		print(verify_date," ",verify_time)
		rollnum_list = get_all_rollnum()
		if rollnum_list  == False:
			return {'status': False}
		enc_data_list = get_all_enc_data()
		if rollnum_list == False:
			return {'status': False}
		print("Rollnumlist: ",rollnum_list)
		print("encdata_list: ",enc_data_list)
		print("enc_fp: ",enc_fp)
		status, rollnum = check_similarity(enc_fp,rollnum_list,enc_data_list)
		if status:
			attended(rollnum,verify_date,verify_time)
			print("yussss")
			return {'status': True,'rollnum': rollnum}
		else:
			print("nooooo")
			return {'status': False}


@app.route('/', methods=['GET', 'POST'])
def view_attendance():
	if request.method == 'POST':
		rollnum = request.form.get('rnum')
		date = request.form.get('attnd_date')
		print(request.form)
		att_dict_list = get_attendance_record(rollnum,date)
		return render_template('/viewtable.html',att_dict_list=att_dict_list)
	else:
		att_dict_list = []#get_attendance_record()
		return render_template('/viewtable.html',att_dict_list=att_dict_list)




api.add_resource(create_entry, '/create')
api.add_resource(verify, '/verify')
			
if __name__ == '__main__':
	app.run(debug = True)
