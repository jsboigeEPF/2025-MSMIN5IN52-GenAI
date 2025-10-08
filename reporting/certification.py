"""
Système de certification des rapports avec signatures numériques et horodatages.
"""

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.exceptions import InvalidSignature
from datetime import datetime
import json
import base64
import hashlib
from typing import Dict, Any, Optional
import os


class ReportCertifier:
    """
    Gère la certification des rapports avec signatures numériques et horodatages.
    """

    def __init__(self, private_key_path: str = "config/private_key.pem"):
        """
        Initialise le système de certification.

        Args:
            private_key_path (str): Chemin vers la clé privée pour la signature.
        """
        self.private_key_path = private_key_path
        self.private_key = self._load_private_key()
        self.public_key = self.private_key.public_key()

    def _load_private_key(self) -> rsa.RSAPrivateKey:
        """
        Charge la clé privée depuis le fichier.

        Returns:
            rsa.RSAPrivateKey: Clé privée chargée.

        Raises:
            FileNotFoundError: Si le fichier de clé privée n'existe pas.
            ValueError: Si le mot de passe est incorrect ou si la clé est invalide.
        """
        try:
            with open(self.private_key_path, "rb") as key_file:
                private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None,  # Pour simplifier, pas de mot de passe
                )
                return private_key
        except FileNotFoundError:
            # Générer une nouvelle clé si elle n'existe pas
            return self._generate_key_pair()

    def _generate_key_pair(self) -> rsa.RSAPrivateKey:
        """
        Génère une paire de clés RSA et sauvegarde la clé privée.

        Returns:
            rsa.RSAPrivateKey: Clé privée générée.
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        # Créer le répertoire de configuration s'il n'existe pas
        os.makedirs(os.path.dirname(self.private_key_path), exist_ok=True)

        # Sauvegarder la clé privée
        with open(self.private_key_path, "wb") as key_file:
            key_file.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )

        return private_key

    def generate_timestamp(self) -> str:
        """
        Génère un horodatage ISO 8601.

        Returns:
            str: Horodatage au format ISO 8601.
        """
        return datetime.now().isoformat()

    def calculate_hash(self, data: Dict[str, Any]) -> str:
        """
        Calcule le hash SHA-256 des données.

        Args:
            data (Dict[str, Any]): Données à hasher.

        Returns:
            str: Hash SHA-256 encodé en hexadécimal.
        """
        # Convertir les données en chaîne JSON canonique
        json_string = json.dumps(data, sort_keys=True, ensure_ascii=False, indent=None)
        # Calculer le hash
        hash_object = hashlib.sha256(json_string.encode('utf-8'))
        return hash_object.hexdigest()

    def sign_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Signe numériquement un rapport.

        Args:
            report_data (Dict[str, Any]): Données du rapport à signer.

        Returns:
            Dict[str, Any]: Données du rapport avec signature et horodatage.
        """
        # Ajouter l'horodatage
        timestamp = self.generate_timestamp()
        report_data['certification'] = {
            'timestamp': timestamp,
            'hash_algorithm': 'SHA-256'
        }

        # Calculer le hash des données
        data_hash = self.calculate_hash(report_data)

        # Signer le hash
        signature = self.private_key.sign(
            data_hash.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA256()
        )

        # Ajouter la signature encodée en base64
        report_data['certification']['signature'] = base64.b64encode(signature).decode('utf-8')
        report_data['certification']['data_hash'] = data_hash

        return report_data

    def verify_signature(self, certified_report: Dict[str, Any]) -> bool:
        """
        Vérifie la validité de la signature d'un rapport certifié.

        Args:
            certified_report (Dict[str, Any]): Rapport certifié à vérifier.

        Returns:
            bool: True si la signature est valide, False sinon.
        """
        try:
            # Extraire les données de certification
            certification = certified_report.get('certification', {})
            signature_b64 = certification.get('signature')
            timestamp = certification.get('timestamp')
            data_hash = certification.get('data_hash')
            hash_algorithm = certification.get('hash_algorithm')

            if not all([signature_b64, timestamp, data_hash, hash_algorithm]):
                return False

            # Recalculer le hash des données
            # Créer une copie des données sans la signature pour recalculer le hash
            report_copy = certified_report.copy()
            report_copy.pop('certification', None)
            calculated_hash = self.calculate_hash(report_copy)

            # Vérifier que les hashes correspondent
            if calculated_hash != data_hash:
                return False

            # Vérifier la signature
            signature = base64.b64decode(signature_b64)
            self.public_key.verify(
                signature,
                data_hash.encode('utf-8'),
                padding.PKCS1v15(),
                hashes.SHA256()
            )

            return True

        except (KeyError, ValueError, InvalidSignature, Exception):
            return False

    def get_public_key_pem(self) -> str:
        """
        Récupère la clé publique au format PEM.

        Returns:
            str: Clé publique au format PEM.
        """
        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return public_pem.decode('utf-8')