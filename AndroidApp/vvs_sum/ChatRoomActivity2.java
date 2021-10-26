package com.example.vvs_sum;

import android.app.Activity;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.os.StrictMode;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.InetAddress;
import java.net.Socket;
import java.net.UnknownHostException;
import java.util.ArrayList;

public class ChatRoomActivity2 extends AppCompatActivity {

    private MyAdapter adapter;

    final Handler handler = new Handler(){
        public void handleMessage(Message msg){
            RecyclerView recyvlerv = findViewById(R.id.recyvlerv);
            adapter.notifyDataSetChanged();
            recyvlerv.scrollToPosition(dataList.size()-1);
        }
    };

    public TextView Toptext;
    public Button ConnButton;
    public Button DiconButton;
    public ImageButton SendButton;
    private Socket socket;

    String TAG = "socketTest";

    private ArrayList<DataItem> dataList;
    LinearLayoutManager manager = new LinearLayoutManager(this,RecyclerView.VERTICAL,false);

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.room2);   //나중에 바꾸기

        ConnButton = findViewById(R.id.button1);
        DiconButton = findViewById(R.id.button2);
        SendButton = findViewById(R.id.btn_send1);

        Log.i(TAG, "Application created");

        int SDK_INT = android.os.Build.VERSION.SDK_INT;
        if (SDK_INT > 8) {
            StrictMode.ThreadPolicy policy = new StrictMode.ThreadPolicy.Builder().permitAll().build();
            StrictMode.setThreadPolicy(policy);
        }

        ConnButton.setOnClickListener(new Button.OnClickListener() {
            @Override
            public void onClick(View view) {
                Toast.makeText(getApplicationContext(), "Connect 시도", Toast.LENGTH_SHORT).show();
                String addr = "114.70.22.237".trim();
                ConnectThread thread = new ConnectThread(addr);

                thread.start();
            }
        });
        SendButton.setOnClickListener(new Button.OnClickListener() {
            @Override
            public void onClick(View view) {
                Toast.makeText(getApplicationContext(), "Send 시도", Toast.LENGTH_SHORT).show();
                StartThread_send sthread = new StartThread_send();

                sthread.start();
            }
        });
        DiconButton.setOnClickListener(new Button.OnClickListener() {
            @Override
            public void onClick(View view) {
                try {
                    socket.close();
                    Toast.makeText(getApplicationContext(), "DisConnect", Toast.LENGTH_SHORT).show();
                    DiconButton.setEnabled(false);
                    ConnButton.setEnabled(true);
                } catch (IOException e) {
                    e.printStackTrace();
                    Toast.makeText(getApplicationContext(), "DisConnect 실패", Toast.LENGTH_SHORT).show();
                }
            }
        });

        init();
    }

    private void init(){
        RecyclerView recyvlerv = findViewById(R.id.recyvlerv);

        LinearLayoutManager manager = new LinearLayoutManager(this,RecyclerView.VERTICAL,false);

        initData();

        recyvlerv.setLayoutManager(manager);

        adapter = new MyAdapter(dataList);
        recyvlerv.setAdapter(adapter);

        recyvlerv.scrollToPosition(dataList.size()-1);
    }

    private void refresh_right(String str){
        dataList.add(new DataItem(str,"고객",Code.ViewType.RIGHT_CONTENT));
        Message msg = handler.obtainMessage();
        handler.sendMessage(msg);
    }

    private void refresh_left(String str){
        dataList.add(new DataItem(str,"점주",Code.ViewType.LEFT_CONTENT));
        Message msg = handler.obtainMessage();
        handler.sendMessage(msg);
    }

    class StartThread_send extends Thread{

        EditText sendtext;

        public StartThread_send(){
            sendtext = findViewById(R.id.editText1);
        }

        public void run() {

            // 데이터 송신
            try {
                String OutData = sendtext.getText().toString();
                byte[] data = OutData.getBytes();
                OutputStream output = socket.getOutputStream();
                output.write(data);
                sendtext.setText(null);
                Log.d(TAG, "refresh 직전");
                refresh_right(OutData);

                Log.d(TAG, OutData + "COMMAND 송신");

            } catch (IOException e) {
                e.printStackTrace();
                Log.d(TAG, "데이터 송신 오류");
            }
        }
    }

    class ConnectThread extends Thread {
        String hostname;
        String data;

        public ConnectThread(String addr) {
            hostname = addr;
        }

        public void run() {
            try { //클라이언트 소켓 생성

                int port = 5050;
                socket = new Socket(hostname, port);
                Log.d(TAG, "Socket 생성, 연결.");

                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        InetAddress addr = socket.getInetAddress();
                        String tmp = addr.getHostAddress();
                        Toast.makeText(getApplicationContext(), "Connected", Toast.LENGTH_LONG).show();

                        DiconButton.setEnabled(true);
                        ConnButton.setEnabled(false);
                    }
                });




            } catch (UnknownHostException uhe) { // 소켓 생성 시 전달되는 호스트(www.unknown-host.com)의 IP를 식별할 수 없음.

                Log.e(TAG, " 생성 Error : 호스트의 IP 주소를 식별할 수 없음.(잘못된 주소 값 또는 호스트 이름 사용)");
                runOnUiThread(new Runnable() {
                    public void run() {
                        Toast.makeText(getApplicationContext(), "Error : 호스트의 IP 주소를 식별할 수 없음.(잘못된 주소 값 또는 호스트 이름 사용)", Toast.LENGTH_SHORT).show();
                        Toptext.setText("Error : 호스트의 IP 주소를 식별할 수 없음.(잘못된 주소 값 또는 호스트 이름 사용)");
                    }
                });

            } catch (IOException ioe) { // 소켓 생성 과정에서 I/O 에러 발생.

                Log.e(TAG, " 생성 Error : 네트워크 응답 없음");
                runOnUiThread(new Runnable() {
                    public void run() {
                        Toast.makeText(getApplicationContext(), "Error : 네트워크 응답 없음", Toast.LENGTH_SHORT).show();
                        Toptext.setText("네트워크 연결 오류");
                    }
                });


            } catch (SecurityException se) { // security manager에서 허용되지 않은 기능 수행.

                Log.e(TAG, " 생성 Error : 보안(Security) 위반에 대해 보안 관리자(Security Manager)에 의해 발생. (프록시(proxy) 접속 거부, 허용되지 않은 함수 호출)");
                runOnUiThread(new Runnable() {
                    public void run() {
                        Toast.makeText(getApplicationContext(), "Error : 보안(Security) 위반에 대해 보안 관리자(Security Manager)에 의해 발생. (프록시(proxy) 접속 거부, 허용되지 않은 함수 호출)", Toast.LENGTH_SHORT).show();
                        Toptext.setText("Error : 보안(Security) 위반에 대해 보안 관리자(Security Manager)에 의해 발생. (프록시(proxy) 접속 거부, 허용되지 않은 함수 호출)");
                    }
                });


            } catch (IllegalArgumentException le) { // 소켓 생성 시 전달되는 포트 번호(65536)이 허용 범위(0~65535)를 벗어남.

                Log.e(TAG, " 생성 Error : 메서드에 잘못된 파라미터가 전달되는 경우 발생.(0~65535 범위 밖의 포트 번호 사용, null 프록시(proxy) 전달)");
                runOnUiThread(new Runnable() {
                    public void run() {
                        Toast.makeText(getApplicationContext(), " Error : 메서드에 잘못된 파라미터가 전달되는 경우 발생.(0~65535 범위 밖의 포트 번호 사용, null 프록시(proxy) 전달)", Toast.LENGTH_SHORT).show();
                        Toptext.setText("Error : 메서드에 잘못된 파라미터가 전달되는 경우 발생.(0~65535 범위 밖의 포트 번호 사용, null 프록시(proxy) 전달)");
                    }
                });


            }

            try {
                Log.d(TAG, "데이터 수신 준비");

                //TODO:수신 데이터(프로토콜) 처리

                while (true) {
                    InputStream input = socket.getInputStream();
                    Log.d(TAG, "수신");

                    BufferedReader reader = new BufferedReader(new InputStreamReader(input));


                    Log.d(TAG, "수신2");
                    data = reader.readLine();
                    Log.d(TAG, "수신3");
                    Log.d(TAG, data);

                    //dataList.add(new DataItem(data,"점주",Code.ViewType.LEFT_CONTENT));
                    refresh_left(data);
                }
            }catch(IOException e){
                e.printStackTrace();
                Log.e(TAG,"수신 에러");
            }


        }
    }

    private void initData(){
        dataList = new ArrayList<>();
        dataList.add(new DataItem("시용자1님 입장했음",null,Code.ViewType.CENTER_CONTENT));
        dataList.add(new DataItem("사용자2님 입장했음",null,Code.ViewType.CENTER_CONTENT));
    }

    @Override
    protected void onStop() {  //앱 종료시
        super.onStop();
        try {
            socket.close(); //소켓을 닫는다.
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}