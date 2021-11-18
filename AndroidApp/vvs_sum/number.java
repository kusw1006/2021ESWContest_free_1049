package com.example.vvs_sum;

public class number {
    private int id1;
    private int id2;

    public int getId1(){
        return id1;
    }
    public int getId2(){
        return id2;
    }
    public void setId1(int id1){
        this.id1 = id1;
    }
    public void setId2(int id2){
        this.id2 = id2;
    }
    private static number instance = null;
    public static synchronized number getInstance(){
        if(null == instance){
            instance = new number();
        }
        return instance;
    }
}
