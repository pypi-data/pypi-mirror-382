
require("config")
require("common")
require("RigidBodyWin/retargetting/module/boneSelectionModule")
require("subRoutines/WRLloader")

--[[ parameters ]]--
--dbg.startTrace()

initialHeight=0

--model=model_files.jump5_cart
--model=model_files.justin_jump_cart
--model=model_files.hyunwoo_real_cart
--model=model_files.hyunwoo_full_cart
--model=model_files.justin_straight_run 
--model=model_files.justin_straight_run_cart
--model=model_files.justin_runf3_cart
--model=model_files.justin_run_cart
--model=model_files.justin_jump
model=model_files.gymnist 
--model=model_files.gymnist model_file='../Resource/scripts/ui/RigidBodyWin/gymnist_old.wrl' initialHeight=0.07

--model=model_files.hyunwoo_fourDOF3
--model=model_files.lowerbody
--model=model_files.lowerbody_allDOF1
--model=model_files.lowerbody_elastic
--model=model_files.lowerbody_elastic

skinScale=100   -- meter to centi-meter

k_p=600	-- Nm/rad
k_d=3 --  Nms/rad. worked in range [0, 1]
timestep=1/5000
rendering_step=1/60
usePenaltyMethod=true
poseMaintain=true
integrator=Physics.DynamicsSimulator.EULER
--integrator=DynamicsSimulator.RUNGE_KUTTA 
--simulator=simulators.SDFAST
--simulator=simulators.AIST
simulator=simulators.gmbs
collisionTestOnlyAnkle=false
useCapturedInitialPose=true
debugContactParam={10, 0, 0.01, 0, 0}-- size, tx, ty, tz, tfront

--[[ implementations ]]--

function rigidTransformMesh(bone, tf)
	local m=tf:copy()
	m:rightMult(bone:getFrame())
	m:leftMult(bone:getFrame():inverse())
	if restrictEditToSubmesh then
		bone:getMesh():rigidTransform(m, restrictEditToSubmesh)
	else
		bone:getMesh():rigidTransform(m)
	end
	-- local COM will be updated only when recalculateParam is called
	--bone:setLocalCOM(m*bone:localCOM())
end

function translateMesh(skel, name, tt)
	local f=RE.motionPanel():motionWin():getCurrFrame()
	mLoader:setPoseDOF(mMotionDOF:row(f))
	local index=skel:getBoneByName(name):treeIndex()
	t=transf()
	t:identity()
	t:leftMultTranslation(tt)
	--skel:VRMLbone(index):transformMesh(t)
	rigidTransformMesh(skel:VRMLbone(index), t)
end

-- rotate name with respect to name2 q
function rotateMesh(skel, name, name2, axis, angle)
   local index1=skel:getBoneByName(name):treeIndex()
   local index2=skel:getBoneByName(name2):treeIndex()
   t=transf() -- transformMesh함수쓰려면 matrix4로 고칠 것.
   t:identity()
   t:leftMultTranslation(skel:VRMLbone(index2):getTranslation()*-1)
   t:leftMultRotation(quater(angle, axis))
   t:leftMultTranslation(skel:VRMLbone(index2):getTranslation())
   
   --skel:VRMLbone(index1):transformMesh(t)
	rigidTransformMesh(skel:VRMLbone(index1), t)
end


-- s: vector3
function scaleMesh(skel, name, s)	
   local index=skel:getBoneByName(name):treeIndex()
   if restrictEditToSubmesh then
	   skel:VRMLbone(index):scaleMesh(s, restrictEditToSubmesh)
   else
	   skel:VRMLbone(index):scaleMesh(s)
   end
end


function translateBone(skel, name, t)
   local index=skel:getBoneByName(name):treeIndex()
   skel:VRMLbone(index):translateBone(t)
   
end

function T(name, t)
   translateMesh(mLoader, name, t)
end

function TM(markerIndex, t)
   mMarkers:translateMarker(markerIndex,t)
end

function R(name1, name2, a,t)
   rotateMesh(mLoader, name1, name2, a, math.rad(t))
end
function S(name, t)
   scaleMesh(mLoader, name, t)
end
function DM(name, pos)
	local f=RE.motionPanel():motionWin():getCurrFrame()
	mLoader:setPoseDOF(mMotionDOF:row(f))
	dbg.namedDraw('Sphere',mLoader:getBoneByName(name):getFrame():toGlobalPos(pos)*skinScale, "marker "..name,'green',2)
end

function DS(name, pos)
	dbg.namedDraw('Sphere',pos*skinScale, "gmaker "..name, 'green',2)
end
--class 'FrameEvent' (EventReceiver)
	FrameEvent=LUAclass(EventReceiver)
function FrameEvent:__init()
  -- EventReceiver.__init(self)
end

function FrameEvent:onFrameChanged(win, iframe)
   if mMarkers then
      mMarkers:onFrameChanged(win, iframe)
      mObjectList:setVisible(this:findWidget("draw markers"):checkButtonValue())
   end
   mBoneSelectionModule:setPose(mMotionDOF:row(iframe))
   if mZMP then
	   dbg.namedDraw('Sphere',mZMP(iframe)*skinScale, "ZMP", 'green',5)
   end
end

	       

function Start(filename, mot_file, initialHeight, _skinScale)
	if _skinScale then
		skinScale=_skinScale
	end

	if string.sub(mot_file, -3)=='bvh' then
		-- convert to dof
		local bvh_file=mot_file
		local wrl_file=filename
		local skel=RE.createMotionLoader(bvh_file, bvh_file)
		local skel2=MainLib.WRLloader(wrl_file);
		local motdof=convertMotionToMotDOF(skel, skel.mMotion, skel2)
		local motdofc=MotionDOFcontainer(skel2.dofInfo, motdof)
		mot_file=string.sub(mot_file, -4)..'dof'
		motdofc:exportMot(mot_file)

		-- bvh files are usually in cm scale.
		skinScale=1 -- mocapManipulation motions
	end
	model=deepCopyTable(model_files.default)
	model.file_name=filename
	model.mot_file=mot_file
	if initialHeight then
		model.initialHeight=initialHeight
	end

	_start()
end
function _start()
   
  initialHeight=model.initialHeight
   mEventReceiver=FrameEvent()
   detachSkin()
   print("start")
   mLoader=MainLib.WRLloader(model_file or model.file_name)
   mLoader:printHierarchy()

   --local markerFile=string.sub(model.file_name ,1, -5).."_comp.mrk"
   --print(markerFile)

   mMarkers=Markers(mLoader, mLoader:fkSolver(), markerFile, mObjectList)  

   mFloor=MainLib.VRMLloader("../Resource/mesh/floor_y.wrl")

   mSimulator=Physics.DynamicsSimulator_TRL_LCP('libccd')
   mSimulator:registerCharacter(mLoader)
   mSimulator:registerCharacter(mFloor)
   registerContactPairAll(model, mLoader, mFloor, mSimulator)
   
   mSimulator:init(timestep, integrator)
   
   mSimulator:setSimulatorParam("debugContact", debugContactParam) 
   mSimulator:setSimulatorParam("penaltyDepthMax", {0.0005})
   -- adjust initial positions

   if useCapturedInitialPose and model.mot_file~=nill then
      motcontainer=MainLib.MotionContainer(mLoader, model.mot_file)
      mMotionDOF=motcontainer.mot
      
	  local tiltedGround=model.tiltedGround
	  if tiltedGround then
		  local mot=mMotionDOF
		  for i=0, mot:numFrames()-1 do
			  local tf=MotionDOF.rootTransformation(mot:row(i))
			  MotionDOF.setRootTransformation(mot:row(i), tiltedGround*tf)
		  end
	  end
      for i=0, mMotionDOF:rows()-1 do
	 mMotionDOF:row(i):set(1, mMotionDOF:row(i)(1)+initialHeight)
      end

	  model.start=math.min(mMotionDOF:rows()-1, model.start)
      initialState=vectorn()
      initialState:assign(mMotionDOF:row(model.start))
      -- set global position
      initialState:set(0,0)
      initialState:set(1,initialState:get(1))
      initialState:set(2,0)
      
      print("initialState=",initialState)
      mSimulator:setLinkData(0, Physics.DynamicsSimulator.JOINT_VALUE, initialState)
      mSimulator:initSimulation()
   else
      -- manually adjust
      local wldst=mSimulator:getWorldState(0)
      wldst:localFrame(mLoader:getBoneByTreeIndex(1)).rotation:setRotation(vector3(1, 0, 0), toRadian(-10))
      wldst:localFrame(mLoader:getBoneByTreeIndex(1)).translation:radd(vector3(0, initialHeight, 0))
      wldst:localFrame(mLoader:getBoneByName(model.bones.left_knee)).rotation:setRotation(vector3(1, 0, 0), toRadian(10))
      wldst:forwardKinematics()
      
      mSimulator:setWorldState(0)
   end

   if motcontainer then
	   mBoneSelectionModule=BoneSelectionModule(mLoader, motcontainer, mSkin, skinScale, 'lightgrey_transparent')
	   mBoneSelectionModule:connect(mmEventFunction)

	   this:updateLayout()
	   this:redraw()
   end
   mLoader:setPoseDOF(mMotionDOF:row(model.start)   )
   local script=getScript()
   
   if script then
	   local doscript=loadstring(script)
	   doscript()
   end
   
  
   local heightEntity=mObjectList:registerEntity("height", "sphere1010.mesh")
   heightEntity:setScale(5,5,5)
   heightEntity:setPosition(mMotionDOF:row(model.start)(0)*skinScale, 95, mMotionDOF:row(model.start)(2)*skinScale)
   
   mLoader:_updateMeshEntity()
   
   
   mMarkers:reconnect(mLoader, mLoader:fkSolver(), mObjectList)
   mMarkers:redraw()
   
   if markerToolVisible then
	   mBrowser=this:findWidget("bones")

	   mBrowser:browserClear()
	   for i=1, mLoader:numBone()-1 do
		   mBrowser:browserAdd(mLoader:bone(i):name())
	   end

	   for i=1, mMarkers.markers:size() do

		   mBrowser:browserAdd(mLoader:bone(mMarkers.markers[i][1]):name()..tostring(i))
	   end
   end
   this:redraw()

   drawSkeleton=this:findWidget("draw skeleton"):checkButtonValue()
   
   createSkin()

   mSkin2=RE.createVRMLskin(mFloor, false)
   
   mSkin2:scale(skinScale,skinScale,skinScale)
   
   
   if poseMaintain then
      poseMaintainer:init(mSimulator)
   end
   
   --	debug.debug()
   mSkin:setPose(mSimulator,0)
   
   
   --mSimulator.setGVector(vector3(0,0,9.8))
   mSimulator:setGVector(vector3(0,9.8,0))
   mSimulator:initSimulation()

   collectgarbage("collect")
   collectgarbage("collect")
   collectgarbage("collect")
   collectgarbage("collect")

end


rotateX90=true
function exportCurrentPose(mLoader, fn)
	local objFolder=string.sub(fn, 1, -5).."_sd"
	print('creating '..objFolder..'. (An error message would be shown if the folder already exists. You can ignore it.)')
	os.createDir(objFolder)
	if rotateX90 then
		local T=transf(quater(math.rad(90), vector3(1,0,0)),vector3(0,0,0))
		mLoader:bone(1):getLocalFrame():leftMult(T)
		mLoader:fkSolver():forwardKinematics()
	end

	mLoader:export(fn)
end
function exportCurrentPoseAsMesh(fn)
	local objFolder=string.sub(model.file_name, 1, -5).."_sd"
	local mesh=MotionUtil.calcSkeletonMesh(fn)
	if rotateX90 then

	end
	mesh:saveOBJ(objFolder.."/_skel.obj",false,false)
end

function onCallback(w, userData)

   if w:id()=="Start (script)" then
	  local filename=Fltk.chooseFile('choose a script file', '../Resource/scripts/modifyModel/' ,'*.lua', false)
	  if filename~='' then
		  dofile(filename)
	  end
	  elseif w:id()=="show marker tools" then
		  showMarkerTools()
  elseif w:id()=="edit submesh" then
	  restrictEditToSubmesh=w:menuValue()-1
	  if restrictEditToSubmesh==-1 then
		  restrictEditToSubmesh=nil
	  else
		  local self=mBoneSelectionModule
		  self.subMeshSelection[self.selected]=restrictEditToSubmesh
	  end
	elseif w:id()=="run" then
		local expMode=this:findWidget("export operation"):menuText()
		if expMode== "export current pose as identity pose" then
			local M=require("RigidBodyWin/retargetting/module/retarget_common")
			M.exportCurrentPoseAsIdentityPose(mLoader, model.file_name)
		elseif expMode=="apply optimization result" then
			dofile("../Resource/scripts/ui/RigidBodyWin/optimization_result.lua")
			adjust(mLoader, model)

			if mSkin~=nill then
				RE.remove(mSkin)
				mSkin=nil
			end

			drawSkeleton=this:findWidget("draw skeleton"):checkButtonValue()
			mSkin=RE.createVRMLskin(mLoader, drawSkeleton)
			mSkin:setThickness(0.015)
			mSkin:scale(skinScale,skinScale,skinScale)
			mSkin:setPose(mSimulator,0)
		elseif expMode=="recalculate param" then
			mLoader:setTotalMass(model.totalmass or 65)
		elseif expMode=="recalculate param (water density)" then
			mLoader:setTotalMass(0)
			local totalMass=0
			for i=1, mLoader:numBone()-1 do
				totalMass=totalMass+mLoader:VRMLbone(i):mass()
			end
			print('total mass ', totalMass)
		elseif expMode=="export (only for blender)" then
			local f=RE.motionPanel():motionWin():getCurrFrame()
			mLoader:setPoseDOF(mMotionDOF:row(f))
			exportCurrentPose(mLoader, model.file_name)
			if not doNotExportSkeletonMesh then
				exportCurrentPoseAsMesh(model.file_name)
			end
			util.writeFile('blenderConfig.py', 'path="'..string.sub(model.file_name, 1,-5)..'_sd/"')

			print([[
			After editing meshes in blender, run blenderExportOBJ.py inside blender
			using text editor -> open -> run]])
			os.execute('blender -P blenderImportOBJ.py')
			updateAll()
		elseif expMode=="export current surface mesh (BVH compatible)" then

			MotionUtil.exportCurrentSurfaceMesh(mLoader, model.file_name)
		elseif expMode=="export model" then
      
			mLoader:updateInitialBone()
			exportCurrentPose(mLoader, model.file_name)
			if getScript() then
				mScript=this:findWidget("script")
				mScript:inputValue("")
			end

			local markerFile=string.sub(model.file_name ,1, -4).."_marker.lua"
			mMarkers:pack(markerFile,true)
			this:redraw()
		end
  elseif w:id()=='obj editing' and mBoneSelectionModule.selected then
	  local bone=mLoader:VRMLbone(mBoneSelectionModule.selected)
	  if w:menuText()=='replace .obj (global)' then
		  local chosenFile=Fltk.chooseFile("Choose obj for "..bone:name(), '../Resource/mesh', "*.obj", false)
		  if chosenFile then
			  if bone:hasShape() then
				  bone:getMesh():convertToOBJ()
			  end
			  local f=RE.motionPanel():motionWin():getCurrFrame()
			  mLoader:setPoseDOF(mMotionDOF:row(f))
			  exportCurrentPose(mLoader, model.file_name)


			  local url=model.file_name
			  local shapeFn=string.sub(url, 1,-5).."_sd/"..bone:name()..".obj"
			  os.copyFile(chosenFile, shapeFn)
			  updateAll()
		  end
	  elseif w:menuText()=='add .obj (local)' then
		  local chosenFile=Fltk.chooseFile("Choose obj for "..bone:name(), '../Resource/mesh', "*.obj", false)
		  if chosenFile then
			  local g=Geometry();
			  g:loadOBJ(chosenFile)
			  print('before ', bone:getMesh():numElements())

			  bone:getMesh():merge(bone:getMesh(), g)
			  print('after ', bone:getMesh():numElements())
			  mBoneSelectionModule.prevSelected_submesh=-1 -- invalidate prev selection.
			  updateSubMeshMenu(mBoneSelectionModule)
			  update()
		  end
	  elseif w:menuText()=="export seleted submesh to .obj" then
		  if restrictEditToSubmesh then
			  local chosenFile=Fltk.chooseFile("Choose obj" , '../Resource/mesh', "*.obj", true)
			  if chosenFile then
				  local g=Geometry();
				  g:extractSubMesh(bone:getMesh(), restrictEditToSubmesh)
				  g:saveOBJ(chosenFile, true, false)
			  end
		  end
	  elseif w:menuText()=='add sphere' then
		  if bone:hasShape() then
			  local g=Geometry();
			  g:initEllipsoid(vector3(5,5,5)/skinScale)
			  bone:getMesh():merge(bone:getMesh(), g)
			  update()
		  end
	  elseif w:menuText()=='add box' then
		  if bone:hasShape() then
			  local g=Geometry();
			  g:initBox(vector3(5,5,5)/skinScale)
			  bone:getMesh():merge(bone:getMesh(), g)
			  update()
		  end
	  elseif w:menuText()=='align cylinder to joints' then
		  if bone:hasShape() and bone:getMesh():numElements()==1
			  and (bone:getMesh():element(0).elementType==OBJloader.Element.CYLINDER
			  or bone:getMesh():element(0).elementType==OBJloader.Element.CAPSULE) then
			  local e=bone:getMesh():element(0)
			  assert(bone:childHead())
			  e.elementSize.y=bone:getFrame().translation:distance(bone:childHead():getFrame().translation)
			  e.elementSize.y=math.max(e.elementSize.y, 0.01)
			  bone:getMesh():_updateMeshFromElements()
			  update()
		  else
			  util.msgBox("This operation doesn't work for the selected bone") 
		  end
	  end
  elseif w:id()=='undo' then
	  local self=mBoneSelectionModule
	  if self and self.pushLoc then
		  local bone=mLoader:VRMLbone(self.pushLoc.bone)
		  bone:getMesh():assign(self.pushLoc[1])
		  update()
	  end

   elseif w:id()=="Start" then
	  local filename=Fltk.chooseFile('choose a wrl file', '../Resource/mocap_manipulation/bvh_files/2/' ,'*.{wrl,wrl.lua,wrl.dat}', false)
	  if filename ~='' then
		  for i,m in pairs(model_files) do
			  if type(m)=='table' and m.file_name==filename then
				  model=m
				  _start()
				  return
			  end
		  end
		  local mot_file=Fltk.chooseFile('choose a motion file', '../Resource/mocap_manipulation/bvh_files/2/' ,'*.{dof,mot,bvh,dof.lua}', false)
		  if mot_file~='' then
			  Start(filename, mot_file)
			  return
		  else
			  local loader=MainLib.WRLloader(filename)
			  _createEmptyMotion(loader, 'empty.dof')
			  Start(filename, 'empty.dof')
		  end
	  end


  elseif w:id()=="goto bind pose" then
	  mLoader:updateInitialBone()
	  updateSkinAndMarkers()
  elseif w:id()=="rotate 90 Y" then
	  mLoader:bone(1):getLocalFrame().rotation:leftMult(quater(math.rad(90), vector3(0,1,0)))
	  mLoader:fkSolver():forwardKinematics()
	  updateSkinAndMarkers()
  elseif w:id()=="goto T pose" then
	  local M=require("RigidBodyWin/retargetting/module/retarget_common")
	  M.setVoca(mLoader)
	  M.gotoTpose(mLoader)
	  updateSkinAndMarkers()
  elseif w:id()=="reload wrl" then
		updateAll()
   elseif w:id()=="draw markers" then      
      mObjectList:setVisible(w:checkButtonValue())

	  elseif w:id()=="marker tool" then
		  local text=w:menuText()
		  if text =="export marker only" then
			  local model_path="../Resource/scripts/ui/RigidBodyWin/"
			  local markerFile=Fltk.chooseFile("Choose a marker file", model_path, "*.mrk", true)
			  if markerFile  ~="" then
				  mMarkers:pack(markerFile)
			  end      
		  elseif text=="export marker (lua)" then
			  local model_path="../Resource/scripts/ui/RigidBodyWin/"
			  local markerFile=Fltk.chooseFile("Choose a marker file", model_path, "*_marker.lua", true)
			  if markerFile  ~="" then
				  mMarkers:pack(markerFile, true)
			  end      
		  elseif text=="import marker only" then
			  local model_path="../Resource/scripts/ui/RigidBodyWin/"
			  local markerFile=Fltk.chooseFile("Choose a marker file", model_path, "*.mrk", false)
			  if markerFile  ~="" then
				  mMarkers:unpackMarkers(markerFile)
				  mMarkers.drawOffset=vector3(0, initialHeight,0)
				  mMarkers:redraw()
			  end      
		  elseif text=="import marker (lua)" or text=="redo" then
			  local model_path="../Resource/scripts/ui/RigidBodyWin/"
			  local markerFile
			  if w:id()=="redo" then
				  markerFile=prevMarkerFile
			  end
			  if markerFile==nil then
				  markerFile=Fltk.chooseFile("Choose a marker file", model_path, "*_marker.lua", false)
				  prevMarkerFile=markerFile
			  end
			  if markerFile ~="" then
				  mMarkers:unpackMarkers(markerFile, true)
				  mMarkers.drawOffset=vector3(0, initialHeight,0)
				  mMarkers:redraw()
			  end      
		  elseif text=="createMarkers" then
			  mBrowser=this:findWidget("bones")
			  for i=1,mLoader:numBone()-1 do

				  if mBrowser:browserSelected(i) then
					  mMarkers.markers:pushBack({i, vector3(0.03,0,0)})
				  end
			  end
			  mMarkers:pack()
			  updateAll()
		  elseif text=="createMarkers (COM)" then
			  mBrowser=this:findWidget("bones")
			  mMarkers.markers:clear()
			  for i=1,mLoader:numBone()-1 do
				  mMarkers.markers:pushBack({i, mLoader:VRMLbone(i):localCOM()})
			  end
			  mMarkers:pack()
			  updateAll()
		  elseif text=="removeMarkers" then
			  mBrowser=this:findWidget("bones")
			  local candi=array:new()
			  for i=1,mMarkers.markers:size() do

				  if mBrowser:browserSelected(i+mLoader:numBone()-1) then
					  candi:pushBack(i)
				  end
			  end
			  out(candi)
			  mMarkers.markers:remove(candi)
			  mMarkers:pack()
			  updateAll()
		  end

   elseif w:id()=="translate" then
      mBrowser=this:findWidget("bones")
      mScript=this:findWidget("script")
      script=mScript:inputValue()
      script=script.."\ntrans=vector3(0,0,0.01)"
      for i=1,mLoader:numBone()-1 do

	 if mBrowser:browserSelected(i) then
	    print(mLoader:bone(i):name())
	    if mLoader:VRMLbone(i):hasShape() then
	       script=script.."\n "..'T("'..mLoader:bone(i):name()..'", trans)'
	    end
	 end
      end

      for i=1, mMarkers.markers:size() do
	 if mBrowser:browserSelected(i+mLoader:numBone()-1) then
	    script=script.."\n "..'TM('..tostring(i)..', trans,'..mLoader:bone(mMarkers.markers[i][1]):name()..')'
	 end
      end

      mScript:inputValue(script)
      updateAll()
  elseif w:id()=='calc ZMP' then
	  mZMP=vector3N(mMotionDOF:numFrames())
	  mLoader:calcZMP(mMotionDOF, mZMP:matView(),1)

   elseif w:id()=="rotate" then
      mBrowser=this:findWidget("bones")
      mScript=this:findWidget("script")
      script=mScript:inputValue()

      script=script.."\naxis=vector3(1,0,0)"
      script=script.."\nangle=1"
      for i=1,mLoader:numBone()-1 do

	 if mBrowser:browserSelected(i) then
	    print(mLoader:bone(i):name())
	    if mLoader:VRMLbone(i):hasShape() then
	       script=script.."\n "..'R("'..mLoader:bone(i):name()..'", "'..mLoader:bone(i):name()..'",axis,angle)'
	    end
	 end
      end
      mScript:inputValue(script)
      updateAll()
   elseif w:id()=="scale" then
      mBrowser=this:findWidget("bones")
      mScript=this:findWidget("script")
      script=mScript:inputValue()

      script=script.."\nscale=vector3(1,1,1)"

      for i=1,mLoader:numBone()-1 do

	 if mBrowser:browserSelected(i) then
	    print(mLoader:bone(i):name())
	    if mLoader:VRMLbone(i):hasShape() then
	       script=script.."\n "..'S("'..mLoader:bone(i):name()..'", scale)'
	    end
	 end
      end
      mScript:inputValue(script)
      updateAll()
   elseif w:id()=="update" then
	   local script=this:findWidget("script"):inputValue()
	   local doscript=loadstring(script)
	   doscript()
      update()
  elseif w:id()=="edit file" then
      mScript=this:findWidget("script")
	  local str=mScript:inputValue()
	  if string.len(str)>0 then
		  util.writeFile('temp.lua',str)
	  end
	  os.vi('temp.lua')
  elseif w:id()=="update from file" then
      mScript=this:findWidget("script")
	  mScript:inputValue(util.readFile('temp.lua'))
	  update()
   end

end

theta=vectorn()
niter=math.floor(rendering_step/timestep+0.5)
--timer=util.PerfTimer(1, niter.."simulation")

-- poseMaintainer is a namespace. Compare it to the class version PoseMaintainer in RagdollFallCompare.lua.
poseMaintainer={}
poseMaintainer.theta=vectorn()
poseMaintainer.dtheta=vectorn()
poseMaintainer.theta_d=vectorn() -- desired q
poseMaintainer.dtheta_d=vectorn() -- desired dq
poseMaintainer.controlforce=vectorn()
poseMaintainer.kp=vectorn()
poseMaintainer.kd=vectorn()


function poseMaintainer.init(self, simulator)
   simulator:getLinkData(0, Physics.DynamicsSimulator.JOINT_VALUE, self.theta_d)
   simulator:getLinkData(0, Physics.DynamicsSimulator.JOINT_VELOCITY, self.dtheta_d)
   local dofInfo=mLoader.dofInfo
   poseMaintainer.kp:setSize(dofInfo:numDOF())
   poseMaintainer.kp:setAllValue(k_p)
   poseMaintainer.kd:setSize(dofInfo:numDOF())
   poseMaintainer.kd:setAllValue(k_d)
   
   
   for i=1,mLoader:numBone()-1 do
      vbone=mLoader:VRMLbone(i)
      nJoint=vbone:numHRPjoints()
      for j=0, nJoint-1 do
	 if vbone:HRPjointType(j)==MainLib.VRMLTransform.SLIDE then
	    print("k_p=",vbone:DOFindex(j), k_p*100)
	    poseMaintainer.kp:set(vbone:DOFindex(j), model.k_p_slide)
	    poseMaintainer.kd:set(vbone:DOFindex(j), model.k_d_slide)
	 end
	 if str_include(vbone:name(), "foot") then
	    poseMaintainer.kp:set(vbone:DOFindex(j), k_p*0.6)
	    poseMaintainer.kd:set(vbone:DOFindex(j), k_d)
	 end
	 
	 if str_include(vbone:name(), "toes") then
	    poseMaintainer.kp:set(vbone:DOFindex(j), k_p*0.3)
	    poseMaintainer.kd:set(vbone:DOFindex(j), k_d)
	 end
	 
      end
   end

   -- exclude root joint
   poseMaintainer.kp:range(0,7):setAllValue(0)
   poseMaintainer.kd:range(0,7):setAllValue(0)

end

function poseMaintainer.generateTorque(self, simulator)
   simulator:getLinkData(0, Physics.DynamicsSimulator.JOINT_VALUE, self.theta)
   simulator:getLinkData(0, Physics.DynamicsSimulator.JOINT_VELOCITY, self.dtheta)
   self.controlforce:setSize(simulator:skeleton(0).dofInfo:numDOF())
   self.controlforce:setAllValue(0)
   
   self.controlforce:assign(self.kp*(self.theta_d-self.theta)+
			 self.kd*(self.dtheta_d-self.dtheta))
   
   
   --[[
   --debug.debug()
   for i=7, self.controlforce:size()-1 do
      self.controlforce:set(i, 
			    self.kp*(self.theta_d:get(i)-self.theta:get(i))
			    +self.kd*(self.dtheta_d:get(i)-self.dtheta:get(i)))
   end
   self.controlforce:set(7,self.controlforce:get(7))
]]--

local skeleton=simulator:skeleton(0)
local dofInfo=skeleton.dofInfo;

--[[
--debug.debug()
for i=2, dofInfo:numBone()-1 do
   local bone=skeleton:bone(i)
   --if str_include(bone:name(),"humerus")	-- problematic
   if false
   then
      self.controlforce:range(
	 dofInfo:startR(i),dofInfo:endR(i)):setAllValue(0)
   end
end]]--
simulator:setLinkData(0, Physics.DynamicsSimulator.JOINT_TORQUE, self.controlforce)
end

print("niter= ",niter)
function frameMove(fElapsedTime)
   if mLoader~=nill and mSimulator and this:findWidget("simulation"):checkButtonValue() then
      
      --		debug.debug()
      temp=vectorn()
      mSimulator:getLinkData(0, Physics.DynamicsSimulator.JOINT_VALUE, temp)
      print ("len", (temp-poseMaintainer.theta_d):length())
      
      --timer:start()
      for iter=0,niter do
	 mSimulator:stepSimulation()
	 if poseMaintain then
	    poseMaintainer:generateTorque(mSimulator)
	 end
      end
      --timer:stop()
      mSimulator:drawDebugInformation()
      mSkin:setPose(mSimulator,0)				
      
      titlebar:setCaption("currentTime="..mSimulator:currentTime())
   end
end

function removeSkin()
	if mSkin then
		RE.motionPanel():motionWin():detachSkin(mSkin)
	end
	mSkin=nil
	collectgarbage()
	collectgarbage()
	collectgarbage()
end
function createSkin()
   mSkin=RE.createVRMLskin(mLoader, drawSkeleton)
   mSkin:setThickness(3/skinScale)
   --mSkin:setMaterial("use_vertexcolor")
   mSkin:setMaterial("lightgrey_transparent")
   mSkin:scale(skinScale,skinScale,skinScale)
   if mMotionDOF then
      mSkin:applyMotionDOF(mMotionDOF)
      RE.motionPanel():motionWin():addSkin(mSkin)
      mAdded=true
   end
   if mBoneSelectionModule then
	   mBoneSelectionModule.skin=mSkin
   end
end

-- called when only meshes (in memory) have been modified.
function update()
	   this:redraw()
   mLoader:_updateMeshEntity()
   local f=RE.motionPanel():motionWin():getCurrFrame()
   removeSkin()
   createSkin()
   RE.motionPanel():motionWin():changeCurrFrame(f)
   --local f=RE.motionPanel():motionWin():getCurrFrame()
   --_start()
   --RE.motionPanel():motionWin():changeCurrFrame(f)
end

-- called when files have been modified.
function updateAll()
	dtor()
	this:redraw()
	local f=RE.motionPanel():motionWin():getCurrFrame()
	_start()
	RE.motionPanel():motionWin():changeCurrFrame(f)
end

function ctor()
   this:create("Button", "Start", "Start")
   this:widget(0):buttonShortcut("FL_ALT+s")
   this:create("Button", "Start (script)", "Start (script)")
   this:widget(0):buttonShortcut("s")

   this:create("Choice", "edit mode", "edit mode",1)
   this:widget(0):menuSize(7)
   this:widget(0):menuItem(0, 'translate','q')
   this:widget(0):menuItem(1, 'rotate','w')
   this:widget(0):menuItem(2, 'rotate in plane','e')
   this:widget(0):menuItem(3, 'scaleXZ')
   this:widget(0):menuItem(4, 'scaleXY')
   this:widget(0):menuItem(5, 'scale','r')
   this:widget(0):menuItem(6, 'scale radius','t')
   this:widget(0):menuValue(0)

   this:create("Choice", "obj editing", "obj editing",1)
   this:widget(0):menuSize(7)
   this:widget(0):menuItem(0, 'choose op for selected bone')
   this:widget(0):menuItem(1, 'replace .obj (global)', 'FL_ALT+c')
   this:widget(0):menuItem(2, 'add .obj (local)')
   this:widget(0):menuItem(3, 'add sphere')
   this:widget(0):menuItem(4, 'add box')
   this:widget(0):menuItem(5, 'export seleted submesh to .obj')
   this:widget(0):menuItem(6, 'align cylinder to joints')
   this:widget(0):menuValue(0)

   this:create("Choice", "edit submesh", "edit submesh", 1)
   this:widget(0):menuSize(1)
   this:widget(0):menuItem(0, 'edit all submeshes')
   this:widget(0):menuValue(0)
   
   this:create('Button', 'undo','undo',0)
   this:widget(0):buttonShortcut('FL_CTRL+u')

   this:create('Button', 'reload wrl','reload wrl',0)


   this:create("Check_Button", "simulation", "simulation", 0, 2,0)
   this:widget(0):checkButtonValue(0)
   this:widget(0):buttonShortcut("FL_ALT+s")
   
   this:create("Button", "single step", "single step", 2, 3,0)
   
   this:create("Check_Button", "draw skeleton", "draw skeleton", 0, 3,0)
   this:widget(0):checkButtonValue(0)

   this:create("Check_Button", "draw markers", "draw markers", 0, 3,0)
   this:widget(0):checkButtonValue(0)
   
   this:create("Choice", "export operation", "export operation",0,2)
   this:widget(0):menuSize(7)
   this:widget(0):menuItem(0, "apply optimization result")
   this:widget(0):menuItem(1, "recalculate param")
   this:widget(0):menuItem(2, "recalculate param (water density)")
   this:widget(0):menuItem(3, "export model")
   this:widget(0):menuItem(4,"export (only for blender)")
   this:widget(0):menuItem(5,"export current surface mesh (BVH compatible)")
   this:widget(0):menuItem(6,"export current pose as identity pose")
   this:widget(0):menuValue(2)
   this:create("Button","run","run", 2,3)



   this:create("Button", "goto bind pose", "goto bind pose", 0,3,0)
   this:create("Button", "rotate 90 Y", "rotate 90 Y", 0,3,0)
   this:create("Button", "goto T pose", "goto T pose", 0,3,0)

   this:create("Button", "calc ZMP", "calc ZMP")
   this:create("Button", "show marker tools", "show marker tools")
   
   mObjectList=Ogre.ObjectList ()

   mLoader=MainLib.WRLloader(model.file_name)
   mLoader:printHierarchy()



   this:updateLayout()
   this:redraw()
   
   titlebar:create()	

   if arg then
	   local filename=string.gsub(arg, ':','/')
	   local loader=MainLib.WRLloader(filename)
	   _createEmptyMotion(loader, 'empty.dof')
	   Start(filename, 'empty.dof')
   end
end

function detachSkin()
   if mAdded then
      RE.motionPanel():motionWin():detachSkin(mSkin)
      mAdded=false
   end
end

function dtor()

	if mBoneSelectionModule then
		mBoneSelectionModule.CON=nil
	end
	detachSkin()
	dbg.finalize()
	-- remove objects that are owned by C++
	if mSkin~=nill then
		mSkin=nil
	end
	if mSkin2~=nill then
		mSkin2=nil
	end
	titlebar:destroy()
	mObjectList:clear()
	-- remove objects that are owned by LUA
	collectgarbage()
end


function handleRendererEvent(ev, button, x, y)
	if not mBoneSelectionModule then return 0 end
	return mBoneSelectionModule:handleRendererEvent(ev, button, x,y)
end

function BoneSelectionModule:handleRendererEvent(ev, button, x, y)
	if self.CON then
		self.CON:handleRendererEvent(ev, button, x,y)
	end
	assert(self.pose)
	--print('button', button)
	if ev=="PUSH" then
		if self.selected and self.CON.selectedVertex~=-1 then
			assert(self.selected==self.CON.selectedVertex+1)
			self.CON:setOption('draggingDisabled', false)

			local bone=mLoader:VRMLbone(self.selected)
			print(bone:name())
			if bone:hasShape() then
				local editMode=this:findWidget("edit mode"):menuText()

				if editMode~="translate" then
					self.CON:setOption('draggingDisabled', true)
				end
				self.pushLoc={
					bone:getMesh():copy(),x,y,
					self.CON.conPos(self.selected-1):copy(),
					mode=editMode,
					bone=self.selected
				}
			else
				self.pushLoc=nil
				--self.CON:setOption('draggingDisabled', true)
				return 0
			end
			return 1
		end
		return 0
	elseif ev=="DRAG" then
		if self.pushLoc then
			local bone=mLoader:VRMLbone(self.selected)
			bone:getMesh():assign(self.pushLoc[1])

			if self.pushLoc.mode=="translate" then
				translateMesh(mLoader, bone:name(), 
				(self.CON.conPos(self.selected-1)-self.pushLoc[4])/skinScale)
			elseif self.pushLoc.mode=="scaleXZ" then
				local bone=mLoader:VRMLbone(self.pushLoc.bone)
				bone:getMesh():assign(self.pushLoc[1])
				bone:getMesh():scale(vector3(1+0.001*(x-self.pushLoc[2]),
									1,
									1+0.001*(y-self.pushLoc[3])));
				update()
			elseif self.pushLoc.mode=="scaleXY" then
				local bone=mLoader:VRMLbone(self.pushLoc.bone)
				bone:getMesh():assign(self.pushLoc[1])
				bone:getMesh():scale(vector3(1+0.001*(x-self.pushLoc[2]),
									
									1+0.001*(y-self.pushLoc[3]),1));
				update()
			elseif self.pushLoc.mode=="scale" then
				local bone=mLoader:VRMLbone(self.pushLoc.bone)
				bone:getMesh():assign(self.pushLoc[1])
				local f=1+0.001*(x-self.pushLoc[2])
				bone:getMesh():scale(vector3(f,f,f));
				update()
			elseif self.pushLoc.mode=="scale radius" then
				local bone=mLoader:VRMLbone(self.pushLoc.bone)
				bone:getMesh():assign(self.pushLoc[1])
				bone:getMesh():scaleElements(vector3(1+0.001*(x-self.pushLoc[2]),
									1,
									1))
				update()
			else
				local v=RE.viewpoint()
				local x_axis, y_axis, z_axis=v:getAxes()

				if self.pushLoc.mode=="rotate in plane" then
					rotateMesh(mLoader, bone:name(), bone:name(), z_axis, math.rad(x-self.pushLoc[2]))
				else
					rotateMesh(mLoader, bone:name(), bone:name(), y_axis, math.rad(x-self.pushLoc[2]))
					rotateMesh(mLoader, bone:name(), bone:name(), x_axis, math.rad(y-self.pushLoc[3]))
				end
			end
			update()


		end
		print(x,y)
		return 1
	elseif ev=="RELEASE" then
		self.CON:setOption('draggingDisabled', true)
		if self.pushLoc then
			self.CON.conPos(self.selected-1):assign(self.pushLoc[4])
			self.CON:redraw()
		end
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

function updateSubMeshMenu(self)
	if self.selected and self.selected~=self.prevSelected_submesh then
		if not self.subMeshSelection then
			self.subMeshSelection={}
		end
		local w=this:findWidget("edit submesh")
		local bone=mLoader:VRMLbone(self.selected)
		local numElt=0
		if bone:hasShape() then
			numElt=bone:getMesh():numElements()
		end
		w:menuSize(numElt+1)
		w:menuItem(0, 'edit all submeshes')
		for i=1,numElt do
			w:menuItem(i, 'edit submesh '..(i-1))
		end
		
		local ss=self.subMeshSelection[self.selected]
		if ss then
			w:menuValue(ss+1)
			-- recover last selection
			restrictEditToSubmesh=ss
		else
			w:menuValue(0)
			restrictEditToSubmesh=nil
		end
		self.prevSelected_submesh=self.selected
	end
end
function mmEventFunction(ev, val, self)
	BoneSelectionModule.eventFunction(ev, val, self)
	if ev=='selected' then
		updateSubMeshMenu(self)
	end
end

function getScript()
	if this:widgetIndex("script")==1 then
		return nil
	end
	return this:findWidget("script"):inputValue()
end

function showMarkerTools()
	markerToolVisible=true
	this:create("Choice", "marker tool", "marker tool")
	this:widget(0):menuSize(9)
	this:widget(0):menuItem(0,"choose marker operation")
	this:widget(0):menuItem(1,"export marker only")
	this:widget(0):menuItem(2,"import marker only")
	this:widget(0):menuItem(3,"export marker (lua)")
	this:widget(0):menuItem(4,"import marker (lua)")
	this:widget(0):menuItem(5,"redo")
	this:widget(0):menuItem(6,"createMarkers")
	this:widget(0):menuItem(7,"createMarkers (COM)")
	this:widget(0):menuItem(8,"removeMarkers")

	this:setWidgetHeight(100)
	this:create("Multi_Browser", "bones", "bones")


	this:setWidgetHeight(20)
	this:create("Box", "edit script below","edit script below")
	this:setWidgetHeight(200)
	this:create("Multiline_Input", "script", "script")

	this:resetToDefault()
	this:create("Button", "translate", "translate", 0,3,1)
	this:widget(0):buttonShortcut("FL_ALT+q")
	this:create("Button", "rotate", "rotate", 0,3,2)
	this:widget(0):buttonShortcut("FL_ALT+w")
	this:create("Button", "scale", "scale", 0,3,3)
	this:widget(0):buttonShortcut("FL_ALT+e")
	this:create("Button", "update", "update", 0,3,3)
	this:widget(0):buttonShortcut("FL_ALT+r")

	this:create("Button", "edit file", "edit file", 0,1,3)
	this:create("Button", "update from file", "update from file", 1,3,3)
	this:widget(0):buttonShortcut("FL_ALT+f")
	this:updateLayout()

end
function updateSkinAndMarkers()
	mSkin:setSamePose(mLoader:fkSolver())
	mMarkers:reconnect(mLoader, mLoader:fkSolver(), mObjectList)
	mMarkers:redraw()
end
