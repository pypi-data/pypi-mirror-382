require("RigidBodyWin/subRoutines/Constraints")
require("moduleIK")

BoneSelectionModule=LUAclass()

function BoneSelectionModule:__init(loader, motionDOFcontainer, skin, skinScale, defaultMaterial)
	self.loader=loader
	self.motionDOFcontainer=motionDOFcontainer
	if not skin then
		self.skin=RE.createSkin(loader)
		self.skin:setScale(skinScale)
		self.skin:setMaterial('lightgrey_verytransparent')
	else
		self.skin=skin
	end

	self.skinScale=skinScale
	self.defaultMaterial=defaultMaterial
	if this:widgetIndex('select bone')==1 then
		this:create('Choice', 'select bone','select bone',0)
		this:widget(0):menuSize(self.loader:numBone())
		this:widget(0):menuItem(0, 'choose bone')
		for i=1, self.loader:numBone()-1 do
			this:widget(0):menuItem(i, self.loader:bone(i):name())
		end
		this:widget(0):menuValue(0)
	end
	do
		local currFrame=0
		self.loader:setPoseDOF(self.motionDOFcontainer.mot:row(currFrame))
		local originalPos={}
		for i=1,self.loader:numBone()-1 do
			local opos=self.loader:bone(i):getFrame()*vector3(0,0,0)
			originalPos[i]=opos*self.skinScale
		end
		originalPos.prefix="boneSel"
		self.CON=Constraints(originalPos)
		self.CON:setOption('draggingDisabled', true)
		self.CON:setOption(1) -- sphere size
		self.CON.unselectRadius=50 -- sphere size for unselect
		self.CON:connect(self.eventFunction, self)
	end
	self.pose=motionDOFcontainer.mot:row(0)
end
function BoneSelectionModule:connect(evf)
	self.eventFunction=evf
	self.CON:connect(evf, self)
end
function BoneSelectionModule.eventFunction(ev, val, self)
	if ev=='selected' then
		local w=this:findWidget('select bone')
		w:menuValue(val+1)
		self:_selectBone(val+1)
		w:redraw()
	end
end

function BoneSelectionModule:setPose(pose, poseq)
	-- reference!
	self.pose=pose
	self.poseq=poseq
	self:updateCON()
end

function BoneSelectionModule:handleRendererEvent(ev, button, x, y)
	if self.CON then
		self.CON:handleRendererEvent(ev, button, x,y)
	end
	assert(self.pose)
	--print('button', button)
	if ev=="PUSH" then
		if self.selected then
			self.CON:setOption('draggingDisabled', false)
			return 1
		end
		return 0
	elseif ev=="DRAG" then
		return 1
	elseif ev=="RELEASE" then
		self.CON:setOption('draggingDisabled', true)
		return 1
	elseif ev=="MOVE" then
		--print("MOVE")
		return 1
	elseif ev=="FORWARD" then
		return 1
	elseif ev=="BACKWARD" then
		return 1
	elseif ev=="LEFT" then
		return 1
	elseif ev=="RIGHT" then
		return 1
	end
	return 0
end


function BoneSelectionModule:onCallback(w, userData)
	if w:id()=='select bone' then
		print(w:menuText())
		self:_selectBone(w:menuValue())
	end
end

-- i==0 or nil for unselection.
function BoneSelectionModule:_selectBone(i)
	if i==0 then i=nil end

	local defaultMat=self.defaultMaterial 
	if self.selected and self.selected~=i and defaultMat and self.skin.setBoneMaterial then
		self.skin:setBoneMaterial(self.selected, defaultMat)
	end
	self.selected=i
	if defaultMat and i and self.skin.setBoneMaterial then
		self.skin:setBoneMaterial(i, 'green_transparent')
	end
end
function BoneSelectionModule:updateCON()
	if self.poseq then
		self.loader:setPose(self.poseq)
		self.skin:setPose(self.poseq)
	else
		self.loader:setPoseDOF(self.pose)
		self.skin:setPoseDOF(self.pose)
	end
	local originalPos={}
	for i=1,self.loader:numBone()-1 do
		local opos=self.loader:bone(i):getFrame()*vector3(0,0,0)
		originalPos[i]=opos*self.skinScale
	end
	self.CON:setPos(originalPos)
end
