import os, json, random
from janome.tokenizer import Tokenizer as token

dict_file = "markov_dict.json"
dic = {}

#辞書への登録
def register_dic(wordlist):
    global dic
    w1 = ""
    w2 = ""
    
    #要素が3未満の場合は何もしない。
    if len(wordlist) < 3 : return
    
    for w in wordlist:
        word = w[0]
        if word == "" or word == "\r\n" or word == "\n" : continue
        #辞書に単語を認定
        if w1 and w2:
            set_dic(dic, w1, w2, word)
        #文末を表す語の場合、連鎖をクリアする。
        if word == "。" or word == "？" or word == "?" :
            w1 = ""
            w2 = ""
            continue
        #次の前後関係を登録するために単語をスライド
        w1, w2 = w2, word
        
    #辞書を保存
    json.dump(dic, open(dict_file, "w", encoding="utf-8"))
    
#応答文の作成
def set_dic(dic, w1, w2, w3):
    #新しい単語の場合は新しい辞書オブジェクトを作成
    if w1 not in dic : dic[w1] = {}
    if w2 not in dic[w1] : dic[w1][w2] = {}
    if w3 not in dic[w1][w2] : dic[w1][w2][w3] = 0
    #単語の出現数をインクリメントする
    dic[w1][w2][w3] += 1

#メイン処理
def make_response(word):
    res = []
    
    #名詞、形容詞、動詞は文章の意図を示していることが多いと想定し、始点の単語とする。
    w1 = word
    res.append(w1)
    w2 = word_choise(dic[w1])
    res.append(w2)
    while True:
        #w1, w2の組み合わせから選択される単語を選択
        if w1 in dic and w2 in dic[w1] : w3 = word_choise(dic[w1][w2])
        else : w3 = ""
        res.append(w3)
        #文末を表す語の場合作文を終了
        if w3 == "。" or w3 == "？" or w3 == "?" or w3 == "" : break
        #次の単語を選択するために単語をスライド
        w1, w2  = w2, w3
    return "".join(res)

def word_choise(candidate):
    keys = candidate.keys()
    return random.choice(list(keys))

#メイン処理

#辞書がすでに存在する場合は最初に読み込む
if os.path.exists(dict_file):
    dic = json.load(open(dict_file, "r"))
    
while True:
    #標準入力から入力を受け付け、さようならが入力されるまで続ける。
    text = input("You -->")
    if text == "" or text == "さようなら":
        print("Bot --> さようなら")
        break
    
    #文章整形
    if text[-1] != "。" and text[-1] != "?" and text[-1] != "？" : text += "。"
    
    #形態素解析
    t = token()
    malist = t.tokenize(text)
    
    #単語と品詞を抽出
    wordlist = []
    for n in malist:
        hinshi = n.part_of_speech.split(',')[0]
        if hinshi not in ["BOS/EOS"]:
            wordlist.append([n.surface, hinshi])
    
    #マルコフ連鎖の辞書に登録
    register_dic(wordlist)
    
    #応答文の作成
    for w in wordlist:
        word = w[0]
        hinshi = w[1]
        #品詞が感動詞の場合、単語はそのまま返す。
        if hinshi in [ "感動詞"] :
            print("Bot -->" + word)
            break
        #品詞が名詞、動詞、形容詞の場合、かつ、辞書に単語が存在する場合は作文を返す。
        
        elif (hinshi in ["名詞", "形容詞", "動詞"]) and (word in dic) :
            print("Bot -->" + make_response(word))
            break