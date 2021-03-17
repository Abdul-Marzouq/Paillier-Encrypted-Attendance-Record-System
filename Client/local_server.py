import requests
import random
import pickle
from tqdm import tqdm
from datetime import datetime



MAX_FINGER_PRINT_LENGTH = 25

#load PUBLIC_KEY
public_key_file = open('publicKey', 'rb')
PUBLIC_KEY = pickle.load(public_key_file)
public_key_file.close()

#load PRIVATE_KEY
private_key_file = open('privateKey', 'rb')
PRIVATE_KEY = pickle.load(private_key_file)
private_key_file.close()

R = 999

CREATE_URL = 'http://127.0.0.1:5000/create'
VERIFY_URL = 'http://127.0.0.1:5000/verify'

NOISE_RATIO = 0.02

def str_to_bin(string):
	return ''.join(format(ord(c),'08b') for c in string).replace('b','')

def str_to_int(string):
	return int(str_to_bin(string),2)

def add_noise(finger_print, noise_ratio = NOISE_RATIO):
	fp_array = [str_to_int(char) for char in finger_print]

	l = len(fp_array)
	l_noise = int(len(fp_array) * noise_ratio)
	indices = random.sample(range(0,l), l_noise)

	for idx in indices:
		fp_array[idx] = chr(random.randint(0,127))

	return fp_array

def register_user(roll_no, finger_print):
	
	#convert finger_print to list of intergers
	fp_array = [str_to_int(char) for char in finger_print]

	enc_roll_no = PUBLIC_KEY.encrypt(str_to_int(roll_no),r_value=R)

	loop = tqdm(fp_array, 
		ascii = False,
		leave = True, 
		desc = 'Registering user', 
		bar_format = '{l_bar}{bar:40}{elapsed}<{remaining}')	
	enc_fp_array = [PUBLIC_KEY.encrypt(i,r_value=R) for i in loop]

	enc_fp_roll = [x._add_encrypted(enc_roll_no) for x in enc_fp_array]
	enc_fp_roll = [x.ciphertext(False) for x in enc_fp_roll]
	enc_fp_roll = str(enc_fp_roll)
	data = {'rollnum' : roll_no,'enc_fproll' : enc_fp_roll}
	r = requests.post(CREATE_URL,data=data)
	print(r.text)

	return

def mark_attendance(fp_array):

	loop = tqdm(fp_array, 
		ascii = False,
		leave = True, 
		desc = 'Verifying user', 
		bar_format = '{l_bar}{bar:40}{elapsed}<{remaining}')
	enc_fp_array = [PUBLIC_KEY.encrypt(i,r_value=R) for i in loop]
	enc_fp_array = [x.ciphertext(False) for x in enc_fp_array]
	enc_fp_array = str(enc_fp_array)
	now = datetime.now()
	dt_str = now.strftime("%Y-%m-%d")
	tim_str = now.strftime("%H:%M:%S")
	data = {'enc_fp' : enc_fp_array,
			'verify_date': dt_str,
			'verify_time' : tim_str}

	r = requests.post(VERIFY_URL, data = data)
	print(r.text)

	return


if __name__ == '__main__':
	exit = False
	while(not exit):
		print('\n')
		print('1. Register new user')
		print('2. Mark attendance')
		print('3. Exit')

		choice = input('Choose an option to continue: ')

		if(choice == '1'):
			roll_no = input('ENTER ROLL NO: ')
			finger_print = input('ENTER FINGER PRINT: ')
			register_user(roll_no, finger_print)

		elif(choice == '2'):
			finger_print = input('ENTER FINGER PRINT: ')
			fp_array = add_noise(finger_print)
			mark_attendance(fp_array)

		elif(choice == '3'):
			exit = True
		else:
			print('INVALID CHOICE')
