# 🚀 ToolOS SDK

Lightweight Python Framework for fast, easy and efficient application development.
Code Your Apps with StateMachine, Multi-Language Support, Caching, Logging, Sound, Sequence System, Drivers, App Management and more.



## Latest Changelog  **v3.3**

### Bugfixes
```bash
    None
```
### Features
```bash
    - More Advanced and Secure Built-in LocalStorage (SHA256 / AES256)
    - Way More Advanced Instancing secure LocalStorage
```
> INFO: ModSDK Still under Development
## 🔧 Installation

```bash
pip install toolos
```

## 🎯 Quick Start

### Settings Setup

```json
{
  "version": "1.0.0",
  "language": "en",
  "cachepath": "data/cache",
  "temppath": "data/temp",
  "logpath": "data/logs",
  "languagepath": "data/lang"
}
```
or as a dictionary in your code:
```python
settings = {
  "version": "1.0.0",
  "name": "MyAppSDK",
  "settings_path": "path/to/settings.json",
  "standard_language_library": True
}
app = MyApp(settings=settings)
...
```

### Basic App
```python
import toolos as engine

class App(engine.Api):
    def __init__(self):
        super().__init__()
        
        # Sprache ändern
        self.Settings.Global("language", "de")
        self.Language.Reload()
        
        # States verwalten
        self.StateMachine.AddKeyState("game_running", True)
        
        # Sound abspielen
        self.Helper.Sound.PlaySound("assets/music.mp3", loop=True)
        
        # Fenster erstellen (PyQt6)
        window = self.Helper.PyQt.CreateWindow("main", "Meine App")
        btn = self.Helper.PyQt.CreateWidget("button", text="Klick mich!")
        
        # 3D Scene (Ursina)
        scene = self.Helper.Ursina.CreateScene("game")
        player = self.Helper.Ursina.CreateEntity("player", model="cube")

```

## 🎮 Coole Features

### 🌍 Mehrsprachigkeit
```python
# Sprach-Dateien (de.json)
{
    "start": "Start",
    "settings": "Einstellungen",
    "quit": "Beenden"
}

# Im Code
print(self.Language.Translate("start"))  # → "Start"
```

### 💾 State Management

```python
# States & Sequenzen
self.StateMachine.SetState("MAINMENU")
if self.StateMachine.IsState("MAINMENU"):
    self.Sequence.DoSequence("menu_animation")

```

### 🎵 Sound System 
```python
# Sound mit Sequenzen
sequence = {
    "sequence": "boss_fight",
    "meta": [
        {"instance": self.Helper.Sound, "method": "PlaySound", "args": ["boss.mp3"]},
        {"instance": player, "method": "animate_scale", "args": [2, 1.5]}
    ]
}
self.Sequence.AddSequence(sequence)
```

### 🎨 GUI Framework (PyQt6)
```python
# Schnelles UI
window = self.Helper.PyQt.CreateWindow("shop")
layout = self.Helper.PyQt.CreateLayout("grid")
items = ["Schwert", "Schild", "Trank"]

for item in items:
    btn = self.Helper.PyQt.CreateWidget("button", text=item)
    layout.addWidget(btn)
```

### 🎲 Game Engine (Ursina)
```python
# 3D Game Objects
player = self.Helper.Ursina.CreateEntity(
    "player",
    model="cube", 
    position=(0,1,0)
)

# Partikelsystem
particles = self.Helper.Ursina.CreateParticleSystem(
    position=(0,2,0),
    particle_count=100,
    particle_lifetime=2.0,
    particle_color_start=color.yellow,
    particle_color_end=color.clear
)
### 📦 Memory System
```python
# Daten speichern
self.Memory.KnowThis("player_stats", {
    "health": 100,
    "level": 1,
    "items": ["Schwert"]
})

# Daten abrufen
stats = self.Memory.Remember("player_stats")
```

### 🔄 Cache & Temp
```python
# Temporäre Daten
self.Cache.WriteCacheFile("level1.cache", "checkpoint_data")
self.Temp.WriteTempFile("session.tmp", "temp_data")
```

## 🛠️ SDK Setup

```python
sdk = {
    "version": "1.0.0",
    "name": "GameSDK",
    "settings_path": "config/settings.json",
    "standard_language_library": True
}

app = Game(sdk=sdk)
```

## 📚 Links
- 🌐 [Docs](https://claytechnologie.github.io/ToolSDK/)
- 📖 [API Referenz](https://claytechnologie.github.io/ToolSDK/api/)

## 📜 Lizenz
MIT