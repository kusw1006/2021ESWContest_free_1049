package com.example.vvs_sum;

import android.app.Activity;
import android.app.Dialog;
import android.content.Intent;
import android.os.Bundle;
import android.os.Message;
import android.provider.MediaStore;
import android.util.Log;
import android.view.Menu;
import android.view.View;
import android.widget.Button;
import android.widget.RadioGroup;
import android.widget.RadioButton;
import android.widget.RadioGroup.OnCheckedChangeListener;

import androidx.annotation.IdRes;
import androidx.appcompat.app.AppCompatActivity;

public class PopActivity extends Activity{
    private RadioGroup radioGroup1, radioGroup2;

    int id1 = number.getInstance().getId1();
    int id2 = number.getInstance().getId2();

    String TAG = "socketTest";

    @Override
    protected void onCreate(Bundle savedInstanceState){
        super.onCreate(savedInstanceState);
        setContentView(R.layout.popup);

        RadioGroup rg1 = findViewById(R.id.radioGroup1);
        RadioGroup rg2 = findViewById(R.id.radioGroup2);

        Log.i(TAG, String.valueOf(id1) + "id1");
        Log.i(TAG, String.valueOf(id2) + "id2");

        if(id1 == 1)
            rg1.check(R.id.man);
        else if(id1 == 2)
            rg1.check(R.id.woman);
        if(id2 == 1)
            rg2.check(R.id.small);
        else if(id2 == 2)
            rg2.check(R.id.middle);
        else if(id2 == 3)
            rg2.check(R.id.large);


        //rg1.setOnCheckedChangeListener(radioGroupButtonChangeListener1);
        //rg2.setOnCheckedChangeListener(radioGroupButtonChangeListener2);

        Button MenuStoreButton = findViewById(R.id.store);
        MenuStoreButton.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View view){
                int check1 = rg1.getCheckedRadioButtonId();
                int check2 = rg2.getCheckedRadioButtonId();
                if(check1 == R.id.man){
                    number.getInstance().setId1(1);
                }
                else if(check1 == R.id.woman){
                    number.getInstance().setId1(2);
                }
                if(check2 == R.id.small){
                    number.getInstance().setId2(1);
                }
                else if(check2 == R.id.middle){
                    number.getInstance().setId2(2);
                }
                else if(check2 == R.id.large){
                    number.getInstance().setId2(3);
                }
                finish();
            }
        });
        Button MenuCloseButton = findViewById(R.id.close);
        MenuCloseButton.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View v) {
                finish();
            }
        });
    }

    RadioGroup.OnCheckedChangeListener radioGroupButtonChangeListener1 = new RadioGroup.OnCheckedChangeListener(){
        @Override
        public void onCheckedChanged(RadioGroup radioGroup, @IdRes int i){
            if(i == R.id.man){
                number.getInstance().setId1(1);
                Log.i(TAG, String.valueOf(i) + "id");
            }
            else if(i == R.id.woman){
                number.getInstance().setId1(2);
                Log.i(TAG, String.valueOf(i) + "id");
            }
        }
    };

    RadioGroup.OnCheckedChangeListener radioGroupButtonChangeListener2 = new RadioGroup.OnCheckedChangeListener(){
        @Override
        public void onCheckedChanged(RadioGroup radioGroup, @IdRes int i){
            if(i == R.id.small){
                number.getInstance().setId2(1);
                Log.i(TAG, String.valueOf(i) + "id");
            }
            else if(i == R.id.middle){
                number.getInstance().setId2(2);
                Log.i(TAG, String.valueOf(i) + "id");
            }
            else if(i == R.id.large){
                number.getInstance().setId2(3);
                Log.i(TAG, String.valueOf(i) + "id");
            }
        }
    };
}
