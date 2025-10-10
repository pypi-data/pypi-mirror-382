# 🚀 ToolOS SDK

Lightweight Python Framework for fast, easy and efficient application development.
Code Your Apps with StateMachine, Multi-Language Support, Caching, Logging, Sound, Sequence System, Drivers, App Management and more.



## Latest Changelog  **v3.3.3**

### Bugfixes
```bash
-   Fixed BasepathCollision
```
### Features
```bash
- Added SettingsAPI BasepathLoading
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
        self.Settings.AddLanguagePackage('de', path)
        self.Language.Reload()
        
        # States verwalten
        self.StateMachine.sSetState("game_running", True)
        self.StateMachine.
        
        # Sound abspielen
        self.Helper.Sound.PlaySound("assets/music.mp3", loop=True)
        
        # Fenster erstellen (PyQt6)
        window = self.Helper.PyQt.CreateWindow("main", "Meine App")
        btn = self.Helper.PyQt.CreateWidget("button", text="Klick mich!")
        
        # 3D Scene (Ursina)
        scene = self.Helper.Ursina.CreateScene("game")
        player = self.Helper.Ursina.CreateEntity("player", model="cube")

        # Event-Handler
        self.Event
        self.Event.setHandler()
        self.Event.Trigger()
        ...

        # Memory Management
        self.Memory
        self.Memory.KnowThis()
        self.Memory.Forget()
        self.Memory.Learn()
        self.Memory.Remember()
        self.Memory.MakeGlobal()
        ...

        # Built-ins

        self.UpdateAPI()
        self.New()
        self.Collect()
        self.Insert()
        self.Fork()
        self.Delete()
        self.Quit()


```

