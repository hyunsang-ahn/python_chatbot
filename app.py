import os
from flask import Flask, request
from pprint import pprint as pp
import requests
import random
from bs4 import BeautifulSoup


app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"
    




api_url = 'https://api.hphk.io/telegram'

token = os.getenv('TELE_TOKEN')

@app.route(f'/{token}', methods=['POST'])
def telegram():
    #print(request.get_json())
    #쉽게 보기 위한 작업 pp
    
    
    #naver api를 사용하기 위한 변수
    naver_client_id = os.getenv('NAVER_ID')
    naver_client_secret = os.getenv('NAVER_SECRET')
    
    
    
    
    
    
    #tele_dict = 데이터 덩어리
    tele_dict = request.get_json()
    pp(request.get_json())
    
    #유저 정보
    chat_id = tele_dict["message"]["chat"]["id"]
    #유저가 입력한 데이터
    text = tele_dict.get("message").get("text")

    
    
    #"번역 안녕하세요" -> 변역이 실시 되도록 하는 코드작성
    # text 는 유저가 입력한 데이터고 앞에 2글자가 번역인지 확인하는 코드로 작성해보자.
    
    #글자 2개 뽑아 내는 문법은 a[:2]
    tran = False
    img = False
    #사용자가 이미지를 넣었는지 확인하는 if문
    if tele_dict.get('message').get('photo') is not None:
        img = True
      
    else:
    #번역 안녕하세요   중 앞에 3글자를 빼고 번역해야함.
        if text[:2]=="번역":
            tran = True
            text = text.replace("번역","")
    
    
        
    if tran:
        papago = requests.post("https://openapi.naver.com/v1/papago/n2mt",
                    headers = {
                        "X-Naver-Client-Id":naver_client_id,
                        "X-Naver-Client-Secret":naver_client_secret
                    },
                    data = {
                        'source':'ko',
                        'target':'en',
                        'text':text
                        }
                    )

        pp(papago.json())
        text = papago.json()['message']['result']['translatedText']
        
    elif img:
        text = "사용자가 이미지를 넣었어요"
        
        #텔레그램에게 사진 정보 가져오기
        file_id = tele_dict['message']['photo'][-1]['file_id']
        file_path = requests.get(f"{api_url}/bot{token}/getFile?file_id={file_id}").json()['result']['file_path']                
        file_url = f"{api_url}/file/bot{token}/{file_path}"
        print(file_url)        
        
        
        
        
        # 사진을 네이버 유명인 인식api 로 넘겨주기
        file = requests.get(file_url, stream=True)
        
        clova = requests.post("https://openapi.naver.com/v1/vision/celebrity",
                    headers = {
                        "X-Naver-Client-Id":naver_client_id,
                        "X-Naver-Client-Secret":naver_client_secret
                    },
                    files = {
                        'image':file.raw.read()
                    
                        }
                    )
        
        
        # 가져온 데이터 중에서 필요한 정보 빼오기.
        
        pp(clova.json())
        
        
        
        #인식이 되었을때
        if clova.json().get('info').get("faceCount"):
            text = clova.json()['faces'][0]['celebrity']['value']
            
            
    
        
        
        else:
            text = "얼굴이 없어요"
        
        
        
        
        #인식이 되지 않았을때
            
    
        

    
    elif text=="메뉴":
        menu_list = ["한식", "중식", "양식", "분식", "선택식"]
        text = random.choice(menu_list)
        
        
    elif text=="토요일":
        menu_list = ["샤브향", "아구찜", "도쿄990", "린느", "궁전제과", "햄버거", "틈새라면"]
        text = random.choice(menu_list)
        
        
    elif text=="로또":
        text = random.sample(range(1,46),6)
        
        
        
        
        
    elif text=="실검":
        url = "https://www.daum.net"
        res = requests.get(url).text
#res = requests.get(url).status_code

        soup = BeautifulSoup(res, 'html.parser')
        pick = soup.select('#mArticle > div.cmain_tmp > div.section_media > div.hotissue_builtin.hide > div.realtime_part > ol > li > div > div:nth-of-type(1) > span.txt_issue > a')

        sil = ""
        for i in pick:
            sil = sil + i.text + '\n'
            print(sil)
        text = sil
            
        
 
            
            
            
            
        # text = pick[0].text
        # text = pick[1].text
        # text = pick[2].text
        # text = pick[3].text
        # text = pick[4].text
        # text = pick[5].text
        # text = pick[6].text
        # text = pick[7].text
        # text = pick[8].text
        # text = pick[9].text
    #print(chat_id)
    #print(text)
    
    
    #유저에게 그대로 돌려주기 코드 작성
    requests.get(f'{api_url}/bot{token}/sendMessage?chat_id={chat_id}&text={text}')
    
    return '', 200
    

app.run(host=os.getenv('IP','0.0.0.0'),port=int(os.getenv('PORT',8080)))




