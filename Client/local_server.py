import requests
import random
import pickle
from tqdm import tqdm
from datetime import datetime

MAX_FINGER_PRINT_LENGTH = 250
#load PUBLIC_KEY
public_key_file = open('publicKey', 'rb')
PUBLIC_KEY = pickle.load(public_key_file)
public_key_file.close()

#load PRIVATE_KEY
private_key_file = open('privateKey', 'rb')
PRIVATE_KEY = pickle.load(private_key_file)
private_key_file.close()

R = 999

CREATE_URL = 'http://20.193.224.100:5000/create'
VERIFY_URL = 'http://20.193.224.100:5000/verify'

NOISE_RATIO = 0.1
BLOCK_SIZE = 5

def str_to_bin(string):
	return ''.join(format(ord(c),'08b') for c in string).replace('b','')

def str_to_int(string):
	return int(str_to_bin(string),2)

def change_num_list(fp_array,block_size=BLOCK_SIZE):
	while len(fp_array)%block_size!=0:
		fp_array.append(0)
	fin_array = []
	for i in range(0,len(fp_array),block_size):
		bin_array = []
		for k in range(block_size):
			bin_array.append(str_to_bin(chr(fp_array[i+k])))
		bin_array = "".join(bin_array)
		fin_array.append(int(bin_array,2))
	return fin_array

def add_noise(finger_print, noise_ratio = NOISE_RATIO,block_size=BLOCK_SIZE):
	fp_array = [str_to_int(char) for char in finger_print]

	l = len(fp_array)
	l_noise = int(len(fp_array) * (noise_ratio/block_size))
	indices = random.sample(range(0,l), l_noise)

	for idx in indices:
		fp_array[idx] = random.randint(33,126)
	print("".join([chr(ch) for ch in fp_array]))
	fp_array = change_num_list(fp_array)
	return fp_array

def register_user(roll_no, finger_print):
	
	#convert finger_print to list of intergers
	fp_array = [str_to_int(char) for char in finger_print]
	fp_array = change_num_list(fp_array)
	#print(fp_array)

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
	#print(enc_fp_array)
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
			#print("Before Adding Noise: ",fp_array)
			fp_array = add_noise(finger_print)
			print("After Adding Noise: ",fp_array)
			mark_attendance(fp_array)

		elif(choice == '3'):
			exit = True
		else:
			print('INVALID CHOICE')
