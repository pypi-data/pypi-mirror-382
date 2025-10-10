require("config")
package.projectPath='../Samples/classification/'
package.path=package.path..";../Samples/classification/lua/?.lua" --;"..package.path
require("common")
require("module")
require("RigidBodyWin/retargetting/module/poseEditingModule")
RC=require("RigidBodyWin/retargetting/module/retarget_common")

SelectUIhandler=LUAclass(SelectUI)
function SelectUIhandler:__init()
end

function SelectUIhandler:click(iframe)

	local t=this:findWidget('timeline operations'):menuText()
	if t=='crop' then
		addPanel({mPanels[1][1]:range(iframe, iframe+1):copy(), 'pose'..tostring(#mPanels)})
	else
		util.msgBox('no operation selected')
	end
end

function SelectUIhandler:selected(startframe, endframe)
	local mStart=startframe
	local mEnd=endframe
	print(mStart, mEnd)

	local t=this:findWidget('timeline operations'):menuText()
	if t=='crop' then
		addPanel({mPanels[1][1]:range(mStart, mEnd):copy(), 'crop'..tostring(#mPanels)})
	else
		util.msgBox('no operation selected')
	end
end
-- panel={motionDOF, label}
function addPanel(panel)
	table.insert(mPanels,panel)

	if panel[1]:numFrames()>1 then
		local con=boolN(panel[1]:numFrames())
		con:setAllValue(true)
		RE.motionPanel():scrollPanel():addPanel(con, CPixelRGB8(255,155,0))
		RE.motionPanel():scrollPanel():setLabel(panel[2])
	end
	local browser=this:findWidget('clips')
	browser:browserAdd(panel[2])
	this:redraw()
end
function selectPanel(label)
	local currFrame=RE.motionPanel():motionWin():getCurrFrame()
	local panel=findPanel(label)
	if panel then
		g_currPanel=label
		print(g_currPanel)
		RE.motionPanel():motionWin():detachSkin(mSkin)
		mSkin:applyMotionDOF(panel[1])
		RE.motionPanel():motionWin():addSkin(mSkin)
		local iframe=math.min(currFrame, panel[1]:numFrames()-1)
		RE.motionPanel():motionWin():changeCurrFrame(iframe)
		selectPose(iframe)
	end
end

function findPanel(label)
	for i=1, #mPanels do
		if mPanels[i][2]==label then
			return mPanels[i]
		end
	end
	return nil
end
function SelectUIhandler:panelSelected(label, iframe)
	print(label..  'selected', iframe)
	selectPanel(label)
end

function ctor()
	mEventReceiver=EVR()
	mSelectUI=SelectUIhandler()
	this:create("Button", "Start (script)", "Start (script)")
	this:widget(0):buttonShortcut('FL_ALT+s')

	this:create("Choice", "save/load", "save/load",1)
	this:widget(0):menuSize(5)
	this:widget(0):menuItem(0, "save scene", 'FL_CTRL+s')
	this:widget(0):menuItem(1, "load scene", 'FL_CTRL+l')
	this:widget(0):menuItem(2, "save current pose");
	this:widget(0):menuItem(3, "save current motion");
	this:widget(0):menuItem(4, "load current pose");

	this:create("Choice", "clip operations", 'clip op')
	this:widget(0):menuSize(12)
	local c=0
	this:widget(0):menuItem(c,'choose one')  c=c+1
	this:widget(0):menuItem(c,'stitch')  c=c+1
	this:widget(0):menuItem(c,'align') c=c+1
	this:widget(0):menuItem(c,'spread edit') c=c+1
	this:widget(0):menuItem(c,'keyframing') c=c+1
	this:widget(0):menuItem(c,'upsample 2x') c=c+1
	this:widget(0):menuItem(c,'duplicate') c=c+1
	this:widget(0):menuItem(c, "rotate light"); c=c+1
	this:widget(0):menuItem(c, "goto T-pose"); c=c+1
	this:widget(0):menuItem(c, "goto identity pose") c=c+1
	this:widget(0):menuItem(c, "draw COM") c=c+1
	this:widget(0):menuItem(c, "clear drawn") c=c+1

	this:create("Choice", "bone operations", 'bone-dep op')
	this:widget(0):menuSize(9)
	c=0
	this:widget(0):menuItem(c,'choose one')  c=c+1
	this:widget(0):menuItem(c,'mirror') c=c+1 -- 사용 전에 왼쪽 어깨 오른쪽 어깨 왼쪽 힙 오른쪽 힙 선택할 것.
	this:widget(0):menuItem(c,'copy pose', 'FL_ALT+c') c=c+1 -- 선택된 본과 그 하위본 정보만 카피됨.
	this:widget(0):menuItem(c,'paste pose', 'FL_ALT+v') c=c+1 -- 선택된 본과 그 하위본 정보만 카피됨.
	this:widget(0):menuItem(c,'draw positions') c=c+1 -- 선택된 본과 그 하위본 정보만 카피됨.
	this:widget(0):menuItem(c,'filter 31') c=c+1 -- 선택된 본과 그 하위본 정보만 카피됨.
	this:widget(0):menuItem(c,'filter 11') c=c+1 -- 선택된 본과 그 하위본 정보만 카피됨.
	this:widget(0):menuItem(c,'filter 5') c=c+1 -- 선택된 본과 그 하위본 정보만 카피됨.
	this:widget(0):menuItem(c,'filter 3') c=c+1 -- 선택된 본과 그 하위본 정보만 카피됨.


	this:create("Choice", "timeline operations", 'timeline')
	this:widget(0):menuSize(2)
	this:widget(0):menuItem(0, 'choose operations')
	this:widget(0):menuItem(1, 'crop')
	this:widget(0):menuValue(0)


	this:setWidgetHeight(100)
	this:create("Multi_Browser", "clips", "clips",0) -- or you can instead use Select_Browser for single select.
	this:widget(0):browserClear()
	this:resetToDefault()
	this:create("Box", "clips_emptyline","")
	this:setWidgetHeight(100)
	this:create("Multi_Browser", "bones", "bones") -- or you can instead use Select_Browser for single select.
	this:widget(0):browserClear()
	this:resetToDefault()
	this:create("Box", "bones_emptyline","")
	this:create("Button", "add selected", "add selected", 0,2)
	this:create("Button", "clear", "clear", 2,3)
	this:updateLayout()

	mObjectList=Ogre.ObjectList()
	camInfo={}
end
function dtor()
	if mPoseEditingModule then
		mPoseEditingModule.CON=nil
	end
	if mSkin then
		RE.motionPanel():motionWin():detachSkin(mSkin)
		mSkin:setVisible(false) -- garbage collection might be delayed
		mSkin=nil
	end
	mMot=nil
	RE.motionPanel():scrollPanel():removeAllPanel()
	local browser=this:findWidget('clips')
	browser:browserClear()
	local browser=this:findWidget('bones')
	browser:browserClear()
	mObjectList:clear()
	-- remove objects that are owned by LUA
	collectgarbage()
	collectgarbage()
	collectgarbage()
	collectgarbage()
end

function handleRendererEvent(ev, button, x, y)
	return mPoseEditingModule:handleRendererEvent(ev, button, x,y)
end

function Start(filename, mot_file, initialHeight, _skinScale)
	config={
		skel=filename,
		motion=mot_file,
		skinScale=_skinScale 
	}
end
function _start(config)
	if not config.skinScale then
		config.skinScale=skinScale or 1
	end
	local mot=loadMotion(config.skel, config.motion)
	mLoader=mot.loader
	mMotionDOFcontainer=mot.motionDOFcontainer
	g_currPanel='mocap'

	if hookAfterMotionLoad then
		hookAfterMotionLoad(mLoader)
	end
	mot.skin=RE.createVRMLskin(mLoader, false)
	local s=config.skinScale
	mot.skin:scale(s,s,s)
	mSkin=mot.skin
	mSkin:setMaterial('lightgrey_transparent')
	mSkin:applyMotionDOF(mMotionDOFcontainer.mot)

	mPanels={}
	addPanel({mMotionDOFcontainer.mot, 'mocap'})

	RE.motionPanel():motionWin():addSkin(mSkin)

	mPoseEditingModule=PoseEditingModule(mLoader, mMotionDOFcontainer, mSkin, config.skinScale, 'auto')
	mPoseEditingModule.poseEditingEventFunction=poseEdited

	selectPanel('mocap')
	selectPose(0)

	this:updateLayout()
end
function poseEdited(poseEM, param1)
	if param1=='undo last edit' then
		mSkin:setPoseDOF(poseEM.pose)
	end
end

function selectPose(iframe)
	local panel=findPanel(g_currPanel)
	if panel then
		local motdof=panel[1]
		if iframe<motdof:numFrames() then
			mPoseEditingModule:setPose(motdof:row(iframe))
			RE.output("iframe", iframe)
		end
	end
end

function stitch(prevMotion, nextSeg, windowSize)

	local mMotion=prevMotion:copy()
	local delta=math.floor(windowSize/2)
	mMotion:resize(prevMotion:numFrames()+nextSeg:numFrames()-1)
	if prevMotion:length()>delta and nextSeg:length()>delta then
		-- not implemented yet
		mMotion:stitch(prevMotion, nextSeg)
	elseif nextSeg:length()<delta then
		-- not implemented yet
		mMotion:stitch(prevMotion, nextSeg)
	else
		mMotion:stitch(prevMotion, nextSeg)
	end
	return mMotion
end

function align(prevMotion, nextSeg, windowSize)
	local mMotion=prevMotion:copy()
	local delta=math.floor(windowSize/2)
	mMotion:resize(prevMotion:numFrames()+nextSeg:numFrames()-1)
	mMotion:align(prevMotion, nextSeg)
	return mMotion
end

function normalizeQ(out)
	for i=0, out:numFrames()-1 do
		local q=out:row(i):toQuater(3)
		q:normalize()
		out:row(i):setQuater(3,q)
	end
end

function onCallback(w, userData)

	if w:id()=="Start (script)" then
		local filename=Fltk.chooseFile('choose a script file', '../Resource/scripts/modifyModel/' ,'*.lua', false)
		if filename~='' then
			dofile(filename)
			_start(config) 
		end
	elseif w:id()=='clear' then
		local browser=this:findWidget('bones')
		browser:browserClear()
	elseif w:id()=="save/load" then
		local tid=w:menuText()
		if tid=="save scene" then
			local out={}
			out.config=config
			for i=2,#mPanels do
				local panel=mPanels[i]
				out[i-1]={panel[1]:matView():copy(), panel[2]}
			end
			local bones={}
			local browser=this:findWidget('bones')
			for i=1, browser:browserSize() do
				table.insert(bones, browser:browserText(i))
			end
			out.bones=bones
			local curr=RE.viewpoint():toTable()
			local view={}
			for i=1,5 do
				RE.FltkRenderer():changeViewNoAnim(i-1)
				view[i]=RE.viewpoint():toTable()
			end
			RE.viewpoint():fromTable(curr)
			out.view=view

			util.saveTableToLua(out, 'temp.scene.lua')
		elseif tid=="load scene" then
			print('loading temp.scene.lua')
			local out=util.loadTableFromLua('temp.scene.lua')
			dtor()
			config=out.config
			_start(config)

			for i=1, #out do
				local panel=out[i]
				local motdofc=MotionDOF(mLoader.dofInfo)
				motdofc:resize(panel[1]:rows())
				motdofc:matView():assign(panel[1])
				addPanel({motdofc, panel[2]})
			end
			if out.bones then
				for i, v in ipairs(out.bones) do
					addSelected(v)
				end
			end
			if out.view then
				local curr=RE.viewpoint():toTable()
				for i, v in ipairs(out.view) do
					RE.viewpoint():fromTable(v)
					RE.FltkRenderer():saveView(i-1)
				end
				RE.viewpoint():fromTable(curr)
			end
			this:redraw()
		elseif tid=="save current motion" then
			local panel=findPanel(g_currPanel)

			if panel then
				local mot=MotionDOFcontainer(mLoader.dofInfo)
				mot:resize(panel[1]:numFrames())
				mot.mot:assign(panel[1])
				mot:exportMot("__temp.dof")
				util.msgBox("exported to __temp.dof ")
			end

		elseif tid=="save current pose" then
			local mot=MotionDOFcontainer(mLoader.dofInfo)
			mot:resize(1)
			mot.mot:row(0):assign(mPoseEditingModule.pose)
			mot:exportMot("__temp.dof")

			util.writeFile("temp.pose.lua", 'pose='..mPoseEditingModule.pose:toLuaString())
			util.msgBox("exported to __temp.dof and temp.pose.lua")
		elseif tid=="load current pose" then
			local mot=MotionDOFcontainer(mLoader.dofInfo, "__temp.dof")
			mLoader:setPoseDOF(mot.mot:row(0))
			local pose=Pose()
			mLoader:getPose(pose)
			mPoseEditingModule:updateSkin(pose)
			mPoseEditingModule:setPose(mPoseEditingModule.pose)
		end

	elseif w:id()=="clips" then
		selectPanel( mPanels[w:browserValue()][2])
	elseif w:id()=='bone operations' then
		local tid=w:menuText()
		if tid=='copy pose' then
			mLoader:setPoseDOF(mPoseEditingModule.pose)
			local bones=getSelectedBones()
			if #bones>0 then
				local clipboard={}
				for i, v in ipairs(bones) do
					local vv=MotionUtil.findChildren(mLoader, v)
					local rot=quaterN(vv:size())
					for j=0, vv:size()-1 do
						rot(j):assign(mLoader:bone(vv(j)):getFrame().rotation)
					end
					clipboard[i]=rot
				end
				m_clipboard=clipboard
				print('pose copied')
			else
				util.msgBox('no bones selected')
			end
		elseif tid:sub(1,6)=='filter' then
			local panel=findPanel(g_currPanel)
			local kernelSize=tonumber(tid:sub(8))
			math.gaussFilter(kernelSize, panel[1]:matView())

			normalizeQ(panel[1])
		elseif tid=='paste pose' then
			mLoader:setPoseDOF(mPoseEditingModule.pose)
			local bones=getSelectedBones()
			if m_clipboard and #bones>0 and #bones==#m_clipboard then
				for i, v in ipairs(bones) do
					local vv=MotionUtil.findChildren(mLoader, v)
					local rot=m_clipboard[i]
					if not rot or vv:size()~=rot:size() then
						print('Warning! Incompatible pose')
						return
					end
					for j=0, vv:size()-1 do
						mLoader:bone(vv(j)):getFrame().rotation:assign(rot(j))
					end
				end
				mLoader:fkSolver():getPoseDOFfromGlobal(mPoseEditingModule.pose)
				mPoseEditingModule:setPose(mPoseEditingModule.pose)
				mSkin:setPoseDOF(mPoseEditingModule.pose)
				print('pose pasted')
			end

		elseif tid=='mirror' then
			local LrootIndices=intvectorn()
			local RrootIndices=intvectorn()
			local bones=getSelectedBones()
			assert(math.fmod(#bones,2)==0)
			for i=1, #bones, 2 do
				LrootIndices:pushBack(bones[i])
				RrootIndices:pushBack(bones[i+1])
			end
			local motdof=RC.mirrorDOF(mLoader, findPanel(g_currPanel)[1], LrootIndices, RrootIndices)
			addPanel({ motdof, 'mirror of '..g_currPanel})
			selectPanel('mirrored'..#mPanels)
		elseif tid=='draw positions' then
			local bones=getSelectedBones()
			mLoader:setPoseDOF(mPoseEditingModule.pose)

			for i, v in ipairs(bones) do
				dbg.drawSphere(mObjectList, mLoader:bone(v):getFrame().translation*config.skinScale, RE.generateUniqueName(), 'green_transparent', 5)
			end
		end
	elseif w:id()=='clip operations' then
		local tid=w:menuText()
		if tid=="spread edit" then
			local origTF=MotionDOF.rootTransformation(mPoseEditingModule.origPose)
			local newTF=MotionDOF.rootTransformation(mPoseEditingModule.pose)

			local delta=newTF*origTF:inverse()

			local motdof=findPanel(g_currPanel)[1]
			for i=1, motdof:numFrames()-1 do
				local tf=MotionDOF.rootTransformation(motdof:row(i))
				MotionDOF.setRootTransformation(motdof:row(i), delta*tf)
			end
		elseif tid=='clear drawn' then
			mObjectList:clear()
		elseif tid=='draw COM' then
			local b=this:findWidget('clips')
			for i=1, b:browserSize() do
				if b:browserSelected(i) then
					local panel=mPanels[i]
					for ii=0, panel[1]:numFrames()-1 do
						mLoader:setPoseDOF(panel[1]:row(ii))
						dbg.drawSphere(mObjectList, mLoader:calcCOM()*config.skinScale, 'COM_'..i..'_'..ii, 'lightgrey_transparent', 5)
					end
				end
			end

		elseif tid=='rotate light' then
			local osm=RE.ogreSceneManager()
			if osm:hasSceneNode("LightNode") then
				local lightnode=osm:getSceneNode("LightNode")
				lightnode:rotate(quater(math.rad(30), vector3(0,1,0)))
			end
		elseif tid=="goto identity pose" then
			local y=mPoseEditingModule.pose(1)
			mLoader:updateInitialBone()
			mLoader:getPoseDOF(mPoseEditingModule.pose) -- lightgrey_transparent
			mPoseEditingModule.pose:set(0,0) -- x pos
			mPoseEditingModule.pose:set(1,y) -- x pos
			mPoseEditingModule.pose:set(2,0) -- z pos
			mPoseEditingModule:updateSkinPoseDOF(mPoseEditingModule.pose)
			mPoseEditingModule:setPose(mPoseEditingModule.pose)
		elseif tid=="goto T-pose" then
			require("moduleIK")
			RC.setVoca(mLoader)
			mLoader:setPoseDOF(mPoseEditingModule.pose)
			RC.gotoTpose(mLoader)
			local pose=Pose()
			mLoader:getPose(pose)
			mPoseEditingModule:updateSkin(pose)
			mPoseEditingModule:setPose(mPoseEditingModule.pose)
		elseif tid=='duplicate' then
			addPanel({ findPanel(g_currPanel)[1]:copy(), 'copied'..#mPanels})
			selectPanel('copied'..#mPanels)
		elseif tid=='keyframing' then
			local panels={}
			local timing={}
			local b=this:findWidget('clips')
			for i=1, b:browserSize() do
				if b:browserSelected(i) then
					assert(b:browserText(i):sub(1,3)=='key')
					table.insert(panels, mPanels[i])
					table.insert(timing, tonumber(b:browserText(i):sub(4)))
				end
			end
			local t=vectorn()
			t:setValues(unpack(timing))
			local m=matrixn(t:size(), panels[1][1]:row(0):size())
			for i=0, t:size()-1 do
				m:row(i):assign(panels[i+1][1]:row(0))
			end

			local curveFit=math.NonuniformSpline(t, m)

			local timing2=vectorn()
			timing2:colon2(0, t(t:size()-1)+1, 1)

			local out=MotionDOF(mLoader.dofInfo)
			out:resize(timing2:size())
			curveFit:getCurve(timing2, out:matView())

			normalizeQ(out)

			addPanel({ out, 'keyframed'..#mPanels})
			selectPanel('keyframed'..#mPanels)
		elseif tid=='upsample 2x' then
			local panel=findPanel(g_currPanel)
			local newMot=MotionDOF(mLoader.dofInfo)
			local nup=2
			newMot:resize(panel[1]:numFrames()*nup)
			local omat=panel[1]:matView():copy()
			omat:upsample(nup)
			newMot:matView():assign(omat)
			normalizeQ(newMot)
			addPanel({ newMot, 'upsampled '..#mPanels})
		elseif tid=='stitch'  or tid=='align' then
			local b=this:findWidget('clips')
			local panels={}
			for i=1, b:browserSize() do
				if b:browserSelected(i) then
					table.insert(panels, mPanels[i])
				end
			end

			if #panels==1 then
				table.insert(panels, panels[1])
			elseif #panels~=2 then
				util.msgBox('stitching more than two clips are not supported')
				return
			end

			if tid=='stitch' then
				addPanel({ stitch(panels[1][1], panels[2][1], 10), 'stitched'..#mPanels})
			else
				addPanel({ align(panels[1][1], panels[2][1], 10), 'stitched'..#mPanels})
			end
			selectPanel('stitched'..#mPanels)
		end
	

	elseif w:id()=='add selected' then
		if mPoseEditingModule.selected  then
			addSelected(mLoader:getBoneByTreeIndex(mPoseEditingModule.selected):name())
			this:redraw()
		end
	else 
		mPoseEditingModule:onCallback(w, userData)
	end
end
function addSelected(boneName)
	local browser=this:findWidget('bones')
	browser:browserAdd(boneName)
end

if EventReceiver then
	EVR=LUAclass(EventReceiver)
	function EVR:__init(graph)
		self.currFrame=0
		self.cameraInfo={}
	end
end


function EVR:onFrameChanged(win, iframe)
	self.currFrame=iframe

	selectPose(iframe)

end

function frameMove(fElapsedTime)
end

function getSelectedBones()
	local browser=this:findWidget('bones')
	local out={}
	for i=1, browser:browserSize() do
		table.insert(out, mLoader:getBoneByName(browser:browserText(i)):treeIndex())
	end
	return out
end


