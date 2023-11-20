from googletrans import Translator, LANGUAGES

translator = Translator()

text = input("번역할 문장을 입력하세요: ")
print(LANGUAGES)
target_language = input("번역하고자 하는 언어코드를 입력하세요: ")

translated = translator.translate(text, dest=target_language)

print(f"번역결과: {translated.text}")