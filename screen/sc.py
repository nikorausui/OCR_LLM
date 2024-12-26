import pyautogui
import PIL
from PIL import Image, ImageDraw, ImageFont
import datetime
import os
import webbrowser
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import os
import google.generativeai as genai
APIk=""
def launch_browser_and_capture():
    WIDTH = 600  # ブラウザの幅
    HEIGHT = 500  # ブラウザの高さ
    
    chrome_options = Options()
    chrome_options.add_argument(f"--window-size={WIDTH},{HEIGHT}")
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    # ウィンドウサイズを正確に制御するための設定
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(WIDTH, HEIGHT)
    driver.get("https://qiita.com/")
    driver.set_window_position(0, 0)
    
    time.sleep(2)
    return driver, WIDTH, HEIGHT

def capture_and_annotate_screenshot():
    try:
        driver, WIDTH, HEIGHT = launch_browser_and_capture()
        
        window_location = driver.get_window_position()
        screenshot = pyautogui.screenshot(region=(
            window_location['x'],
            window_location['y'],
            WIDTH,
            HEIGHT
        ))
        
        draw = ImageDraw.Draw(screenshot)
        EDGE_PADDING = 10
        GRID_SPACING = 50
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", 12)
            except:
                font = ImageFont.load_default()
        
        # 横方向の番号付け
        counter = 1
        for y in range(EDGE_PADDING, HEIGHT - EDGE_PADDING, GRID_SPACING):
            for x in range(EDGE_PADDING, WIDTH - EDGE_PADDING, GRID_SPACING):
                draw.point((x, y), fill='red')
                text = str(counter)
                
                # テキストの背景を白く
                text_bbox = draw.textbbox((x+2, y+2), text, font=font)
                padded_bbox = (
                    text_bbox[0] - 2,
                    text_bbox[1] - 2,
                    text_bbox[2] + 2,
                    text_bbox[3] + 2
                )
                draw.rectangle(padded_bbox)
                draw.text((x+2, y+2), text, fill='red', font=font)
                counter += 1
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        save_path = os.path.join(os.getcwd(), filename)
        
        screenshot.save(save_path)
        print(f"スクリーンショットを保存しました: {save_path}")
        
        driver.quit()
        return filename
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        if 'driver' in locals():
            driver.quit()
        return None

if __name__ == "__main__":
    try:
        filename = capture_and_annotate_screenshot()
        if filename:
            path = str(filename)
            print(path)

            genai.configure(api_key=APIk)

            def upload_to_gemini(path, mime_type=None):
                file = genai.upload_file(path, mime_type=mime_type)
                print(f"Uploaded file '{file.display_name}' as: {file.uri}")
                return file

            generation_config = {
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
                "response_mime_type": "text/plain",
            }

            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=generation_config,
            )

            files = [
                upload_to_gemini(path, mime_type="image/png"),
            ]

            chat_session = model.start_chat(
                history=[
                    {
                        "role": "user",
                        "parts": [
                            files[0],
                            "以下のスクリーンショットでは、画像のxy軸に番号が連番で割り振られている。「questionをクリックしたい場合にクリックするべき番号を一つ出力してください。」",
                        ],
                    },
                ]
            )

            response = chat_session.send_message("画像を分析して、questionの位置に最も近い番号を教えてください。")
            print(response.text)
            
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
