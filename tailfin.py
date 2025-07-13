import os
import sys
import subprocess
from openai import OpenAI
import google.generativeai as genai
import colorama
from colorama import Fore, Style


colorama.init(autoreset=True)


API_KEYS = {
    'openai': "",    # ChatGPT
    'deepseek': "",  # Deepseek
    'gemini': ""     # Gemini
}

class Terminal:
    def __init__(self):
        self.current_ai = None
        self.clients = {
            'chatgpt': None,
            'deepseek': None,
            'gemini': None
        }
        self.init_clients()
    
    def init_clients(self):

        try:
            if API_KEYS['openai']:
                self.clients['chatgpt'] = OpenAI(api_key=API_KEYS['openai'])
            if API_KEYS['deepseek']:
                self.clients['deepseek'] = OpenAI(
                    api_key=API_KEYS['deepseek'],
                    base_url="https://api.deepseek.com/v1"
                )
            if API_KEYS['gemini']:
                genai.configure(api_key=API_KEYS['gemini'])
                self.clients['gemini'] = genai.GenerativeModel('gemini-pro')
        except Exception as e:
            print(f"{Fore.RED}[!] Ошибка API: {str(e)}")

    def clear_screen(self):

        os.system('cls' if os.name == 'nt' else 'clear')

    def print_logo(self):

        print(Fore.BLUE + r"""
  _______      _ _  ______ _____ 
 |__   __|    | | | |  ___|_   _|
    | | _ __ | | | | |_    | |  
    | || '_ \| | | |  _|   | |  
    | || | | | | | | |    _| |_ 
    |_||_| |_|_|_|_|_|    \___/ 
        """)
        print(Fore.GREEN + "# Tailfin Terminal")
        print(Fore.YELLOW + "# Доступные AI: ChatGPT, Deepseek, Gemini")
        print(Style.RESET_ALL + "-" * 50)

    def print_prompt(self):

        if self.current_ai:
            return input(f"user@tailfin:[{self.current_ai}]$ ")
        return input("user@tailfin:~$ ")

    def chat_session(self, ai_name):

        self.current_ai = ai_name
        client = self.clients.get(ai_name.lower())
        
        if not client:
            api_key = input(f"{Fore.YELLOW}Введите API ключ для {ai_name}:{Style.RESET_ALL} ")
            if not api_key:
                print(f"{Fore.RED}[!] API ключ не может быть пустым!")
                return
            
            try:
                if ai_name.lower() == 'gemini':
                    genai.configure(api_key=api_key)
                    client = genai.GenerativeModel('gemini-pro')
                else:
                    base_url = "https://api.deepseek.com/v1" if ai_name.lower() == 'deepseek' else None
                    client = OpenAI(api_key=api_key, base_url=base_url)
                self.clients[ai_name.lower()] = client
            except Exception as e:
                print(f"{Fore.RED}[!] Ошибка подключения: {str(e)}")
                return
        
        print(f"{Fore.GREEN}[+] Сессия {ai_name} запущена (выход: 'exit')")
        
        messages = []
        if ai_name.lower() != 'gemini':
            messages.append({"role": "system", "content": "You are a helpful assistant."})
        
        while True:
            try:
                user_input = self.print_prompt()
                if not user_input:
                    continue
                if user_input.lower() == 'exit':
                    break
                
                if ai_name.lower() == 'gemini':
                    response = client.generate_content(user_input)
                    print(f"{Fore.CYAN}AI: {response.text}{Style.RESET_ALL}")
                else:
                    messages.append({"role": "user", "content": user_input})
                    model = "deepseek-chat" if ai_name.lower() == 'deepseek' else "gpt-3.5-turbo"
                    response = client.chat.completions.create(
                        model=model,
                        messages=messages
                    )
                    ai_response = response.choices[0].message.content
                    print(f"{Fore.CYAN}AI: {ai_response}{Style.RESET_ALL}")
                    messages.append({"role": "assistant", "content": ai_response})
            
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}[!] Для выхода введите 'exit'")
            except Exception as e:
                print(f"{Fore.RED}[!] Ошибка: {str(e)}")
        
        self.current_ai = None
        print(f"{Fore.GREEN}[+] Сессия {ai_name} завершена")

    def command_mode(self):

        print(f"\n{Fore.GREEN}[+] Режим командной строки (выход: 'back')")
        
        while True:
            try:
                cmd = self.print_prompt()
                if not cmd:
                    continue
                if cmd.lower() == 'back':
                    break
                
                if cmd.lower() == 'clear':
                    self.clear_screen()
                    self.print_logo()
                    continue
                
                result = subprocess.run(
                    cmd, 
                    shell=True, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8'
                )
                
                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    print(f"{Fore.RED}[!] {result.stderr}")
            
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}[!] Для выхода введите 'back'")
            except Exception as e:
                print(f"{Fore.RED}[!] Ошибка: {str(e)}")

    def show_help(self):

        help_text = f"""
{Fore.YELLOW}# Доступные команды:
chatgpt    - Чат с ChatGPT
deepseek   - Чат с Deepseek
gemini     - Чат с Google Gemini
cmd        - Режим командной строки
clear      - Очистить экран
help       - Показать справку
exit       - Выход

{Fore.YELLOW}# Примеры:
user@tailfin:~$ chatgpt
user@tailfin:~$ cmd
user@tailfin:~$ dir
"""
        print(help_text)

    def run(self):

        self.clear_screen()
        self.print_logo()
        
        while True:
            try:
                user_input = self.print_prompt()
                if not user_input:
                    continue
                
                if user_input.lower() == 'exit':
                    print(f"{Fore.GREEN}[+] Завершение работы...")
                    break
                
                elif user_input.lower() == 'clear':
                    self.clear_screen()
                    self.print_logo()
                
                elif user_input.lower() == 'chatgpt':
                    self.chat_session('ChatGPT')
                
                elif user_input.lower() == 'deepseek':
                    self.chat_session('Deepseek')
                
                elif user_input.lower() == 'gemini':
                    self.chat_session('Gemini')
                
                elif user_input.lower() == 'cmd':
                    self.command_mode()
                
                elif user_input.lower() == 'help':
                    self.show_help()
                
                else:
                    print(f"{Fore.RED}[!] Неизвестная команда. Введите 'help'")
            
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}[!] Для выхода введите 'exit'")
            except Exception as e:
                print(f"{Fore.RED}[!] Ошибка: {str(e)}")

if __name__ == "__main__":
    try:
        terminal = Terminal()
        terminal.run()
    except Exception as e:
        print(f"{Fore.RED}[!] Критическая ошибка: {str(e)}")
        sys.exit(1)
