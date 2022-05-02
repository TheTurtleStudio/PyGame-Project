from MainEngine import Types #NEEDED. Mainly for Types.GameObject creation.
from GameObjects import Grid, Healthbar, Wall
from GameObjects import GameObject
import random
import pygame
from MainEngine.Engine import Engine


class Enemy(): #Change this to the name of your script
    def __init__(self, engine: Engine):
        self.gameObject = Types.GameObject(engine)
        self.engine = engine
        self.creator = None
        self._oldCurrentCell1: Types.Cell = None
        self._oldCurrentCell2: Types.Cell = None
        self.Animator = Types.Animator(self.gameObject)
        self.enemyType: Types.EnemyTypes._GENERIC = Types.EnemyTypes._GENERIC
        self.animationVariationIndex = 0
        self._hasAttackedThisCycle = False
        self._attackAnimationPlaying = False
    def Start(self):
        self.gridAccessor = self.engine.FindObject("GRID")
        yPos = self.gridAccessor.obj.CellToPosition((0, random.randint(1, self.gridAccessor.obj.gridSize.y - 2))).y
        self.gameObject.position = Types.Vector3(-self.gameObject.size.x - 1, yPos, 500000)
        self.gameObject.image = "NOTEXTURE"
        self._destination = None
        self.animationVariationIndex = random.randint(0, len(self.enemyType._WalkingAnimation) - 1)
        

    def Update(self):
        if (self._destination != None):
            self.Animator.AnimationStep(self.enemyType._WalkingAnimation[self.animationVariationIndex])
            currentCell: Types.Cell = self.gridAccessor.obj.GetGridCellFULL(Types.Vector2(self.gameObject.position.x + (self.gameObject.size.x / 2), self.gameObject.position.y + (self.gameObject.size.y / 2)))
            yCellOffset = -(currentCell.cell.y - self._destination.y) #-1=up, 1=down
            yChange = ((1 if (yCellOffset > 0) else -1) * self.enemyType.speed * self.engine.GetDeltaTime())
            checkPos = Types.Vector2(self.gameObject.position.x + (self.gameObject.size.x / 2), self.gameObject.position.y + (self.gameObject.size.y if (yCellOffset > 0) else 0) + yChange)
            if (not self.gridAccessor.obj.gridMatrix.CellExistsCheck(self.gridAccessor.obj.PositionToCell(checkPos))):
                self.gameObject.position = Types.Vector3(self.gameObject.position.x, self.gridAccessor.obj.CellToPosition(currentCell.cell).y, self.gameObject.position.z)
                self.UpdateLink(False)
                self._destination = None
                return
            futureCell: Types.Cell = self.gridAccessor.obj.GetGridCellFULL(checkPos)
            if (futureCell.cell.y == self._destination.y):
                self.gameObject.position = Types.Vector3(self.gameObject.position.x, self.gridAccessor.obj.CellToPosition(currentCell.cell).y, self.gameObject.position.z)
                self._destination = None
            else:
                self.gameObject.rotation = 270 if (yCellOffset > 0) else 90
                self.gameObject.position += Types.Vector3(0, yChange, 0)
            self.UpdateLink(False)
            
        else:
            self.gameObject.rotation = 0
            move = True
            currentCell: Types.Cell = None
            futureCell: Types.Cell = None
            tempPos = Types.Vector2(self.gameObject.position.x + (self.gameObject.size.x / 2), self.gameObject.position.y + (self.gameObject.size.y / 2))
            if self.gridAccessor.obj.gridMatrix.CellExistsCheck(self.gridAccessor.obj.PositionToCell(tempPos)):
                currentCell = self.gridAccessor.obj.GetGridCellFULL(tempPos)
            tempPos = Types.Vector2(self.gameObject.position.x + self.gameObject.size.x + (self.enemyType.speed * self.engine.GetDeltaTime()), self.gameObject.position.y + (self.gameObject.size.y / 2))
            if self.gridAccessor.obj.gridMatrix.CellExistsCheck(self.gridAccessor.obj.PositionToCell(tempPos)):
                futureCell = self.gridAccessor.obj.GetGridCellFULL(tempPos)
            
            if (futureCell != None) and (type(futureCell.objectLink) == Wall.Create):
                self.gameObject.position = Types.Vector3(self.gameObject.position.x, self.gridAccessor.obj.CellToPosition(currentCell.cell).y, self.gameObject.position.z)
                move = False

            if move:
                if (currentCell != None) and (currentCell.cell.x == self.gridAccessor.obj.gridSize.x - 1) and (futureCell == None): #If they've reached the main wall
                    self.HandleBaseWallDamage()
                else:
                    if self._attackAnimationPlaying:
                        self.Animator.AnimationStep(self.enemyType._AttackAnimation)
                        self._attackAnimationPlaying = not self.Animator.finished
                    else:
                        self.gameObject.position += Types.Vector3(self.enemyType.speed * self.engine.GetDeltaTime(), 0, 0)
                        self.Animator.AnimationStep(self.enemyType._WalkingAnimation[self.animationVariationIndex])
                self.UpdateLink()
                
            else: #If there's something in the way (a wall)
                immediateAbove = None
                immediateBelow = None
                encounteredWallAbove = None
                encounteredWallBelow = None
                if (currentCell.aboveCell_OL):
                    immediateAbove = currentCell.aboveCell_OL.objectLink
                if (currentCell.belowCell_OL):
                    immediateBelow = currentCell.belowCell_OL.objectLink
                if (futureCell.aboveCell_OL):
                    encounteredWallAbove = futureCell.aboveCell_OL.objectLink
                if (futureCell.belowCell_OL):
                    encounteredWallBelow = futureCell.belowCell_OL.objectLink
                current = self.gridAccessor.obj.PositionToCell(self.gameObject.position)
                canGoAbove = (immediateAbove == None) and (encounteredWallAbove == None) and self.gridAccessor.obj.gridMatrix.CellExistsCheck((current.x, current.y - 1))
                canGoBelow = (immediateBelow == None) and (encounteredWallBelow == None) and self.gridAccessor.obj.gridMatrix.CellExistsCheck((current.x, current.y + 1))
                if (canGoAbove or canGoBelow):
                    if (canGoAbove and canGoBelow):
                        goAbove = bool(random.getrandbits(1))
                    else:
                        goAbove = canGoAbove
                    self._destination = currentCell.cell + Types.Vector2(0, -2 if goAbove else 2)
                else:
                    self.HandleWallAttack(futureCell)


    def HandleBaseWallDamage(self):
        healthBarObj: Healthbar.Healthbar = self.engine.FindObject("HEALTHBAR").obj
        if healthBarObj.health != 0:
            self.Animator.AnimationStep(self.enemyType._AttackAnimation)
            if (self.Animator.currentFrame == self.enemyType._AttackAnimationAttackFrame):
                if not self._hasAttackedThisCycle:
                    healthBarObj.health -= self.enemyType.damage
                    self._hasAttackedThisCycle = True
            else:
                self._hasAttackedThisCycle = False
            if (self.Animator.finished):
                self.Animator.ResetAnimationState()
            self._attackAnimationPlaying = not self.Animator.finished
        else:
            self.Animator.ResetAnimationState() #Play idle here instead

    def HandleWallAttack(self, wall: Types.Cell):
        self.Animator.AnimationStep(self.enemyType._AttackAnimation)
        if (self.Animator.currentFrame == self.enemyType._AttackAnimationAttackFrame):
            if not self._hasAttackedThisCycle:
                wall.objectLink.obj.health -= self.enemyType.damage
                self._hasAttackedThisCycle = True
                if wall.objectLink.obj.health <= 0:
                    self.gridAccessor.obj.DestroyWallChain(wall)
        else:
            self._hasAttackedThisCycle = False
        if (self.Animator.finished):
            self.Animator.ResetAnimationState()
        self._attackAnimationPlaying = not self.Animator.finished

    def GetEndPoints(self, horizontal=True):
        if (horizontal):
            position1 = (self.gameObject.position.x + self.gameObject.size.x, self.gameObject.position.y + (self.gameObject.size.y / 2))
            position2 = (self.gameObject.position.x, self.gameObject.position.y + (self.gameObject.size.y / 2))
        else:
            position1 = (self.gameObject.position.x + (self.gameObject.size.x / 2), self.gameObject.position.y + self.gameObject.size.y)
            position2 = (self.gameObject.position.x + (self.gameObject.size.x / 2), self.gameObject.position.y)
        return (position1, position2)
    def UpdateLink(self, horizontal=True):
        position1, position2 = self.GetEndPoints(horizontal=horizontal)
        if self._oldCurrentCell1:
            self._oldCurrentCell1.enemyLink = None
        if self._oldCurrentCell2:
            self._oldCurrentCell2.enemyLink = None
        if self.gridAccessor.obj.gridMatrix.CellExistsCheck(self.gridAccessor.obj.PositionToCell(position1)): #Check if the first cell position exists
            newCurrentCell = self.gridAccessor.obj.GetGridCellFULL(Types.Vector2(position1[0], position1[1]))
            newCurrentCell.enemyLink = self
            self._oldCurrentCell1 = newCurrentCell
        if self.gridAccessor.obj.gridMatrix.CellExistsCheck(self.gridAccessor.obj.PositionToCell(position2)): #Check if the first cell position exists
            newCurrentCell = self.gridAccessor.obj.GetGridCellFULL(Types.Vector2(position2[0], position2[1]))
            newCurrentCell.enemyLink = self
            self._oldCurrentCell2 = newCurrentCell
        
            

#Create needs to be defined for every script in this folder. Everything should be exactly the same except for what is commented below, read that.
class Create():
    def __init__(self, engine):
        self.obj = Enemy(engine) #Replace Template with the name of your class
        self.obj.creator = self
    @property
    def gameObject(self):
        return self.obj.gameObject
