#!/usr/bin/env python
# coding: utf-8

import numpy as np
import os
import cv2
from matplotlib import pyplot as plt
import wave

# Text Steganography
def txt_encode(text, filetext):
    l = len(text)
    add = ''
    for i in range(l):
        t = ord(text[i])
        if 32 <= t <= 64:
            t1 = t + 48
            t2 = t1 ^ 170  # 170: 10101010
            res = bin(t2)[2:].zfill(8)
            add += "0011" + res
        else:
            t1 = t - 48
            t2 = t1 ^ 170
            res = bin(t2)[2:].zfill(8)
            add += "0110" + res
    res1 = add + "111111111111"
    print("The string after binary conversion applying all the transformation: " + res1)
    length = len(res1)
    print("Length of binary after conversion: ", length)
    HM_SK = ""
    ZWC = {"00": u'\u200C', "01": u'\u202C', "11": u'\u202D', "10": u'\u200E'}
    
    with open(filetext, "r") as file1:
        nameoffile = input("\nEnter the name of the Stego file after Encoding (with extension): ")
        with open(nameoffile, "w", encoding="utf-8") as file3:
            words = file1.read().split()
            i = 0
            while i < len(res1):
                s = words[i // 12]
                HM_SK = ""
                for j in range(0, 12, 2):
                    x = res1[i + j] + res1[i + j + 1]
                    HM_SK += ZWC[x]
                s1 = s + HM_SK
                file3.write(s1 + " ")
                i += 12
            for t in range(len(res1) // 12, len(words)):
                file3.write(words[t] + " ")
    print("\nStego file has been successfully generated")

def encode_txt_data():
    while True:
        t = input("Enter text file name with extension/path: ")
        if os.path.isfile(t):
            break
        else:
            print("File not found! Please try again.\n")
    
    with open(t, "r") as file1:
        count2 = sum(len(line.split()) for line in file1)
    
    bt = count2
    print("Maximum number of words that can be inserted: ", bt // 6)
    text1 = input("\nEnter data to be encoded: ")
    if len(text1) <= bt:
        print("\nInput message can be hidden in the cover file\n")
        txt_encode(text1, t)
    else:
        print("\nString is too big, please reduce string size")
        encode_txt_data()

def BinaryToDecimal(binary):
    return int(binary, 2)

def decode_txt_data():
    ZWC_reverse = {u'\u200C': "00", u'\u202C': "01", u'\u202D': "11", u'\u200E': "10"}
    stego = input("\nPlease enter the stego file name (with extension) to decode the message: ")
    
    with open(stego, "r", encoding="utf-8") as file4:
        temp = ''
        for line in file4:
            for word in line.split():
                T1 = word
                binary_extract = ""
                for letter in T1:
                    if letter in ZWC_reverse:
                        binary_extract += ZWC_reverse[letter]
                if binary_extract == "111111111111":
                    break
                else:
                    temp += binary_extract
    
    print("\nEncrypted message presented in code bits:", temp)
    lengthd = len(temp)
    print("\nLength of encoded bits: ", lengthd)
    
    final = ''
    for i in range(0, len(temp), 12):
        t3 = temp[i:i+4]
        t4 = temp[i+4:i+12]
        decimal_data = BinaryToDecimal(t4)
        if t3 == '0110':
            final += chr((decimal_data ^ 170) + 48)
        elif t3 == '0011':
            final += chr((decimal_data ^ 170) - 48)
    
    print("\nMessage after decoding from the stego file: ", final)

def txt_steg():
    while True:
        print("\n\t\tTEXT STEGANOGRAPHY OPERATIONS") 
        print("1. Encode the Text message")  
        print("2. Decode the Text message")  
        print("3. Exit")  
        choice1 = int(input("Enter the Choice: "))   
        if choice1 == 1:
            encode_txt_data()
        elif choice1 == 2:
            decode_txt_data()
        elif choice1 == 3:
            break
        else:
            print("Incorrect Choice")
        print("\n")

# Image Steganography
def msgtobinary(msg):
    if isinstance(msg, str):
        return ''.join([format(ord(i), "08b") for i in msg])
    elif isinstance(msg, bytes) or isinstance(msg, np.ndarray):
        return [format(i, "08b") for i in msg]
    elif isinstance(msg, int) or isinstance(msg, np.uint8):
        return format(msg, "08b")
    else:
        raise TypeError("Input type is not supported")

def encode_img_data(img):
    data = input("\nEnter the data to be Encoded in Image: ")
    if not data:
        raise ValueError('Data entered to be encoded is empty')
    
    nameoffile = input("\nEnter the name of the New Image (Stego Image) after Encoding (with extension): ")
    no_of_bytes = (img.shape[0] * img.shape[1] * 3) // 8
    print("\nMaximum bytes to encode in Image:", no_of_bytes)
    
    if len(data) > no_of_bytes:
        raise ValueError("Insufficient bytes Error, Need Bigger Image or give Less Data!")
    
    data += '*^*^*'    
    binary_data = msgtobinary(data)
    length_data = len(binary_data)
    print("\nThe Length of Binary data", length_data)
    
    index_data = 0
    for i in img:
        for pixel in i:
            r, g, b = msgtobinary(pixel)
            if index_data < length_data:
                pixel[0] = int(r[:-1] + binary_data[index_data], 2) 
                index_data += 1
            if index_data < length_data:
                pixel[1] = int(g[:-1] + binary_data[index_data], 2) 
                index_data += 1
            if index_data < length_data:
                pixel[2] = int(b[:-1] + binary_data[index_data], 2) 
                index_data += 1
            if index_data >= length_data:
                break
    
    cv2.imwrite(nameoffile, img)
    print("\nEncoded the data successfully in the Image and the image is saved as", nameoffile)

def decode_img_data(img):
    data_binary = ""
    for i in img:
        for pixel in i:
            r, g, b = msgtobinary(pixel) 
            data_binary += r[-1]  
            data_binary += g[-1]  
            data_binary += b[-1]  
            total_bytes = [data_binary[i: i+8] for i in range(0, len(data_binary), 8)]
            decoded_data = ""
            for byte in total_bytes:
                decoded_data += chr(int(byte, 2))
                if decoded_data[-5:] == "*^*^*":
                    print("\nThe Encoded data hidden in the Image was:", decoded_data[:-5])
                    return 

def img_steg():
    while True:
        print("\n\t\tIMAGE STEGANOGRAPHY OPERATIONS\n") 
        print("1. Encode the Text message") 
        print("2. Decode the Text message") 
        print("3. Exit")  
        choice1 = int(input("Enter the Choice: "))   
        if choice1 == 1:
            i = input("Enter the image file name (with extension): ").strip()
            image = cv2.imread(i)
            encode_img_data(image)
        elif choice1 == 2:
            i = input("Enter the Image you need to Decode to get the Secret message: ").strip()
            image = cv2.imread(i)
            decode_img_data(image)
        elif choice1 == 3:
            break
        else:
            print("Incorrect Choice")
        print("\n")

# Audio Steganography
def encode_aud_data():
    nameoffile = input("Enter name of the file (with extension): ")
    song = wave.open(nameoffile, mode='rb')
    nframes = song.getnframes()
    frames = song.readframes(nframes)
    frame_bytes = bytearray(list(frames))
    
    data = input("\nEnter the secret message: ")
    data += '*^*^*'
    
    res = ''.join(format(i, '08b') for i in bytearray(data, encoding='utf-8'))
    length = len(res)
    print("\nThe string after binary conversion: " + res)
    print("\nLength of binary after conversion: ", length)
    
    j = 0
    for i in range(len(res)):
        frame_bytes[j] = (frame_bytes[j] & 254) | int(res[i])
        j += 1
    
    frame_modified = bytes(frame_bytes)
    
    stegofile = input("\nEnter name of the stego file (with extension): ")
    with wave.open(stegofile, 'wb') as fd:
        fd.setparams(song.getparams())
        fd.writeframes(frame_modified)
    
    print("\nEncoded the data successfully in the audio file.")
    song.close()

def decode_aud_data():
    nameoffile = input("Enter name of the file to be decoded: ")
    song = wave.open(nameoffile, mode='rb')
    nframes = song.getnframes()
    frames = song.readframes(nframes)
    frame_bytes = bytearray(list(frames))
    
    extracted = ""
    for i in range(len(frame_bytes)):
        extracted += str(frame_bytes[i] & 1)
    
    total_bytes = [extracted[i:i+8] for i in range(0, len(extracted), 8)]
    decoded_data = ""
    for byte in total_bytes:
        decoded_data += chr(int(byte, 2))
        if decoded_data[-5:] == "*^*^*":
            print("The Encoded data was:", decoded_data[:-5])
            break

def aud_steg():
    while True:
        print("\n\t\tAUDIO STEGANOGRAPHY OPERATIONS") 
        print("1. Encode the Text message")  
        print("2. Decode the Text message")  
        print("3. Exit")  
        choice1 = int(input("Enter the Choice: "))   
        if choice1 == 1:
            encode_aud_data()
        elif choice1 == 2:
            decode_aud_data()
        elif choice1 == 3:
            break
        else:
            print("Incorrect Choice")
        print("\n")

# Main Function
def main():
    print("\t\t      STEGANOGRAPHY")   
    while True:  
        print("\n\t\t\tMAIN MENU\n")  
        print("1. IMAGE STEGANOGRAPHY {Hiding Text in Image cover file}")  
        print("2. TEXT STEGANOGRAPHY {Hiding Text in Text cover file}")  
        print("3. AUDIO STEGANOGRAPHY {Hiding Text in Audio cover file}")
        print("4. Exit\n")  
        choice1 = int(input("Enter the Choice: "))   
        if choice1 == 1: 
            img_steg()
        elif choice1 == 2:
            txt_steg()
        elif choice1 == 3:
            aud_steg()
        elif choice1 == 4:
            break
        else:
            print("Incorrect Choice")
        print("\n\n")

if __name__ == "__main__":
    main()
