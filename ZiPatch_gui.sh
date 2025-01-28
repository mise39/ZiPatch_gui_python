#!/bin/bash

# 設置語言環境為繁體中文 UTF-8
export LANG=zh_TW.UTF-8
export LC_ALL=zh_TW.UTF-8

# 設置 Python 路徑（如果需要）
export PATH="/usr/bin:$PATH"

# 切換到腳本所在目錄
cd "$(dirname "$0")" || exit

# 運行 Python 腳本
python3 ZiPatch_gui.py

# 運行遊戲（假設 %command% 是 Steam 的遊戲啟動命令）
eval $@
