from PIL import Image
import pytesseract
import pyautogui

# Tesseractの実行ファイルパスを設定
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

# 画像を開く
image = Image.open('a.png')

# テキストと座標情報を取得
data = pytesseract.image_to_data(image, lang='jpn', output_type=pytesseract.Output.DICT)

# 結果を出力
for i, text in enumerate(data['text']):
    if text.strip():
        x = data['left'][i]
        y = data['top'][i]
        print(f"テキスト: {text}, 座標: ({x}, {y})")
def click_text(target_text):
    for i, text in enumerate(data['text']):
        if text.strip() == target_text:
            x = data['left'][i]
            y = data['top'][i]
            print(f"{target_text}を座標({x}, {y})でクリックします")
            pyautogui.click(x, y)
            return
    print(f"{target_text}が見つかりませんでした")

# 使用例
click_text("目次")
