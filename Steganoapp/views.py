from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from Steganography import settings
from .models import *
import numpy as np
import math
from PIL import Image
import os
import uuid


from PIL import Image
import numpy as np
import math

def EmbPixels(x, y):
    x -= 2
    y -= 2
    if x < 0 or y < 0:
        return 0
    return (x * y + (x & 1) * (y & 1)) >> 1

def Embed_Text(Cover, txt, Stego, N=0, Wrap=False):
    # Load and prepare image
    img = Image.open(Cover)
    
    # Convert to RGB if needed (handles RGBA, L, P, etc.)
    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGB')
    elif img.mode == 'RGBA':
        img = img.convert('RGB')  # Remove alpha channel

    array = np.array(img, dtype=np.int16)
    width, height = img.size
    num_pix = EmbPixels(height, width)

    if num_pix == 0:
        raise ValueError("Image too small to embed any data.")

    # Calculate embedding depth N if not provided
    if N <= 0:
        N = len(txt) * 7 // (num_pix * 3) + (0 if (len(txt) * 7) % (num_pix * 3) == 0 else 1)
        if Wrap and N == 1:
            N = 2
    elif N > 7:
        raise ValueError("The embedding depth must be a positive integer less than eight.")
    elif len(txt) * 7 > num_pix * N * 3:
        raise ValueError("Text too large for this image and embedding depth.")

    # Convert text to binary string
    msg = ""
    for i in txt:
        if ord(i) > 127:
            raise ValueError("Only ASCII characters are supported.")
        msg += bin(ord(i))[2:].zfill(7)

    # Padding or wrapping logic
    r = N - len(msg) % N
    r = 0 if r == N else r

    if Wrap:
        msg *= N // math.gcd(N, r)
        r = len(msg) % 7
    else:
        msg += "0" * r

    L = [msg[i:i+N] for i in range(0, len(msg), N)]

    # Embed parameters in pixel (0,0)
    for k in range(3):
        array[0][0][k] = (array[1][0][k] + array[0][1][k]) // 2
    array[0][0][0] += N
    array[0][0][1] += r

    shift = (1 << (N - 1))
    index = 0
    flag = False

    for i in range(1, height - 1):
        for j in range(1, width - 1):
            if (i + j) & 1 == 0:
                for k in range(3):
                    avg = (array[i - 1][j][k] + array[i + 1][j][k] + array[i][j - 1][k] + array[i][j + 1][k]) // 4
                    new_val = avg - shift
                    if index < len(L):
                        new_val += int(L[index], 2)
                        index = (index + 1) % len(L) if Wrap else index + 1
                    else:
                        new_val -= 1
                        flag = True
                    array[i][j][k] = min(255, max(0, new_val))
                if flag:
                    break
        if flag:
            break

    array = array.astype(np.uint8)
    img = Image.fromarray(array)
    img.save(Stego)
    print(f"✅ Text embedded successfully in: {Stego}")




def Extract_Text(Stego, Cover):
        img = Image.open(Stego).convert('RGB')   
        array = np.array(img, dtype=np.int16)
        width, height = img.size
        N = array[0][0][0] - math.ceil((array[0][1][0] + array[1][0][0]) // 2)
        r = array[0][0][1] - math.ceil((array[0][1][1] + array[1][0][1]) // 2)
        msg = ""
        shift = 1 << (N - 1)
        flag = 0
        for i in range(1, height - 1):
            for j in range(1, width - 1):
                if (i + j) % 2 == 0:
                    for k in range(3):
                        cell = math.ceil((array[i-1][j][k] + array[i+1][j][k] + array[i][j-1][k] + array[i][j+1][k]) // 4)
                        val = array[i][j][k] - cell + shift
                        array[i][j][k] = cell
                        if val == (-1):
                            flag = 1
                            break
                        msg += bin(val)[2:].zfill(N)
                if flag:
                    break
            if flag:
                break
        array = array.astype(np.uint8)
        img = Image.fromarray(array)
        img.show()
        img.save(Cover)
        if r:
            msg = msg[:-r]
        L = [msg[i:i+7] for i in range(0, len(msg), 7)]
        if len(L[-1]) < 7:
            L.pop()
        str = ""
        for i in L:
            str += chr(int(i, 2))
        print(str)
        return str

def index(request):
    msg = ""
    if request.POST:
        email = request.POST['email']
        password = request.POST['password']
        user_check = User.objects.filter(email=email).first()
        if user_check:
            if user_check.check_password(password):
                if user_check.is_active:
                    request.session['uid'] = user_check.id
                    if user_check.is_superuser:
                        return redirect('/adminhome')
                    return redirect('/userhome')
                else:
                    msg="User is restricted by admin"
            else:
                msg = "Incorrect Password"
        else:
            msg = "User not Found"
    return render(request, 'index.html', {'msg': msg})

def registration(request):
    msg = ""
    if request.POST:
        name = request.POST['name']
        number = request.POST['phonenumber']
        mail = request.POST['mail']
        age = request.POST['age']
        password = request.POST['password']
        image = request.FILES['image']
        try:
            user = User.objects.create_user(username=mail, password=password, email=mail, is_active=True)
            Registeration.objects.create(name=name, number=number, mail=mail, age=age, image=image, user=user)
            msg = 'Registration Successful'
        except:
            msg = 'User Already Exists'
    return render(request, 'registration.html', {'msg': msg})

def encrypt(request):
    msg = ""
    if request.session.get('uid'):
        user = Registeration.objects.get(user_id=request.session['uid'])
        if request.POST:
            coverimage = request.FILES['coverimage']
            embedtext = request.POST['embedtext']
            uhistory=Userhistory.objects.create(stegoimage=coverimage, user=user)
            uhistory.save()
            unique_name = f"{uhistory.id}_{coverimage.name}"
            img_path = os.path.join(settings.MEDIA_ROOT, coverimage.name)
            enc_path = os.path.join(settings.MEDIA_ROOT, "enc", unique_name)
            try:
                Embed_Text(img_path, embedtext, enc_path, 2, False)
                msg = "Encryption Successful!"
                return render(request, 'encryption.html', {"encrypted_img": "enc/" + unique_name, 'msg': msg})
            except :
                msg = "⚠️ Please ensure the image meets the following requirements: it must be a PNG file, have a minimum resolution of 128×128 pixels, and the message length must be appropriate for the image size to allow successful embedding."
                return render(request, 'encryption.html', {"encrypted_img": "enc/" + unique_name, 'msg': msg})

    return render(request, 'encryption.html', {'msg': msg,'user':user})

def decrypt(request):
    text = ""
    user = Registeration.objects.get(user_id=request.session['uid'])
    if request.POST:
        stegoimage = request.FILES['stegoimage']
        dec=Decrypt.objects.create(image=stegoimage)
        dec.save()
        uniquename=os.path.join(settings.MEDIA_ROOT,dec.image.name)
        try:
            text = Extract_Text(uniquename, uniquename )
        except:
            text = "❗ Decryption Failed Because of some error in the image file"

    return render(request, 'decryption.html', {'text': text,'user':user})

def userhistory(request):
    user=Registeration.objects.get(user=request.session['uid'])
    uhistory=Userhistory.objects.filter(user=user)
    return render(request, 'userhistory.html',{'data':uhistory,'user':user})

def feedback(request):
    user =Registeration.objects.get(user=request.session['uid'])
    msg=''
    feedbacks=Feedback.objects.filter(user=user)
    if request.POST:
        feed=request.POST['feedback']
        rating=request.POST['rating']
        try:
            feedback=Feedback.objects.create(feedback=feed,star=rating,user=user)
        except:
            feedback=Feedback.objects.create(feedback=feed,star=0,user=user)
        
        feedback.save()
        msg='Feedback saved'
    return render(request, 'feedback.html',{'msg':msg,'feedbacks':feedbacks,'user':user})

def adminhome(request):
    return render(request, 'adminhome.html')

def userhome(request):
    user = Registeration.objects.get(user_id=request.session['uid'])
    return render(request, 'userhome.html',{'user':user})

def adminfeedback(request):
    feedbacks=Feedback.objects.all()
    return render(request, 'adminfeedback.html',{'feedbacks':feedbacks})

def userview(request):
    user = Registeration.objects.get(user_id=request.session['uid'])
    return render(request, 'userview.html',{'user':user})

def userlist(request):
    users = Registeration.objects.all()
    return render(request, 'userlist.html', {'users': users})

def toggleuser(request):
    user = User.objects.get(id=request.GET['id'])
    user.is_active = not user.is_active
    user.save()
    return redirect('/userlist')

def userprofile(request):
    user = Registeration.objects.get(user_id=request.session['uid'])
    return render(request,'userprofile.html',{'user':user})

