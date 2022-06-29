import face_recognition
from imutils.video import VideoStream
import numpy as np
import argparse
import imutils
import time
import cv2
import datetime
import json

from web3 import Web3,HTTPProvider

d=datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
time.sleep(2.0)
img_counter = 0
path = "C:\\mainproject\\Election\static\\student_images\\"

# truffle development blockchain address
blockchain_address = 'http://127.0.0.1:7545'
# Client instance to interact with the blockchain
web3 = Web3(HTTPProvider(blockchain_address))
# Set the default account (so we don't need to set the "from" for every transaction call)
web3.eth.defaultAccount = web3.eth.accounts[0]

compiled_contract_path = 'C:\\mainproject\\Election\\node_modules\\.bin\\build\\contracts\\CollegeElection.json'
# Deployed contract address (see `migrate` command output: `contract address`)
deployed_contract_address = '0x6b678C90D38b07a5d29Edc1951B190D583b94D91'

class cam :
    def camera(self):

        while True:
            # grab the frame from the threaded video stream and resize it
            # to have a maximum width of 400 pixels
            frame = vs.read()
            frame = imutils.resize(frame,width=400)
            imgname = path+"h3.jpg".format(img_counter)
            cv2.imwrite(imgname, frame)

            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF

            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break


        cv2.destroyAllWindows()
        vs.stop()

        from PIL import Image
        from DBConnection import Db
        db = Db()
       # res = db.select("select * from student_details")
        with open(compiled_contract_path) as file:
            contract_json = json.load(file)  # load contract info as JSON
            contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
        contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
        blocknumber = web3.eth.get_block_number()
        print(blocknumber)

        regno1 = []
        res1 = []
        for i in range(blocknumber, 222, -1):
            a = web3.eth.get_transaction_by_block(i, 0)
            decoded_input = contract.decode_function_input(a['input'])
            print("aaaa",decoded_input[0])

            res = {}
            if str(decoded_input[0]) =='<Function addStudent(string,string,string,string,string)>':
                res['name'] = decoded_input[1]['_Name']
                res['regno'] = decoded_input[1]['_Regno']
                res['dept'] = decoded_input[1]['_Dept']
                res['course'] = decoded_input[1]['_Course']
                res['image'] = decoded_input[1]['_Image']
                res1.append(res)
                regno1.append(decoded_input[1]['_Regno'])

        # for i in res1:
        #     print(i['image'])
        print('eeffgg',res1)
        known_faces = []
        userids = []
        person_name = []
        identified = []


        if res1 is not None:
            for result in res1:
                picc = result["image"]
                pname = picc.split("/")
                img = path + pname[len(pname) - 1]
                print(img)
                b_img = face_recognition.load_image_file(img)
                b_imgs = face_recognition.face_encodings(b_img)[0]
                known_faces.append(b_imgs)
                userids.append(result["regno"])
                person_name.append(result["name"])
                print(str(len(known_faces)) + "done")

            # unknown_image = face_recognition.load_image_file(staticpath + "a_270.jpg")
            unknown_image = face_recognition.load_image_file(path + "h3.jpg")
            unkonownpersons = face_recognition.face_encodings(unknown_image)
            print(len(unkonownpersons), "llllllllllllllllllllllll")
            try:
                if len(unkonownpersons) > 0:

                        for i in range(0, len(unkonownpersons)):
                            h = unkonownpersons[i]

                            red = face_recognition.compare_faces(known_faces, h, tolerance=0.45)  # true,false,false,false]
                            print(red)
                            for i in range(0, len(red)):
                                if red[i] == True:
                                    identified.append(userids[i])
                        print(identified,"kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")
                        print(len(identified))
                        if len(identified) > 0:

                            l=identified
                            for i in l:
                                with open(compiled_contract_path) as file:
                                    contract_json = json.load(file)  # load contract info as JSON
                                    contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
                                contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
                                blocknumber = web3.eth.get_block_number()
                                print(blocknumber)

                                regno2 = []
                                uname = []
                                pswd = []
                                res2 = []
                                for i in range(blocknumber, 222, -1):
                                    a = web3.eth.get_transaction_by_block(i, 0)
                                    decoded_input = contract.decode_function_input(a['input'])
                                    print(decoded_input)
                                    res = {}
                                    if str(decoded_input[0])=='<Function addlogin(string,string,string)>':

                                        res['name'] = decoded_input[1]['_name']
                                        res['regno'] = decoded_input[1]['_regno']
                                        res['pswd'] = decoded_input[1]['_pswd']

                                        res2.append(res)
                                        regno2.append(decoded_input[1]['_regno'])
                                        uname.append(decoded_input[1]['_name'])
                                        pswd.append(decoded_input[1]['_pswd'])
                                print('aabbcc',res2)

                                # print("eeeeeeeeee",res1['regno'])
                                # print("qqqqqqqqq",res2[0]['regno'])


                                print("regno1",regno1,"reqno2",regno2)

                                for i in range(len(regno1)):
                                    if str(regno1[i]) == str(identified[0]):
                                        return uname[i],pswd[i],regno1[i]
                                else:
                                    print('incorrect datas')

                                print(len(identified))

                        else:
                             print("invalid user")
                             return "none","none","none"


            except Exception as e:
                return "invalid person"


