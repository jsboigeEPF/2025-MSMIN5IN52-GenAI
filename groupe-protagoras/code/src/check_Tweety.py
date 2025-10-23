import jpype
import jpype.imports
from jpype.types import *

# Démarre la JVM si elle n'est pas déjà lancée
if not jpype.isJVMStarted():
    jar_path = "C:/Users/julie/Documents/5A/GenAI Projet 4/2025-MSMIN5IN52-GenAI/groupe-protagoras/code/src/tweetyproject-full-with-dependencies-1.29.jar"
    jpype.startJVM(classpath=[jar_path])
    print("✅ JVM initialisée avec TweetyProject.")
