import random

def ret_rand_str(size):
	charlist = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!$%&()*+,-./:;<=>?@^_`{|}~"
	res = ''.join(random.choices(charlist, k = size))
	return res

f = open("fprint.txt", "a")
for i in range(5):
	f.write(ret_rand_str(250)+"\n\n")
f.close()