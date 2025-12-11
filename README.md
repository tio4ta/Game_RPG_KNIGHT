# ⚔️ L'Ascension du Héros : Mini-RPG Textuel

Ce projet est une implémentation d'un mini-RPG (Role-Playing Game) de combat au tour par tour, développé en Python avec la bibliothèque Pygame. Il combine des mécaniques de combat, de gestion d'inventaire, d'équipement et de progression par niveaux et étages.

---

## 🚀 Fonctionnalités Principales

* **Système de Combat au Tour par Tour :** Affrontez des ennemis standards et des boss.
* **Progression du Personnage :** Gain d'expérience (XP), montée de niveau, et amélioration des statistiques.
* **Classes de Personnage :** Choisissez parmi le **Guerrier** (Attaque/Critique), le **Tank** (Défense/PV), et le **Mage** (Soins améliorés).
* **Gestion de l'Équipement :** Équipez des armes et armures (Casque, Plastron, Jambières, Bottes) pour augmenter votre Attaque et Défense.
* **Inventaire et Magasin :** Ramassez du butin (loot), utilisez des potions, gérez votre inventaire et achetez de nouveaux objets.
* **Boss Fights et Mécaniqes Spéciales :** Les boss ont des mécaniques uniques (charge d'attaque) et le joueur peut recevoir des bonus temporaires avant le combat.
* **Sauvegarde et Chargement :** Sauvegardez et chargez votre progression pour reprendre l'aventure plus tard.
* **Interface Utilisateur Simple (Pygame) :** Barres de vie, popups de dégâts, et journal d'actions (log) en temps réel.

---

## 🛠️ Configuration et Lancement

### Prérequis

Assurez-vous d'avoir Python installé (version 3.6+ recommandée).

1.  **Installez Pygame :**
    ```bash
    pip install pygame
    ```

### Structure des Fichiers

Pour que le jeu fonctionne, vous devez créer l'arborescence suivante :

RPGV19.5.py  (ou le nom de votre fichier principal)assets/background.jpgforest_bg.jpgboss_bg.jpgpoubelle.pnghero1.png (Guerrier)hero2.png (Tank)hero3.png (Mage)goblin.png (Ennemi par défaut)boss_*.png (Bosses, si vous en avez)guerrier.png (Image Game Over)tank.png (Image Game Over)mage.png (Image Game Over)saves/(Contiendra les fichiers de sauvegarde au format JSON)*(**Note :** Le code contient des substituts visuels au cas où les images réelles (`assets/`) ne seraient pas trouvées.)*

### Lancer le Jeu

Exécutez le script principal dans votre terminal :

```bash
python RPGV19.5.py
🎮 Commandes et Raccourcis ClavierLe jeu est jouable à la fois à la souris (clics sur les boutons) et au clavier.ÉcranActionRaccourci ClavierMenu PrincipalNouvelle PartieNCharger PartieCQuitterQ ou ESCCombatAttaquer1Défendre2Utiliser Potion3FuirFSauvegarderSInventaireIMagasinMGénéralPause/Menu PrincipalESCMenu Victoire/Mort/FuiteContinuer/Retour au MenuA ou ENTERInventaire/MagasinRetour au CombatESC ou I/M💡 Remarques sur le CodeCorrection Critique : La version actuelle (V19.5) inclut la correction de l'erreur AttributeError: 'GameEngine' object has no attribute 'check_level_up'. La vérification de niveau est maintenant correctement effectuée sur l'objet Player.Modularité : Le code est organisé en classes (Character, Enemy, GameEngine, Button) pour une meilleure gestion de la logique et de l'état du jeu.UI : Les classes DamagePopup et InfoPopup gèrent l'affichage dynamique des dégâts et des messages d'information en combat.Équilibrage : Les statistiques des ennemis et l'XP nécessaire pour monter de niveau sont ajustés dynamiquement en fonction de l'étage (stage).
