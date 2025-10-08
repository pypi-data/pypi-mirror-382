# pyfunc_happyset
<img src="https://img.shields.io/badge/-Python-000.svg?logo=python&style=popout">

## Overview
Pythonの自分的便利関数詰め合わせセット

## Requirement
- MacOS
- Python 3.11.5

## Features
### データ取得系
- csvファイルから読み込んでリストにする : Get_csv2List
- テキストファイルから任意の区切り文字で読み込んでリストにする : Get_text2List
- 指定したリストの重複を削除する : Get_uniqueList
- 辞書型で値からキーを取得する : Get_keyFromValue
### データ書き込み
- 1次元配列を指定したファイルの末尾に追加する : Write_a_1dlist
- 2次元配列を指定したファイルの末尾に追加する : Write_a_2dlist
- 1次元配列を指定したファイルに上書きする : Write_w_1dlist
- 2次元配列を指定したファイルに上書きする : Write_w_2dlist
### ファイル操作
- 指定したディレクトリの下にあるディレクトリの名前をリストで返す : Get_dirList
- 指定したディレクトリの下にあるファイルの名前をリストで返す : Get_fileList
- 指定したディレクトリの下にあるファイルの絶対パスを返す　: Get_filepathList
- 指定したファイルを指定した場所に移動する : Move_file
- ディレクトリの中身を空にする : Clear_dir
- ファイルの中身を空にする : Clear_file
- 指定したディレクトリ以下の構造を複製する : Copy_dir
### そのほか
- 2次元配列を1次元配列にする : Conv_2dListTo1dList
- 正規表現にマッチする箇所を置き換える : Replace_match
- 指定秒停止する : Wait
