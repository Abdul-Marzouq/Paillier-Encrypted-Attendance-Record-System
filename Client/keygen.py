from phe import paillier
import pickle

try:
	PUBLIC_KEY, PRIVATE_KEY = paillier.generate_paillier_keypair()

	#save PUBLIC_KEY
	public_key_file = open('publicKey','wb')
	pickle.dump(PUBLIC_KEY, public_key_file)
	public_key_file.close()

	#save PRIVATE_KEY
	private_key_file = open('privateKey', 'wb')
	pickle.dump(PRIVATE_KEY, private_key_file)
	private_key_file.close() 

	print('KEY GENERATED')
except :
	print('KEY GENERATION FAILED')



