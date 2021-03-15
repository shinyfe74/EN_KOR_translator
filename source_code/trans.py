from tkinter import *
from tkinter import ttk
import numpy as np
from PIL import ImageGrab
from PIL import Image
from pytesseract import *
import re
import cv2
from googletrans import Translator as google_translator
from pypapago import Translator as papago_translator
from kakaotrans import Translator as kakao_translator

pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'

form = Tk()
form.geometry("300x250")
form.title("영한 번역기")

# 색상 설정
Blue = (255, 0, 0)
Green = (0, 255, 0)
Red = (0, 0, 255)
White = (255, 255, 255)
Black = (0, 0, 0)

point1 = (0, 0)
point2 = (0, 0)
click1 = False

translator_combo_Label = Label(form, text="--------------------번역기 선택---------------------")
translator_combo_Label_Var = StringVar()
translator_combo = ttk.Combobox(form, width=10, textvariable=translator_combo_Label_Var)
translator_combo['values'] = ('구글', '파파고','카카오')
translator_combo.set("구글")

translator_combo.current(0)



def resultform():
    global point1, point2, t_start, translator
    img = ImageGrab.grab()
    img2 = np.array(img)

    if translator_combo_Label_Var.get() == '카카오':
        translator = kakao_translator()
    elif translator_combo_Label_Var.get() == '파파고':
        translator = papago_translator()
    else:
        translator = google_translator()

    resultbox = Tk()
    resultbox.geometry("780x300")
    resultbox.title("번역 결과")
    # resultbox.wm_attributes("-transparentcolor", "white")

    left = Frame(resultbox)

    t_start = Text(left, height=20, width=68,
                   font=("arial", 15))
    t_start.pack(side=LEFT, fill=Y) 
    s_start = Scrollbar(left)
    t_start.insert(INSERT, "F2를 눌러서 번역영역을 선택해주세요.")
    s_start.pack(side=RIGHT, fill=Y)
    s_start.config(command=t_start.yview)
    t_start.config(yscrollcommand=s_start.set)
    
    left.pack(side=LEFT, fill=Y)


    def exit(event):
        resultbox.destroy()

    resultbox.bind("<Escape>", exit)
    resultbox.bind("<F2>", translate)

    resultbox.mainloop()


def translate(event):
    global point1, point2, t_start
    img = ImageGrab.grab()
    img2 = np.array(img)
    t_start.delete(1.0, 'end')

    tesserect_lang = 'eng'

    def click(event, x, y, flags, params):
        global click1, point1, point2
        if event == cv2.EVENT_LBUTTONDOWN:
            # if mousedown, store the x,y position of the mous
            click1 = True
            point1 = (x, y)
        elif event == cv2.EVENT_MOUSEMOVE and click1:
            # when dragging pressed, draw rectangle in image
            img_copy = img2.copy()
            cv2.rectangle(img_copy, point1, (x, y), (0, 0, 255), 2)
            cv2.imshow("Image", img_copy)
        elif event == cv2.EVENT_LBUTTONUP:
            # on mouseUp, create subimag
            click1 = False                        
            if (x <= point1[0]) & (y <= point1[1]) :
                point2 = point1
                point1 = (x, y)
            elif (x <= point1[0]) & (y > point1[1]):
                point2 = (point1[0], y)
                point1 = (x, point1[1])
            elif (x > point1[0]) & (y <= point1[1]):
                point2 = (x, point1[1])
                point1 = (point1[0], y)
            else:
                point2 = (x,y)
                
            sub_img = img2[point1[1]:point2[1], point1[0]:point2[0]]

            cv2.imshow("subimg", sub_img)
            setup_try = False
            cv2.destroyAllWindows()
        
    cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("Image", click)

    cv2.imshow("Image", img2)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
        # 번역 부분
    source_image = img2[point1[1]:point2[1], point1[0]:point2[0]]
    source = cv2.resize(
                source_image, (int((point2[0]-point1[0])*1.5), int((point2[1]-point1[1])*1.5)))


    translate_result = []
    temp = pytesseract.image_to_string(source, lang=tesserect_lang)
    text = ' '.join(temp.splitlines())

    if text.startswith('"'):
        text = text[1:]

    source_text = open('source.txt', 'w', encoding='utf-8')
    source_text.write(text)
    source_text.close()


    result = None

    try:
        with open('source.txt', encoding='utf-8') as f:
            line = f.readline()
            forTranslateString = line

            if translator_combo_Label_Var.get() == '카카오':
                result = translator.translate(
                forTranslateString, src='en', tgt='kr')

            elif translator_combo_Label_Var.get() == '파파고':
                result = translator.translate(
                forTranslateString, source='en', target='ko')

            else:
                print(translator.translate(
                forTranslateString, src='en', dest='ko'))
                result = translator.translate(
                forTranslateString, src='en', dest='ko').text

    except TypeError:
        result = '번역불가'
        pass

    except KeyError:
        result = '번역불가'
        pass

    t_start.insert(INSERT, result)


btn_trans = Button(form, text="번역 시작",
                        command=resultform, width=30)

btn_end = Button(form, text="번역기 프로그램 종료", command=form.destroy, width=30)

btn_trans.grid(row=0, columnspan=3, padx=30, pady=20)

btn_end.grid(row=1, columnspan=3, padx=30, pady=5)


translator_combo_Label.grid(row=4, columnspan=5)
translator_combo.grid(row=5, column=1, padx=5)



Manual_Label = Label(
    form, text="F2 영역 선택 / ESC or 닫기 번역 중지")
Manual_Label.grid(row=6, columnspan=3, padx=30, pady=10)

Maker_Label = Label(
    form, text="---------만든사람 : tobeptcoder------------")
Maker_Label.grid(row=7, columnspan=3, padx=30, pady=5)
Email_Label = Label(
    form, text="------------tobeptcoder@gmail.com------------")
Email_Label.grid(row=8, columnspan=3, padx=30, pady=5)

form.mainloop()