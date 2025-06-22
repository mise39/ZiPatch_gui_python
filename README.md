本軟體是方便一切需要安裝補丁的遊戲做的軟體，  
50% AI構成(ChatGPT和DeepSeek)和50%人工修正。  
無需任何Python額外插件。  

預設資料夾為/Home/deck/Downloads  
暫存資料夾為/Home/deck/Downloads/Temp (會自動建立資料夾)  
目標資料夾為/home/deck/.local/share/Steam/steamapps/common  


# 使用方法:  
1.請把兩個檔案放在同一個位置下  
2.用非Steam遊戲新增為捷徑

本軟體不支援有密碼的壓縮檔，  
請使用本軟體時遵守一切道德行為。  

## *如無任何反應，請為檔案加權限(用konsole輸入)  
```
chmox +x /你的檔案位置/ZiPatch_gui.sh
```


## *關於Chmod not found的解決方法  
請先konsole輸入
```
passwd
```
設定密碼
然後再輸入  
```
sudo pacman -Sy coreutils
```
Chmod 指令就不會報錯  
