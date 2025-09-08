from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
import os
from django.core.files.storage import FileSystemStorage
import pymysql
from PIL import Image
import cv2
import base64
import numpy as np
import ftplib
import urllib 

global username, password, contact, gender, email, address, finger, finger_image

face_detection = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
recognizer = cv2.face_LBPHFaceRecognizer.create()

def DownloadFileAction(request):
    if request.method == 'GET':
        global username
        img = request.GET.get('fname', False)

        infile = open("SecureBiometricApp/static/files/"+img, 'rb')
        data = infile.read()
        infile.close()
        

        response = HttpResponse(data, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=%s' % img
        return response

def Download(request):
    if request.method == 'GET':
        global username
        font = '<font size="" color="black">'
        output = '<table border="1" align="center" width="100%"><tr><th>'+font+'Username</th><td>'+font+'Filename</th><td>'+font+'Download File</th></tr>'
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'securebiometric',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM upload")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username:
                    output+="<tr><td>"+font+row[0]+"</td><td>"+font+row[1]+"</td>"
                    output+='<td><a href=\'DownloadFileAction?fname='+row[1]+'\'><font size=3 color=black>Click Here</font></a></td></tr>'
        context= {'data':output}
        return render(request, "Download.html", context)

def UploadAction(request):
    if request.method == 'POST':
        global username
        file = request.FILES['t1']
        filename = request.FILES['t1'].name
        fs = FileSystemStorage()
        fs.save('SecureBiometricApp/static/files/'+filename, file)
        ftp = ftplib.FTP_TLS("ftp.drivehq.com")
        ftp.login("cdaproject", "Offenburg965#")
        ftp.prot_p()
        file = open('SecureBiometricApp/static/files/'+filename, "rb")
        ftp.storbinary("STOR "+filename, file)
        file.close()
        ftp.close()
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'securebiometric',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "INSERT INTO upload(username,filename) VALUES('"+str(username)+"','"+filename+"')"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        print(db_cursor.rowcount, "Record Inserted")
        if db_cursor.rowcount == 1:
            output = filename+' saved at driveHQ Cloud'
        context= {'data':output}
        return render(request, 'Upload.html', context)

def Upload(request):
    if request.method == 'GET':
       return render(request, 'Upload.html', {}) 

def ValidateFace(request):
    if request.method == 'GET':
       return render(request, 'ValidateFace.html', {}) 

def Login(request):
    if request.method == 'GET':
       return render(request, 'UserLogin.html', {})  

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def Signup(request):
    if request.method == 'GET':
       return render(request, 'Signup.html', {})
    
def getUserImages():
    names = []
    ids = []
    faces = []
    dataset = "SecureBiometricApp/static/profile"
    count = 0
    for root, dirs, directory in os.walk(dataset):
        for j in range(len(directory)):
            pilImage = Image.open(root+"/"+directory[j]).convert('L')
            imageNp = np.array(pilImage,'uint8')
            name = os.path.splitext(directory[j])[0]
            names.append(name)
            faces.append(imageNp)
            ids.append(count)
            count = count + 1
    print(str(names)+" "+str(ids))        
    return names, ids, faces        


def getName(predict, ids, names):
    name = "Unable to get name"
    for i in range(len(ids)):
        if ids[i] == predict:
            name = names[i]
            break
    return name

def ValidateFaceAction(request):
    if request.method == 'POST':
        global username
        status = "unable to predict user"
        img = cv2.imread('SecureBiometricApp/static/photo/test.png')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_component = None
        faces = face_detection.detectMultiScale(img,scaleFactor=1.1,minNeighbors=5,minSize=(30,30),flags=cv2.CASCADE_SCALE_IMAGE)
        status = "Unable to predict.Please retry"
        #for (x, y, w, h) in faces:
        #    face_component = gray[y:y+h, x:x+w]
        faces = sorted(faces, reverse=True,key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))[0]
        (fX, fY, fW, fH) = faces
        face_component = gray[fY:fY + fH, fX:fX + fW]
        if face_component is not None:
            names, ids, faces = getUserImages()
            recognizer.train(faces, np.asarray(ids))
            predict, conf = recognizer.predict(face_component)
            print(str(predict)+" === "+str(conf))
            if(conf < 80):
                validate_user = getName(predict, ids, names)
                print(str(validate_user)+" "+str(username))
                if validate_user == username:
                    status = "success"
        else:
            status = "Unable to detect face"
        if status == "success":
            context= {'data':"Welcome "+username+" Both finger & face successfully matched"}
            return render(request, 'UserScreen.html', context)
        else:
            context= {'data':status+". Please try again"}
            return render(request, 'ValidateFace.html', context)

def UserLoginAction(request):
    global username, finger
    if request.method == 'POST':
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        finger_image = request.FILES['t3'].read()
        index = 0
        msg = "Login or finger matching failed"
        finger = ""
        page = 'UserLogin.html'
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'securebiometric',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select username,password,finger FROM signup")
            rows = cur.fetchall()
            for row in rows:
                print(str(row[2]))
                if row[0] == username and password == row[1]:
                    finger = row[2]
                    index = 1
                    break                
        if index == 1:
            with open('SecureBiometricApp/static/finger/'+finger, "rb") as file:
                content = file.read()
            file.close()
            if content == finger_image:
                msg = "Login & Finger Matching Successful"
                page = 'ValidateFace.html'
        context= {'data':msg}
        return render(request, page, context)
        
def SignupAction(request):
    if request.method == 'POST':
        global username, password, contact, gender, email, address, finger, finger_image
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        contact = request.POST.get('t3', False)
        gender = request.POST.get('t4', False)
        email = request.POST.get('t5', False)
        address = request.POST.get('t6', False)
        finger_image = request.FILES['t7']
        finger = request.FILES['t7'].name        
        output = "none"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'securebiometric',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select username FROM signup")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username:
                    output = username+" Username already exists"
                    break
        if output == 'none':
            fs = FileSystemStorage()
            filename = fs.save('SecureBiometricApp/static/finger/'+finger, finger_image)
            context= {'data':username+" please capture your face"}
            return render(request, 'CaptureFace.html', context)
        else:
            context= {'data':username+" already exists"}
            return render(request, 'Signup.html', context)
      
def WebCam(request):
    if request.method == 'GET':
        data = str(request)
        formats, imgstr = data.split(';base64,')
        imgstr = imgstr[0:(len(imgstr)-2)]
        data = base64.b64decode(imgstr)
        print(data)
        if os.path.exists("SecureBiometricApp/static/photo/test.png"):
            os.remove("SecureBiometricApp/static/photo/test.png")
        with open('SecureBiometricApp/static/photo/test.png', 'wb') as f:
            f.write(data)
        f.close()
        context= {'data':"done"}
        return HttpResponse("Image saved")

def CaptureFaceAction(request):
    if request.method == 'POST':
        global username, password, contact, gender, email, address, finger
        img = cv2.imread('SecureBiometricApp/static/photo/test.png')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_component = None
        faces = face_detection.detectMultiScale(gray, 1.3,5)
        for (x, y, w, h) in faces:
            face_component = img[y:y+h, x:x+w]
        if face_component is not None:
            cv2.imwrite('SecureBiometricApp/static/profile/'+username+'.png',face_component)
            db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'securebiometric',charset='utf8')
            db_cursor = db_connection.cursor()
            student_sql_query = "INSERT INTO signup(username,password,contact_no,gender,email,address,finger) VALUES('"+username+"','"+password+"','"+contact+"','"+gender+"','"+email+"','"+address+"','"+finger+"')"
            db_cursor.execute(student_sql_query)
            db_connection.commit()
            print(db_cursor.rowcount, "Record Inserted")
            if db_cursor.rowcount == 1:
                context= {'data':'Signup Process Completed'}
                return render(request, 'Signup.html', context)
            else:
                context= {'data':'Unable to detect face. Please retry'}
                return render(request, 'CaptureFace.html', context)    

