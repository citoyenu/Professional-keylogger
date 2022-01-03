from cryptography.fernet import Fernet
key = ""

kie = "kl.txt"
sie = "sie.txt"
cie = "cie.txt"
encrypted_files = [kie,sie,cie]
count = 0

for decrypting_files in encrypted_files:
    with open(encrypted_files[count],'rb') as f:
        data = f.read()

    fernet = Fernet(key)
    decrypted = fernet.decrypt(data)

    with open("decription.txt",'ab') as f:
        f.write(decrypted)

    count += 1
