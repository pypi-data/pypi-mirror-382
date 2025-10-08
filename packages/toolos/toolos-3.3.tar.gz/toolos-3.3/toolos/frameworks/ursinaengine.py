from ursina import (
    Ursina, Entity, Scene, Vec3, color, destroy,
    application, EditorCamera, Audio,
    Text, Button, Sprite, Panel, WindowPanel,
    PointLight, DirectionalLight, AmbientLight, SpotLight,
    BoxCollider, SphereCollider, MeshCollider, CapsuleCollider,
    curve, held_keys, time
)
import random

def lerp(start, end, t):
    """Linear interpolation between start and end values"""
    return start + (end - start) * t

class PhysicsSystem:
    """Simple physics system for basic collision detection"""
    def __init__(self):
        self.entities = []
        
    def add_entity(self, entity):
        if entity not in self.entities:
            self.entities.append(entity)
            
    def remove_entity(self, entity):
        if entity in self.entities:
            self.entities.remove(entity)
            
    def update(self):
        # Basic collision detection between entities
        for i, entity1 in enumerate(self.entities):
            if not hasattr(entity1, 'collider'):
                continue
                
            for entity2 in self.entities[i+1:]:
                if not hasattr(entity2, 'collider'):
                    continue
                    
                # Simple AABB collision check
                if self._check_collision(entity1, entity2):
                    if hasattr(entity1, 'on_collision'):
                        entity1.on_collision(entity2)
                    if hasattr(entity2, 'on_collision'):
                        entity2.on_collision(entity1)
                        
    def _check_collision(self, entity1, entity2):
        """Simple AABB collision check"""
        bounds1 = self._get_bounds(entity1)
        bounds2 = self._get_bounds(entity2)
        
        return (bounds1[0] < bounds2[1] and bounds1[1] > bounds2[0] and
                bounds1[2] < bounds2[3] and bounds1[3] > bounds2[2])
                
    def _get_bounds(self, entity):
        """Get entity bounds as [min_x, max_x, min_y, max_y]"""
        pos = entity.position
        scale = entity.scale
        return [
            pos.x - scale.x/2,
            pos.x + scale.x/2,
            pos.y - scale.y/2,
            pos.y + scale.y/2
        ]
from typing import Optional, Dict, List, Union
import math

class UrsinaFramework:
    def __init__(self, app=None):
        self.App = app
        self.Engine = Ursina()
        self.Entities = {}
        self.Scenes = {}
        self.ActiveScene = None
        self.DefaultCamera = None
        self.Physics = False
        
        # Registriere Event-Handler
        self.Engine.update = self.update
        self.Engine.input = self.input
        
    def CreateScene(self, name: str):
        scene = Scene()
        self.Scenes[name] = scene
        if not self.ActiveScene:
            self.ActiveScene = scene
        return scene
    
    def SetActiveScene(self, name: str):
        if name in self.Scenes:
            self.ActiveScene = self.Scenes[name]
            return True
        return False
    
    def CreateEntity(self, name: str, model: str = 'cube', texture: str = None, 
                    position: tuple = (0,0,0), rotation: tuple = (0,0,0), 
                    scale: tuple = (1,1,1), entity_color = color.white):
        entity = Entity(
            model=model,
            texture=texture,
            position=Vec3(*position),
            rotation=Vec3(*rotation),
            scale=Vec3(*scale),
            color=entity_color
        )
        self.Entities[name] = entity
        return entity
    
    def CreateLight(self, type_name: str = 'point', position: tuple = (0,0,0), 
                   light_color = color.white, intensity: float = 1.0):
        light_types = {
            'point': PointLight,
            'directional': DirectionalLight,
            'ambient': AmbientLight,
            'spot': SpotLight
        }
        
        if type_name not in light_types:
            raise ValueError(f"Unknown light type: {type_name}")
            
        light = light_types[type_name](
            position=Vec3(*position),
            color=light_color,
            intensity=intensity
        )
        return light
    
    def SetupCamera(self, position: tuple = (0,0,-10), rotation: tuple = (0,0,0), 
                   fov: float = 60, orthographic: bool = False):
        self.DefaultCamera = EditorCamera()
        self.DefaultCamera.position = Vec3(*position)
        self.DefaultCamera.rotation = Vec3(*rotation)
        self.DefaultCamera.fov = fov
        self.DefaultCamera.orthographic = orthographic
        return self.DefaultCamera
    
    def EnablePhysics(self, gravity: tuple = (0,-9.81,0)):
        self.Physics = True
        application.physics_system = PhysicsSystem()
        application.physics_system.setGravity(Vec3(*gravity))
    
    def AddCollider(self, entity: Entity, type_name: str = 'box'):
        collider_types = {
            'box': BoxCollider,
            'sphere': SphereCollider,
            'mesh': MeshCollider,
            'capsule': CapsuleCollider
        }
        
        if type_name not in collider_types:
            raise ValueError(f"Unknown collider type: {type_name}")
            
        return collider_types[type_name](entity)
    
    def CreateAnimation(self, entity: Entity, attribute: str, value, 
                       duration: float = 1.0, animation_curve = curve.linear):
        # Manuelle Animation statt animate()
        start_value = getattr(entity, attribute)
        
        def update_animation():
            nonlocal start_value
            t = time.dt / duration
            current = lerp(start_value, value, t)
            setattr(entity, attribute, current)
            
            if t >= 1:
                entity.update = None
                
        entity.update = update_animation
        return entity
    
    def CreateSound(self, path: str, autoplay: bool = False, loop: bool = False):
        audio = Audio(path, autoplay=autoplay, loop=loop)
        return audio
    
    def CreateParticleSystem(self, position: tuple = (0,0,0), 
                           particle_count: int = 100,
                           particle_lifetime: float = 1.0,
                           emission_rate: float = 10,
                           particle_speed: float = 1.0,
                           particle_scale: float = 0.1,
                           particle_color_start = color.white,
                           particle_color_end = color.clear,
                           particle_direction: tuple = (0,1,0)):
        """
        Erstellt ein erweitertes Partikelsystem
        """
        particle_system = Entity(position=Vec3(*position))
        particle_system.particles = []
        particle_system.max_particles = particle_count
        particle_system.emission_timer = 0
        particle_system.emission_rate = emission_rate
        
        # Erstelle ein Partikel-Präfab für bessere Performance
        particle_prefab = Entity(
            model='sphere',
            scale=particle_scale,
            color=particle_color_start,
            enabled=False  # Deaktiviert, wird nur als Template verwendet
        )
        
        def emit_particle():
            if len(particle_system.particles) >= particle_system.max_particles:
                return
                
            # Erstelle neuen Partikel
            particle = Entity(
                model=particle_prefab.model,
                parent=particle_system,
                position=Vec3(
                    random.uniform(-0.1, 0.1),
                    random.uniform(-0.1, 0.1),
                    random.uniform(-0.1, 0.1)
                ),
                scale=particle_scale
            )
            
            # Setze Partikel-Eigenschaften
            particle.velocity = Vec3(
                random.uniform(-0.5, 0.5) + particle_direction[0],
                random.uniform(-0.5, 0.5) + particle_direction[1],
                random.uniform(-0.5, 0.5) + particle_direction[2]
            ) * particle_speed
            
            particle.lifetime = particle_lifetime
            particle.age = 0
            particle.color_start = particle_color_start
            particle.color_end = particle_color_end
            
            particle_system.particles.append(particle)
        
        def update_particles():
            # Aktualisiere Emission
            particle_system.emission_timer += time.dt
            if particle_system.emission_timer >= 1.0 / emission_rate:
                emit_particle()
                particle_system.emission_timer = 0
            
            # Aktualisiere existierende Partikel
            particles_to_remove = []
            for particle in particle_system.particles:
                particle.age += time.dt
                life_ratio = particle.age / particle.lifetime
                
                if life_ratio >= 1:
                    particles_to_remove.append(particle)
                    continue
                
                # Bewege Partikel
                particle.position += particle.velocity * time.dt
                
                # Aktualisiere Farbe mit Überblendung
                particle.color = color.rgba(
                    lerp(particle.color_start.r, particle.color_end.r, life_ratio),
                    lerp(particle.color_start.g, particle.color_end.g, life_ratio),
                    lerp(particle.color_start.b, particle.color_end.b, life_ratio),
                    lerp(particle.color_start.a, particle.color_end.a, life_ratio)
                )
                
                # Optional: Füge Rotation hinzu
                particle.rotation_y += random.uniform(-90, 90) * time.dt
            
            # Entferne tote Partikel
            for particle in particles_to_remove:
                if particle in particle_system.particles:
                    particle_system.particles.remove(particle)
                    destroy(particle)
        
        particle_system.update = update_particles
        return particle_system

    def lerp(self, start, end, t):
        return start + (end - start) * t
    
    def CreateUI(self, type_name: str, **kwargs):
        ui_types = {
            'text': Text,
            'button': Button,
            'panel': Panel,
            'image': Sprite,
            'window': WindowPanel
        }
        
        if type_name not in ui_types:
            raise ValueError(f"Unknown UI type: {type_name}")
            
        return ui_types[type_name](**kwargs)
    
    def StartGame(self):
        self.Engine.run()
    
    def QuitGame(self):
        application.quit()