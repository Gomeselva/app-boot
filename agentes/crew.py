import os
from crewai import Agent, Task, Crew, Process
from transformers import pipeline

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# Ferramenta personalizada de processamento de áudio
class AudioProcessingTool:
    """
    Ferramenta que processa áudio: transcrição e tradução.
    """

    def __init__(self):
        self.name = "audio_processing_tool"
        self.description = "Transcreve mensagens de áudio e traduz para inglês e espanhol."
        # Inicializar modelos de transcrição e tradução
        self.transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-large")
        self.translator_en = pipeline("translation", model="Helsinki-NLP/opus-mt-mul-en")
        self.translator_es = pipeline("translation", model="Helsinki-NLP/opus-mt-en-es")

    def func(self, audio_url: str) -> str:
        """
        Processa áudio: transcreve e traduz para inglês e espanhol.
        """
        try:
            transcription = self.transcriber(audio_url)["text"]
            translation_en = self.translator_en(transcription)[0]["translation_text"]
            translation_es = self.translator_es(transcription)[0]["translation_text"]
            return (
                f"Texto original: {transcription}\n"
                f"Tradução para inglês: {translation_en}\n"
                f"Tradução para espanhol: {translation_es}"
            )
        except Exception as e:
            return f"Erro ao processar áudio: {e}"


# Ferramenta de processamento de mensagens
class MessageProcessingTool:
    def __init__(self, text_agent, voice_agent):
        self.text_agent = text_agent
        self.voice_agent = voice_agent

    def process_message(self, json_data: dict) -> str:
        """
        Identifica e processa mensagens (texto, áudio, etc.) a partir de um JSON.
        """
        try:
            payload = json_data.get("payload", {})
            body = payload.get("body", "")
            has_media = payload.get("hasMedia", False)
            media = payload.get("media", {})
            media_url = media.get("url", "")

            if has_media and media_url and "audio" in media.get("mimetype", ""):
                print("Mensagem identificada como áudio.")
                return self.voice_agent.tools[0].func(media_url)
            elif body:
                print("Mensagem identificada como texto.")
                return f"Texto recebido: {body}\n[Traduzir utilizando outro agente]"
            else:
                return "Mensagem não contém áudio ou texto processável."
        except Exception as e:
            return f"Erro no processamento da mensagem: {e}"


# Processador principal
class FlexibleMessageProcessor:
    def __init__(self):
        # Criar a ferramenta de áudio
        audio_tool = AudioProcessingTool()

        # Agente para processamento de áudio
        self.voice_agent = Agent(
            role="Transcritor de Voz",
            goal="Transcrever mensagens de voz para texto em inglês e espanhol.",
            backstory="Especialista em transcrição e tradução de áudio.",
            tools=[audio_tool],
        )

        # Configuração de outros agentes e tarefas
        self.text_agent = Agent(
            role="Tradutor de Texto",
            goal="Traduzir mensagens de texto para inglês e espanhol.",
            backstory="Especialista em tradução eficiente e precisa.",
        )

        # Configuração da tarefa de processamento
        self.process_task = Task(
            description="Interpretar e processar mensagens de maneira flexível.",
            expected_output="Mensagem processada de acordo com seu tipo.",
            agent=self.voice_agent,
        )

        # Configurar a Crew
        self.crew = Crew(
            agents=[self.voice_agent, self.text_agent],
            tasks=[self.process_task],
            process=Process.sequential,
        )

    def process_message(self, json_data):
        """
        Executa o processamento da mensagem.
        """
        return self.crew.kickoff(inputs={"mensagem": json_data})


# Testando a integração
if __name__ == "__main__":
    processor = FlexibleMessageProcessor()

    # Exemplo de entrada JSON esperado
    json_data = {
        "id": "evt_01jhxf1m36yzazag8tg5vx3yc9",
        "event": "message",
        "session": "default",
        "metadata": {},
        "me": {"id": "5521996892345@c.us", "pushName": "Finance_ai"},
        "payload": {
            "id": "false_17712179403@c.us_3A00059EC2FAB9438A77",
            "timestamp": 1737229388,
            "from": "17712179403@c.us",
            "fromMe": False,
            "to": "5521996892345@c.us",
            "body": "",
            "hasMedia": True,
            "media": {
                "url": "http://localhost:3000/api/files/default/false_17712179403@c.us_3A00059EC2FAB9438A77.oga",
                "filename": None,
                "mimetype": "audio/ogg; codecs=opus",
            },
            "mediaUrl": "http://localhost:3000/api/files/default/false_17712179403@c.us_3A00059EC2FAB9438A77.oga",
        },
        "engine": "WEBJS",
        "environment": {
            "version": "2025.1.3",
            "engine": "WEBJS",
            "tier": "CORE",
            "browser": "/usr/bin/chromium",
        },
    }

    # Processar mensagem
    result = processor.process_message(json_data)
    print("Resultado do processamento:")
    print(result)