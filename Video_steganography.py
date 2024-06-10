import cv2
import os
import numpy as np
import tkinter as tk
from tkinter import filedialog
from termcolor import colored
from pyfiglet import figlet_format

def msgtobinary(msg):
    if type(msg) == str:
        result = ''.join([format(ord(i), "08b") for i in msg])
    elif type(msg) == bytes or type(msg) == np.ndarray:
        result = [format(i, "08b") for i in msg]
    elif type(msg) == int or type(msg) == np.uint8:
        result = format(msg, "08b")
    else:
        raise TypeError("Input type is not supported in this function")
    return result

def KSA(key):
    key_length = len(key)
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % key_length]) % 256
        S[i], S[j] = S[j], S[i]
    return S

def PRGA(S, n):
    i = 0
    j = 0
    key = []
    while n > 0:
        n = n - 1
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        K = S[(S[i] + S[j]) % 256]
        key.append(K)
    return key

def preparing_key_array(s):
    return [ord(c) for c in s]

def encryption(plaintext, key):
    key = preparing_key_array(key)
    S = KSA(key)
    keystream = np.array(PRGA(S, len(plaintext)))
    plaintext = np.array([ord(i) for i in plaintext])
    cipher = keystream ^ plaintext
    ctext = ''.join([chr(c) for c in cipher])
    return ctext

def decryption(ciphertext, key):
    key = preparing_key_array(key)
    S = KSA(key)
    keystream = np.array(PRGA(S, len(ciphertext)))
    ciphertext = np.array([ord(i) for i in ciphertext])
    decoded = keystream ^ ciphertext
    dtext = ''.join([chr(c) for c in decoded])
    return dtext

def embed(frame, data, key):
    data = encryption(data, key)
    if len(data) == 0:
        raise ValueError('Data entered to be encoded is empty')
    data += '*^*^*'
    binary_data = msgtobinary(data)
    length_data = len(binary_data)
    index_data = 0
    for i in frame:
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
    return frame

def extract(frame, key):
    data_binary = ""
    final_decoded_msg = ""
    for i in frame:
        for pixel in i:
            r, g, b = msgtobinary(pixel)
            data_binary += r[-1]
            data_binary += g[-1]
            data_binary += b[-1]
            total_bytes = [data_binary[i: i + 8] for i in range(0, len(data_binary), 8)]
            decoded_data = ""
            for byte in total_bytes:
                decoded_data += chr(int(byte, 2))
                if decoded_data[-5:] == "*^*^*":
                    for i in range(len(decoded_data) - 5):
                        final_decoded_msg += decoded_data[i]
                    final_decoded_msg = decryption(final_decoded_msg, key)
                    print("\n\nThe Encoded data which was hidden in the Video was :-- ", final_decoded_msg)
                    return

def decode_vid_data(frame_, key):
    root = tk.Tk()
    root.withdraw()
    print("\tSelect the video")
    root.attributes('-alpha', 0.0)
    root.attributes('-topmost', True)
    video_path = filedialog.askopenfilename(title="Select a video to decode the message")

    if video_path:
        cap = cv2.VideoCapture(video_path)
        max_frame = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            max_frame += 1
        print("Total number of Frames in selected Video:", max_frame)
        print("Enter the secret frame number from where you want to extract data: ", end='')
        n = int(input())
        vidcap = cv2.VideoCapture(video_path)
        frame_number = 0
        while vidcap.isOpened():
            frame_number += 1
            ret, frame = vidcap.read()
            if not ret:
                break
            if frame_number == n:
                extract(frame_, key)
                return

def encode_vid_data():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-alpha', 0.0)
    root.attributes('-topmost', True)
    video_path = filedialog.askopenfilename(title="Select a video to embed message")

    if video_path:
        cap = cv2.VideoCapture(video_path)
        vidcap = cv2.VideoCapture(video_path)    
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        frame_width = int(vidcap.get(3))
        frame_height = int(vidcap.get(4))

        size = (frame_width, frame_height)
        out = cv2.VideoWriter('temp.mp4', fourcc, 25.0, size)
        max_frame = 0
        print("\n\tReading video frames, Wait...\n")
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            max_frame += 1
        cap.release()
        print("Total number of Frames in selected Video: ", max_frame)
        print("Enter the frame number where you want to embed data: ", end='')
        n = int(input())
        frame_number = 0
        while vidcap.isOpened():
            frame_number += 1
            ret, frame = vidcap.read()
            if not ret:
                break
            if frame_number == n:
                data = input("Enter the data to be embedded in the video: ")
                key = input("Enter the encryption key: ")
                change_frame_with = embed(frame, data, key)
                frame_ = change_frame_with
                frame = change_frame_with
            out.write(frame)
        
        out.release()
        print("\nEncoded the data successfully in the video file.")
        print("\nEnter the filename to save the embedded frame (without extension): ", end='')
        filename = input()
        
        result_dir = 'C:/Users/jagat/Downloads/Project stegonography/Steganography-Tools/Result_files'
        os.makedirs(result_dir, exist_ok=True)
        
        output_filename = os.path.join(result_dir, f'{filename}_embedded.mp4')
        frame_filename = os.path.join(result_dir, f'{filename}_embedded_frame.npy')

        os.rename('temp.mp4', output_filename)
        np.save(frame_filename, frame_)

        print(f"\nEncoded video saved as {output_filename}")
        print(f"Secret frame saved as {frame_filename}")
        return frame_
    else: 
        print("\n\tFile opening cancelled by user\n")

def vid_steg():
    print(colored(figlet_format("Hidden Layers"), color='red'))
    while True:
        print("\nSELECT THE VIDEO STEGANOGRAPHY OPERATION\n") 
        print("1. Encode the Text message")  
        print("2. Decode the Text message")  
        print("3. Exit")  
        choice1 = int(input("Enter the Choice: "))   
        if choice1 == 1:
            print("\tSelect the video file")
            a = encode_vid_data()
        elif choice1 == 2:
            keys = input("\tTell me that secret key: ")
            root = tk.Tk()
            root.attributes('-alpha', 0.0)
            root.attributes('-topmost', True)
            a_path = filedialog.askopenfilename(title="Select the secret frame <.npy_file> ")
            with open(a_path, 'rb') as file:
                a = np.load(file, allow_pickle=True)
            decode_vid_data(a, keys)
        elif choice1 == 3:
            break
        else:
            print("Incorrect Choice")
        print("\n")

if __name__ == "__main__":
    vid_steg()
