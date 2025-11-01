import sys, httpx, os
sys.dont_write_bytecode = True

from dotenv import load_dotenv

from langchain_openai.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage

load_dotenv()

DATA_PATH = os.getenv("DATA_PATH")
FAISS_PATH = os.getenv("FAISS_PATH")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
RAG_K_THRESHOLD = 5
LLM_MODEL = "gpt-35-turbo"
CUSTOMED_ENDPOINT = "https://aalto-openai-apigw.azure-api.net"


class ChatBot():
  def __init__(self, api_key: str, model: str):
    self.llm = ChatOpenAI(
      model=model, 
      api_key=api_key, 
      temperature=0.1
    )

  def generate_subquestions(self, question: str):
    system_message = SystemMessage(content="""
      Tu es un expert en acquisition de talents. Sépare cette description de poste en 3 à 4 aspects plus ciblés afin de faciliter la recherche de CV pertinents.
      Assure-toi que chaque aspect important de la requête est couvert dans au moins une sous-requête. Tu peux supprimer les informations inutiles pour la recherche de CV, telles que le salaire prévu, l'ID du poste, la durée du contrat, etc.
      Utilise uniquement les informations de la description initiale. N'invente aucun critère.
      Mets chaque sous-requête sur une ligne séparée.
      """)
    
    user_message = HumanMessage(content=f"""
      Génère 3 à 4 sous-requêtes basées sur cette description de poste :
      {question}
    """)

    oneshot_example = HumanMessage(content="""
      Génère 3 à 4 sous-requêtes basées sur cette description de poste :

      Wordpress Developer
      (exemple conservé tel quel volontairement)
    """)

    oneshot_response = AIMessage(content="""
      1. Compétences Développeur WordPress :
        - WordPress, technologies front-end (CSS3, JavaScript, HTML5, jQuery), outils de débogage (Chrome Inspector, Firebug), outils de versioning (Git, Mercurial, SVN).
        - Expérience requise : 3 ans WordPress, 2 ans web design.
    
      2. Responsabilités Développeur WordPress :
        - Rencontre avec les clients, conception front-end, création d'architecture, intégration base de données/serveur, génération de thèmes/plugins, tests de performance, résolution de problèmes, formation client, suivi du site en production.

      3. Exigences supplémentaires :
        - Diplôme Licence informatique ou similaire, expérience confirmée, compréhension architecture web, gestion de projet, communication.

      4. Compétences et qualifications :
        - Compétences front-end, outils Git, debugging, communication, gestion.
    """)

    response = self.llm.invoke([system_message, oneshot_example, oneshot_response, user_message])
    result = response.content.split("\n\n")
    return result

  def generate_message_stream(self, question: str, docs: list, history: list, prompt_cls: str):
    context = "\n\n".join(doc for doc in docs)
    
    if prompt_cls == "retrieve_applicant_jd":
      system_message = SystemMessage(content="""
        Tu es un expert en recrutement chargé de déterminer le meilleur candidat parmi plusieurs CV adaptés.
        Utilise les informations fournies pour identifier le meilleur profil correspondant à la description de poste.
        Fournis des explications détaillées pour justifier ton choix.
        Comme plusieurs candidats peuvent avoir des noms similaires, utilise l'ID candidat dans ta réponse.
        Si tu ne sais pas, dis-le. N'invente jamais de réponse.
      """)

      user_message = HumanMessage(content=f"""
        Historique de conversation : {history}
        Contexte : {context}
        Question : {question}
      """)

    else:
      system_message = SystemMessage(content="""
        Tu es un expert en recrutement chargé d'analyser des CV pour aider au tri des candidatures.
        Utilise le contexte et l'historique pour répondre.
        Ne mentionne jamais que tu reçois un historique ou un contexte externe.
        Si tu ne sais pas, dis-le. N'invente rien.
      """)

      user_message = HumanMessage(content=f"""
        Historique : {history}
        Question : {question}
        Contexte : {context}
      """)

    stream = self.llm.stream([system_message, user_message])
    return stream
