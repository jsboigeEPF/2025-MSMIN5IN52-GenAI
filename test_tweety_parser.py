import jpype
import jpype.imports
import os
import pathlib

# Démarrage de la JVM (comme dans ton projet)
if not jpype.isJVMStarted():
    # Utiliser la même logique de découverte de JAR que java_config.py pour la robustesse
    jar_dir = pathlib.Path("groupe-protagoras/code/src")
    if not jar_dir.exists():
        raise FileNotFoundError(f"Le répertoire des JARs Tweety est introuvable: {jar_dir.absolute()}")

    jars = [str(p) for p in jar_dir.glob("*.jar")]
    if not jars:
        raise FileNotFoundError(f"Aucun fichier .jar trouvé dans {jar_dir.absolute()}")

    print(f"INFO: Démarrage de la JVM avec le classpath: {jars}")
    jpype.startJVM(classpath=jars)

PlParser = jpype.JClass("org.tweetyproject.logics.pl.parser.PlParser")

parser = PlParser()

tests = ["A&~B", "A & ~B", "A->B", "A -> B", "A=>B", "A => B", "!(A&B)", "not (A & B)", "A|B", "A | B", "(A | B)"]

for f in tests:
    try:
        parsed = parser.parseFormula(f)
        print(f"✅ OK: '{f}' \t→ {parsed}")
    except Exception as e:
        print(f"❌ FAIL: '{f}' \t→ {e.__class__.__name__}")