package com.example.vvs_sum;

import android.app.Application;

class arraycount{
    int count;
    arraycount(){}
    public arraycount(int num){
        this.count = num;
    }
    public int returnnum(){
        return count;
    }
}

class arraynum{
    int line;
    arraynum(){
    }
    public arraynum(int line){
        this.line = line;
    }
    public int returnid(){
        return line;
    }
}

class man_or_woman{
    int morw;
    man_or_woman(){}
    public man_or_woman(int morw){ this.morw = morw; }
    public int returnmw() { return morw; }
}

class emotion{
    int emo;
    emotion(){}
    public emotion(int emo){ this.emo = emo; }
    public int returnemo() { return emo; }
}