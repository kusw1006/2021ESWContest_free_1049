# run_sentences.py

> 경로: /home/dcl2003/spacing/korean-spacing-model
>
> 작성자: 김한비 코드제작: 이찬현, 김한비

<br>

> 학습된 띄어쓰기 모델을 기반으로 문장 띄어쓰기 진행
>
> char_file=/home/dcl2003/spacing/korean-spacing-model/resources/chars-4996
>
> model_file=/home/dcl2003/spacing/korean-spacing-model/models/checkpoint-12.ckpt
>
> training_config=/home/dcl2003/spacing/korean-spacing-model/resources/config.json 

<br>

## 변경사항

```python
import json
from argparse import ArgumentParser
#from typing_extensions import _AnnotatedAlias
import chardet
import tensorflow as tf

from train import SpacingModel

import socket
import threading

HOST = '114.70.22.237'
PORT = 5052

parser = ArgumentParser()
parser.add_argument("--char-file", type=str, required=True)
parser.add_argument("--model-file", type=str, required=True)
parser.add_argument("--training-config", type=str, required=True)

recv_data=[]


def main():
	#########
    # <중략> #
    #########
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    client_socket.connect((HOST, PORT))
    print("socket")
    print(threading.active_count())
    
    thread1 = threading.Thread(target=recv, args=(client_socket, ))
    # thread1.daemon = True
    thread1.start()
    
    thread2 = threading.Thread(target=send, args=(client_socket, inference))
    # thread2.daemon = True
    thread2.start()
      

def recv(client_sock):
    while True:
        try:
            global recv_data
            recv = client_sock.recv(1024)
            
            if len(recv):
                print("받은 데이터", len(recv))
                recv_data.append(recv.decode('utf8'))
                print(recv_data)

                print("1")
        except:
            print("연결이 해제되었습니다.")
            break

        
def send(client_sock, inference):
    global recv_data
    while True:
        try:
            if len(recv_data)!=0:
                print("@@남은 데이터",len(recv_data))
                
                target_str = recv_data.pop(0)
                start = target_str.find('}')
                token = target_str[:start+1]
                target_str = target_str[start+1:]
                
                target_str = tf.constant(target_str)
                
                result = inference(target_str).numpy()
                
                result_str = b"".join(result).decode("utf-8")
                if(token.find('T')):
                    token = token.replace('T','C')
                if(token.find('R')):
                    token = token.replace('T','D')
                result_str = token + result_str
                print(result_str)
                client_sock.send(result_str.encode())

        except:
            print("연결이 해제되었습니다.")
            break
    
################################
```

server와 연결 후 recv & send 함수 실행

<br>

- recv

> tcp 서버로 부터 문장을 받아옴
>
> 만약 받은 문장이 있다면 utf8 옵션으로 decode한 후 recv_data배열에 저장(처리하는 동안 여러 문장이 들어올 수 있기 때문에 배열에 저장)

<br>

- send

> recv_data에서 가장 처음 들어온 문장을 pop해서 target_str에 저장
>
> target_str에서 토큰을 기준으로 target_str와 token에 나눠서 저장
>
> 토큰은 T(디코드)->C(디코드 띄어쓰기), R(리스코어)->D(리스코어 띄어쓰기)로 변경
>
> 다시 토큰과 문장 결합해서 tcp에게 전송

<br>

thread가 죽지 않는 문제를 해결하기 위해 try, except 도입

<br>

<br>

## 코드 전문

```python
import json
from argparse import ArgumentParser
#from typing_extensions import _AnnotatedAlias
import chardet
import tensorflow as tf

from train import SpacingModel

import socket
import threading

HOST = '114.70.22.237'
PORT = 5052

parser = ArgumentParser()
parser.add_argument("--char-file", type=str, required=True)
parser.add_argument("--model-file", type=str, required=True)
parser.add_argument("--training-config", type=str, required=True)

recv_data=[]


def main():

    args = parser.parse_args()

    with open(args.training_config) as f:
        config = json.load(f)

    with open(args.char_file) as f:
        content = f.read()
        keys = ["<pad>", "<s>", "</s>", "<unk>"] + list(content)
        values = list(range(len(keys)))

        vocab_initializer = tf.lookup.KeyValueTensorInitializer(keys, values, key_dtype=tf.string, value_dtype=tf.int32)
        vocab_table = tf.lookup.StaticHashTable(vocab_initializer, default_value=3)

    model = SpacingModel(
        config["vocab_size"],
        config["hidden_size"],
        conv_activation=config["conv_activation"],
        dense_activation=config["dense_activation"],
        conv_kernel_and_filter_sizes=config["conv_kernel_and_filter_sizes"],
        dropout_rate=config["dropout_rate"],
    )

    model.load_weights(args.model_file)
    model(tf.keras.Input([None], dtype=tf.int32))
    model.summary()

    inference = get_inference_fn(model, vocab_table)
    
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    client_socket.connect((HOST, PORT))
    print("socket")
    print(threading.active_count())
    
    thread1 = threading.Thread(target=recv, args=(client_socket, ))
    # thread1.daemon = True
    thread1.start()
    
    thread2 = threading.Thread(target=send, args=(client_socket, inference))
    # thread2.daemon = True
    thread2.start()

    
             
        

def recv(client_sock):
    while True:
        try:
            global recv_data
            # recv_data.append(repr(client_socket.recv(1024).decode()))
            # recv = client_sock.recv(1024).decode("unicode_escape")
            recv = client_sock.recv(1024)
            
            if len(recv):
                print("받은 데이터", len(recv))
                recv_data.append(recv.decode('utf8'))
                print(recv_data)

                print("1")
        except:
            print("연결이 해제되었습니다.")
            break

        
def send(client_sock, inference):
    global recv_data
    while True:
        try:
            if len(recv_data)!=0:
                print("@@남은 데이터",len(recv_data))
                # print(recv_data)
                target_str = recv_data.pop(0)
                start = target_str.find('}')
                token = target_str[:start+1]
                target_str = target_str[start+1:]
                # print("111",target_str)
                target_str = tf.constant(target_str)
                # print("222",target_str)
                result = inference(target_str).numpy()
                # print(b"".join(result).decode("utf8"))
                result_str = b"".join(result).decode("utf-8")
                if(token.find('T')):
                    token = token.replace('T','C')
                if(token.find('R')):
                    token = token.replace('R','D')
                result_str = token + result_str
                print(result_str)
                client_sock.send(result_str.encode())

        except:
            print("연결이 해제되었습니다.")
            break
    
        
def get_inference_fn(model, vocab_table):
    @tf.function
    def inference(tensors):
        byte_array = tf.concat(
            [tf.strings.unicode_split(tf.strings.regex_replace(tensors, " +", " "), "UTF-8")], axis=0
        )
        strings = vocab_table.lookup(byte_array)[tf.newaxis, :]

        model_output = tf.argmax(model(strings), axis=-1)[0]
        return convert_output_to_string(byte_array, model_output)

    return inference


def convert_output_to_string(byte_array, model_output):
    sequence_length = tf.size(model_output)
    while_condition = lambda i, *_: i < sequence_length

    def while_body(i, o):
        o = tf.cond(
            model_output[i] == 1,
            lambda: tf.concat([o, [byte_array[i], " "]], axis=0),
            lambda: tf.cond(
                (model_output[i] == 2) and (byte_array[i] == " "),
                lambda: o,
                lambda: tf.concat([o, [byte_array[i]]], axis=0),
            ),
        )
        return i + 1, o

    _, strings_result = tf.while_loop(
        while_condition,
        while_body,
        (tf.constant(0), tf.constant([], dtype=tf.string)),
        shape_invariants=(tf.TensorShape([]), tf.TensorShape([None])),
    )
    return strings_result


if __name__ == "__main__":
    main()

```

