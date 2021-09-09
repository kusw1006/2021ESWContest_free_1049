https://github.com/proghjy/cppSocket/blob/master/server.cpp



https://m.blog.naver.com/whtie5500/221692793640



https://m.blog.naver.com/whtie5500/221692811349

\1. 각종 변수들을 정의합니다. socket와 client socket의 fd를 받을 변수, socket address을 받을 변수, pthread id을 받을 변수 등을 선언합니다.



\2. int sockfd = socket(domain, type, protocol) : 이 함수는 socket을 생성하는 함수입니다.

sockfd : 소켓 디스크립터

domain : AF_INET (IPv4 protocol), AF_INET6 (IPv6 protocol)중 무엇을 이용할지 정합니다.

type : SOCK_STREAM (tcp socket), SOCK_DGRAM (udp socket)중 무엇을 이용할지 결정합니다.

protocol : 0



\3. int setsockopt(int sockfd, int level, int optname, const void* optval, socklen_t optlen);

소켓의 옵션을 설정하는것으로, port, address을 재사용하는데 도움을 줍니다. 한번 특정 포트를 이용하던 프로그램이 죽으면 몇초간 해당 포트를 이용하지 못하게 되는데, 그런것들을 막아주는 역할을 합니다.



\4. server의 주소값을 담을 변수를 초기화하고, 저의 임의로 domain, port number등을 지정해줍니다.



\5. int bind(int sockfd, const struct sockaddr * addr, socklen_t addrlen); 

소켓을 생성한 이후, 소켓의 address와 port number을 묶어주는 역할을 합니다.



\6. int listen(int sockfd, int backlog);

서버소켓이 클라이언트소켓이 연결해올때까지 기다립니다. backlog은 소켓에 연결하기 위해 들어가있는 큐의 크기입니다.



\7. 이제 socket 설정을 완료 하였으니 서버는 while문 을 돌며 클라이언트 소켓을 기다립니다.



\8. int new_socket = accept(int sockfd, struct sockaddr *addr, socklen_t *addrlen);

클라이언트 소켓이 연결해오면 해당 클라이언트 소켓의 파일디스크립터를 반환하는 함수입니다. 클라이언트 소켓이 진입할 때 까지 대기합니다.



\9. 클라이언트 소켓이 들어오면 thread을 생성하여 하나의 스레드와 하나의 클라이언트가 통신하도록 만듭니다. pthrad을 생성하는 방법은 저의 이전 포스팅을 참고해주세요



\10. 이제 thread함수로 진입했습니다. 위에서는 받아온 입력 파라미터들을 정리하고요, while문을 돌며 클라이언트와 통신합니다. 클라이언트가 데이터를 받아오면 console창에 출력하고, 그 데이터 그대로 다시 클라이언트에 수신합니다. 에코서버이죠