import math
import random
from GameObjects import Barrel, Enemy, GameObject, Rocket, ToothpickTrap
from GameObjects.Wall import Wall
from MainEngine import BMathL, Engine, Types #NEEDED. Mainly for Types.GameObject creation.
import pygame
class Weapon(): #Change this to the name of your script
    def __init__(self, engine):
        self.gameObject = Types.GameObject(engine)
        self.weaponType: Types.WeaponTypes._GENERIC = None
        self.oldWeaponType = None
        self.engine: Engine.Engine = engine
        self.creator = None
        self.cell = None
        self.maxHealth = None
        self.health = None
        self.hasBase = False
        self.baseGO = None
        self.placedRot = 0
        self.lastFired = 0
        self.finishedStartup = False
    def Destroy(self):
        self._UpdateLinkedMatrix()
        try:
            self.engine._Globals.sceneObjectsArray.remove(self.creator)
        except Exception:
            pass
        try:
            if self.hasBase:
                self.engine._Globals.sceneObjectsArray.remove(self.baseGO)
                del self.baseGO
        except Exception:
            pass
    def _UpdateLinkedMatrix(self):
        if (self.cell == None):
            return
        self.cell.weaponLink = None
    def Update(self):
        if self.engine.timeScale == 0:
            return
        if self.oldWeaponType != self.weaponType:
            self.lastFired = self.engine.GetTotalTime()
            self.oldWeaponType = self.weaponType
        if self.lastFired + self.weaponType.fireSpeed > self.engine.GetTotalTime():
            if self.weaponType == Types.WeaponTypes.BottleRocket:
                if self.lastFired + (self.weaponType.fireSpeed * 0.85) < self.engine.GetTotalTime():
                    self.gameObject.image = "BOTTLEROCKETFULL"
            return
        fired = False
        enemyList = []
        if self.weaponType == Types.WeaponTypes.NerfGun:
            newSearchCells = self.weaponType.searchCells
            newSearchOffset = self.weaponType.searchOffset
            rot = self.placedRot
            if rot == 270:
                newSearchOffset = Types.Vector2(newSearchOffset.y, newSearchOffset.x)
                newSearchCells = Types.Vector2(newSearchCells.y, newSearchCells.x)
            if rot == 180:
                newSearchOffset = Types.Vector2(0, newSearchOffset.y)
            if rot == 90:
                newSearchOffset = Types.Vector2(newSearchOffset.y, 0)
                newSearchCells = Types.Vector2(newSearchCells.y, newSearchCells.x)
            
            for x in range(newSearchCells.x):
                for y in range(newSearchCells.y):
                    cellToSearch = newSearchOffset + Types.Vector2(x, y) + self.cell.cell
                    if self.engine.FindObject("GRID").obj.gridMatrix.CellExistsCheck(cellToSearch):
                        for enemy in self.engine.FindObject("GRID").obj.gridMatrix.GetCell(cellToSearch).enemyLinkDefinite:
                            if not enemy in enemyList:
                                enemyList.append(enemy)
            array = []
            linkedObjArray = []
            if (len(enemyList) != 0):
                for enemy in enemyList:
                    array.append((Types.Vector2(self.gameObject.position.x, self.gameObject.position.y) - Types.Vector2(enemy.gameObject.position.x, enemy.gameObject.position.y)).magnitude) #Add z component to array
                    linkedObjArray.append(enemy) #Add GameObject to array
                n = len(array)
                BMathL.Math.QuickSort.LinkedObject.QuickSort(array, linkedObjArray, 0, n-1) #Use our linked object quicksort algorithm
                V = (linkedObjArray[0].gameObject.position.x - self.gameObject.position.x, linkedObjArray[0].gameObject.position.y - self.gameObject.position.y)
                
                rotation = math.degrees(math.acos((V[1]) / ( ((V[0] ** 2) + (V[1] ** 2)) ** 0.5 )))
                
                self.gameObject.rotation = 90 - rotation - (180 if (linkedObjArray[0].gameObject.position.x - self.gameObject.position.x) > 0 else 0)
                self.gameObject.rotation = -self.gameObject.rotation if (linkedObjArray[0].gameObject.position.x - self.gameObject.position.x) > 0 else self.gameObject.rotation
                linkedObjArray[0].Damage(self.weaponType.damage)
                self.engine.PlaySound("Assets\\Sounds\\nerf_minigun.mp3")
                fired = True
        if self.weaponType == Types.WeaponTypes.BarrelOfMonkeys:
            if self.gameObject.renderEnabled is False:
                return
            if len(self.engine.FindObject("GRID").obj.gridMatrix.GetCell(self.cell.cell).enemyLinkDefinite) != 0:
                for x in range(self.weaponType.searchCells.x):
                    for y in range(self.weaponType.searchCells.y):
                        cellToSearch = self.weaponType.searchOffset + Types.Vector2(x, y) + self.cell.cell
                        if self.engine.FindObject("GRID").obj.gridMatrix.CellExistsCheck(cellToSearch):
                            #self.engine.FindObject("GRID").obj.gridMatrix.GetCell(cellToSearch).objectLink.obj.health -= self.weaponType.damage
                            for enemy in self.engine.FindObject("GRID").obj.gridMatrix.GetCell(cellToSearch).enemyLinkDefinite:
                                if not enemy in enemyList:
                                    enemyList.append(enemy)
                barrel:Barrel.Create = Barrel.Create(self.engine)
                barrel.gameObject.size = self.gameObject.size
                barrel.gameObject.position = self.gameObject.position
                barrel.gameObject.image = "MONKEYBARRELBROKEN"
                barrel.obj.arm = GameObject.Create(self.engine)
                barrel.obj.arm.gameObject.size = Types.Vector2(barrel.gameObject.size.x * 0.5, barrel.gameObject.size.y)
                barrel.obj.arm.gameObject.position = barrel.gameObject.position + Types.Vector3(-barrel.gameObject.size.x / 2, 0, 0.1)
                barrel.obj.arm.gameObject.image = "MONKEYARM"
                self.engine.CreateNewObject(barrel)
                self.engine.CreateNewObject(barrel.obj.arm)
                barrel.obj.enemies = enemyList.copy()
                barrel.obj.barrelCreator = self
                self.engine.PlaySound("Assets\\Sounds\\monkey_barrel_cracking.mp3")
                self.gameObject.renderEnabled = False

        if self.weaponType == Types.WeaponTypes.BottleRocket:
            enemies = self.engine.FindObject("WAVEPROGRESSION").obj.enemies
            if len(enemies) == 0:
                return
            target: Enemy.Create = random.choice(enemies)
            if target.obj.Targeted == True:
                return
            rocket = Rocket.Create(self.engine)
            self.gameObject.image = "BOTTLEROCKETEMPTY"
            rocket.gameObject.size = self.gameObject.size
            rocket.gameObject.position = self.gameObject.position + Types.Vector3(0, 0, 0.0001)
            rocket.obj.enemy = target.obj
            rocket.gameObject.image = "BOTTLEROCKETPROJECTILE"
            target.obj.Targeted = True
            self.engine.CreateNewObject(rocket)
            self.engine.PlaySound("Assets\\Sounds\\mortar_shoot.mp3")
            fired = True

        if self.weaponType == Types.WeaponTypes.ToothpickTrap:
            enemyList = self.engine.FindObject("GRID").obj.gridMatrix.GetCell(self.cell.cell).enemyLinkDefinite
            if len(enemyList) == 0:
                return
            else:
                trap = ToothpickTrap.Create(self.engine)
                trap.gameObject.size = self.gameObject.size
                trap.gameObject.position = self.gameObject.position
                trap.gameObject.image = self.gameObject.image
                trap.gameObject.rotation = self.gameObject.rotation
                self.engine.CreateNewObject(trap)
                trap.obj.enemies = enemyList.copy()
                self.Destroy()
                
                
                

        
        if fired:
            self.lastFired = self.engine.GetTotalTime()



#Create needs to be defined for every script in this folder. Everything should be exactly the same except for what is commented below, read that.
class Create():
    def __init__(self, engine):
        self.obj = Weapon(engine) #Replace Template with the name of your class
        self.obj.creator = self
    @property
    def gameObject(self):
        return self.obj.gameObject
