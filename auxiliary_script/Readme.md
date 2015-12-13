以手勢執行 Home event:

* Short_Home_Key: 短按Home鍵
* Long_Home_Key: 長按Home鍵
* Tap_Close_App: 長按Home鍵後按叉叉關掉App (需先執行長按Home鍵)

執行方法
```
adb push shell.sh /data/local/tmp/
adb shell chmod 755 /data/local/tmp/shell.sh
adb shell sh /data/local/tmp/ shell.sh
```

執行時間大約為幾秒鐘, 要耐心等待它執行完

另外Marionette.kill_all()會連HomeScreen也一起關閉

此時可以:

* Executor._dispatch_home_button_event() (目前作法), 或
* Long_Home_Key + Tap_Close_App

就可以把HomeScreen首頁呼叫回來