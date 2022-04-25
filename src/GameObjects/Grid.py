import math
import GameObjects
from MainEngine import Types #NEEDED. Mainly for Types.GameObject creation.
import pygame
class Grid(): #Change this to the name of your script
    
    def __init__(self, engine):
        self.gameObject = Types.GameObject(engine)
        self.gameObject.renderEnabled = False
        self.engine = engine
        self.gridSize = Types.Vector2(30,15)
        self.gridMatrix = Types.Matrix2x2(self.gridSize.x, self.gridSize.y)

    def Update(self):
        if (self.engine.Input.TestFor.RIGHTMOUSEDOWN()):
            cell = self.GetGridCell(self.engine.Input.TestFor.MOUSEPOS())
            if (type(cell) is Types.Cell):
                print(cell.cell.whole)
                self.gridMatrix.SetCell(cell.cell, cell)
            
    def GetGridCell(self, raycastPos):
        relative = Types.Vector3(raycastPos[0], raycastPos[1], 0) - self.gameObject.position
        gridCellSize = Types.Vector2(self.gameObject.size.x / self.gridSize.x, self.gameObject.size.y / self.gridSize.y)
        if (relative.x < 0 or relative.y < 0 or relative.x > self.gameObject.size.x or relative.y > self.gameObject.size.y):
            return None
        else: #If in the grid system do this
            cell = Types.Vector2(math.floor(relative.x / gridCellSize.x), math.floor(relative.y / gridCellSize.y))
            
            cellPos = Types.Vector2(cell.x * gridCellSize.x, cell.y * gridCellSize.y) + Types.Vector2(self.gameObject.position.x, self.gameObject.position.y)
            return Types.Cell(cellPos, gridCellSize, cell)




#Create needs to be defined for every script in this folder. Everything should be exactly the same except for what is commented below, read that.
class Create():
    def __init__(self, engine):
        self.obj = Grid(engine) #Replace Template with the name of your class
    @property
    def gameObject(self):
        return self.obj.gameObject