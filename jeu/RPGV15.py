import pygame, sys, os, json, random
from typing import Optional, Dict, Any, List

# Initialisation de Pygame
pygame.init()
pygame.font.init()

# -----------------------
# Settings & utilities
# -----------------------
# Variables globales pour la fenêtre
WIDTH, HEIGHT = 1000, 640
WIN = None # Sera initialisé plus tard
FULLSCREEN = False

FPS = 60
FONT_SIZE_SM = 18
FONT_SIZE_MD = 24
FONT_SIZE_LG = 36

FONT = pygame.font.SysFont("Arial", FONT_SIZE_SM)
MED_FONT = pygame.font.SysFont("Arial", FONT_SIZE_MD)
BIG_FONT = pygame.font.SysFont("Arial", FONT_SIZE_LG)

ASSETS_DIR = "assets"
SAVE_DIR = "saves"
os.makedirs(SAVE_DIR, exist_ok=True) 

# COULEURS (Inchangé)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (70, 130, 180) 
DARK_BLUE = (30, 70, 100) 
GREY_BUTTON = (90, 90, 90)
GOLD = (255, 215, 0) 

# Liste globale pour les popups de dégâts
ALL_POPUPS: List['DamagePopup'] = []

def load_image(name: str, size=None):
    """Charge une image depuis le dossier assets et la redimensionne."""
    path = os.path.join(ASSETS_DIR, name)
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.smoothscale(img, size)
        return img
    except Exception:
        w, h = size or (160, 160)
        surf = pygame.Surface((w, h))
        
        is_boss_missing = "boss_" in name
        is_gameover_missing = name in ("guerrier.png", "tank.png", "mage.png")

        fill_color = (120, 0, 0) if is_boss_missing else ((50, 50, 50) if is_gameover_missing else (120, 120, 120))
        txt_color = YELLOW if is_boss_missing or is_gameover_missing else WHITE
        
        surf.fill(fill_color)
        txt = FONT.render(f"{name} MISSING", True, txt_color)
        surf.blit(txt, (5, 5))
        return surf

def load_global_assets():
    """Charge ou recharge tous les assets globaux (fonds, icônes) avec les dimensions actuelles."""
    global BG_MENU, BG_BATTLE, BG_BOSS, ICON_DELETE
    BG_MENU = load_image("background.jpg", (WIDTH, HEIGHT))
    BG_BATTLE = load_image("forest_bg.jpg", (WIDTH, HEIGHT))
    BG_BOSS = load_image("boss_bg.jpg", (WIDTH, HEIGHT))
    ICON_DELETE = load_image("poubelle.png", (30, 30))

def setup_window(w, h, fs):
    """Initialise ou reconfigure la fenêtre du jeu (plein écran ou fenêtré)."""
    global WIN, WIDTH, HEIGHT, FULLSCREEN
    WIDTH, HEIGHT = w, h
    FULLSCREEN = fs
    
    flags = pygame.SCALED
    if fs:
        flags |= pygame.FULLSCREEN
        screen_info = pygame.display.Info()
        WIDTH, HEIGHT = screen_info.current_w, screen_info.current_h
        
    WIN = pygame.display.set_mode((WIDTH, HEIGHT), flags)
    pygame.display.set_caption("Mini RPG - V19.2") # Mise à jour de la version
    
    # Recharger les fonds d'écran avec les nouvelles dimensions
    load_global_assets()
    
# Initialisation initiale
setup_window(1000, 640, False)

def draw_text(surface, text, x, y, font=FONT, color=WHITE, center=False):
    """Dessine le texte avec une option de centrage."""
    text_surface = font.render(text, True, color)
    if center:
        x -= text_surface.get_width() // 2
    surface.blit(text_surface, (x, y))
    
def wrap_text(surface, text: str, max_width: int, x: int, y: int, font=FONT, color=WHITE, center=False, line_spacing=20) -> int:
    """Dessine un texte qui s'enroule sur plusieurs lignes, et retourne la position Y finale."""
    words = text.split(' ')
    wrapped_lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + word + " "
        test_surface = font.render(test_line, True, color)
        
        if test_surface.get_width() <= max_width:
            current_line = test_line
        else:
            wrapped_lines.append(current_line.strip())
            current_line = word + " "
            
    wrapped_lines.append(current_line.strip())

    current_y = y
    for line in wrapped_lines:
        if center:
            line_surface = font.render(line, True, color)
            line_x = x - line_surface.get_width() // 2
            surface.blit(line_surface, (line_x, current_y))
        else:
            draw_text(surface, line, x, current_y, font, color, center=False)
            
        current_y += line_spacing
        
    return current_y

def clamp(v, a, b): return max(a, min(b, v))

def get_all_saves():
    """Lit tous les fichiers save_*.json et retourne le nom du joueur, niveau, et stage."""
    saves = []
    for filename in os.listdir(SAVE_DIR):
        if filename.startswith("save_") and filename.endswith("json"):
            filepath = os.path.join(SAVE_DIR, filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                saves.append({
                    "filename": filename,
                    "name": data.get("name", "Inconnu"),
                    "level": data.get("level", 1),
                    "stage": data.get("stage", 1),
                })
            except Exception:
                pass
    return saves

# -----------------------
# Classes de l'interface utilisateur (Inchangé)
# -----------------------
class DamagePopup(pygame.sprite.Sprite):
    # ... (Code inchangé)
    def __init__(self, x, y, value, color=(255, 255, 255), is_crit=False):
        super().__init__()
        
        self.value = value
        self.font = BIG_FONT if is_crit else MED_FONT
        self.color = color
        self.image = self.font.render(str(self.value), True, self.color)
        self.rect = self.image.get_rect(center=(x, y))
        self.lifetime = 60
        self.y_vel = -0.5

    def update(self):
        self.lifetime -= 1
        self.rect.y += self.y_vel
        self.y_vel += 0.05
        
        if self.lifetime < 10:
            alpha = int(clamp(self.lifetime * 25, 0, 255))
            self.image.set_alpha(alpha)
            
        if self.lifetime <= 0:
            self.kill()

class Button:
    # ... (Code inchangé)
    def __init__(self, text, rect, active=True, color=BLUE, hover_color=DARK_BLUE, text_font=MED_FONT, text_color=WHITE):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.active = active
        self.color = color
        self.hover_color = hover_color
        self.font = text_font
        self.base_text_color = text_color
        
    def draw(self, surface):
        current_color = self.color
        text_color = self.base_text_color
        
        if not self.active:
            current_color = (50, 50, 70)
            text_color = (150, 150, 150)
        else:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                current_color = self.hover_color
        
        pygame.draw.rect(surface, current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)
        
        draw_text(surface, self.text, self.rect.centerx, self.rect.centery - self.font.get_height() // 2 + 2, 
                  font=self.font, color=text_color, center=True)
        
        return self.rect

def draw_button(surface, rect, text, active=True, color=BLUE, hover_color=DARK_BLUE, text_font=MED_FONT, text_color=WHITE):
    """Fonction wrapper pour dessiner un bouton utilisant la classe Button."""
    btn = Button(text, rect, active, color, hover_color, text_font, text_color)
    return btn.draw(surface)

# -----------------------
# Loot & Shop data (Inchangé)
# -----------------------

ARMOR_SLOTS = ["chest", "helmet", "greaves", "boots"] 
ARMOR_TYPES = ARMOR_SLOTS 

POSSIBLE_LOOT = [
    {"name": "Grande Potion", "type": "potion", "amount": 1, "desc": "Restaure beaucoup de vie.", "cost": 0},
    {"name": "Plastron en Cuir", "type": "chest", "defense": 2, "desc": "Protection basique pour le torse. +2 DEF.", "cost": 0},
    {"name": "Epée Rouillée", "type": "weapon", "attack": 3, "desc": "Une vieille epée. +3 ATK.", "cost": 0},
    {"name": "Casque de Recrue", "type": "helmet", "defense": 1, "desc": "Protection pour la tete. +1 DEF.", "cost": 0},
    {"name": "Potion Standard", "type": "potion", "amount": 1, "desc": "Restaure de la vie.", "cost": 0},
    {"name": "Pièces d'Or", "type": "gold", "amount": 80, "desc": "De l'argent.", "cost": 0},
]

def generate_loot():
    """Sélectionne un objet aléatoirement avec un taux de drop ajusté."""
    
    if random.random() < 0.60: 
        return random.choice(POSSIBLE_LOOT[:4])
    else:
        return random.choice(POSSIBLE_LOOT[4:])

SHOP_ITEMS_ALL = [
    {"name": "Potion Standard", "type": "potion", "amount": 1, "desc": "Une potion de base pour se soigner. Restaure de la vie (base 35PV).", "cost": 30, "level_required": 1},
    {"name": "Bottes de Cuir", "type": "boots", "defense": 1, "desc": "Simples bottes en cuir pour une legere protection des pieds.", "cost": 40, "level_required": 1},
    {"name": "Epée Aiguisée", "type": "weapon", "attack": 5, "desc": "Meilleure que la rouille. Ajoute des points d'attaque.", "cost": 80, "level_required": 2},
    {"name": "Plastron de Maille", "type": "chest", "defense": 4, "desc": "Une bonne protection contre les coups. Protection pour le torse.", "cost": 120, "level_required": 3},
    {"name": "Jambières de Fer", "type": "greaves", "defense": 3, "desc": "Protection pour les jambes. Offre une defense solide.", "cost": 100, "level_required": 4},
    {"name": "Casque de Guerrier", "type": "helmet", "defense": 3, "desc": "Casque solide. Protege la tete contre les chocs.", "cost": 90, "level_required": 4},
]

# --- Helper Stats (Inchangé) ---
def get_base_stats_for_class(char_class: str) -> Dict[str, int]:
    """Retourne les stats de base (initiales) pour une classe."""
    base_stats = {"HP": 100, "ATK": 12, "DEF": 5}
    if char_class == "Guerrier":
        base_stats.update({"HP": 110, "ATK": 14, "DEF": 6})
    elif char_class == "Tank":
        base_stats.update({"HP": 120, "ATK": 10, "DEF": 8})
    elif char_class == "Mage":
        base_stats.update({"HP": 90, "ATK": 15, "DEF": 4})
    return base_stats


# -----------------------
# Game classes (Inchangé)
# -----------------------
class Character:
    # ... (Code inchangé, propriétés et méthodes de Character)
    def __init__(self, name: str, char_class: str, max_hp=100, base_attack=12, base_defense=5, crit_chance=0.1, avatar_file="hero1.png", gold=0):
        # Stats initiales
        base_stats = get_base_stats_for_class(char_class)
        self.name = name
        self.char_class = char_class
        self.max_hp = base_stats["HP"]
        self.hp = self.max_hp
        self.base_attack = base_stats["ATK"]
        self.base_defense = base_stats["DEF"]
        self.crit_chance = crit_chance
        self.xp = 0
        self.level = 1
        self.gold = gold

        self.inventory = {"potion": 2, "items": []} # items: liste de dicts
        
        self.equipment = {
            "weapon": None, 
            "chest": None, 
            "helmet": None,
            "greaves": None,
            "boots": None
        } # stocke des dicts
        
        self.avatar_file = avatar_file
        self.avatar = load_image(avatar_file, (160,160))
        self.popup_pos = (110, 80) 

    @property
    def attack(self):
        bonus = 0
        if self.equipment["weapon"]:
            bonus += self.equipment["weapon"].get("attack", 0)
        return self.base_attack + bonus

    @property
    def defense(self):
        bonus = 0
        
        for slot in ARMOR_SLOTS: # Utilisation de ARMOR_SLOTS
            if self.equipment[slot]:
                bonus += self.equipment[slot].get("defense", 0)
                
        return self.base_defense + bonus
        
    def is_alive(self):
        return self.hp > 0

    def take_damage(self, dmg: int, is_counter=False):
        old = self.hp
        self.hp = clamp(self.hp - dmg, 0, self.max_hp)
        dealt = old - self.hp
        
        if dealt > 0:
            color = RED if not is_counter else (255, 100, 0) 
            ALL_POPUPS.append(DamagePopup(self.popup_pos[0], self.popup_pos[1], dealt, color))
        
        return dealt

    def heal(self, amount: int):
        old = self.hp
        self.hp = clamp(self.hp + amount, 0, self.max_hp)
        healed = self.hp - old
        
        if healed > 0:
            ALL_POPUPS.append(DamagePopup(self.popup_pos[0], self.popup_pos[1], f"+{healed}", GREEN))
            
        return healed
        
    def use_potion(self, base_heal_amount=35):
        if self.inventory.get("potion", 0) <= 0:
            return 0
        
        self.inventory["potion"] -= 1
        
        base_heal = base_heal_amount + self.level * 2
        
        if self.char_class == "Mage":
            heal_amount = int(base_heal * 1.5)
        else:
            heal_amount = base_heal
            
        healed = self.heal(heal_amount)
        return healed
    
    def equip_item(self, item: Dict[str, Any], index_in_inventory: Optional[int] = None):
        item_type = item.get("type")
        
        valid_slots = ["weapon"] + ARMOR_SLOTS
        
        if item_type not in valid_slots:
            return "Item non equipable (type non reconnu)."

        old_item = self.equipment[item_type]
        self.equipment[item_type] = item
        
        if index_in_inventory is not None:
            if index_in_inventory < len(self.inventory["items"]):
                self.inventory["items"].pop(index_in_inventory)
        
        if old_item:
            self.inventory["items"].append(old_item)
            return f"{item['name']} equipe dans le slot {item_type}. L'ancien objet est dans l'inventaire."
        
        return f"{item['name']} equipe dans le slot {item_type}."

    def unequip_item(self, item_type: str):
        valid_slots = ["weapon"] + ARMOR_SLOTS
        
        if item_type not in valid_slots or not self.equipment[item_type]:
            return f"Emplacement {item_type.upper()} vide ou non reconnu."
            
        old_item = self.equipment[item_type]
        self.equipment[item_type] = None
        self.inventory["items"].append(old_item)
        
        return f"{old_item['name']} desequipe et remis dans l'inventaire."

    def apply_level_up_stats(self):
        self.max_hp += 10
        self.base_defense += 1
        self.crit_chance = clamp(self.crit_chance + 0.01, 0.1, 0.5)
        
        if self.char_class == "Tank":
            self.max_hp += 10
            self.base_defense += 2
        elif self.char_class == "Guerrier":
            self.base_attack += 3
            self.crit_chance = clamp(self.crit_chance + 0.02, 0.1, 0.5)
        else: # Mage
             self.base_attack += 2
             self.max_hp += 5
             
        self.hp = self.max_hp

    def check_level_up(self):
        leveled = False
        
        xp_needed_base = 80 
        
        while self.xp >= xp_needed_base * self.level:
            self.xp -= xp_needed_base * self.level
            self.level += 1
            self.apply_level_up_stats()
            leveled = True
            
        return leveled

    def to_dict(self):
        return {
            "name": self.name, "char_class": self.char_class, "max_hp": self.max_hp, 
            "hp": self.hp, "base_attack": self.base_attack, "base_defense": self.base_defense,
            "crit_chance": self.crit_chance, "xp": self.xp, "level": self.level, 
            "inventory": self.inventory, 
            "equipment": self.equipment, 
            "avatar_file": self.avatar_file,
            "gold": self.gold
        }

    @classmethod
    def from_dict(cls, d):
        base_stats = get_base_stats_for_class(d.get("char_class", "Heros"))
        
        c = cls(d.get("name","Héros"), d.get("char_class", "Heros"), 
                 max_hp=base_stats["HP"], base_attack=base_stats["ATK"], base_defense=base_stats["DEF"], 
                 crit_chance=d.get("crit_chance", 0.1), avatar_file=d.get("avatar_file","hero1.png"), 
                 gold=d.get("gold", 0))
        
        c.max_hp = d.get("max_hp", c.max_hp)
        c.base_attack = d.get("base_attack", c.base_attack)
        c.base_defense = d.get("base_defense", c.base_defense)

        c.hp = d.get("hp", c.max_hp)
        c.xp = d.get("xp", 0)
        c.level = d.get("level", 1)
        c.inventory = d.get("inventory", {"potion": 0, "items": []})
        
        loaded_eq = d.get("equipment", {})
        
        if "armor" in loaded_eq:
            if loaded_eq["armor"] and not loaded_eq.get("chest"):
                c.equipment["chest"] = loaded_eq["armor"]
        
        for slot in c.equipment.keys():
            if slot in loaded_eq:
                c.equipment[slot] = loaded_eq[slot]

        c.avatar = load_image(c.avatar_file, (160,160))
        c.popup_pos = (110, 80)
        return c

class Enemy:
    # ... (Code inchangé)
    def __init__(self, name: str, max_hp: int, attack: int, defense: int, xp_reward: int = 10, avatar_file="goblin.png", is_boss=False, boss_type=""):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.attack_power = attack
        self.defense = defense
        self.xp_reward = xp_reward
        self.is_boss = is_boss
        self.boss_type = boss_type
        self.charging = False
        # Doit utiliser WIDTH global
        self.popup_pos = (WIDTH - 120, 80) 
        
        if self.is_boss:
            if self.boss_type == "Gobelin":
                self.avatar_file = "boss_goblin.png"
            elif self.boss_type == "Orque":
                self.avatar_file = "boss_orque.png"
            elif self.boss_type == "Golem":
                self.avatar_file = "boss_golem.png"
            elif self.boss_type == "Bandit":
                self.avatar_file = "boss_bandit.png"
            else:
                self.avatar_file = avatar_file 
        else:
             self.avatar_file = avatar_file
             
        self.avatar = load_image(self.avatar_file, (160,160))
        
    def is_alive(self):
        return self.hp > 0

    def take_damage(self, dmg: int, is_crit=False):
        old = self.hp
        self.hp = clamp(self.hp - dmg, 0, self.max_hp)
        dealt = old - self.hp
        
        if dealt > 0:
            color = YELLOW if is_crit else WHITE
            ALL_POPUPS.append(DamagePopup(self.popup_pos[0], self.popup_pos[1], dealt, color, is_crit))
            
        return dealt
    
    def attack(self, target: Character):
        if self.charging:
            dmg = max(1, self.attack_power * 2 - (target.defense // 2))
            self.charging = False
            return ("charged", dmg)

        if self.is_boss:
            r = random.random()
            
            if r < 0.15: 
                self.charging = True
                return ("charge_prepare", 0)
                
            elif r < 0.30: 
                dmg = max(1, int(self.attack_power * 1.6))
                return ("heavy", dmg)

        dmg = max(1, self.attack_power) 
        return ("normal", dmg)


# -----------------------
# Game engine (Inchangé)
# -----------------------
class GameEngine:
    # ... (Code inchangé)
    def __init__(self):
        self.player: Optional[Character] = None
        self.current_enemy: Optional[Enemy] = None
        self.stage = 1
        self.log_lines = []
        self.state = "menu" 
        self.defending = False
        
        self.last_loot: Optional[Dict[str,Any]] = None
        self.last_xp: int = 0
        self.leveled_up: bool = False
        # Le système `discovered_shop_items` est maintenu pour la persistance, 
        # mais n'est plus utilisé pour l'affichage dans shop_screen.
        self.discovered_shop_items: List[str] = [item['name'] for item in SHOP_ITEMS_ALL if item.get("level_required", 1) == 1]

    def log(self, text: str):
        self.log_lines.append(text)
        if len(self.log_lines) > 8:
            self.log_lines.pop(0)

    def new_game(self, chosen_avatar="hero1.png", name="Heros", char_class="Heros"):
        self.player = Character(name, char_class=char_class, avatar_file=chosen_avatar, gold=50) 
        self.stage = 1
        self.log_lines = []
        self.log(f"Nouvelle partie demarree. Classe: {char_class}. Gold: {self.player.gold}.")
        
        # Réinitialisation correcte des articles découverts
        self.discovered_shop_items = [item['name'] for item in SHOP_ITEMS_ALL if item.get("level_required", 1) == 1]
        self.spawn_enemy()
    
    def generate_enemy(self, stage: int) -> Enemy:
        enemy_type = random.choice(["Gobelin", "Orque", "Golem", "Bandit"]) 
        is_boss = stage % 5 == 0
        
        hp = 50 + stage * 15
        
        base_atk = 2
        scaling_atk = 3
        atk = base_atk + stage * scaling_atk
        
        defense = 3 + stage * 1
        xp = 10 + stage * 5
        
        avatar_file = "goblin.png"
        
        if enemy_type == "Orque":
             avatar_file = "enemy.png"
             hp = int(hp * 1.1) 
             atk = int(atk * 1.2) 
        elif enemy_type == "Golem":
             avatar_file = "enemy.png" 
             hp = int(hp * 1.3) 
             defense += 2 
             atk = int(atk * 0.9) 
        elif enemy_type == "Bandit":
             avatar_file = "enemy.png" 
             
        
        if is_boss:
            name = "Boss " + enemy_type
            hp = int(hp * 1.5)
            atk = int(atk * 1.2)
            defense += 2
            xp = int(xp * 2)
            return Enemy(name, max_hp=hp, attack=atk, defense=defense, xp_reward=xp, avatar_file=avatar_file, is_boss=is_boss, boss_type=enemy_type)
        
        return Enemy(enemy_type, max_hp=hp, attack=atk, defense=defense, xp_reward=xp, avatar_file=avatar_file, is_boss=is_boss, boss_type=enemy_type)

    def spawn_enemy(self):
        # L'ennemi doit être re-créé avec le bon popup_pos basé sur le nouveau WIDTH
        if self.current_enemy:
            # Si on recharge après un plein écran/fenêtré, on recalcule le boss
             self.current_enemy = self.generate_enemy(self.stage)
        
        if self.current_enemy is None:
             self.current_enemy = self.generate_enemy(self.stage)

        # Assurer que popup_pos est correct
        self.current_enemy.popup_pos = (WIDTH - 120, 80)
        
        self.log(f"Un {self.current_enemy.name} (Etage {self.stage}) apparait !")
        self.state = "battle"
        self.defending = False
    
    def save_game(self):
        if not self.player: return
        
        safe_name = "".join(c for c in self.player.name if c.isalnum()) or "default"
        save_file = os.path.join(SAVE_DIR, f"save_{safe_name}.json")
        
        data = self.player.to_dict()
        data["stage"] = self.stage
        data["discovered_shop_items"] = self.discovered_shop_items 
        
        try:
            with open(save_file, 'w') as f:
                json.dump(data, f, indent=4)
            self.log(f"Partie sauvegardee sous le nom : {safe_name}.")
            return True
        except Exception:
            self.log("Erreur de sauvegarde.")
            return False

    def load_game(self, filename: str):
        load_file = os.path.join(SAVE_DIR, filename)
        if not os.path.exists(load_file): 
            self.log("Fichier de sauvegarde non trouve.")
            self.state = "menu"
            return

        try:
            with open(load_file, 'r') as f:
                data = json.load(f)
            self.player = Character.from_dict(data)
            self.stage = data.get("stage", 1)
            
            initial_discovered = [item['name'] for item in SHOP_ITEMS_ALL if item.get("level_required", 1) == 1]
            self.discovered_shop_items = data.get("discovered_shop_items", initial_discovered)
            
            self.log(f"Partie chargee : {self.player.name}. Etage: {self.stage}.")
            self.spawn_enemy()
        except Exception:
            self.log("Erreur de chargement. Le fichier est peut-etre corrompu.")
            self.state = "menu"
            
    def delete_save(self, filename: str):
        filepath = os.path.join(SAVE_DIR, filename)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                self.log(f"Sauvegarde {filename} supprimee.")
                return True
            except OSError as e:
                self.log(f"Erreur de suppression: {e}")
                return False
        return False
    
    def player_attack(self):
        if not self.player or not self.current_enemy: return
            
        is_crit = random.random() < self.player.crit_chance
        
        raw = self.player.attack + random.randint(-2,2)
        dmg = max(1, raw - self.current_enemy.defense)
        
        if is_crit:
            dmg = int(dmg * 2)
            self.log(f"CRITIQUE! {self.player.name} attaque.")
        
        dealt = self.current_enemy.take_damage(dmg, is_crit)
        
        if not is_crit:
            self.log(f"{self.player.name} attaque et inflige {dealt} degats.")

    def enemy_turn(self):
        # Correction de l'erreur NameError: Remplacer 'engine.' par 'self.'
        if not self.player or not self.current_enemy: return
            
        is_blocked = self.defending and random.random() < 1/3
        
        temp_defense_bonus = self.player.defense if self.defending else 0
        temp_defense = self.player.defense + temp_defense_bonus
        
        action_type, raw_dmg = self.current_enemy.attack(self.player)
        
        if action_type == "charge_prepare":
            self.log(f"{self.current_enemy.name} se concentre pour charger...")
            self.defending = False
            return
            
        dmg = max(1, raw_dmg - temp_defense)
        
        dealt = 0
        if is_blocked:
            self.log(f"BLOCAGE PARFAIT! {self.player.name} ne prend aucun degat.")
            dealt = 0
        else:
            dealt = self.player.take_damage(dmg) 
        
        # Correction de l'erreur NameError
        if self.defending and dealt > 0:
            riposte_dmg = max(1, dealt // 4) 
            riposte_dealt = self.current_enemy.take_damage(riposte_dmg)
            self.log(f"Contre-attaque ! Riposte de {riposte_dealt} degats a l'ennemi.")
        
        if is_blocked:
             pass 
        elif self.defending:
            self.log(f"Tu defends ! {self.current_enemy.name} inflige {dealt} degats (Defense renforcee).")
        elif action_type == "charged":
            self.log(f"{self.current_enemy.name} CHARGE et inflige {dealt} degats!")
        elif action_type == "heavy":
            self.log(f"{self.current_enemy.name} assene un coup lourd et inflige {dealt} degats.")
        else:
            self.log(f"{self.current_enemy.name} attaque et inflige {dealt} degats.")
            
        self.defending = False
    
    def apply_loot(self, loot: Dict[str, Any]):
        if not self.player: return
        
        item_type = loot.get("type")
        item_name = loot["name"]
        amount = loot.get("amount", 1)
        
        if item_type == "potion":
            self.player.inventory["potion"] = self.player.inventory.get("potion", 0) + amount
            self.log(f"Tu trouves une {item_name}. Tu en as {self.player.inventory['potion']}.")
        elif item_type == "gold":
            self.player.gold += amount
            self.log(f"Tu trouves {amount} pieces d'or. Total: {self.player.gold}.")
        elif item_type in ["weapon"] + ARMOR_SLOTS: 
            self.player.inventory["items"].append(loot)
            self.log(f"Tu places {item_name} dans l'inventaire.")

    def check_level_up(self):
        if self.player:
            leveled = self.player.check_level_up()
            
            if leveled:
                self.log(f"Niveau up ! Tu es niveau {self.player.level}. Stats augmentees.")
                
            return leveled
        return False

    def use_potion(self):
        if self.player:
            healed = self.player.use_potion(base_heal_amount=35) 
            if healed > 0:
                self.log(f"Tu bois une potion et recuperes {healed} PV.")
                self.enemy_turn()
            else:
                self.log("Pas de potions...")

    def handle_victory(self):
        if not self.player or not self.current_enemy: return
            
        self.last_xp = self.current_enemy.xp_reward
        self.player.xp += self.last_xp
        self.log(f"Tu as vaincu {self.current_enemy.name} ! +{self.last_xp} XP.")
        self.stage += 1
        
        self.last_loot = generate_loot()
        self.apply_loot(self.last_loot)
        self.leveled_up = self.check_level_up()
        
        self.state = "victory_screen"
        
    def handle_flee(self):
        if not self.player or not self.current_enemy: return
        
        flee_chance = 0.5
        if self.player.char_class == "Mage": 
            flee_chance = 0.6
        
        ok = random.random() < flee_chance
            
        if ok:
            self.log(f"[{self.player.name}]: \"Ce combat n'en vaut pas la peine. Je me replie !\"")
            self.log("Fuite reussie ! (Appuyez sur A)") 
            
            self.state = "flee_success"
        else:
            self.log(f"[{self.player.name}]: \"Oups, l'ennemi m'a bloque !\"")
            self.log("Fuite echouee ! L'ennemi attaque...")
            self.enemy_turn() 
            self.defending = False 


# -----------------------
# UI helpers (Inchangé)
# -----------------------
def draw_health_bar(surface, x, y, hp_current, hp_max, width=200, height=25, color_full=(50, 200, 50)):
    ratio = hp_current / hp_max
    
    pygame.draw.rect(surface, (50, 50, 50), (x, y, width, height), border_radius=3)
    
    fill_width = int(width * ratio)
    if fill_width > 0:
        pygame.draw.rect(surface, color_full, (x, y, fill_width, height), border_radius=3)
        
    pygame.draw.rect(surface, WHITE, (x, y, width, height), 2, border_radius=3)
    
    hp_text = f"{hp_current}/{hp_max} HP"
    draw_text(surface, hp_text, x + width // 2, y + height // 2 - FONT_SIZE_SM // 2 + 1, font=FONT, color=WHITE, center=True)

# -----------------------
# Pause Menu Screen (Inchangé)
# -----------------------

def pause_menu(engine: 'GameEngine'):
    # ... (Code inchangé)
    """Affiche le menu de pause pendant le combat."""
    clock = pygame.time.Clock()
    
    # Dessiner la scène de combat en arrière-plan avant le menu de pause
    render_game(engine) 
    
    # Créer un fond semi-transparent pour le menu de pause
    pause_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pause_surf.fill((0, 0, 0, 180)) 
    WIN.blit(pause_surf, (0, 0))

    draw_text(WIN, "PAUSE", WIDTH//2, HEIGHT//2 - 150, BIG_FONT, YELLOW, center=True)
    
    btn_w, btn_h = 300, 60
    btn_y_start = HEIGHT//2 - 60
    
    buttons = {}
    
    # Bouton Reprendre
    rect_resume = pygame.Rect(WIDTH//2 - btn_w//2, btn_y_start, btn_w, btn_h)
    buttons["resume"] = draw_button(WIN, rect_resume, "Reprendre (ESC)", True)
    
    # Bouton Sauvegarder
    rect_save = pygame.Rect(WIDTH//2 - btn_w//2, btn_y_start + 80, btn_w, btn_h)
    buttons["save"] = draw_button(WIN, rect_save, "Sauvegarder", True, color=GREEN, hover_color=(0, 150, 0))

    # Bouton Menu Principal
    rect_menu = pygame.Rect(WIDTH//2 - btn_w//2, btn_y_start + 160, btn_w, btn_h)
    buttons["menu"] = draw_button(WIN, rect_menu, "Aller au Menu Principal", True, color=RED, hover_color=(150, 0, 0))
    
    pygame.display.flip()
    
    # Boucle de gestion des événements pour le menu de pause
    while True:
        clock.tick(30)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: return "battle" # Reprendre
            
            elif e.type == pygame.MOUSEBUTTONDOWN:
                mx,my = pygame.mouse.get_pos()
                
                if buttons["resume"].collidepoint(mx,my): return "battle"
                
                if buttons["save"].collidepoint(mx,my): 
                    if engine.save_game():
                        # Petit feedback visuel rapide sur le bouton Sauvegarder
                        draw_button(WIN, rect_save, "SAUVEGARDE REUSSIE!", True, color=(0, 255, 0), hover_color=(0, 200, 0))
                        pygame.display.flip()
                        pygame.time.wait(500)
                    return "battle" # Retourne au combat après la sauvegarde

                if buttons["menu"].collidepoint(mx,my): return "menu"

# -----------------------
# Render Game (Inchangé)
# -----------------------

def render_game(engine: GameEngine):
    """Fonction principale de rendu du jeu."""
    global ALL_POPUPS
    
    if engine.state == "menu":
        WIN.blit(BG_MENU, (0, 0))
        
        draw_text(WIN, "L'ASCENSION DU HEROS", WIDTH//2, 120, BIG_FONT, YELLOW, center=True)
        draw_text(WIN, "MINI-RPG TEXTUEL EN PYGAME", WIDTH//2, 165, MED_FONT, WHITE, center=True)

        btn_w, btn_h = 300, 60
        btn_y = HEIGHT // 2
        
        new_game_rect = draw_button(WIN, pygame.Rect(WIDTH//2-btn_w//2, btn_y, btn_w, btn_h), "Nouvelle Partie (N)", True)
        
        load_active = len(get_all_saves()) > 0
        load_game_rect = draw_button(WIN, pygame.Rect(WIDTH//2-btn_w//2, btn_y + 80, btn_w, btn_h), "Charger Partie (C)", load_active)
        quit_rect = draw_button(WIN, pygame.Rect(WIDTH//2-btn_w//2, btn_y + 160, btn_w, btn_h), "Quitter (Q/ESC)", True, color=RED, hover_color=(150,0,0))
        
        # --- Bouton Plein Écran (Nouveau) ---
        fs_btn_w, fs_btn_h = 200, 40
        fs_text = "Quitter Plein Écran" if FULLSCREEN else "Plein Écran"
        fs_rect = draw_button(WIN, pygame.Rect(WIDTH - fs_btn_w - 20, 20, fs_btn_w, fs_btn_h), fs_text, True, color=GREY_BUTTON, hover_color=DARK_BLUE, text_font=FONT)
        
        return {"new_game": new_game_rect, "load_game": load_game_rect, "quit": quit_rect, "fullscreen": fs_rect}

    if engine.state in ("battle", "victory_screen", "gameover", "flee_success"):
        
        current_bg = BG_BOSS if engine.current_enemy and engine.current_enemy.is_boss else BG_BATTLE
        WIN.blit(current_bg, (0, 0))
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100)) 
        WIN.blit(overlay, (0, 0))

        # Header
        draw_text(WIN, f"Etage: {engine.stage}", 12, 8, BIG_FONT)
        draw_text(WIN, "Mini RPG - V19.2", WIDTH//2, 8, BIG_FONT, YELLOW, center=True)
        draw_text(WIN, f"Etat: {engine.state.upper().replace('_', ' ')}", WIDTH - 150, 8, MED_FONT)
        
        # Gold display 
        if engine.player:
            draw_text(WIN, f"Gold: {engine.player.gold}", WIDTH - 100, 40, MED_FONT, GOLD, center=True)
        
        # --- Stats du Joueur ---
        if engine.player:
            
            # Repositionnement de l'avatar et des popups en fonction de la taille
            player_x, player_y = 30, 80
            engine.player.popup_pos = (player_x + 80, player_y)
            
            # Affichage de l'avatar du personnage pour le combat
            if engine.state != "gameover":
                 WIN.blit(engine.player.avatar, (player_x, player_y))
            
            draw_health_bar(WIN, player_x, 250, engine.player.hp, engine.player.max_hp, width=200, height=25)
            
            draw_text(WIN, f" {engine.player.name} (Lvl {engine.player.level} - {engine.player.char_class})", player_x, 285, MED_FONT, YELLOW)
            
            temp_def_val = engine.player.defense * 2 if engine.defending else engine.player.defense
            
            draw_text(WIN, f"ATK: {engine.player.attack} | DEF: {temp_def_val} | Crit: {int(engine.player.crit_chance*100)}%", player_x, 315)
            
            # --- Affichage de l'Équipement (Seulement si équipé) ---
            eq_text_y = 345
            
            # Ordre d'affichage des slots
            equipment_display_order = [
                ("weapon", "Arme"), 
                ("helmet", "Casque"), 
                ("chest", "Plastron"),
                ("greaves", "Jambières"),
                ("boots", "Bottes")
            ]
            
            for slot_key, display_name in equipment_display_order:
                item = engine.player.equipment[slot_key]
                if item: # N'afficher que si un objet est équipé
                    name = item.get("name", "Erreur")
                    
                    draw_text(WIN, f"{display_name}: {name}", player_x, eq_text_y, font=FONT)
                    eq_text_y += 18 
                
            # Affichage XP
            xp_needed = 80 * engine.player.level 
            xp_bar_w = 200
            
            # Ajustement de la position Y de la barre XP et du texte pour s'adapter à la place réduite
            xp_y = eq_text_y + 10 # Commence après le dernier équipement affiché (+10px)
            
            xp_ratio = clamp(engine.player.xp / xp_needed, 0, 1)
            pygame.draw.rect(WIN, (50,50,50), (player_x, xp_y, xp_bar_w, 10)) 
            pygame.draw.rect(WIN, (0,255,255), (player_x, xp_y, xp_bar_w * xp_ratio, 10))
            draw_text(WIN, f"XP: {engine.player.xp}/{xp_needed}", player_x, xp_y + 15, FONT)
            
        # --- Stats de l'Ennemi ---
        if engine.current_enemy:
            enemy_x = WIDTH - 200
            enemy_y = 80
            
            # Mise à jour de la position du popup de l'ennemi
            engine.current_enemy.popup_pos = (enemy_x + 80, enemy_y)

            WIN.blit(engine.current_enemy.avatar, (enemy_x, enemy_y))
            draw_health_bar(WIN, enemy_x, 250, engine.current_enemy.hp, engine.current_enemy.max_hp, width=200, height=25, color_full=RED)
            
            draw_text(WIN, f" {engine.current_enemy.name}", enemy_x, 285, MED_FONT, RED)
            draw_text(WIN, f"ATK: {engine.current_enemy.attack_power} | DEF: {engine.current_enemy.defense}", enemy_x, 315)
            if engine.current_enemy.is_boss:
                draw_text(WIN, "MINI-BOSS", enemy_x, 345, MED_FONT, RED)
            if engine.current_enemy.charging:
                draw_text(WIN, "CHARGE EN COURS !", enemy_x, 375, MED_FONT, YELLOW)
            
        # Log box (Déplacé au centre) - MASQUÉ si GAME OVER
        log_box_rect = pygame.Rect(220, 360, 560, 160)
        
        if engine.state != "gameover":
            pygame.draw.rect(WIN, (0,0,0, 150), log_box_rect, border_radius=5)
            pygame.draw.rect(WIN, WHITE, log_box_rect, 2, border_radius=5)
            
            y = 365
            line_spacing = 18 
            for line in engine.log_lines:
                draw_text(WIN, line, 230, y, font=FONT)
                y += line_spacing

        # --- Rendu des Popups de Dégâts ---
        for popup in ALL_POPUPS:
            popup.update()
            WIN.blit(popup.image, popup.rect)
        
        ALL_POPUPS = [p for p in ALL_POPUPS if p.lifetime > 0] 

        # --- Gestion des États Spéciaux (GameOver/Victory/Flee) ---
        if engine.state == "gameover":
            
            if engine.player:
                class_name_lower = engine.player.char_class.lower()
                gameover_avatar_name = f"{class_name_lower}.png"
                if class_name_lower == "guerrier":
                    gameover_avatar_name = "guerrier.png"
                
                gameover_avatar = load_image(gameover_avatar_name, (200, 200))
                WIN.blit(gameover_avatar, (WIDTH//2 - 100, 100)) 
                
                draw_text(WIN, "GAME OVER", WIDTH//2, 330, BIG_FONT, RED, center=True)
                draw_text(WIN, f"{engine.player.name} ({engine.player.char_class}, Lvl {engine.player.level}) est tombe au combat.", WIDTH//2, 380, MED_FONT, center=True)
                
            continue_rect = draw_button(WIN, pygame.Rect(WIDTH//2-150, HEIGHT-70, 300, 50), "Retour au Menu (N)", True)
            return {"continue": continue_rect}
            
        elif engine.state == "victory_screen":
            draw_text(WIN, "VICTOIRE !", WIDTH//2, HEIGHT//2 - 100, BIG_FONT, GREEN, center=True)
            
            draw_text(WIN, f"Gain d'XP: +{engine.last_xp}", WIDTH//2, HEIGHT//2 - 40, MED_FONT, center=True)
            if engine.leveled_up:
                draw_text(WIN, f"NIVEAU {engine.player.level} ATTEINT !", WIDTH//2, HEIGHT//2 - 10, BIG_FONT, YELLOW, center=True)
            
            if engine.last_loot:
                draw_text(WIN, f"Objet Trouve: {engine.last_loot['name']}", WIDTH//2, HEIGHT//2 + 30, MED_FONT, center=True)
            
            continue_rect = draw_button(WIN, pygame.Rect(WIDTH//2-150, HEIGHT-70, 300, 50), "Continuer (A)", True)
            return {"continue": continue_rect}
        
        elif engine.state == "flee_success":
            draw_text(WIN, "FUITE RÉUSSIE", WIDTH//2, HEIGHT//2 - 100, BIG_FONT, GREEN, center=True)
            draw_text(WIN, f"{engine.player.name} a echappe au combat a l'Etage {engine.stage}.", WIDTH//2, HEIGHT//2 - 40, MED_FONT, center=True)
            draw_text(WIN, "(Toutefois, fuir ne rapporte ni XP, ni Gold.)", WIDTH//2, HEIGHT//2, MED_FONT, center=True)
            
            continue_rect = draw_button(WIN, pygame.Rect(WIDTH//2-150, HEIGHT-70, 300, 50), "Retourner au Menu (A)", True)
            return {"continue": continue_rect}


        # --- Rendu des Boutons de Combat/Action ---
        elif engine.state == "battle":
            btn_w, btn_h = 140, 44
            
            bx_main = WIDTH//2 - (btn_w*3 + 20)//2
            by_main = HEIGHT - 70
            
            attack_rect = draw_button(WIN, pygame.Rect(bx_main, by_main, btn_w, btn_h), "Attaquer (1)", True)
            defend_color = YELLOW if engine.defending else BLUE 
            defend_h_color = (200, 200, 0) if engine.defending else DARK_BLUE
            defend_rect = draw_button(WIN, pygame.Rect(bx_main+btn_w+10, by_main, btn_w, btn_h), "Defendre (2)", True, color=defend_color, hover_color=defend_h_color)
            
            potion_active = engine.player and engine.player.inventory.get("potion",0) > 0
            potion_rect = draw_button(WIN, pygame.Rect(bx_main+(btn_w+10)*2 + 10, by_main, btn_w, btn_h), f"Potion ({engine.player.inventory.get('potion',0)})", potion_active)
            
            by_func = HEIGHT - 110
            
            flee_rect = draw_button(WIN, pygame.Rect(30, by_func, 120, 36), "Fuir (F)", True)
            save_rect = draw_button(WIN, pygame.Rect(WIDTH-150, by_func, 120, 36), "Sauver (S)", True)
            
            inv_rect = draw_button(WIN, pygame.Rect(30, HEIGHT-70, 120, 36), "Inventaire (I)", True, color=GREY_BUTTON)
            shop_rect = draw_button(WIN, pygame.Rect(WIDTH-150, HEIGHT-70, 120, 36), "Magasin (M)", True, color=GREY_BUTTON)


            return {"attack":attack_rect,"defend":defend_rect,"potion":potion_rect,"flee":flee_rect,"save":save_rect, "inventory": inv_rect, "shop": shop_rect}
            
    return {}

# -----------------------
# Inventory Screen (Inchangé)
# -----------------------

def inventory_screen(engine: 'GameEngine'):
    """Écran de gestion de l'inventaire et de l'équipement."""
    clock = pygame.time.Clock()
    player = engine.player
    
    hovered_index_inv = None
    hovered_slot_eq = None
    
    eq_slots = ["weapon"] + ARMOR_SLOTS
    
    # Paramètres des cartes ajustés (taille augmentée pour mieux utiliser l'écran)
    CARD_HEIGHT = 45 
    CARD_SPACING = 8 
    COL1_W = 300 
    COL2_W = 350 
    COL3_W = 250 

    while True:
        clock.tick(30)
        
        WIN.blit(BG_MENU, (0, 0))
        
        draw_text(WIN,"INVENTAIRE", WIDTH//2, 50, BIG_FONT, YELLOW, center=True)
        # Affichage de l'Or
        draw_text(WIN, f"Gold: {player.gold}", WIDTH - 100, 60, MED_FONT, GOLD, center=True) 
        
        mouse_pos = pygame.mouse.get_pos()
        hovered_index_inv = None
        hovered_slot_eq = None
        
        # Colonne 1: Équipement Actuel (x=50)
        eq_x, eq_y = 50, 120
        draw_text(WIN, "EQUIPEMENT ACTUEL", eq_x, eq_y, MED_FONT, YELLOW)
        
        eq_buttons = {}
        
        for i, slot in enumerate(eq_slots):
            y = eq_y + 40 + i * (CARD_HEIGHT + CARD_SPACING)
            rect = pygame.Rect(eq_x, y, COL1_W, CARD_HEIGHT)
            
            item = player.equipment[slot]
            
            text = f"[{slot.upper()}] " + (item['name'] if item else "VIDE")
            color = GREEN if item else GREY_BUTTON
            
            btn = Button(text, rect, color=color, hover_color=DARK_BLUE, text_font=FONT) 
            eq_buttons[slot] = btn.draw(WIN)
            
            if rect.collidepoint(mouse_pos) and item:
                hovered_slot_eq = slot
                
        # Colonne 3: Détails des Objets et Consommables (Position ajustée à droite)
        inv_x = eq_x + COL1_W + 20 
        detail_x = inv_x + COL2_W + 20
        detail_y = 120 
        
        detail_box_h = HEIGHT - 120 - 90 
        detail_box = pygame.Rect(detail_x, detail_y, COL3_W, detail_box_h) 
        
        pygame.draw.rect(WIN, (0, 0, 0, 180), detail_box, border_radius=5)
        pygame.draw.rect(WIN, WHITE, detail_box, 2, border_radius=5)
        
        draw_text(WIN, "DÉTAILS & CONSOMMABLES", detail_x + 10, detail_y + 10, FONT, YELLOW)
        
        detail_text_y = detail_y + 40
        
        draw_text(WIN, f"Potions: {player.inventory.get('potion', 0)}", detail_x + 10, detail_text_y, MED_FONT, GREEN)
        detail_text_y += 30
        
        item_to_detail = None
        
        # Colonne 2: Inventaire (Objets) (Entre Col 1 et Col 3)
        inv_y = 120
        draw_text(WIN, "OBJETS A ÉQUIPER", inv_x, inv_y, MED_FONT, YELLOW)
        
        inv_buttons = {}
        
        equippable_types = ["weapon"] + ARMOR_SLOTS
        equippable_items = [item for item in player.inventory["items"] if item.get("type") in equippable_types]
        
        for i, item in enumerate(equippable_items):
            y = inv_y + 40 + i * (CARD_HEIGHT + CARD_SPACING)
            # Limiter le nombre d'éléments affichés pour éviter le dépassement de l'écran
            if y + CARD_HEIGHT > detail_box.bottom:
                 break
            
            rect = pygame.Rect(inv_x, y, COL2_W, CARD_HEIGHT)
            
            item_type = item['type'].upper()
            text = f"[{item_type}] {item['name']}"
            
            btn = Button(text, rect, color=BLUE, hover_color=DARK_BLUE, text_font=FONT) 
            inv_buttons[i] = btn.draw(WIN)
            
            if rect.collidepoint(mouse_pos):
                hovered_index_inv = i
        
        
        # Détails de l'objet survolé
        if hovered_index_inv is not None:
            item_to_detail = equippable_items[hovered_index_inv]
        elif hovered_slot_eq is not None:
            item_to_detail = player.equipment[hovered_slot_eq]
        
        if item_to_detail:
            draw_text(WIN, item_to_detail['name'], detail_x + 10, detail_text_y, MED_FONT, WHITE)
            detail_text_y += 30
            
            item_type = item_to_detail.get('type')
            if item_type == "weapon":
                draw_text(WIN, f"Attaque: +{item_to_detail.get('attack', 0)}", detail_x + 10, detail_text_y, FONT)
                detail_text_y += 20
            elif item_type in ARMOR_SLOTS:
                draw_text(WIN, f"Defense ({item_type.capitalize()}): +{item_to_detail.get('defense', 0)}", detail_x + 10, detail_text_y, FONT)
                detail_text_y += 20
            
            detail_text_y += 10
            draw_text(WIN, "Description:", detail_x + 10, detail_text_y, FONT, YELLOW)
            detail_text_y += 20
            
            max_desc_width = detail_box.width - 20
            desc_text = item_to_detail.get('desc', 'Pas de description.')
            
            # Utiliser la fonction wrap_text pour gérer l'enroulement
            wrap_text(WIN, desc_text, max_desc_width, detail_x + 10, detail_text_y, font=FONT, color=WHITE, line_spacing=18)

        # Bouton Retour (Bas de l'écran)
        back_rect = draw_button(WIN, pygame.Rect(20, HEIGHT-40, 150, 30), "Retour (ESC)", True, color=GREY_BUTTON, hover_color=DARK_BLUE, text_font=FONT)

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE or e.key == pygame.K_i: return "battle"
                    
            elif e.type == pygame.MOUSEBUTTONDOWN:
                mx,my = pygame.mouse.get_pos()
                
                # Clics sur l'équipement
                for slot, rect in eq_buttons.items():
                    if rect.collidepoint(mx,my) and player.equipment[slot]:
                        log_msg = player.unequip_item(slot)
                        engine.log(log_msg)
                        return "inventory" 
                        
                # Clics sur l'inventaire
                for index, rect in inv_buttons.items():
                    if rect.collidepoint(mx,my):
                        item_to_equip = equippable_items[index]
                        try:
                            # Tente de trouver l'index exact pour l'enlever de la liste
                            item_index_in_list = player.inventory["items"].index(item_to_equip)
                        except ValueError:
                            # En cas de doublons, trouve le premier match pour le pop()
                            item_index_in_list = [i for i, item in enumerate(player.inventory["items"]) if item == item_to_equip][0]
                        
                        log_msg = player.equip_item(item_to_equip, index_in_inventory=item_index_in_list)
                        engine.log(log_msg)
                        return "inventory" 

                if back_rect.collidepoint(mx,my):
                    return "battle"


# -----------------------
# Shop Screen (MODIFIÉ : Affichage de TOUS les articles)
# -----------------------

def shop_screen(engine: 'GameEngine'):
    """Écran du Magasin pour acheter des objets, avec affichage complet de la progression."""
    clock = pygame.time.Clock()
    player = engine.player
    
    # --- LOGIQUE D'AFFICHAGE MODIFIÉE ---
    # On affiche TOUS les articles du SHOP_ITEMS_ALL
    available_items = SHOP_ITEMS_ALL 
    
    # Si le joueur a atteint un niveau qui débloque de nouveaux objets,
    # on les ajoute à la liste des "découverts" pour la persistance si on le souhaite plus tard.
    # On maintient le log pour les notifications de déblocage.
    for item in SHOP_ITEMS_ALL:
        if player.level >= item.get("level_required", 1) and item['name'] not in engine.discovered_shop_items:
            engine.discovered_shop_items.append(item['name'])
            engine.log(f"MAGASIN: Nouvel article debloque (Lvl {player.level}): {item['name']} !")
            
    
    if not available_items:
        engine.log("Magasin vide.")
        return "battle"
        
    hovered_index_shop = 0 
    if available_items:
        hovered_index_shop = clamp(hovered_index_shop, 0, len(available_items) - 1)
        
    # Paramètres des cartes ajustés (taille augmentée pour mieux utiliser l'écran)
    CARD_HEIGHT = 45 
    CARD_SPACING = 8 
    COL1_W = WIDTH // 2 - 50 
    COL2_W = WIDTH - COL1_W - 80 

    while True:
        clock.tick(30)
        
        WIN.blit(BG_MENU, (0, 0))
        
        draw_text(WIN,"MAGASIN", WIDTH//2, 50, BIG_FONT, YELLOW, center=True)
        draw_text(WIN, f"Gold: {player.gold}", WIDTH - 100, 60, MED_FONT, GOLD, center=True) 
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Colonne 1: Articles à Vendre (x=30)
        shop_x, shop_y = 30, 120
        draw_text(WIN, "ARTICLES DISPONIBLES", shop_x, shop_y, MED_FONT, YELLOW)
        
        shop_buttons = {}
        
        for i, item in enumerate(available_items):
            y = shop_y + 40 + i * (CARD_HEIGHT + CARD_SPACING) 
            if y + CARD_HEIGHT > HEIGHT - 90: break 
            
            rect = pygame.Rect(shop_x, y, COL1_W, CARD_HEIGHT) 
            
            level_req = item.get("level_required", 1)
            can_buy_level = player.level >= level_req 
            
            text = f"{item['name']} ({item['cost']} Gold)"
            
            # Gère la couleur du bouton et l'affichage du niveau requis
            if not can_buy_level:
                text = f"[Lvl {level_req} requis] {item['name']} ({item['cost']} Gold)"
                color = (40, 40, 60) # Très gris/bleu foncé (indisponible)
                hover_color = (40, 40, 60)
                text_color_btn = (150, 150, 150)
            elif i == hovered_index_shop:
                color = GOLD
                hover_color = (255, 200, 0)
                text_color_btn = (0, 0, 0) # Texte noir sur fond jaune
            else:
                color = BLUE
                hover_color = DARK_BLUE
                text_color_btn = WHITE
                
            btn = Button(text, rect, active=True, color=color, hover_color=hover_color, text_font=FONT, text_color=text_color_btn) 
            shop_buttons[i] = btn.draw(WIN)
            
            if rect.collidepoint(mouse_pos):
                hovered_index_shop = i

        # Colonne 2: Détails de l'Article (À droite de l'écran)
        detail_x = shop_x + COL1_W + 20 
        detail_y = 120 
        
        detail_box_h = HEIGHT - 120 - 90 
        detail_box = pygame.Rect(detail_x, detail_y, COL2_W, detail_box_h) 
        
        pygame.draw.rect(WIN, (0, 0, 0, 180), detail_box, border_radius=5)
        pygame.draw.rect(WIN, WHITE, detail_box, 2, border_radius=5)
        
        draw_text(WIN, "DESCRIPTION DE L'ARTICLE", detail_x + 10, detail_y + 10, FONT, YELLOW)
        detail_text_y = detail_y + 40
        
        item_to_detail = available_items[hovered_index_shop]
        level_req = item_to_detail.get("level_required", 1)
        
        can_buy_gold = player.gold >= item_to_detail['cost']
        can_buy_level = player.level >= level_req
        can_buy = can_buy_gold and can_buy_level
        
        if item_to_detail:
            draw_text(WIN, item_to_detail['name'], detail_x + 10, detail_text_y, BIG_FONT, WHITE)
            detail_text_y += 40
            
            item_type = item_to_detail.get('type')
            
            # Affichage de l'information de niveau requis si non atteint
            if not can_buy_level:
                draw_text(WIN, f"NIVEAU {level_req} REQUIS", detail_x + 10, detail_text_y, MED_FONT, RED)
                detail_text_y += 40
                
            draw_text(WIN, f"Type: {item_type.upper()}", detail_x + 10, detail_text_y, MED_FONT)
            detail_text_y += 30
            
            if item_type == "weapon":
                draw_text(WIN, f"Attaque: +{item_to_detail.get('attack', 0)}", detail_x + 10, detail_text_y, MED_FONT)
                detail_text_y += 30
            elif item_type in ARMOR_SLOTS: 
                draw_text(WIN, f"Defense ({item_type.capitalize()}): +{item_to_detail.get('defense', 0)}", detail_x + 10, detail_text_y, MED_FONT)
                detail_text_y += 30
            elif item_type == "potion":
                draw_text(WIN, f"Soins: +{35 + player.level*2} PV (Base)", detail_x + 10, detail_text_y, MED_FONT)
                
                detail_text_y += 30 
                if player.char_class == "Mage":
                    draw_text(WIN, f"(Mage: Soins 50% plus efficaces)", detail_x + 10, detail_text_y, FONT, GREEN)
                    detail_text_y += 20 
            
            detail_text_y += 10
            draw_text(WIN, "Description:", detail_x + 10, detail_text_y, FONT, YELLOW)
            detail_text_y += 25 
            
            max_desc_width = detail_box.width - 20
            desc_text = item_to_detail.get('desc', 'Pas de description.')
            
            # Utilisation de wrap_text pour remplir la zone
            wrap_text(WIN, desc_text, max_desc_width, detail_x + 10, detail_text_y, font=FONT, color=WHITE, line_spacing=18)
            
            # Bouton Acheter positionné en bas de la zone de détails
            buy_rect = pygame.Rect(detail_x + 50, detail_box.bottom - 60, COL2_W - 100, 50) 
            
            buy_text = f"ACHETER (E) pour {item_to_detail['cost']} Gold"
            
            if not can_buy_level:
                 buy_text = f"NIVEAU {level_req} REQUIS"
                 
            elif not can_buy_gold:
                 buy_text = f"GOLD INSUFFISANT ({item_to_detail['cost']} G)"
                 
            # Le bouton est actif SEULEMENT si can_buy est vrai
            buy_btn = draw_button(WIN, buy_rect, buy_text, can_buy, color=GREEN, hover_color=(0, 150, 0))
        
        else:
             draw_text(WIN, "Survolez ou selectionnez un article.", detail_x + 10, detail_y + 40, MED_FONT)


        # Bouton Retour (Bas de l'écran)
        back_rect = draw_button(WIN, pygame.Rect(20, HEIGHT-40, 150, 30), "Retour (ESC)", True, color=GREY_BUTTON, hover_color=DARK_BLUE, text_font=FONT)

        pygame.display.flip()

        def perform_purchase():
            nonlocal can_buy, item_to_detail
            if can_buy:
                player.gold -= item_to_detail['cost']
                
                # IMPORTANT: Utiliser item_to_detail.copy() pour que l'item dans l'inventaire 
                # soit distinct de l'item dans le SHOP_ITEMS_ALL (si c'est un dict mutable).
                # Cette pratique est bonne.
                if item_to_detail['type'] == 'potion':
                    player.inventory['potion'] += item_to_detail.get('amount', 1)
                    engine.log(f"Achete {item_to_detail['name']}. Total: {player.inventory['potion']} potions.")
                else:
                    player.inventory['items'].append(item_to_detail.copy()) 
                    engine.log(f"Achete {item_to_detail['name']} et place dans l'inventaire.")

        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "quit"
            
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE or e.key == pygame.K_m: return "battle"
                
                if e.key == pygame.K_e:
                    perform_purchase()
                
                if e.key == pygame.K_DOWN and available_items:
                    hovered_index_shop = (hovered_index_shop + 1) % len(available_items)
                if e.key == pygame.K_UP and available_items:
                    hovered_index_shop = (hovered_index_shop - 1) % len(available_items)
                    
            elif e.type == pygame.MOUSEBUTTONDOWN:
                mx,my = pygame.mouse.get_pos()
                
                if item_to_detail and can_buy and buy_btn.collidepoint(mx,my):
                    perform_purchase()

                for i, rect in shop_buttons.items():
                    if rect.collidepoint(mx, my):
                        hovered_index_shop = i
                        
                if back_rect.collidepoint(mx,my):
                    return "battle"


# -----------------------
# Logique de la boucle principale
# -----------------------

# CLASSES DE PERSONNAGE (Inchangé)
CLASSES = [
    ("Guerrier", "hero1.png", "Attaquant. ATK+ et Degats Critiques. Bon HP/DEF."), 
    ("Tank", "hero2.png", "Defenseur. HP++ et DEF++ a chaque niveau. Moins de Degats."), 
    ("Mage", "hero3.png", "Polyvalent. ATK/DEF faibles, mais Potions 50% plus efficaces pour la survie."), 
]

def simple_text_input(prompt: str, default="Heros"):
    """
    Commence avec un texte vide (txt="") pour simuler la barre clignotante.
    Si l'utilisateur valide le vide, on utilise la valeur par défaut.
    """
    clock = pygame.time.Clock()
    
    txt = "" 
    
    input_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2, 400, 40)
    
    # Pour le curseur clignotant
    cursor_visible = True
    cursor_timer = 0
    CURSOR_BLINK_RATE = 30 

    while True:
        clock.tick(30)
        cursor_timer = (cursor_timer + 1) % CURSOR_BLINK_RATE
        if cursor_timer == 0:
            cursor_visible = not cursor_visible

        for e in pygame.event.get():
            if e.type == pygame.QUIT: return default
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: return None 
                
                if e.key == pygame.K_RETURN: return txt.strip() or default 
                
                elif e.key == pygame.K_BACKSPACE: txt = txt[:-1]
                else:
                    if len(e.unicode)==1 and e.key not in (pygame.K_LSHIFT, pygame.K_RSHIFT) and len(txt) < 15: 
                        txt += e.unicode.upper() 

        WIN.blit(BG_MENU, (0, 0))
        
        draw_text(WIN, prompt, WIDTH//2, HEIGHT//2 - 60, BIG_FONT, YELLOW, center=True)
        pygame.draw.rect(WIN, WHITE, (input_rect), 2, border_radius=5)
        pygame.draw.rect(WIN, DARK_BLUE, (input_rect), 0, border_radius=5)
        
        # Affiche le texte en cours de saisie
        draw_text(WIN, txt, input_rect.x + 10, input_rect.y + 10, MED_FONT)
        
        # CURSEUR CLIGNOTANT
        if cursor_visible:
            text_surf = MED_FONT.render(txt, True, WHITE)
            cursor_x = input_rect.x + 10 + text_surf.get_width()
            pygame.draw.line(WIN, WHITE, (cursor_x, input_rect.y + 8), (cursor_x, input_rect.y + 32), 2)


        draw_text(WIN, f"(Nom par defaut: {default})", WIDTH//2, HEIGHT//2 + 60, FONT, center=True)
        draw_text(WIN, "(ENTER pour valider | ESC pour Annuler)", WIDTH//2, HEIGHT//2 + 80, FONT, center=True)
        pygame.display.flip()
        
    return txt.strip() or default 

def simple_choice_screen(options):
    # ... (Code inchangé)
    clock = pygame.time.Clock()
    chosen=0
    
    while True:
        clock.tick(30)
        for e in pygame.event.get():
            if e.type==pygame.QUIT: return -1
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_ESCAPE: return -1 
                if e.key==pygame.K_RIGHT: chosen=(chosen+1)%len(options)
                elif e.key==pygame.K_LEFT: chosen=(chosen-1)%len(options)
                elif e.key==pygame.K_RETURN: return chosen
            
            elif e.type == pygame.MOUSEBUTTONDOWN:
                mx,my = pygame.mouse.get_pos()
                
                # Clic sur une carte pour la sélectionner
                card_width = 240
                padding = 20
                total_width = len(options) * card_width + (len(options) - 1) * padding
                start_x = (WIDTH - total_width) // 2
                card_y = 120
                
                for i in range(len(options)):
                    x = start_x + i * (card_width + padding)
                    box_rect = pygame.Rect(x, card_y, card_width, 480) 
                    if box_rect.collidepoint(mx, my):
                        chosen = i
                        
                # Clic sur le bouton de retour
                if back_rect.collidepoint(mx,my):
                    return -1


        WIN.blit(BG_MENU, (0, 0))
        draw_text(WIN,"Choisis ta CLASSE (fleches/clic puis ENTER):", WIDTH//2, 50, BIG_FONT, YELLOW, center=True)
        
        card_width = 240 
        card_height = 480 
        padding = 20
        
        total_width = len(options) * card_width + (len(options) - 1) * padding
        start_x = (WIDTH - total_width) // 2 
        
        for i,(label,fname, desc) in enumerate(options):
            img_size = (120, 120) 
            img=load_image(fname, img_size) 
            x = start_x + i * (card_width + padding)
            y = 120
            
            box_rect = pygame.Rect(x, y, card_width, card_height) 
            
            if i==chosen:
                pygame.draw.rect(WIN, DARK_BLUE, box_rect, border_radius=10)
                pygame.draw.rect(WIN, YELLOW, box_rect, 5, border_radius=10) 
                
                img_y = y + 10 
                WIN.blit(img,(x + card_width//2 - img_size[0]//2, img_y)) 
                
                title_y = img_y + img_size[1] + 10 
                draw_text(WIN,label,x + card_width//2, title_y, BIG_FONT, YELLOW, center=True)
                
                stats = get_base_stats_for_class(label)
                
                stat_x_offset = x + 20
                stat_y_start = title_y + 50 
                
                stat_box_rect = pygame.Rect(stat_x_offset - 5, stat_y_start - 5, card_width - 30, 95)
                pygame.draw.rect(WIN, (0, 0, 0, 150), stat_box_rect, border_radius=5)
                
                draw_text(WIN, "Stats de Base (Lvl 1):", stat_x_offset, stat_y_start, FONT, YELLOW)
                stat_y_start += 20
                
                draw_text(WIN, f"HP: {stats['HP']}", stat_x_offset, stat_y_start, FONT)
                stat_y_start += 20
                draw_text(WIN, f"ATK: {stats['ATK']}", stat_x_offset, stat_y_start, FONT)
                stat_y_start += 20
                draw_text(WIN, f"DEF: {stats['DEF']}", stat_x_offset, stat_y_start, FONT)
                
                desc_y = stat_y_start + 40 
                draw_text(WIN, "Caracteristiques:", x + card_width//2, desc_y, FONT, YELLOW, center=True)
                desc_y += 20
                
                wrap_text(WIN, desc, card_width - 20, x + card_width//2, desc_y, font=FONT, color=WHITE, center=True)
                
            else:
                pygame.draw.rect(WIN, (30, 30, 40), box_rect, border_radius=10)
                WIN.blit(img,(x + card_width//2 - img_size[0]//2, y + 10))
                draw_text(WIN,label,x + card_width//2, y + img_size[1] + 10, MED_FONT, (150, 150, 150), center=True)
            
        # Bouton Retour réduit et repositionné
        back_rect = draw_button(WIN, pygame.Rect(WIDTH//2-100, HEIGHT-70, 200, 50), "Retour au Menu (ESC)", True, color=RED, hover_color=(150,0,0))

        pygame.display.flip()
        
    return chosen
        
def load_game_selection_screen(engine: 'GameEngine'):
    # ... (Code inchangé)
    clock = pygame.time.Clock()
    
    saves = get_all_saves()
    
    if not saves:
        engine.log("Aucune sauvegarde disponible.")
        return "menu"
        
    chosen_index = 0
    
    while True:
        clock.tick(30)
        
        WIN.blit(BG_MENU, (0, 0))
        draw_text(WIN,"Selectionnez une partie (fleches/clic puis ENTER):", WIDTH//2, 50, BIG_FONT, YELLOW, center=True)
        
        btn_w, btn_h = 450, 50
        icon_size = 30
        icon_padding = 10
        start_y = 150
        buttons = {}
        delete_buttons = {}

        if chosen_index >= len(saves):
            chosen_index = max(0, len(saves) - 1)


        for i, save in enumerate(saves):
            y = start_y + i * 60
            rect = pygame.Rect(WIDTH//2 - btn_w//2, y, btn_w, btn_h)
            
            text = f"{save['name']} (Lvl {save['level']} | Etage {save['stage']})"
            
            color = BLUE
            hover_color = DARK_BLUE
            if i == chosen_index:
                color = YELLOW
                hover_color = (200, 200, 0)
                
            btn = Button(text, rect, color=color, hover_color=hover_color)
            buttons[i] = btn.draw(WIN)
            
            delete_rect = pygame.Rect(rect.right + icon_padding, y + (btn_h - icon_size) // 2, icon_size, icon_size)
            WIN.blit(ICON_DELETE, delete_rect)
            
            if rect.collidepoint(pygame.mouse.get_pos()):
                chosen_index = i
            
            delete_buttons[i] = delete_rect
            
        back_rect = draw_button(WIN, pygame.Rect(WIDTH//2-100, HEIGHT-70, 200, 50), "Retour (ESC)", True, color=RED, hover_color=(150,0,0))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: return "menu"
                if e.key == pygame.K_RETURN and saves: 
                    engine.load_game(saves[chosen_index]["filename"])
                    return "battle"
                if e.key == pygame.K_DOWN: 
                    chosen_index = (chosen_index + 1) % len(saves)
                if e.key == pygame.K_UP:
                    chosen_index = (chosen_index - 1) % len(saves)
                    
            elif e.type == pygame.MOUSEBUTTONDOWN:
                mx,my = pygame.mouse.get_pos()
                
                for i, rect in buttons.items():
                    if rect.collidepoint(mx, my):
                        chosen_index = i
                        if e.button == 1: # Clic gauche
                             engine.load_game(saves[chosen_index]["filename"])
                             return "battle"
                        
                for i, rect in delete_buttons.items():
                    if rect.collidepoint(mx, my):
                        if engine.delete_save(saves[i]["filename"]):
                            saves = get_all_saves()
                            chosen_index = max(0, chosen_index - 1)
                            break 
                    
                if back_rect.collidepoint(mx,my):
                    return "menu"


# --- Boucle principale (Inchangé) ---

def main():
    clock = pygame.time.Clock()
    engine = GameEngine()
    engine.log("Bienvenue ! N: nouvelle | C: charger | Q: quitter")
    name_input_result = ""

    running = True
    while running:
        clock.tick(FPS)
        
        # Le rendu met à jour les coordonnées des boutons
        if engine.state not in ("load_select", "inventory", "shop", "name_input", "character_select", "pause_menu"):
             buttons = render_game(engine)
        else:
             buttons = {} # Empêche les clics fantômes pendant les menus modaux
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                
                # Gestion de la touche ESCAPE pour la pause en combat
                if event.key == pygame.K_ESCAPE:
                    if engine.state == "battle":
                        engine.state = "pause_menu"
                        
                    elif engine.state in ("menu", "gameover", "load_select"): 
                        running = False
                    elif engine.state in ("inventory", "shop", "flee_success"):
                        engine.state = "battle"
                    elif engine.state in ("victory_screen"): 
                        # ESC en victoire/fuyard ramène au menu
                        engine.state = "menu"
                    
                
                # Raccourcis Menu
                elif engine.state == "menu":
                    if event.key == pygame.K_q:
                        running = False
                    elif event.key == pygame.K_n:
                        engine.state = "name_input"
                    elif event.key == pygame.K_c and len(get_all_saves()) > 0:
                        engine.state = "load_select"
                
                # Raccourcis Combat/Fin/Actions
                elif engine.state == "victory_screen" and event.key == pygame.K_a:
                    if "continue" in buttons: engine.spawn_enemy()
                
                elif engine.state == "gameover" and event.key == pygame.K_n:
                    if "continue" in buttons: engine.state = "menu"
                
                elif engine.state == "flee_success" and event.key == pygame.K_a:
                    engine.state = "menu"
                    engine.current_enemy = None


                elif engine.state == "battle":
                    key_map = {pygame.K_1: "attack", pygame.K_2: "defend", pygame.K_3: "potion", 
                               pygame.K_f: "flee", pygame.K_s: "save", pygame.K_i: "inventory", pygame.K_m: "shop"}
                    if event.key in key_map:
                        action = key_map[event.key]
                        if action == "inventory":
                            engine.state = "inventory"
                        elif action == "shop":
                            engine.state = "shop"
                        elif action == "flee":
                            engine.handle_flee() 
                        else:
                            handle_battle_click(engine, action, buttons)


            # Traitement des événements de souris
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx,my = pygame.mouse.get_pos()
                
                if engine.state == "menu":
                    if "new_game" in buttons and buttons["new_game"].collidepoint(mx,my):
                        engine.state = "name_input"
                    elif "load_game" in buttons and buttons["load_game"].collidepoint(mx,my) and len(get_all_saves()) > 0:
                        engine.state = "load_select"
                    elif "quit" in buttons and buttons["quit"].collidepoint(mx,my):
                         running = False
                    
                    # Logique du Bouton Plein Écran
                    elif "fullscreen" in buttons and buttons["fullscreen"].collidepoint(mx,my):
                        
                        # Basculement de l'état
                        new_fs = not FULLSCREEN
                        if new_fs:
                            # Tenter le plein écran sur la taille actuelle de l'écran
                            screen_info = pygame.display.Info()
                            setup_window(screen_info.current_w, screen_info.current_h, True)
                        else:
                            # Revenir à la taille fenêtrée par défaut
                            setup_window(1000, 640, False)
                        
                        # Si l'état était en combat, on doit re-vérifier les positions des popups (fait dans render_game/spawn_enemy)
                        if engine.current_enemy:
                             engine.current_enemy.popup_pos = (WIDTH - 120, 80)
                             
                        # Force le re-rendu pour mettre à jour les coordonnées des boutons
                        continue


                elif engine.state in ("victory_screen", "gameover", "flee_success") and "continue" in buttons and buttons["continue"].collidepoint(mx,my):
                    if engine.state == "victory_screen":
                        engine.spawn_enemy()
                    elif engine.state == "gameover":
                        engine.state = "menu"
                    elif engine.state == "flee_success":
                        engine.state = "menu"
                        engine.current_enemy = None
                        
                elif engine.state == "battle" and engine.player:
                    for action in ["attack", "defend", "potion", "flee", "save", "inventory", "shop"]:
                        if buttons.get(action) and buttons[action].collidepoint(mx,my):
                            if action == "inventory":
                                engine.state = "inventory"
                            elif action == "shop":
                                engine.state = "shop"
                            elif action == "flee":
                                engine.handle_flee() 
                            else:
                                handle_battle_click(engine, action, buttons)
                            
        # Gestion des états modaux
        if engine.state == "name_input":
            name_input_result = simple_text_input("Nom du heros (ENTER):", default="Heros")
            if name_input_result is None:
                engine.state = "menu"
            else:
                engine.state = "character_select"
                
        elif engine.state == "character_select":
            choice = simple_choice_screen(CLASSES)
            
            if choice == -1: # Retour au menu (via ESC ou bouton)
                engine.state = "menu"
            else:
                char_class, avatar_file, _ = CLASSES[choice]
                engine.new_game(chosen_avatar=avatar_file, name=name_input_result, char_class=char_class)
                engine.state = "battle"
                
        elif engine.state == "load_select":
            next_state = load_game_selection_screen(engine)
            if next_state == "quit": running=False
            else: engine.state = next_state
            
        elif engine.state == "pause_menu":
            next_state = pause_menu(engine)
            if next_state == "quit": running=False
            else: engine.state = next_state
            
        elif engine.state == "inventory":
            next_state = inventory_screen(engine)
            if next_state == "quit": running=False
            else: engine.state = next_state
        elif engine.state == "shop":
            next_state = shop_screen(engine)
            if next_state == "quit": running=False
            else: engine.state = next_state


def handle_battle_click(engine: GameEngine, action: str, buttons: Dict[str, Any]):
    player_turn_over = False
    
    if not engine.player or not engine.current_enemy: return

    if action == "attack":
        engine.player_attack()
        player_turn_over = True
    elif action == "defend":
        engine.defending=True
        engine.log("Posture defensive activee pour le tour. 33% de chance de bloquer.")
        player_turn_over = True 

    elif action == "potion":
        if engine.player.inventory.get("potion",0) > 0:
            engine.use_potion()
            return
        else:
            engine.log("Pas de potions...")
            return
        
    elif action == "flee":
        engine.handle_flee()
        return
        
    elif action == "save":
        engine.save_game()
        return 

    if player_turn_over and engine.state == "battle": 
        if engine.current_enemy.is_alive():
            engine.enemy_turn() 
        else:
            engine.handle_victory() 

    if engine.player and not engine.player.is_alive():
        engine.log(f"{engine.player.name} est tombe au combat !")
        engine.state="gameover"
        engine.current_enemy = None


# -----------------------
# Entrypoint
# -----------------------
if __name__=="__main__":
    try:
        main()
    except Exception as e:
        print("Erreur critique:", e)
        pygame.quit()
        import traceback
        traceback.print_exc()
        sys.exit(1)