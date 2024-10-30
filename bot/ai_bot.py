import os
from decouple import config

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

os.environ["GROQ_API_KEY"] = config("GROQ_API_KEY")   


class AIbot:
    def __init__(self):
        self.__chat = ChatGroq(model="llama-3.1-70b-versatile")

    def invoke(self, question):

        formato = """"
        texto em espanhol
        ===============
        texto em inglês
        """


        prompt = PromptTemplate(
            input_variables=["texto"],
            template=''''
            Você é um tradutor de textos que traduz o <texto> do usuário para o inglês e o espanhol.
            Não forneça nenhuma outra mensagem, somente o <texto> traduzido no <formato>{formato}<formato>.
            <texto> 
            {texto}
            </texto>'''
        )


        chain = prompt | self.__chat | StrOutputParser()
        response = chain.invoke({
            "texto": question,
            "formato": formato                  
        })
        return response
        



    # ai_bot = AIbot()
    # response = ai_bot.invoke("Olá, como você está?")
    # print(response)