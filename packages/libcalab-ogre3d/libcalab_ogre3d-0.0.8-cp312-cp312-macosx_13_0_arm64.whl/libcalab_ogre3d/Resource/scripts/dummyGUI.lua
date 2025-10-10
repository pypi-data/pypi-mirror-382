-- GUI classes that does nothing
-- the original codes in c++ will be overwritten!!! 

function MotionDOF:skeleton()
	print('do not use this!')
	assert(false)
end

MotionDOFview.skeleton=MotionDOF.skeleton

MotionPanel=LUAclass()
function MotionPanel:__init(x,y,w,h)
end

Ogre={}
Ogre.ObjectList=LUAclass()
function Ogre.ObjectList:__init()
end
Ogre.FrameListener=LUAclass()
Ogre.FrameEvent=LUAclass()
function Ogre.FrameEvent:__init()
	self.timeSinceLastFrame=0
end
Ogre.Light=LUAclass()
Ogre.AnimationState=LUAclass()
Ogre.SceneManager=LUAclass()

function Ogre.SceneManager:setShadowTextureSize(size) end
function Ogre.SceneManager:setShadowTextureCount(count) end
Ogre.Node=LUAclass()

function Ogre.Node:getParent()
	return nil
end
Ogre.SceneNode=LUAclass(Ogre.Node) 
Ogre.MovableObject=LUAclass()
Ogre.Entity=LUAclass(Ogre.MovableObject)
Ogre.ColourValue=LUAclass() 
Ogre.SimpleRenderable=LUAclass() 
FlLayout=LUAclass()

FlLayout.Widget=LUAclass()
function FlLayout.Widget:__init(a,b,c)
	self.args={a,b,c}
end
function FlLayout.Widget:buttonShortcut(v)
end
function FlLayout.Widget:sliderRange(a,b)
	self.sliderRange={a,b}
end
function FlLayout.Widget:sliderValue(v)
	if v then
		self.value=v
	else
		return self.value
	end
end
function FlLayout.Widget:checkButtonValue(v)
	if v then
		self.value=v
	else
		if self.value==1 or self.value==true then
			return true
		elseif self.value==0 or self.value==false then
			return false
		end
		return true
	end
end

function FlLayout:__init()
	self.widgets={}
end
function FlLayout:widget(i)
	return self.widgets[#self.widgets+i]
end
function FlLayout:create(a,b,c)
	table.insert(self.widgets, FlLayout.Widget())
end
function FlLayout.updateLayout()
end

this=FlLayout()

function dbg.namedDraw()
end
function dbg.draw()
end

