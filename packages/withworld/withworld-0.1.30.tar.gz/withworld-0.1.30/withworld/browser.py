import webbrowser
import pyautogui
import time
import re
import pyperclip
import sys
from withworld.autokey import paste, enter, esc, f12, close_tab
from withworld.bufer import get_bufer, load_to_bufer

def open_browser_console(url, time_sleep):
    """
    Открывает браузер с указанным URL. и ждет 5 секунд
    """
    
    webbrowser.open(url)
    time.sleep(time_sleep)  # даём время открыть браузер и кликнуть на него
    f12()
    esc()
    esc()

    paste("copy('js_panel')")
    esc()
    esc()
    paste("copy('js_panel')")
    if get_bufer() == 'js_panel':
        return True
    else:
        return False


def get_element(selector):
    """Получает код элемента по селектору"""
    selector = selector.replace("\\", "\\\\")   # удвоение всех слэшей
    selector = re.sub(r"(:)", r"\\\1", selector) # двоеточие -> \:
    selector = re.sub(r"(\[)", r"\\\1", selector) # [ -> \[
    selector = re.sub(r"(\])", r"\\\1", selector) # ] -> \]
    paste(f"copy(document.querySelector('{selector}'))")
    time.sleep(0.5)
    return get_bufer()


def click_element(selector):
    """Кликает по элементу"""
    selector = selector.replace("\\", "\\\\")   # удвоение всех слэшей
    selector = re.sub(r"(:)", r"\\\1", selector) # двоеточие -> \:
    selector = re.sub(r"(\[)", r"\\\1", selector) # [ -> \[
    selector = re.sub(r"(\])", r"\\\1", selector) # ] -> \]
    paste(f"copy(document.querySelector('{selector}'))")
    temp_bufer = False
    while  temp_bufer is False:
        time.sleep(1)
        paste(f"copy(document.querySelector('{selector}'))")
        temp_bufer = get_bufer()

    paste(f"document.querySelector('{selector}').click()")
    print('Успешный клик')
    time.sleep(0.5)


def check_element(selector):
    """Возвращает True или False в зависимости от существования элемента на странице"""
    selector = selector.replace("\\", "\\\\")   # удвоение всех слэшей
    selector = re.sub(r"(:)", r"\\\1", selector) # двоеточие -> \:
    selector = re.sub(r"(\[)", r"\\\1", selector) # [ -> \[
    selector = re.sub(r"(\])", r"\\\1", selector) # ] -> \]
    paste(f"copy(document.querySelector('{selector}'))")
    return get_bufer() != 'null'


def POST(url, body):
    """Отправка ПОСТ запроса application/json"""
        
    requset = '''
    // Получаем CSRF-токен из куки
    function getCsrfToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrfToken') {
                return value;
            }
        }
        return '';
    }
    
    // Альтернативно: ищем токен в meta-тегах
    function getCsrfTokenFromMeta() {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        return metaTag ? metaTag.content : '';
    }
    
    // Основная функция запроса
    async function fetchGoodsList() {
        const csrfToken = getCsrfToken() || getCsrfTokenFromMeta();
        const headers = {
            "Content-Type": "application/json"
        };
        if (csrfToken) {
            headers["X-CSRF-Token"] = csrfToken;
        }
    
        try {
            const response = await fetch(\'''' + url + '''\', {
                method: 'POST',
                headers: headers,
                body: JSON.stringify(''' + body + ''')
            });
    
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
    
            const data = await response.json();
            return data; // просто возвращаем данные
        } catch (error) {
            console.error('Ошибка:', error);
        }
    }
    
    const result_post = await fetchGoodsList();
    console.log(result_post);
    '''
    return requset


def GET(url, id_element):
    id_element = str(id_element)
    """Отправка ПОСТ запроса application/json"""
        
    requset = '''
    // Получаем CSRF-токен из куки
    function getCsrfToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrfToken') {
                return value;
            }
        }
        return '';
    }
    
    // Альтернативно: ищем токен в meta-тегах
    function getCsrfTokenFromMeta() {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        return metaTag ? metaTag.content : '';
    }
    
    // Основная функция запроса
    async function fetchGoodsList() {
        const csrfToken = getCsrfToken() || getCsrfTokenFromMeta();
        const headers = {
            "Content-Type": "application/json"
        };
        if (csrfToken) {
            headers["X-CSRF-Token"] = csrfToken;
        }
    
        try {
            const response = await fetch(\'''' + url + id_element + '''\', {
                method: 'GET',
                headers: headers
            });
    
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
    
            const data = await response.json();
            return data; // просто возвращаем данные
        } catch (error) {
            console.error('Ошибка:', error);
        }
    }
    
    const result_get = await fetchGoodsList();
    console.log(result_get);
    '''
    return requset