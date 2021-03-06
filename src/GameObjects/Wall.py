from MainEngine import Types #NEEDED. Mainly for Types.GameObject creation.
import pygame
class Wall(): #Change this to the name of your script
    def __init__(self, engine):
        self.gameObject = Types.GameObject(engine)
        self.engine = engine
        self.wallType: Types.WallTypes._GENERIC = None
        self.creator = None
        self.cell = None
        self.maxHealth = None
        self.health = None
        self.attachedWeapons = []
    def Destroy(self):
        self._UpdateLinkedMatrix()
        for weapon in self.attachedWeapons.copy():
            weapon.Destroy()
            self.attachedWeapons.remove(weapon)
            del weapon
        self.engine._Globals.sceneObjectsArray.remove(self.creator)
        del self #Should garbage collect now but there's still a reference somewhere in stack
    def _UpdateLinkedMatrix(self):

        if (self.cell == None):
            return
        if (self.engine.FindObject("GRID").obj.gridMatrix.CellExistsCheck(self.cell.cell + Types.Vector2(0, -1))):
            self.engine.FindObject("GRID").obj.gridMatrix.GetCell(self.cell.cell + Types.Vector2(0, -1)).belowCell_OL = None
        
        if (self.engine.FindObject("GRID").obj.gridMatrix.CellExistsCheck(self.cell.cell + Types.Vector2(0, 1))):
            self.engine.FindObject("GRID").obj.gridMatrix.GetCell(self.cell.cell + Types.Vector2(0, 1)).aboveCell_OL = None

        if (self.engine.FindObject("GRID").obj.gridMatrix.CellExistsCheck(self.cell.cell + Types.Vector2(1, 0))):
            self.engine.FindObject("GRID").obj.gridMatrix.GetCell(self.cell.cell + Types.Vector2(1, 0)).leftCell_OL = None

        if (self.engine.FindObject("GRID").obj.gridMatrix.CellExistsCheck(self.cell.cell + Types.Vector2(-1, 0))):
            self.engine.FindObject("GRID").obj.gridMatrix.GetCell(self.cell.cell + Types.Vector2(-1, 0)).rightCell_OL = None
        self.cell.objectLink = None
#Create needs to be defined for every script in this folder. Everything should be exactly the same except for what is commented below, read that.
class Create():
    def __init__(self, engine):
        self.obj = Wall(engine) #Replace Template with the name of your class
        self.obj.creator = self
    @property
    def gameObject(self):
        return self.obj.gameObject
