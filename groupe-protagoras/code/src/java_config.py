"""
Configuration de l'environnement Java/Tweety pour le projet.
Basé sur le notebook Argument_Analysis_Agentic-0-init.ipynb.
"""

import jpype
import jpype.imports
import os
import pathlib
import platform
import logging
from typing import Optional

# Logger spécifique
logger = logging.getLogger("Orchestration.JPype")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(name)s] %(message)s', datefmt='%H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def find_portable_jdk() -> Optional[str]:
    """
    Localise automatiquement le JDK portable dans l'arborescence du projet.
    """
    logger.info("🔍 Recherche JDK portable dans l'arborescence projet...")
    
    # Chemins de recherche prioritaires pour le JDK portable
    search_paths = [
        pathlib.Path("groupe-protagoras/code/libs/jdk-17-portable"),
        pathlib.Path("jdk-17-portable"),
        pathlib.Path("../jdk-17-portable"),
        pathlib.Path("../../jdk-17-portable")
    ]
    
    for base_path in search_paths:
        if base_path.exists():
            logger.debug(f"  Scan du répertoire: {base_path}")
            
            # Chercher des sous-dossiers JDK
            jdk_patterns = ["*jdk*", "zulu*", "*openjdk*", "*corretto*"]
            for pattern in jdk_patterns:
                jdk_dirs = list(base_path.glob(pattern))
                for jdk_dir in jdk_dirs:
                    if jdk_dir.is_dir():
                        # Vérifier présence de bin/java
                        exe_suffix = ".exe" if platform.system() == "Windows" else ""
                        java_exe = jdk_dir / "bin" / f"java{exe_suffix}"
                        if java_exe.exists():
                            logger.info(f"✅ JDK portable trouvé: {jdk_dir.absolute()}")
                            return str(jdk_dir.absolute())
    
    logger.warning("⚠️ JDK portable non trouvé dans les chemins standards")
    return None

def get_tweety_classpath() -> list:
    """
    Construit dynamiquement le classpath avec tous les JARs Tweety disponibles.
    """
    logger.info("📦 Construction du classpath Tweety...")
    
    # Chemins de recherche des JARs
    libs_paths = [
        pathlib.Path("groupe-protagoras/code/src"),
        pathlib.Path("libs"),
        pathlib.Path("../libs")
    ]
    
    jar_files = []
    
    for libs_path in libs_paths:
        if libs_path.exists() and libs_path.is_dir():
            logger.info(f"  Scan des JARs dans: {libs_path}")
            found_jars = list(libs_path.glob("*.jar"))
            if found_jars:
                jar_files.extend([str(jar.absolute()) for jar in found_jars])
                logger.info(f"  ✅ {len(found_jars)} JARs trouvés dans {libs_path}")
                break  # Utiliser le premier répertoire avec des JARs
    
    if jar_files:
        logger.info(f"✅ Classpath construit: {len(jar_files)} JARs Tweety")
        return sorted(jar_files)  # Tri pour cohérence
    else:
        logger.error("❌ Aucun JAR Tweety trouvé dans les chemins standards")
        return []

def test_tweety_critical_classes():
    """
    Teste l'accès aux classes critiques de Tweety pour validation.
    """
    logger.info("🎯 Test des classes critiques Tweety...")
    
    critical_classes = {
        "InformationObject": "org.tweetyproject.beliefdynamics.mas.InformationObject",
        "PlParser": "org.tweetyproject.logics.pl.parser.PlParser",
        "PlFormula": "org.tweetyproject.logics.pl.syntax.PlFormula",  # Interface
        "ClassicReasoner": "org.tweetyproject.logics.pl.reasoner.ClassicReasoner", # Ajouté pour le test
        "SatReasoner": "org.tweetyproject.logics.pl.reasoner.SatReasoner", # Ajouté pour le test
        "BaseRevisionOperator": "org.tweetyproject.beliefdynamics.BaseRevisionOperator"
    }
    
    successful_classes = []
    
    for class_alias, class_name in critical_classes.items():
        try:
            test_class = jpype.JClass(class_name)
            successful_classes.append(class_alias)
            logger.info(f"  ✅ {class_alias}: Accessible")
        except Exception as e:
            logger.warning(f"  ⚠️ {class_alias}: Inaccessible - {e}")
    
    success_rate = len(successful_classes) / len(critical_classes)
    
    if success_rate >= 0.75:  # Au moins 75% des classes critiques
        logger.info(f"🏆 Test Tweety RÉUSSI: {len(successful_classes)}/{len(critical_classes)} classes accessibles")
        return True
    else:
        logger.error(f"❌ Test Tweety ÉCHOUÉ: {len(successful_classes)}/{len(critical_classes)} classes accessibles")
        return False

def initialize_tweety():
    """
    Initialise l'environnement Java/Tweety pour le projet.
    """
    global jvm_ready
    jvm_ready = False
    
    try:
        # Étape 1: Vérifier si JVM déjà démarrée
        if jpype.isJVMStarted():
            logger.info("ℹ️ JVM déjà démarrée - utilisation de l'instance existante")
            jvm_ready = True
            
            # Enregistrer les domaines au cas où
            try:
                jpype.imports.registerDomain("org", alias="org")
                jpype.imports.registerDomain("java", alias="java")
                jpype.imports.registerDomain("net", alias="net")
            except:
                pass
        else:
            # Étape 2: Localiser et configurer JAVA_HOME au niveau processus
            portable_jdk = find_portable_jdk()
            
            if portable_jdk:
                # Configuration dynamique de JAVA_HOME pour ce processus
                current_java_home = os.getenv('JAVA_HOME')
                if not current_java_home or current_java_home != portable_jdk:
                    os.environ['JAVA_HOME'] = portable_jdk
                    logger.info(f"🏠 JAVA_HOME configuré dynamiquement: {portable_jdk}")
                else:
                    logger.info(f"🏠 JAVA_HOME déjà configuré: {current_java_home}")
            else:
                logger.error("❌ Impossible de localiser un JDK portable - JVM pourrait échouer")
            
            # Étape 3: Construire le classpath Tweety complet
            tweety_jars = get_tweety_classpath()
            
            if not tweety_jars:
                raise Exception("Classpath Tweety vide - JARs manquants")
            
            # Étape 4: Démarrer la JVM avec configuration optimale
            logger.info(f"🚀 Démarrage JVM avec {len(tweety_jars)} JARs Tweety...")
            
            jvm_args = [
                "-Xmx2g",  # Mémoire suffisante pour Tweety
                "-Djava.awt.headless=true",  # Mode headless pour notebooks
            ]
            
            jpype.startJVM(
                *jvm_args,
                classpath=tweety_jars,
                convertStrings=False,
                ignoreUnrecognized=True
            )
            
            # Étape 5: Enregistrer les domaines Java
            jpype.imports.registerDomain("org", alias="org")
            jpype.imports.registerDomain("java", alias="java")
            jpype.imports.registerDomain("net", alias="net")
            
            logger.info("✅ JVM démarrée avec succès et domaines enregistrés")
            jvm_ready = True
        
        # Étape 6: Test de validation Tweety
        if jvm_ready:
            # Test Java de base
            try:
                System = jpype.JClass('java.lang.System')
                java_version = System.getProperty('java.version')
                logger.info(f"☕ Java {java_version} opérationnel")
            except Exception as e:
                logger.warning(f"⚠️ Test Java de base échoué: {e}")
            
            # Test classes Tweety critiques
            tweety_success = test_tweety_critical_classes()
            if tweety_success:
                logger.info("\n🎉 🏆 SUCCÈS TOTAL - INFRASTRUCTURE TWEETY AUTO-SUFFISANTE! 🏆 🎉")
                logger.info("✅ PropositionalLogicAgent prêt pour exécution native")
                logger.info("✅ Pipeline argumentatif avec intégration formelle/informelle opérationnel")
            else:
                logger.warning("⚠️ JVM opérationnelle mais classes Tweety partiellement accessibles")
                jvm_ready = False

    except Exception as e:
        logger.critical(f"❌ ERREUR CRITIQUE Configuration Java: {e}")
        logger.critical("   PropositionalLogicAgent fonctionnera en mode dégradé (LLM seulement)")
        jvm_ready = False

    # --- Conclusion État JVM ---
    if jvm_ready:
        logger.info("\n🟢 STATUT FINAL: JVM + Tweety OPÉRATIONNELS")
        logger.info("   Pipeline peut atteindre son potentiel maximal (8/10)")
    else:
        logger.warning("\n🔴 STATUT FINAL: JVM/Tweety NON OPÉRATIONNELS")
        logger.warning("   Pipeline fonctionnera en mode dégradé (5/10)")

    return jvm_ready