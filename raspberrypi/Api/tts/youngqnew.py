# -*- coding: utf-8 -*-

#import string
from google.cloud import texttospeech

client=texttospeech.TextToSpeechClient()


voice_eng = texttospeech.types.VoiceSelectionParams(
    language_code="en-US",
    ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL
)
voice_kor = texttospeech.types.VoiceSelectionParams(
    language_code="ko-KR",
    ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL
)
audio_config = texttospeech.types.AudioConfig(
    audio_encoding=texttospeech.enums.AudioEncoding.MP3
)

def exchange_eng(input_text):
    synthesis_input = texttospeech.types.SynthesisInput(text=input_text)
    response = client.synthesize_speech(synthesis_input, voice_eng, audio_config)
    return response.audio_content

def exchange_kor(input_text):
    synthesis_input = texttospeech.types.SynthesisInput(text=input_text)
    response = client.synthesize_speech(synthesis_input, voice_kor, audio_config)
    return response.audio_content

def makeFile_originlist(textList, *adder):
    if len(adder)==0:
        adder='output'
    else:
        adder = adder[0]

    for i, text in enumerate(textList):
        if type(text) == type(list()):
            with open('/home/pi/esw_tts_test/tts_test/resultfile/'+str(adder)+str(i)+'_eng.mp3','wb') as out:
                out.write(exchange_eng(text[0]))
            with open('/home/pi/esw_tts_test/tts_test/resultfile/'+str(adder)+str(i)+'_kor.mp3','wb') as out:
                out.write(exchange_kor(text[1]))
        else:
            with open('/home/pi/esw_tts_test/tts_test/resultfile/'+str(adder)+str(i)+'.mp3','wb') as out:
                out.write(exchange_eng(text))

def makeFile(textList, *adder):
    if len(adder)==0:
        adder='output'
    else:
        adder = adder[0]

    for i, text in enumerate(textList):
        if type(text) == type(str):
            with open('/home/pi/esw_tts_test/tts_test/resultfile/'+str(adder)+str(i)+'_eng.mp3','wb') as out:
                out.write(exchange_eng(text[0]))
            with open('/home/pi/esw_tts_test/tts_test/resultfile/'+str(adder)+str(i)+'_kor.mp3','wb') as out:
                out.write(exchange_kor(text[1]))
        else:
            with open('/home/pi/esw_tts_test/tts_test/resultfile/'+str(adder)+str(i)+'.mp3','wb') as out:
                out.write(exchange_eng(text))
                
                
                
location = ['in front of a fountain', 'in a clothing store', 'at a construction site', 'at a plaza',
            'in a parking lot', 'in a shopping district', 'at a crosswalk']
# makeFile(location, 'location')

behavior = [['he is sitting arm in arm','그는 팔짱을 끼고 앉아있다.'],
            ['he is holding up something','그는 무언가를 들고있다.'],
            ['they are smiling at each other','그들은 서로를 보며 웃고있다.'],
            ['he is legs crossed','그는 다리를 꼬고있다.'],
            ['A man is raising his hand','한 남자가 손을 들고있다.']]

# makeFile(behavior, 'behavior')
#str1=input('입력하시오: ')            
#textinput_eng=[]
textinput=[]
select=int(input('languagenum(0=eng, 1=kor):'))
if select == 0:    
    str_e=raw_input('English sentense: ')
    textinput.append(str_e)
    makeFile_originlist(textinput, 'input_eng')
    #makeFile(str_e, 'input_eng')

elif select == 1:
    #text_i=input()
    str_k=raw_input('Korean sentense: ')
    #textinput.append(str_k)
    #makeFile_originlist(textinput, 'input_kor')
    makeFile(str_k, 'input_kor')
    
else:
    print('try again')
    

        
