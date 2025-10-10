require("config")
package.projectPath='../Samples/classification/'
package.path=package.path..";../Samples/classification/lua/?.lua" --;"..package.path
require("common")
require("module")
require("RigidBodyWin/retargetting/module/poseEditingModule")
RC=require("RigidBodyWin/retargetting/module/retarget_common")


function ctor()
	mEventReceiver=EVR()
   this:create("Button", "Start (script)", "Start (script)")
   this:widget(0):buttonShortcut('FL_ALT+s')
   this:create("Button", "Start", "Start")

	this:create("Check_Button", "attach camera", "attach camera",1);
	this:widget(0):checkButtonValue(false);
	this:create("Button", "save current pose", "save current pose",1);
	this:create("Button", "save current pose as DOF", "save current pose as DOF",1);
	this:create("Button", "load current pose", "load current pose",1);
	this:create("Button", "load pose (lua)", "load pose (lua)",1);
	this:create("Button", "mirror pose", "mirror pose",1);
	this:create("Button", "rotate light", "rotate light",1);
	this:create("Button", "goto T-pose", "goto T-pose")
	this:create("Button", "goto identity pose", "goto identity pose")
   this:create("Button", "export current pose as identity pose", "export current pose as identity pose", 0,3,0)
	this:updateLayout()


	camInfo={}
end
function dtor()
	if mPoseEditingModule then
		mPoseEditingModule.CON=nil
	end
	if mSkin then
		RE.motionPanel():motionWin():detachSkin(mSkin)
		mSkin=nil
	end
	-- remove objects that are owned by LUA
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

	if hookAfterMotionLoad then
		hookAfterMotionLoad(mLoader)
	end
	mot.skin=RE.createVRMLskin(mLoader, false)
	local s=config.skinScale
	mot.skin:scale(s,s,s)
	mSkin=mot.skin
	mSkin:setMaterial('lightgrey_transparent')
	mSkin:applyMotionDOF(mMotionDOFcontainer.mot)

	RE.motionPanel():motionWin():addSkin(mSkin)
	do
		local vpos=RE.viewpoint().vpos:copy()
		local vat=RE.viewpoint().vat:copy()
		local rootpos=mMotionDOFcontainer.mot:row(0):toVector3(0)*config.skinScale
		local vdir=vat-vpos

		RE.viewpoint().vpos:assign(rootpos-vdir)
		RE.viewpoint().vat:assign(rootpos)
		RE.viewpoint():update()
	end

	mPoseEditingModule=PoseEditingModule(mLoader, mMotionDOFcontainer, mSkin, config.skinScale, 'auto')

	mPoseEditingModule:setPose(mMotionDOFcontainer.mot:row(0))

	this:updateLayout()
end

function onCallback(w, userData)

   if w:id()=="Start (script)" then
	  local filename=Fltk.chooseFile('choose a script file', '../Resource/scripts/modifyModel/' ,'*.lua', false)
	  if filename~='' then
		  dofile(filename)
		  _start(config) 
	  end
  elseif w:id()=="Start" then
	  local filename=Fltk.chooseFile('choose a wrl file', '../Resource/motion/' ,'*.wrl', false)
	  if filename ~='' then
		  local mot_file=Fltk.chooseFile('choose a motion file', '../Resource/motion/' ,'*', false)
		  if mot_file~='' then
			  Start(filename, mot_file, 0, 100)
			  _start(config) 
			  return
		  else
			  local loader=MainLib.VRMLloader(filename)
			  _createEmptyMotion(loader, 'empty.dof')
			  Start(filename, 'empty.dof', 0, 100)
			  _start(config) 
		  end
	  end
  elseif w:id()=="save current pose" then
	  local mot=MotionDOFcontainer(mLoader.dofInfo)
	  mot:resize(1)
	  mot.mot:row(0):assign(mPoseEditingModule.pose)
	  mot:exportMot("__temp.dof")

	  util.writeFile("temp.pose.lua", 'pose='..mPoseEditingModule.pose:toLuaString())
	  util.msgBox("exported to __temp.dof and temp.pose.lua")

  elseif w:id()=="mirror pose" then
	  local mot=MotionDOFcontainer(mLoader.dofInfo)
	  mot:resize(1)
	  mot.mot:row(0):assign(mPoseEditingModule.pose)

	  local Mot=Motion(mot.mot)
	  local TMot=Motion()

	  LrootIndices=intvectorn()
	  RrootIndices=intvectorn()
	  LrootIndices:pushBack(mLoader:getBoneByName("LeftShoulder"):treeIndex())
	  RrootIndices:pushBack(mLoader:getBoneByName("RightShoulder"):treeIndex())
	  LrootIndices:pushBack(mLoader:getBoneByName("LeftHip"):treeIndex())
	  RrootIndices:pushBack(mLoader:getBoneByName("RightHip"):treeIndex())
	  TMot:mirrorMotion(Mot, LrootIndices, RrootIndices)

	  dbg.console()
	  mLoader:setPose(TMot:pose(0))
	  mLoader:getPoseDOF(mPoseEditingModule.pose)
	  mPoseEditingModule:updateSkinPoseDOF(mPoseEditingModule.pose)
	  mPoseEditingModule:setPose(mPoseEditingModule.pose)

  elseif w:id()=="save current pose as DOF" then
	  local mot=MotionDOFcontainer(mLoader.dofInfo)
	  mot:resize(100)
	  for i=0,99 do
		  mot.mot:row(i):assign(mPoseEditingModule.pose)
	  end
	  mot:exportMot("__temp.dof")

	  util.writeFile("temp.pose.lua", 'pose='..mPoseEditingModule.pose:toLuaString())
	  util.msgBox("exported to __temp.dof and temp.pose.lua")
  elseif w:id()=="load current pose" then
	  local mot=MotionDOFcontainer(mLoader.dofInfo, "__temp.dof")
	  mLoader:setPoseDOF(mot.mot:row(0))
	  local pose=Pose()
	  mLoader:getPose(pose)
	  mPoseEditingModule:updateSkin(pose)
	  mPoseEditingModule:setPose(mPoseEditingModule.pose)
  elseif w:id()=="load pose (lua)" then
	  local f, msg=loadstring(util.readFile("temp.pose.lua"))
	  if not f then
		  print (msg)
	  else
		  f()
		  local mot=MotionDOFcontainer(mLoader.dofInfo, "__temp.dof")
		  mLoader:setPoseDOF(pose)
		  local pose=Pose()
		  mLoader:getPose(pose)
		  mPoseEditingModule:updateSkin(pose)
		  mPoseEditingModule:setPose(mPoseEditingModule.pose)
	  end
  elseif w:id()== "export current pose as identity pose" then
	  RC.exportCurrentPoseAsIdentityPose(mLoader, config.skel)
  elseif w:id()=="goto identity pose" then
	  local y=mPoseEditingModule.pose(1)
	  mLoader:updateInitialBone()
	  mLoader:getPoseDOF(mPoseEditingModule.pose) -- lightgrey_transparent
	  mPoseEditingModule.pose:set(0,0) -- x pos
	  mPoseEditingModule.pose:set(1,y) -- x pos
	  mPoseEditingModule.pose:set(2,0) -- z pos
	  mPoseEditingModule:updateSkinPoseDOF(mPoseEditingModule.pose)
	  mPoseEditingModule:setPose(mPoseEditingModule.pose)
  elseif w:id()=="goto T-pose" then
	  require("moduleIK")
	  RC.setVoca(mLoader)
	  mLoader:setPoseDOF(mPoseEditingModule.pose)
	  RC.gotoTpose(mLoader)
	  local pose=Pose()
	  mLoader:getPose(pose)
	  mPoseEditingModule:updateSkin(pose)
	  mPoseEditingModule:setPose(mPoseEditingModule.pose)
	elseif w:id()=="attach camera" then
		camInfo.attachToBody=w:checkButtonValue();
	elseif w:id()=='rotate light' then
		local osm=RE.ogreSceneManager()
		if osm:hasSceneNode("LightNode") then
			local lightnode=osm:getSceneNode("LightNode")
			lightnode:rotate(quater(math.rad(30), vector3(0,1,0)))
		end
	else 
		mPoseEditingModule:onCallback(w, userData)
	end
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

	mPoseEditingModule:setPose(mMotionDOFcontainer.mot:row(iframe))
	RE.output("iframe", iframe)

	if camInfo.attachToBody then
		local motionDOF=mMotionDOFcontainer.mot
		local p1=vector3(0,0,0);

		p1:assign(motionDOF:row(iframe):toVector3(0)*config.skinScale )

		local up=vector3(0,1,0)
		local vec=(p2-p1)/2;
		vec:normalize();
		local vec2=vec:copy();
		local xAxis=vec2:cross(up);

		RE.viewpoint().vpos:assign(p1+vec*30+xAxis*230+up*10)
		RE.viewpoint().vat:assign(p1+vec*60+up*10)

		RE.viewpoint():setFOVy(60)
		RE.viewpoint():setNearClipDistance(10)
		RE.viewpoint():update()
	end


end

function frameMove(fElapsedTime)
end



