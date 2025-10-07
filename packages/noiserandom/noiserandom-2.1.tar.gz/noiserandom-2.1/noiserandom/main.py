from os import remove,sep
from secrets import choice,randbits
from gmpy2 import is_prime as isprime
import sys
import cv2
from time import sleep
from Crypto.PublicKey import RSA

# Captures Images 
def captureImage(path,total_images=1,camera=0):
    image_names = []
    cap = cv2.VideoCapture(camera)

    if not cap.isOpened():
        raise Exception("Cannot open camera")

    ret,frame = cap.read()
    sleep((1 + 1/(randbits(16)+0.000001))) #Waits for the cam to open.
    for i in range(total_images):
        if not ret:
            raise Exception("Can't receive frame (stream end?). Exiting ...")
        else:
            ret,frame = cap.read()
            # Save the captured image
            image_name = path + sep + str(i) + ".bmp"
            image_names.append(image_name)
            cv2.imwrite(image_name, frame)
    cap.release()
    cv2.destroyAllWindows()
    return image_names


class NoiseRandom():
    
    def __init__(self,path:str,strength=1,cameras=[0],disable_scramble=False,disable_delete_images=False):
        self.disable_scramble = disable_scramble
        self.disable_delete_images = disable_delete_images
        self.path = path
        self.images = []
        self.cameras = cameras
        self.strength = strength
        if(self.strength<1):
            self.strength = 1
        
    def randomInt(self,get_bytes=False)->int|bytes:
        self.__captureImages()
        with open(choice(self.images), "rb") as f:
            data = f.read()
            f.close()
        if(not self.disable_delete_images):
            self.__deleteImages()
        starting_image_index = 0 #data.find(b"\xFF\xDA")
        ending_image_index = -1 #data.find(b"\xFF\xD9")
        data = self.__scramble(data[starting_image_index+1:ending_image_index])
        if(get_bytes):
            return data
        sys.set_int_max_str_digits(len(data) * 3)
        return  int.from_bytes(data,"big",signed=False)
    
    def randomBytes(self,total_bytes:int,get_bytes=True) -> int|bytes:
        if(total_bytes<=0):
            raise ValueError("The value of total_bytes can't be 0 or less.")
        random_pool = self.randomInt(True)
        selected_bytes = [choice(random_pool) & 0xFF for _ in range(total_bytes)]
        selected_bytes[0] |= (1<<7)
        if(get_bytes):
            return bytes(selected_bytes)
        return int.from_bytes(selected_bytes,"big",signed=False)
    
    def randomPrime(self,total_bytes:int) -> int:
        if(total_bytes<=0):
            raise ValueError("The value of total_bytes can't be 0 or less.")
        random_pool = self.randomInt(True)
        selected_bytes = [choice(random_pool) & 0xFF for _ in range(total_bytes)]
        selected_bytes[0] |= (1<<7)
        prime_number = int.from_bytes(selected_bytes,"big",signed=False)
        while(not isprime(prime_number)):
            selected_bytes = [choice(random_pool) & 0xFF for _ in range(total_bytes)]
            selected_bytes[0] |= (1<<7)
            prime_number = int.from_bytes(selected_bytes,"big",signed=False)
        return prime_number
    
    def generate_rsa_keys(self,p, q, e=65537, private_key_name="private.pem", public_key_name="public.pem"):
        # Compute modulus
        n = p * q
        phi = (p - 1) * (q - 1)

        # Ensure e and phi are coprime
        from math import gcd
        if gcd(e, phi) != 1:
            raise ValueError("e and phi(n) are not coprime. Choose another prime pair or e.")

        # Compute private exponent d
        d = pow(e, -1, phi)

        # Construct the RSA key manually
        key = RSA.construct((n, e, d, p, q))

        # Export keys in PEM format
        private_pem = key.export_key()
        public_pem = key.publickey().export_key()

        with open(private_key_name, "wb") as pkey:
            pkey.write(private_pem)
            pkey.close()
        with open(public_key_name, "wb") as pkey:
            pkey.write(public_pem)
            pkey.close()

    def random1024(self)->int:
        return self.randomBytes(1024//8,False)
    
    def random2048(self)->int:
        return self.randomBytes(2048//8,False)

    def random4096(self)->int:
        return self.randomBytes(4096//8,False)
    
    def randomPrime1024(self):
        return self.randomPrime(1024//8)

    def randomPrime2048(self):
        return self.randomPrime(2048//8)
    
    def randomPrime4096(self):
        return self.randomPrime(4096//8)
              
    def __deleteImages(self) -> None:
        if(self.disable_delete_images):
            return None
        for image_path in self.images:
            remove(image_path)
        self.images.clear()

    def __captureImages(self) -> None:
        self.images = self.images + captureImage(self.path,self.strength,camera=choice(self.cameras))
        
    def __scramble(self,data):
        byte_list = list(data)
        data_size = len(byte_list)
        scrambled_data = b""
        for i in range(data_size*3):
            p1 = randbits(4*8) % data_size
            p2 = randbits(4*8) % data_size

            byte_list[p1], byte_list[p2] = byte_list[p2], byte_list[p1]

        for byte in byte_list:
            scrambled_data += byte.to_bytes()
        
        return scrambled_data