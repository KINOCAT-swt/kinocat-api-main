import os
import sys
from groq import Groq
from config import config_by_name

class AIServiceError(Exception):
    """Servise ozel bir hata sinifi"""
    pass

class AIService:
    def __init__(self):
        # config_by_name sozlugunden local/development ayarlarini yukluyoruz
        # Uretim ortaminda (Render) 'production' olarak yuklenmesi icin bunu dinamiklestirebilirsiniz:
        env = os.environ.get('FLASK_ENV', 'development')
        self.config = config_by_name[env]
        self.api_key = self.config.GROQ_API_KEY

    def _get_system_instruction(self):
        """Sistem talimatini config'den okuyan yardimci metot"""
        return self.config.BUSINESS_CONTEXT

    def yanit_uret(self, mesaj, gecmis=None):
        """Kullanici mesajini alip Groq API'sine gonderen ve yaniti donduren ana metot"""
        if gecmis is None:
            gecmis = []

        # Yonerge Sabiti: Anahtar yoksa cokmek yerine "demo modu" mesaji dondurme
        if not self.api_key or self.api_key == "demo":
            return "KINOCAT Demo Modu: Sistem baglantisi basarili! Yapay zeka anahtariniz henuz yuklenmedigi icin bu mesaj donmektedir."

        try:
            # self.api_key dogru referans ile cagirildi
            client = Groq(api_key=self.api_key)

            # Sistem talimatini gecmise ekliyoruz
            # self._get_system_instruction dogru referans ile cagirildi
            messages = [{"role": "system", "content": self._get_system_instruction()}]

            # Onceki sohbet gecmisini ekliyoruz
            for m in gecmis:
                messages.append(m)

            # Guncel kullanici mesajini ekliyoruz
            messages.append({"role": "user", "content": mesaj})

            chat_completion = client.chat.completions.create(
                messages=messages,
                model="openai/gpt-oss-120b", # Kullandiginiz model ismi
                temperature=0.7,
                max_tokens=1024
            )

            return chat_completion.choices[0].message.content

        except Exception as e:
            raise AIServiceError(f"Groq API hatasi: {str(e)}")
