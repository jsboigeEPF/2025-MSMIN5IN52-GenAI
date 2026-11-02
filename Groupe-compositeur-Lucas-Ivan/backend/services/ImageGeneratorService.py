import requests
import os

class ImageGeneratorService:
    def __init__(self):
        self.output_dir = "generated_images"
        os.makedirs(self.output_dir, exist_ok=True)
        print("🎨 Service de génération d'images initialisé")
    
    def generate_image(self, description, generation_id):
        """
        Génère une image à partir d'une description
        Utilise l'API Pollinations.ai (gratuite, sans clé)
        """
        try:
            # Formater la description : remplacer espaces par underscores
            prompt = description.replace(" ", "_").replace(",", "").lower()
            
            # Construire l'URL
            url = f"https://pollinations.ai/p/{prompt}"
            
            print(f"🎨 Génération d'image pour : {description}")
            print(f"   URL : {url}")
            
            # Télécharger l'image
            response = requests.get(url, timeout=120)
            response.raise_for_status()
            
            # Sauvegarder l'image
            image_path = f"{self.output_dir}/image_{generation_id}.jpg"
            with open(image_path, 'wb') as file:
                file.write(response.content)
            
            print(f"✅ Image sauvegardée : {image_path}")
            
            return {
                "success": True,
                "image_path": image_path,
                "prompt": description
            }
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur lors de la génération d'image : {e}")
            return {
                "success": False,
                "error": str(e),
                "image_path": None
            }
        except Exception as e:
            print(f"❌ Erreur inattendue : {e}")
            return {
                "success": False,
                "error": str(e),
                "image_path": None
            }