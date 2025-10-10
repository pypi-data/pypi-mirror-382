   
require("config")
require("module")
require("common")
require("cameraTracker")

SelectUIhandler=LUAclass(SelectUI)
function SelectUIhandler:__init()
end
function SelectUIhandler:selected(startframe, endframe)
	mDrawPoses.mStart=startframe
	mDrawPoses.mEnd=endframe
	print(mStart, mEnd)
end
function SelectUIhandler:panelSelected(label, iframe)
end
model_path="../Resource/motion/"
-- debugVis: uncomment driverDynamic.lua : GUI("showOgreTraceManager",{}) for the most verbose output
debugVis=false 
--totalmass=60	-- recalculate inertia if totalmass~=nill
useNearestSamplingWhenExportingBVH=false

--dbg.startTrace3()
function plot(fn)

	require('pyMrdplot')
	mPython=true
	plotSignal("plot horizontal COM speed")
	mPython=nil
	if fn then
		fn=string.gsub(fn, "\\.dof",".mrd")
		pyMrdplot3('debug_plot.mrd', fn, true)
	else
		pyMrdplot3('debug_plot.mrd')
	end
end

function rotateBackground(angle)
	  local osm=RE.ogreSceneManager()
	  if osm:hasSceneNode("BackgroundNode") then
		  local lightnode=osm:getSceneNode("BackgroundNode")
		  lightnode:rotate(quater(angle, vector3(1,0,0)))
	  end
end
function adjustHeight(initialHeight)
		local mot=mMotionDOFcontainer.mot
		for i=0, mot:numFrames()-1 do
			mot:row(i):set(1, mot:row(i):get(1)+initialHeight)
		end
		mSkin:applyMotionDOF(mMotionDOFcontainer.mot)
end
function scr(p,p2) -- for commandline use, e.g. lua short.lua wrlv "ctor();scr(3)"
	p =p or 1
	if p==1 or p==2 then
		--lpred='justin_jump'
		--model=model_files[lpred]
		--if model then
			--_start(model.file_name)
			--_applyMotion(model.mot_file)
		--else
			--print('no model '..lpred..' found')
		--end
		if p==1 then
			onCallback(this:findWidget("load debug_plot.dof"),0)
		else
			onCallback(this:findWidget("load debug_plot.dof (debug)"),0)
		end
--		mEventReceiver:attachCamera()
	elseif p==3 then
		_start("../Resource/scripts/ui/RigidBodyWin/gymnist_raw.wrl")
		_applyMotion("../Resource/scripts/ui/RigidBodyWin/gymnist_raw.mot")
	elseif p==4 then
		local l=RE.motionLoader("../Resource/scripts/ui/RigidBodyWin/gymnist_raw.mot")
		local l2=MainLib.VRMLloader("../Resource/scripts/ui/RigidBodyWin/gymnist_raw.wrl")
		print('num bones: ',l:numBone(), l:numRotJoint(), l:numTransJoint())
		print('num bones: ',l2:numBone(), l2:numRotJoint(), l2:numTransJoint())
		dbg.console()
	else
		model=scenarios.toModel(useCase.scenario)
		chosenFile=model.file_name
		_start(model.file_name)
		_applyMotion(p)
		if debugVis then
			mSkin:setMaterial('lightgrey_transparent')
		end
		mEventReceiver:loadTraceManager()
	end
end

function ctor()

	mEventReceiver=EVR()
	mSelectUI=SelectUIhandler()

	--   this:create("Button", "load a predefined model", "load a predefined model", 0,3,0)


	-- modelChooser is defined in common.lua
	modelChooser:createMenu("load a predefined model") --
	this:create("Choice", "load file format")
	do
		this:widget(0):menuSize(8)
		this:widget(0):menuItem(0, "load file format")
		this:widget(0):menuItem(1, "load debug_plot.dof",'FL_CTRL+d' )
		this:widget(0):menuItem(2, "load debug_plot.dof (debug)" )
		this:widget(0):menuItem(3, "load a dof/bvh file",'FL_CTRL+l' )
		this:widget(0):menuItem(4, "add a dof file" )
		this:widget(0):menuItem(5, "load a model" ,'FL_CTRL+m')
		this:widget(0):menuItem(6, "load from script", 'FL_CTRL+s' )
		this:widget(0):menuItem(7, "generate a random motion" )
		this:widget(0):menuValue(0)
	end
	this:create("Choice", "export")
	do
		this:widget(0):menuSize(9)
		this:widget(0):menuItem(0,'export file format')
		this:widget(0):menuItem(1,'export BVH')
		this:widget(0):menuItem(2,'export BVH (original size)')
		this:widget(0):menuItem(3,'export WRL')
		this:widget(0):menuItem(4,'export DOF')
		this:widget(0):menuItem(5,"export identity pose")
		this:widget(0):menuItem(6,"export identity pose (original size)")
		this:widget(0):menuItem(7,"export 2D pos")
		this:widget(0):menuItem(8,"export current surface mesh")
		this:widget(0):menuValue(0)
	end

	do
		this:create("Choice", "motion editing")
		this:widget(0):menuSize(14)
		this:widget(0):menuItem(0, "motion editing");
		this:widget(0):menuItem(1, "center motion");
		this:widget(0):menuItem(2, "+initialheight");
		this:widget(0):menuItem(3, "+1");
		this:widget(0):menuItem(4, "rotate motion");
		this:widget(0):menuItem(5, "measure height");
		this:widget(0):menuItem(6, "auto Y translation");
		this:widget(0):menuItem(7, "1cm up");
		this:widget(0):menuItem(8, "1cm down");
		this:widget(0):menuItem(9, "50cm up");
		this:widget(0):menuItem(10, "50cm down");
		this:widget(0):menuItem(11, "4x downsample");
		this:widget(0):menuItem(12, "append identity pose");
		this:widget(0):menuItem(13, "append T-pose");
		this:widget(0):menuValue(0)
	end

	do
		this:create("Choice", "plot signal", "", 0)
		this:widget(0):menuSize(11)
		this:widget(0):menuItem(0, "plot signal")
		this:widget(0):menuItem(1, "draw COM traj")
		this:widget(0):menuItem(2, "plot pose")
		this:widget(0):menuItem(3, "plot horizontal COM speed (python)")
		this:widget(0):menuItem(4, "plot contact force")
		this:widget(0):menuItem(5, "plot contact force (python)")
		this:widget(0):menuItem(6,  "set comparision target")
		this:widget(0):menuItem(7,  "compare horizontal COM speed")
		this:widget(0):menuItem(8,  "hand-tune comparision plot")
		this:widget(0):menuItem(9,  "compare pose")
		this:widget(0):menuItem(10,  "draw poses")
		this:widget(0):menuValue(0)
	end

	this:create("Button", "test","test",0,1,0)
	this:create("Button", "filter", "filter", 1, 3,0)
	this:create("Button", "capture applied motion", "capture applied motion",0,3,0)
	this:create("Button", "capture applied motion (no filter)", "capture applied motion (no filter)",0,3,0)
	this:create("Button", "capture applied motion (0.25x)", "capture applied motion (0.25x)",0,3,0)
	this:create("Button", "capture frames", "capture frames",0,3,0)
	this:create("Button", "rotate light", "rotate light",0,2,0)
	this:create("Button", "rotate background", "background",2,3,0)
	this:create("Button", "rotate background +5", "+5",2,3,0)
	this:create("Button", "rotate background -5", "-5",2,3,0)

	this:create("Button", "discard later motion", "discard later motion",0,2)
	this:create("Button", "discard earlier motion", "earlier",2,3)
	this:create("Button", "chop 300-800","chop 300-800",0,3)
	this:widget(0):buttonShortcut("FL_ALT+p")

	this:create("Button", "attach camera", "attach camera",0,2)
	this:widget(0):buttonShortcut("FL_ALT+c")
	this:create("Button", "attach camera2", "camera2",2,3)
	this:widget(0):buttonShortcut("FL_ALT+d")

	this:create("Check_Button", "draw skeleton", "draw skeleton", 0, 3,0)
	this:widget(0):checkButtonValue(0)
	this:create("Check_Button", "draw debuginfo", "draw debuginfo", 0, 3,0)
	this:widget(0):checkButtonValue(debugVis)
	this:create('Button', 'init useCase', 'init useCase',0,2,0)
	this:widget(0):buttonShortcut("FL_ALT+u")
	this:create('Button', 'init useCaseMenu', 'menu',2)

	this:updateLayout()
	this:redraw()

	mObjectList=Ogre.ObjectList()

	RE.viewpoint():setFOVy(44.999999)
	local vpos=vector3(94.777964, 126.724047, 352.393547)
	local vat=vector3(-34.317428, 67.508947, -4.622992)
	RE.viewpoint().vpos:assign(vat+(vpos-vat)*1.5)
	RE.viewpoint().vat:assign(vat)
	RE.viewpoint():update()
	RE.renderer():fixedTimeStep(false)   
end


function extractDiscontinuity(mot)

   discontinuity=boolN(mot:numFrames())

   for i=0,mot:numFrames()-1 do
      discontinuity:set(i, mot:isConstraint(i, FootstepDetection.IS_DISCONTINUOUS))
   end

   return discontinuity
end

function loadFileFormat(option)
	if option=="load debug_plot.dof" then
		if util.isFileExist("debug_plot.dof") then
			if model==nil then
				package.projectPath='../Samples/QP_controller/'
				package.path=package.path..";../Samples/QP_controller/lua/?.lua"
				require("IPC_based/useCases")
				model=scenarios.toModel(useCase.scenario)
				_start(model.file_name)
				rotateBackground(useCase.slope or 0)
			end
			_applyMotion("debug_plot.dof")
		end
	elseif option=="load debug_plot.dof (debug)" then
		if util.isFileExist("debug_plot.dof") then
			if model==nil then
				model=scenarios.toModel(useCase.scenario)
				_start(model.file_name)
			end
			_applyMotion("debug_plot.dof")
			mSkin:setMaterial('lightgrey_transparent')
			mEventReceiver:loadTraceManager()
		end
	elseif option=='load from script' or option=='load from script2' then
		local path='../Resource/scripts/modifyModel/'
		if option=='load from script2' then
			path='../work'
		end
		local filename=Fltk.chooseFile('choose a wrl file',  path,'*.lua', false)
		if filename then
			local f=util.readFile(filename)
			f=[[
			function Start(wrlfile, doffile, height)
				_start(wrlfile)
				loadDOF(doffile)
				adjustHeight(height)
			end
			]]..f
			loadstring(f)()
		end
	elseif option=="load a dof/bvh file" then
		chosenFile=Fltk.chooseFile("Choose a file", ".", "*.{dof,bvh}", false)
		if chosenFile~="" then
			if string.sub(chosenFile,-4)=='.dof' then
				loadDOF(chosenFile)
			else
				loadBVH(chosenFile)
			end
		end
	elseif option=="add a dof file" then
		chosenFile=Fltk.chooseFile("Choose a file", ".", "*.dof", false)
		if chosenFile~="" then
			skin_old=mSkin
			drawSkeleton=this:findWidget("draw skeleton"):checkButtonValue()


			mSkin=RE.createVRMLskin(mLoader, drawSkeleton)
			mSkin:setThickness(0.03)
			mSkin:scale(100,100,100)
			_applyMotion(chosenFile, true)
		end
   elseif option=="load a model" then
	   chosenFile=Fltk.chooseFile("Choose a model", model_path, "*.{wrl,wrl.lua,wrl.dat}", false)
	   _start(chosenFile)
   elseif option=="apply a motion" then

	   chosenFile=Fltk.chooseFile("choose a motion", model_path, "*.{dof,mot,bvh}", false)
	   _applyMotion(chosenFile)
   elseif option=="generate a random motion" then
		   chosenMotFile='random'
		mMotionDOFcontainer=MotionDOFcontainer(mLoader.dofInfo)
		mMotionDOFcontainer:resize(100)

		local mot= mMotionDOFcontainer.mot
		for i=0, 99 do
			local pose=mot:row(i)
			local dofInfo=mot.dofInfo
			for j=1, dofInfo:skeleton():numBone()-1 do
				local bone=dofInfo:skeleton():bone(j)
				local vbone=bone:treeIndex()
				local nJoint=dofInfo:numDOF(vbone)
				if nJoint==4 then
					-- ball joint
					local dofIndex=dofInfo:DOFindex(vbone,0)
					pose:setQuater(dofIndex,quater(1,0,0,0))
				elseif nJoint==7 then
					-- free joint
					local dofIndex=dofInfo:DOFindex(vbone,3)
					pose:setQuater(dofIndex,quater(1,0,0,0))
				end
				for k=0, nJoint-1 do
					local dofIndex=dofInfo:DOFindex(vbone,k)
					if dofInfo:DOFtype(vbone,k)==MotionDOFinfo.SLIDE then
						pose:set(dofIndex, math.random()*0.1)
					elseif dofInfo:DOFtype(vbone,k)==MotionDOFinfo.ROTATE then
						if i==0 then
							pose:set(dofIndex,0)
						else
							pose:set(dofIndex, math.random()*math.rad(40))
						end
					end
				end
			end
		end
		mSkin:applyMotionDOF(mMotionDOFcontainer.mot)
		RE.motionPanel():motionWin():detachSkin(mSkin)
		RE.motionPanel():motionWin():addSkin(mSkin)
   elseif option=="apply a motion (with noise reduction)" or option=="apply a motion (with filtering)" then
	   local noiseReduction=option=="apply a motion (with noise reduction)"

	   if mLoader~=nill then
		   chosenFile=Fltk.chooseFile("choose a motion", model_path, "*.{dof,mot}", false)

		   mMotionDOFcontainer=MotionDOFcontainer(mLoader.dofInfo, chosenFile)

		   mMotionDOF=mMotionDOFcontainer.mot

		   local discont=mMotionDOFcontainer.discontinuity
		   local cols=mMotionDOF:matView():cols()
		   mVelocity=matrixn(mMotionDOF:numFrames(), cols)

		   local segFinder=SegmentFinder(discont)

		   for i=0, segFinder:numSegment()-1 do
			   local s=segFinder:startFrame(i)
			   local e=segFinder:endFrame(i)

			   print("noiseReduction", s,e)
			   if s~=e then
				   local dofInfo=mMotionDOF.dofInfo
				   for j=2, dofInfo:skeleton():numBone()-1 do
					   local bone=dofInfo:skeleton():bone(j)
					   local vbone=bone:treeIndex()
					   local nJoint=dofInfo:numDOF(vbone)
					   for k=0, nJoint-1 do
						   if dofInfo:DOFtype(vbone,k)~=MotionDOFinfo.SLIDE then
							   local dofIndex=dofInfo:DOFindex(vbone,k)
							   math.alignAngles(mMotionDOF:range(s,e):column(dofIndex),0)
						   end
					   end
				   end

				   if noiseReduction then
					   MotionUtil.noiseReduction(mMotionDOF:range(s,e), 32, mVelocity:range(s,e,0, cols))
				   else
					   math.filter(mMotionDOF:range(s,e), 63)
				   end
				   MotionUtil.renormalize(mMotionDOF:range(s,e))
			   end
		   end
		   print("noiseReduction finished")

		   --	 mMotionDOF:get(mMotion)
		   mSkin:applyMotionDOF(mMotionDOF)
		   mMotionDOFcontainer:exportMot(str.left(chosenFile, -4).."_smooth.dof")
		   --	 RE.motionPanel():motionWin():detachAllSkin()
		   RE.motionPanel():motionWin():detachSkin(mSkin)
		   RE.motionPanel():motionWin():addSkin(mSkin)

	   end
	end
end
function exportFileFormat(option)
	if option=="export BVH" then
		local chosenFile=Fltk.chooseFile("Choose a BVH file to create", model_path, "*.bvh", true)
		if chosenFile ~='' then
			_exportBVH(chosenFile, false,0,	useNearestSamplingWhenExportingBVH)
		end
	elseif option=="export BVH (original size)" then
		local chosenFile=Fltk.chooseFile("Choose a BVH file to create", model_path, "*.bvh", true)
		if chosenFile ~='' then
			_exportBVH(chosenFile, false,0,	useNearestSamplingWhenExportingBVH, 1, quater(1,0,0,0))
		end
	elseif option=="export WRL" then
		local chosenFile=Fltk.chooseFile("Choose a WRL file to create", ".", "*.wrl", true)
		if mLoader~=nill and chosenFile~="" then
			mLoader:exportVRML(chosenFile)
		end
	elseif option=="export DOF" then
		local chosenFile=Fltk.chooseFile("Choose a DOF file to create", ".", "*.dof", true)
		if mLoader~=nill and chosenFile~="" then
			mMotionDOFcontainer:exportMot(chosenFile)
		end
	elseif option=="export identity pose" then
		local chosenFile=Fltk.chooseFile("Choose a BVH file to create", model_path, "*.bvh", true)
		_exportBVH(chosenFile, true)
	elseif option=="export identity pose (original size)" then
		local chosenFile=Fltk.chooseFile("Choose a BVH file to create", model_path, "*.bvh", true)
		_exportBVH(chosenFile, true,0,	useNearestSamplingWhenExportingBVH, 1, quater(1,0,0,0))
	elseif option=='export 2D pos' then
	  
		local names={'pelvis','upperback', 
		'_right_ball', '_right_heel','_right_knee', '_right_hip',  
		'_left_ball', '_left_heel','_left_knee', '_left_hip', 'COM' }
		local indexes={}
		for i=1, #names do
			local name=names[i]
			if string.sub(name,1,1)=='_' then
				name=model.bones[string.sub(name,2)]
			end
			if name=='COM' then
				indexes[i]=-1
			else
				indexes[i]=mLoader:getTreeIndexByName(name)
				assert(indexes[i]~=-1 )
			end
		end

		local s=0
		local e=mMotionDOFcontainer.mot:numFrames()-1
		mLoader:setPoseDOF(mMotionDOFcontainer.mot:row(s))
		local p1=mLoader:VRMLbone(indexes[1]):getFrame().translation
		mLoader:setPoseDOF(mMotionDOFcontainer.mot:row(e))
		local p2=mLoader:VRMLbone(indexes[1]):getFrame().translation

		local t=matrix4()
		t:identity()
		local q=quater()
		q:setAxisRotation(vector3(0,1,0), p2-p1, vector3(0,0,1))
		t:leftMultRotation(q)
		local p=p1:copy()
		p.y=0
		t:leftMultTranslation(p*-1)


		traj={}
		for i=1, #names do
			traj[i]=vector3N(e-s+1)
		end
		for j=s,e do
			mLoader:setPoseDOF(mMotionDOFcontainer.mot:row(j))
			for i=1, #names do
				if names[i]=='COM' then
					traj[i](j):assign(mLoader:calcCOM())
				else
					traj[i](j):assign(mLoader:VRMLbone(indexes[i]):getFrame().translation)
				end
				traj[i](j):assign(t*traj[i](j))
			end
		end
		for i=1, #names do
			mObjectList:registerObject(names[i], "LineList", "solidred", traj[i]:matView()*100,0)
		end

		local str=""
		for i=1, #names do
			local axis={'_x','_y','_z'}
			for j=1,3 do
				str=str..names[i]..axis[j]..'\t'
			end
		end
		str=str..'\n'

		for j=s,e do
			for i=1, #names do
				str=str..tostring(traj[i](j).x)..'\t'
				str=str..tostring(traj[i](j).y)..'\t'
				str=str..tostring(traj[i](j).z)..'\t'
			end
			str=str..'\n'
		end
		util.writeFile('2dpos.txt', str)

	elseif option=="export current surface mesh" then
		MotionUtil.exportCurrentSurfaceMesh(mLoader, model.file_name)
	end
end
function onCallback(w, userData)
	print(w:id())
	if w:id()=="export" then
		local txt=w:menuText()
		exportFileFormat(txt)
	elseif w:id()=="motion editing" then
		local txt=w:menuText()
		motionEditing(txt)

	elseif w:id()=="load file format" then
		local txt=w:menuText()
		loadFileFormat(txt)
	elseif w:id()=="plot signal" then
		local txt=w:menuText()
		plotSignal(txt)
  elseif w:id()=="rotate background" then
	  rotateBackground(useCase.slope)
  elseif w:id()=="rotate background +5" then
	  rotateBackground(math.rad(5))
  elseif w:id()=="rotate background -5" then
	  rotateBackground(math.rad(-5))
  elseif w:id()=='rotate light' then
	  local osm=RE.ogreSceneManager()
	  if osm:hasSceneNode("LightNode") then
		  local lightnode=osm:getSceneNode("LightNode")
		  lightnode:rotate(quater(math.rad(30), vector3(0,1,0)))
	  end
    
   elseif w:id()=="load a predefined model" then

      model=modelChooser.models[w:menuValue()]
      _start(model.file_name)
	  chosenFile=model.file_name
      _applyMotion(model.mot_file)

  elseif w:id()=="chop 300-800" then
      local startF=300
      local endF=800

	  mMotionDOFcontainer=mMotionDOFcontainer:sub(startF, endF)
      --local mot=mMotionDOFcontainer.mot:copy()
      --mMotionDOFcontainer:resize(endF-startF)
      --mMotionDOFcontainer.mot:assign(mot:range(startF, endF))
      mSkin:applyMotionDOF(mMotionDOFcontainer.mot)

      RE.motionPanel():motionWin():detachSkin(mSkin)
      RE.motionPanel():motionWin():addSkin(mSkin)

  elseif w:id()=="discard later motion" then
      mMotionDOFcontainer=mMotionDOFcontainer:sub(0,mEventReceiver.currFrame+1)      
      mSkin:applyMotionDOF(mMotionDOFcontainer.mot)
--      RE.motionPanel():motionWin():detachAllSkin()
      RE.motionPanel():motionWin():detachSkin(mSkin)
      RE.motionPanel():motionWin():addSkin(mSkin)

   elseif w:id()=="discard earlier motion" then
      local startF=mEventReceiver.currFrame
      local endF=mMotionDOFcontainer:numFrames()

      local mot=mMotionDOFcontainer.mot:copy()
      mMotionDOFcontainer:resize(endF-startF)
      mMotionDOFcontainer.mot:assign(mot:range(startF, endF))
      mSkin:applyMotionDOF(mMotionDOFcontainer.mot)

      RE.motionPanel():motionWin():detachSkin(mSkin)
      RE.motionPanel():motionWin():addSkin(mSkin)

   elseif w:id()=="attach camera" then
      mEventReceiver:attachCamera()
	  mEventReceiver.cameraInfo.attachToBody=false
   elseif w:id()=="attach camera2" then
      mEventReceiver:attachCamera()
	  mEventReceiver.cameraInfo.attachToBody=true
   elseif w:id()=='init useCaseMenu' then
	   package.projectPath='../Samples/QP_controller/'
	   package.path=package.path..";../Samples/QP_controller/lua/?.lua"
	   require("IPC_based/useCases")
	   modelChooser:createUseCaseMenu("load a use case")
	   this:updateLayout()
   elseif w:id()=='init useCase' then
	   package.projectPath='../Samples/QP_controller/'
	   package.path=package.path..";../Samples/QP_controller/lua/?.lua"
	   require("IPC_based/useCases")
	   model=scenarios.toModel(useCase.scenario)
	   _start(model.file_name)
	   if useCase.mot_file then
		   _applyMotion(useCase.mot_file)
	   else
		   _applyMotion(model.mot_file)
	   end
   elseif w:id()=="load a use case" then
	   package.projectPath='../Samples/QP_controller/'
	   package.path=package.path..";../Samples/?.lua"
	   require("IPC_based/useCases")
	   local useCase=modelChooser.useCases[w:menuValue()]
	   model=scenarios.toModel(useCase.scenario)
	   _start(model.file_name)
	   if useCase.mot_file then
		   _applyMotion(useCase.mot_file)
	   else
		   _applyMotion(model.mot_file)
	   end
   elseif w:id()=="draw debuginfo" then
	   debugVis=this:findWidget("draw debuginfo"):checkButtonValue()
	   if debugVis and mSkin then
			mSkin:setMaterial('lightgrey_transparent')
		end
   elseif w:id()=="test" then
	   _start(model_path.."gymnist.wrl")
	   _applyMotion("debug_plot_cartwheel.dof")
	   _exportBVH("debug_plot_cartwheel.bvh")

   elseif w:id()=="capture applied motion" then
	   chosenFile=chosenFile or 'dump.dof'
	   local fn=os.processFileName(chosenFile)
	   os.createDir('../dump/'..fn)
	   if true then -- capture jpeg sequence
		   RE.renderer():setScreenshotPrefix('../dump/'..fn)
		   RE.renderer():setScreenshotMotionBlur(8)
		   RE.renderer():screenshot(true)
		   local info=mMotionDOFcontainer.mot.dofInfo

		   --
		   function cameraZitter(i)
			   local antiAliasing=1/3000 
			   local vpos=RE.viewpoint().vpos:copy()
			   local vat=RE.viewpoint().vat:copy()
			   if antiAliasing ~=0 then
				   local vup=vector3(0,1,0)
				   local vdir=vat-vpos
				   vdir:normalize()
				   local vside=vector3()
				   vside:cross(vup, vdir)
				   vside:normalize()
				   vup:cross(vside, vdir)

				   local v1=vup*antiAliasing
				   local v2=vside*antiAliasing*4/3
				   if math.mod(i,8)==0 then
					   RE.viewpoint().vat:add(vpos+vdir,v1 )
				   elseif math.mod(i,8)==1 then
					   RE.viewpoint().vat:add(vpos+vdir,-v1)
				   elseif math.mod(i,8)==2 then
					   RE.viewpoint().vat:add(vpos+vdir,v2)
				   elseif math.mod(i,8)==3 then
					   RE.viewpoint().vat:add(vpos+vdir,-v2)
				   elseif math.mod(i,8)==4 then
					   RE.viewpoint().vat:add(vpos+vdir,v1+v2)
				   elseif math.mod(i,8)==5 then
					   RE.viewpoint().vat:add(vpos+vdir,v1-v2)
				   elseif math.mod(i,8)==6 then
					   RE.viewpoint().vat:add(vpos+vdir,-v1+v2)
				   elseif math.mod(i,8)==7 then
					   RE.viewpoint().vat:assign(vpos+vdir)
				   end
			   end
			   return vat
		   end
		   for i=0, mMotionDOFcontainer.mot:numFrames()-2 do
			   mSkin:setPoseDOF(mMotionDOFcontainer.mot:row(i))
			   if mEventReceiver.trajectory then
				   local curPos=mEventReceiver.trajectory:row(i):toVector3(0)*100
				   RE.viewpoint().vpos:assign(mEventReceiver.cameraInfo.vpos+curPos)
				   RE.viewpoint().vat:assign(mEventReceiver.cameraInfo.vat+curPos)
				   RE.viewpoint():update()     
			   end
			   local vat=cameraZitter(i*2)
			   RE.renderOneFrame(false)
			   RE.viewpoint().vat:assign(vat)

		       local v1=vectorn()
		       info:blend(v1, mMotionDOFcontainer.mot:row(i), mMotionDOFcontainer.mot:row(i+1),0.5)
			   mSkin:setPoseDOF(v1)
			   if mEventReceiver.trajectory then
				   local curPos=mEventReceiver.trajectory:row(i):toVector3(0)*100
				   local curPos2=mEventReceiver.trajectory:row(i+1):toVector3(0)*100
				   curPos=(curPos+curPos2)*0.5
				   RE.viewpoint().vpos:assign(mEventReceiver.cameraInfo.vpos+curPos)
				   RE.viewpoint().vat:assign(mEventReceiver.cameraInfo.vat+curPos)
				   RE.viewpoint():update()     
			   end
			   local vat=cameraZitter(i*2+1)
			   RE.renderOneFrame(false)
			   RE.viewpoint().vat:assign(vat)
		   end
		   RE.renderer():screenshot(false)
	   end
	   os.encodeToDivx('../dump/'..fn, fn..'.avi')
   elseif w:id()=="capture applied motion (no filter)" then
	   chosenFile=chosenFile or 'dump.dof'
	   local fn=os.processFileName(chosenFile)
	   os.createDir('../dump/'..fn)
	   if true then -- capture jpeg sequence
		   RE.renderer():setScreenshotPrefix('../dump/'..fn)
		   RE.renderer():screenshot(true)
		   local info=mMotionDOFcontainer.mot.dofInfo
		   for i=0, mMotionDOFcontainer.mot:numFrames()-1-4,4 do
			   mSkin:setPoseDOF(mMotionDOFcontainer.mot:row(i))
			   mOgreSkin:setPoseDOF(mMotionDOFcontainer.mot:row(i))
				if mEventReceiver.trajectory then
					local curPos=mEventReceiver.trajectory:row(i+2):toVector3(0)*100
					RE.viewpoint().vpos:assign(mEventReceiver.cameraInfo.vpos+curPos)
					RE.viewpoint().vat:assign(mEventReceiver.cameraInfo.vat+curPos)
					RE.viewpoint():update()     
				end
				RE.renderOneFrame(false)
		   end
		   RE.renderer():screenshot(false)
	   end
	   os.encodeToDivx('../dump/'..fn, fn..'.avi')
   elseif w:id()=="capture applied motion (0.25x)" then
	   chosenFile=chosenFile or 'dump.dof'
	   local fn=os.processFileName(chosenFile)
	   os.createDir('../dump/'..fn)
	   if true then -- capture jpeg sequence
		   RE.renderer():setScreenshotPrefix('../dump/'..fn)
		   RE.renderer():screenshot(true)
		   local info=mMotionDOFcontainer.mot.dofInfo
		   for i=0, mMotionDOFcontainer.mot:numFrames()-5, 1 do
			   mSkin:setPoseDOF(mMotionDOFcontainer.mot:row(i))
				if mEventReceiver.trajectory then
					local curPos=mEventReceiver.trajectory:row(i+2):toVector3(0)*100
					RE.viewpoint().vpos:assign(mEventReceiver.cameraInfo.vpos+curPos)
					RE.viewpoint().vat:assign(mEventReceiver.cameraInfo.vat+curPos)
					RE.viewpoint():update()     
				end
				RE.renderOneFrame(false)
		   end
		   RE.renderer():screenshot(false)
	   end
	   os.encodeToDivx('../dump/'..fn, fn..'.avi')
   elseif w:id()=="capture frames" then
	   local fn='../dump/capture.dat'
	   os.createDir('../dump/'..fn)
	   --local frames={10,20, 48, 129,157,  213, 221,241, 250, 263 , 290,   314, 339, 375,  392, 445, 467, 519, 548, 610, 624}
		local	frames={3745,3766,3786,3853,3877,3928,3948, 4000,4020, 4067,4088,4136, 4157, 4204, 4226, 4275, 4296,4345}--,4369},

	   if true then -- capture jpeg sequence
		   RE.renderer():setScreenshotPrefix('../dump/'..fn)
		   RE.renderer():screenshot(true)
		   local info=mMotionDOFcontainer.mot.dofInfo
		   for iiii, i in ipairs(frames) do
			   mSkin:setPoseDOF(mMotionDOFcontainer.mot:row(i))
				if mEventReceiver.trajectory then
					local curPos=mEventReceiver.trajectory:row(i+2):toVector3(0)*100
					RE.viewpoint().vpos:assign(mEventReceiver.cameraInfo.vpos+curPos)
					RE.viewpoint().vat:assign(mEventReceiver.cameraInfo.vat+curPos)
					RE.viewpoint():update()     
				end
				RE.renderOneFrame(false)
		   end
		   RE.renderer():screenshot(false)
	   end
   elseif w:id()=="filter" then

	   if mLoader~=nill then
		   local discont=mMotionDOFcontainer.discontinuity
		   mMotionDOF=mMotionDOFcontainer.mot
		   local cols=mMotionDOF:matView():cols()

		   local segFinder=SegmentFinder(discont)

		   for i=0, segFinder:numSegment()-1 do
			   local s=segFinder:startFrame(i)
			   local e=segFinder:endFrame(i)

			   print("noiseReduction", s,e)
			   if s~=e then
				   local dofInfo=mMotionDOF.dofInfo
				   for j=2, dofInfo:skeleton():numBone()-1 do
					   local bone=dofInfo:skeleton():bone(j)
					   local vbone=bone:treeIndex()
					   local nJoint=dofInfo:numDOF(vbone)
					   for k=0, nJoint-1 do
						   if dofInfo:DOFtype(vbone,k)~=MotionDOFinfo.SLIDE then
							   local dofIndex=dofInfo:DOFindex(vbone,k)
							   math.alignAngles(mMotionDOF:range(s,e):column(dofIndex),0)
						   end
					   end
				   end

				   print(s,e)
				   math.filter(mMotionDOF:range(s,e), 4)
				   MotionUtil.renormalize(mMotionDOF:range(s,e))
			   end
		   end
		   print("noiseReduction finished")

		   --	 mMotionDOF:get(mMotion)
		   mSkin:applyMotionDOF(mMotionDOF)
		   RE.motionPanel():motionWin():detachSkin(mSkin)
		   RE.motionPanel():motionWin():addSkin(mSkin)
	   end
   end
end
function _start(chosenFile)
	dtorSub()


	print(chosenFile.."\n")
	local ext
	if str.length(chosenFile)>0 then
		local fn, path=os.processFileName(chosenFile)
		ext=fn:sub(-4)
		model_file=str.left(fn, -4) -- excluding .WRL
		model_path=os.absoluteToRelativePath(path)..'/'
		if model_path=='/' then
			model_path='./'
		end
	else
		model_file=nil
		print('no such model')
	end

	if model_file==nil then return nil end

	if model_file:sub(-4)=='.wrl' then
		require("subRoutines/WRLloader")
		mLoader=MainLib.WRLloader(model_path..model_file..ext)
	else
		mLoader=MainLib.VRMLloader(model_path..model_file..".wrl")
	end
	if totalmass~=nil then
		mLoader:setTotalMass(totalmass)		-- recalculate mass/inertia based on shapes.
	end

	drawSkeleton=this:findWidget("draw skeleton"):checkButtonValue()
	mSkin=RE.createVRMLskin(mLoader, drawSkeleton)
	mSkin:setThickness(0.03)
	mSkin:scale(100,100,100)

end

function dtorSub()
	-- if RE.motionPanelValid() then
	--    RE.motionPanel():motionWin():detachAllSkin()
	-- end

	if RE.motionPanelValid() then
		if mSkin then
			RE.motionPanel():motionWin():detachSkin(mSkin)
			mSkin=nil
		end
	end

	-- remove objects that are owned by LUA
	collectgarbage()
end

function dtor()
	dbg.finalize()
	dtorSub()
end
function EVR:loadTraceManager(filecount)

	if filecount then
		self.loaded=filecount
		local binaryFile=util.BinaryFile()
		local fn=string.sub(chosenMotFile,1, -5).."_"..filecount..".cf"
		print(fn)
		if not os.isFileExist(fn) then return end
		self.traceManager=array:new()
		binaryFile:openRead(fn)
		local contactForce=matrixn()
		binaryFile:unpack(contactForce)
		local n=binaryFile:unpackInt()
		n=math.min(500,n) -- too large n tends to overflow memory
		for i=1, n do
			local message=TStrings()
			binaryFile:unpack(message)
			self.traceManager:pushBack(message)
		end
		binaryFile:close()
	else
		self.loaded=-1
	end
end

EVR.onFrameChanged_cameraOnly=EVR.onFrameChanged
function EVR:onFrameChanged(win, iframe)
	self.currFrame=iframe
	
	local export_freq
	if mrd_info then
		export_freq=mrd_info.export_freq
	else
		export_freq=50
	end
	local filecount=math.floor(iframe/export_freq)+1
	if filecount~=self.loaded then
		self:loadTraceManager(filecount)
	end
	if self.traceManager and debugVis then
		local message=self.traceManager[math.mod(iframe, export_freq)+1]
		if message then
			dbg.eraseAllDrawn()
			RE.outputEraseAll(2)
			for i=0, message:size()-1,2 do
				if string.sub(message(i),1,10)== 'namedDraw_' then
					local tbl=table.fromstring2(message(i+1))
					if tbl then 
						dbg._namedDraw(unpack(tbl))
					end
				else
					RE.output2(message(i), message(i+1))
				end
			end
		end
	end
	local signals=mMotionDOFcontainer.signals
	if signals  and signals.pose1 and debugVis then
		if mSkin2==nil then
			mSkin2=RE.createVRMLskin(mLoader, drawSkeleton)
			mSkin2:setThickness(0.03)
			mSkin2:scale(100,100,100)
			mSkin2:setTranslation(100,0,0)
			if signals.pose2 then
				mSkin3=RE.createVRMLskin(mLoader, drawSkeleton)
				mSkin3:setThickness(0.03)
				mSkin3:scale(100,100,100)
				mSkin3:setTranslation(-100,0,0)
			end
		end
		mSkin2:setPoseDOF(signals.pose1:row(iframe))
		if signals.pose2 then
			mSkin3:setPoseDOF(signals.pose2:row(iframe))
		end
	end
	if mEventReceiver.trajectory then
		local curPos=mEventReceiver.trajectory:row(iframe):toVector3(0)*100
		RE.viewpoint().vpos:assign(mEventReceiver.cameraInfo.vpos+curPos)
		RE.viewpoint().vat:assign(mEventReceiver.cameraInfo.vat+curPos)
		RE.viewpoint():update()     
	end
	if debugVis then
		for k,v in pairs(signals) do
			if string.sub(k,1,6)=='coord_' then
				local tf=transf()
				tf.translation:assign(v:row(iframe):toVector3(0)*0.01)
				local q=v:row(iframe):toQuater(3)
				tf.rotation:assign(q)
				if tf.rotation:length()>0.9 then
					dbg.namedDraw('Coordinate', tf, k)
				else
					-- bug
				end
			end
		end
	end
end


function frameMove(fElapsedTime)
end
function _applyMotion(chosenFile, nodetach)

	if mLoader~=nil then

		_G.chosenMotFile=chosenFile
		mMotionDOFcontainer=MotionDOFcontainer(mLoader.dofInfo,chosenFile)
		mSkin:applyMotionDOF(mMotionDOFcontainer.mot)
		-- if not nodetach then
		-- 	 RE.motionPanel():motionWin():detachAllSkin()
		-- end
		RE.motionPanel():motionWin():detachSkin(mSkin)
		RE.motionPanel():motionWin():addSkin(mSkin)
		local nf=mMotionDOFcontainer.mot:numFrames()
		mDrawPoses={ mStart=0, mEnd=nf, mDelta=math.round(nf/10)}
	end
end
function rotateMotion(angle)
	local mot=mMotionDOFcontainer.mot
	local tf=transf()
	tf:identity()
	tf:leftMultRotation(quater(angle, vector3(0,1,0)))

	for i=0, mot:numFrames()-1 do
		MotionDOF.setRootTransformation(mot:row(i), tf*MotionDOF.rootTransformation(mot:row(i)))
	end
	mSkin:applyMotionDOF(mMotionDOFcontainer.mot)
end
function drawPoses(zoffset)
	zoffset=zoffset or 0
	local mStart=mDrawPoses.mStart
	local mEnd=mDrawPoses.mEnd
	local mDelta=mDrawPoses.mDelta
	if mStart then
		if m_aSkins then
			for i=1,#m_aSkins do
				m_aSkins[i]=nil
			end
			collectgarbage()
			collectgarbage()
			collectgarbage()
		end
		m_aSkins={}
		local c=1

		-- taeki : 
		for i=mStart, mEnd-1, mDelta do
			print(i)
			m_aSkins[c]=RE.createVRMLskin(mLoader, false)
			m_aSkins[c]:scale(100,100,100)
			local pose=mMotionDOFcontainer.mot:row(i):copy()
			pose:set(2, pose(2)+zoffset*c)
			m_aSkins[c]:setPoseDOF(pose)
			c=c+1
		end
	end
end
function plotSignal(option)
	if option=="compare horizontal COM speed" then
		require('pyMrdplot')
		mPython=true
		plotSignal("plot horizontal COM speed")
		mPython=nil

		pyMrdplot_comp3({'debug_plot.mrd', 'debug_plot_comp.mrd'},0, {"syn", "mocap"})

		os.sleep(0.5)
		os.rename('debug_plot2.png', 'debug_plot2_compCOM.png')

	elseif option=='draw poses' then
	
		drawPoses()

	elseif option=="hand-tune comparision plot" then
		require('pyMrdplot')
		pyMrdplot_comp2({'debug_plot.mrd', 'debug_plot_comp.mrd'}, 
		{500+55, 0}, -- startFrame
		{"simulated", "captured"}, --file titles
		{{key='pitch', name="pitch [rad]"},
		{key='roll', name="roll [rad]"},
		{key='comspeedz', name="forward speed [m/s]"},
		{key='comspeedx', name="side speed [m/s]"},
		{key='com_y', name="COM height [m]"},
		{key='foot_y', name="left foot height [m]"},
		{key='knee', name="left knee [rad]"},
		})
	elseif option=="draw COM traj" then
		do -- test
			local comtraj=calcCOMtrajectory(mLoader, mMotionDOFcontainer.mot, mMotionDOFcontainer.discontinuity)
			mObjectList:registerObject("comtraj", "LineList", "solidred", comtraj:matView()*100,0)
		end
	elseif option=="plot contact force" or option=="plot contact force (python)" then
		local contactForce=matrixn()
		local binaryFile=util.BinaryFile()
		local fn=string.sub(chosenMotFile,1, -5)..".cf"
		if not os.isFileExist(fn) then
			binaryFile:openRead(fn)
			binaryFile:unpack(contactForce)
			binaryFile:close()

			math.changeChartPrecision(50)
			math.drawSignals( "LcontactForceY.bmp", contactForce:column(1):column())
			math.drawSignals( "RcontactForceY.bmp", contactForce:column(4):column())
			RE.motionPanel():scrollPanel():addPanel("LcontactForceY.bmp")
			RE.motionPanel():scrollPanel():addPanel("RcontactForceY.bmp")

			local mrdplot=MRDplot()
			mrdplot:initMRD(6, contactForce:rows(), 1)
			mrdplot.units:set(0, "N")
			mrdplot.units:set(1, "N")
			mrdplot.units:set(2, "N")
			mrdplot.units:set(3, "N")
			mrdplot.units:set(4, "N")
			mrdplot.units:set(5, "N")
			mrdplot.names:set(0, "LeftFoot.x")
			mrdplot.names:set(1, "LeftFoot.y")
			mrdplot.names:set(2, "LeftFoot.z")
			mrdplot.names:set(3, "RightFoot.x")
			mrdplot.names:set(4, "RightFoot.y")
			mrdplot.names:set(5, "RightFoot.z")
			mrdplot.data:assign(contactForce)
			mrdplot:save("debug_plot_cf.mrd")
			if option=="plot contact force (python)" then
				math.mrdplotFile("debug_plot_cf.mrd")
			end
		else
			print("file not exist")
		end

	elseif option=="plot pose" then

		require('pyMrdplot')
		math.changeChartPrecision(20)
		local mrdplot
		mrdplot=Physics.MRDplotwrap()
		local function addPanel(a, source, tag)
			if source then
				assert(string.upper(string.sub(a,-4))=='.BMP')
				math.drawSignals(a, source)
				local label=string.sub(a, 1, -5)
				if mrdplot then mrdplot:add(label, source,tag) end
				if RE.motionPanel().scrollPanel then
					RE.motionPanel():scrollPanel():addPanel(a)
					RE.motionPanel():scrollPanel():setLabel(label..string.format(" Min:%f Max:%f", source:minimum(), source:maximum()))
				end
			end
		end

		local motionDOF=mMotionDOFcontainer.mot
		local dofInfo=motionDOF.dofInfo
		local skel=mLoader

		for i=2,mLoader:numBone()-1 do
			local bone=mLoader:VRMLbone(i)
			local boneName=bone:name()
			for j=0,bone:numHRPjoints()-1 do
				local dofIndex=bone:DOFindex(j)

				addPanel(boneName.."_"..bone:HRPjointAxis(j)..'.bmp', 
				motionDOF:matView():sub(0,0,dofIndex,dofIndex+1),boneName)
			end
		end
		mrdplot:init()
		mrdplot:save("debug_plot.mrd")
		pyMrdplot3('debug_plot.mrd')
	elseif option=="set comparision target" then
		require('pyMrdplot')
		mPython=true
		plotSignal("plot horizontal COM speed")
		mPython=nil
		os.rename('debug_plot.mrd', 'debug_plot_comp.mrd')
		os.rename('debug_plot_pose.mrd', 'debug_plot_pose_comp.mrd')
	elseif option=="compare pose" then
		require('pyMrdplot')
		mPython=true
		plotSignal("plot horizontal COM speed")
		mPython=nil
		pyMrdplot_comp2(
		{'debug_plot_pose.mrd', 'debug_plot_pose_comp.mrd'},
		{300, 0}, -- startFrame
		{"simulated", "captured"})
		os.sleep(0.5)
		os.rename('debug_plot2.png', 'debug_plot2_compPose.png')
	elseif option=="plot horizontal COM speed (python)" then
		plot()

	elseif option=="plot horizontal COM speed" then 
		if false then
			local comtraj=calcCOMtrajectory(mLoader, mMotionDOFcontainer.mot, mMotionDOFcontainer.discontinuity)
			mObjectList:registerObject("comtraj", "LineList", "solidred", comtraj:matView()*100,0)
		end

		local discont=mMotionDOFcontainer.discontinuity      

		local segFinder=SegmentFinder(discont)

		local speedAll=vectorn (mMotionDOFcontainer:numFrames())
		local speedZ=vectorn (mMotionDOFcontainer:numFrames())
		local speedX=vectorn (mMotionDOFcontainer:numFrames())      
		local speedY=vectorn (mMotionDOFcontainer:numFrames())
		local roll=vectorn (mMotionDOFcontainer:numFrames())
		local pitch=vectorn (mMotionDOFcontainer:numFrames())
		local yaw=vectorn (mMotionDOFcontainer:numFrames())
		local com=matrixn(mMotionDOFcontainer:numFrames(),3)
		local con=vectorn(mMotionDOFcontainer:numFrames())
		local knee=vectorn(mMotionDOFcontainer:numFrames())
		local hip=vectorn(mMotionDOFcontainer:numFrames())
		local footL=vector3N(mMotionDOFcontainer:numFrames())
		local footR=vector3N(mMotionDOFcontainer:numFrames())
		local head=vector3N(mMotionDOFcontainer:numFrames())
		local headvel=vector3N(mMotionDOFcontainer:numFrames())
		local footLori=vectorn(mMotionDOFcontainer:numFrames())
		local footRori=vectorn(mMotionDOFcontainer:numFrames())
		local deltaangle=vectorn(mMotionDOFcontainer:numFrames())
		local rotspeed=vectorn(mMotionDOFcontainer:numFrames())
		local pose=matrixn(mMotionDOFcontainer:numFrames(), 3+3+1+1) -- Lhip, Rhip, Lknee, Rknee
		package.path=package.path..";../Samples/classification/lua/?.lua" --;"..package.path
		require('subRoutines/ZMPcalculator')
		local kneeIndex, hipIndex
		do 
			if mLoader:getTreeIndexByName(model.bones.left_knee.."_cart")~=-1 then
				kneeIndex=mLoader:VRMLbone(mLoader:getTreeIndexByName(model.bones.left_knee.."_cart")):DOFindex(0)
				hipIndex=mLoader:VRMLbone(mLoader:getTreeIndexByName(model.bones.left_hip.."_cart")):DOFindex(0)
			elseif mLoader:getTreeIndexByName(model.bones.left_knee)~=-1 then
				kneeIndex=mLoader:VRMLbone(mLoader:getTreeIndexByName(model.bones.left_knee)):DOFindex(0)
				hipIndex=mLoader:VRMLbone(mLoader:getTreeIndexByName(model.bones.left_hip)):DOFindex(0)
			end
		end
		for iseg=0, segFinder:numSegment()-1 do
			local s=segFinder:startFrame(iseg)
			local e=segFinder:endFrame(iseg)

			print(s,e)
			local motionDOF=mMotionDOFcontainer.mot:range(s,e)

			local dmotionDOF=calcDerivative(motionDOF)

			local zc=ZMPcalculator:new(mLoader, motionDOF, dmotionDOF)
			local comvel=zc.comvel

			mObjectList:registerObject("comtraj"..tostring(i), "LineList", "solidgreen", zc.com:matView()*100, 0)

			local comvelyBackup=comvel:y():copy()
			comvel:y():setAllValue(0)

			local speed=vectorn(comvel:size())

			for i=0, speed:size()-1 do speed:set(i, math.min(comvel(i):length(),6)) end

			comvel:y():assign(comvelyBackup)
			speedAll:range(s,e):assign(speed)

			local footIndex
			if model.bones.left_ball then
				footIndex=mLoader:getTreeIndexByName(model.bones.left_ball)
			else
				footIndex=mLoader:getTreeIndexByName(model.bones.left_heel)
			end
			local footRIndex
			if model.bones.right_ball then
				footRIndex=mLoader:getTreeIndexByName(model.bones.right_ball)
			else
				footRIndex=mLoader:getTreeIndexByName(model.bones.right_heel)
			end
			local headIndex
			headIndex=mLoader:getTreeIndexByName(model.bones.head)

			local kneeLindex=mLoader:VRMLbone(mLoader:getTreeIndexByName(model.bones.left_knee)):DOFindex(0)
			local kneeRindex=mLoader:VRMLbone(mLoader:getTreeIndexByName(model.bones.right_knee)):DOFindex(0)
			local hipLindex=mLoader:VRMLbone(mLoader:getTreeIndexByName(model.bones.left_hip)):DOFindex(0)
			local hipRindex=mLoader:VRMLbone(mLoader:getTreeIndexByName(model.bones.right_hip)):DOFindex(0)

			for i=s,e-1 do

				local rootTF=MotionDOF.rootTransformation(mMotionDOFcontainer.mot:row(i))
				local rotY=rootTF.rotation:rotationY()
				local upward=vector3(0,1,0)
				upward:rotate(rootTF.rotation)
				local localRot=rotY:inverse()*rootTF.rotation
				local pp=localRot:rotationAngleAboutAxis(vector3(0,0,1))
				local rr=localRot:rotationAngleAboutAxis(vector3(1,0,0))	    
				roll:set(i, pp)
				pitch:set(i, rr)
				yaw:set(i,rotY:rotationVector().y)

				local vcomvel=comvel:row(i-s):copy()

				do
					-- delta angle
					local qy=quater()
					local tangent=vcomvel:copy()
					tangent.y=0
					local horizSpeed=tangent:length()
					qy:setAxisRotation(vector3(0,1,0), rotate(vector3(0,0,1), rotY), tangent) 
					deltaangle:set(i, qy:rotationAngleAboutAxis(vector3(0,1,0)))
				end

				if i~=e-1 then
					-- rotation speed
					local rootTF2=MotionDOF.rootTransformation(mMotionDOFcontainer.mot:row(i+1))
					local rotY2=rootTF2.rotation:rotationY()
					local d=quater()
					d:difference(rotY, rotY2)
					rotspeed:set(i, d:rotationAngleAboutAxis(vector3(0,1,0))*mLoader.dofInfo:frameRate())
				else
					rotspeed:set(i,0)
				end

				if i>200 and i<400 and math.mod(i,8)==0 then
					local pPos=zc.com(i-s)
					dbg.draw('Line', pPos*100, pPos*100+vcomvel*100, 'gvel'..i, 'solidgreen')
					dbg.draw('Line', pPos*100, pPos*100+rotate(vector3(0,0,1),rotY)*100, 'gvel2', 'solidred')
				end
				vcomvel:rotate(rotY:inverse())
				speedX:set(i, vcomvel.x)
				speedY:set(i, vcomvel.y)
				speedZ:set(i, vcomvel.z)

				if kneeIndex then
					knee:set(i, mMotionDOFcontainer.mot:row(i)(kneeIndex))
					hip:set(i, mMotionDOFcontainer.mot:row(i)(hipIndex))
				else
					knee:set(i,0) hip:set(i,0)
				end

				if zc.com:size()>i then
					com:row(i):setVec3(0, zc.com(i))
				else
					com:row(i):setVec3(0, zc.com(zc.com:size()-1))
				end
				if mMotionDOFcontainer.conL(i) and 
					mMotionDOFcontainer.conR(i) then
					con:set(i, 0.5)
				elseif mMotionDOFcontainer.conL(i) then 
					con:set(i, 0)
				elseif mMotionDOFcontainer.conR(i) then
					con:set(i, 1)
				else
					con:set(i, 0.6)
				end

				mLoader:setPoseDOF(mMotionDOFcontainer.mot:row(i))
				local projCom=zc.com(i-s):copy() projCom.y=0
				projCom.x=0 projCom.z=0 local rotY=rotY:copy() rotY:identity()
				footL(i):assign(rotate(mLoader:VRMLbone(footIndex):getTranslation()-projCom, rotY:inverse()))
				footR(i):assign(rotate(mLoader:VRMLbone(footRIndex):getTranslation()-projCom, rotY:inverse()))
				footLori:set(i,mLoader:VRMLbone(footIndex):getFrame().rotation:rotationY():rotationVector().y)
				footRori:set(i,mLoader:VRMLbone(footRIndex):getFrame().rotation:rotationY():rotationVector().y)
				head(i):assign(mLoader:VRMLbone(headIndex):getFrame().translation)

				local pp=mMotionDOFcontainer.mot:row(i)
				pose:row(i):assign(pp:range(hipLindex, hipLindex+3)..pp:range(hipRindex, hipRindex+3)..CT.vec(pp(kneeLindex), pp(kneeRindex)))
			end
			local function calcVel(pos)
				local vel=matrixn()
				vel:setSize(pos:size(),3)
				for i=1, pos:size()-2 do
					vel:row(i):setVec3(0, (pos(i+1)-pos(i-1))*(120/2))
				end
				vel:row(0):assign(vel:row(1))
				vel:row(vel:rows()-1):assign(vel:row(vel:rows()-2))
				return vel
			end
			local function calcAcc(pos)
				local acc=matrixn()
				acc:setSize(pos:size(),3)
				for i=1, pos:size()-2 do
					-- vi=pi-pi-1*120
					-- vi+1=pi+1-pi*120
					-- acc=vi+1-vi * 120
					acc:row(i):setVec3(0, (pos(i+1)+pos(i-1)-2*pos(i))*(120*120))
				end
				acc:row(0):assign(acc:row(1))
				acc:row(acc:rows()-1):assign(acc:row(acc:rows()-2))
				return acc
			end
			local matHeadVel=calcVel(head:range(s,e))
			local headAcc=calcAcc(head:range(s,e))
			for i=s,e-1 do
				local rootTF=MotionDOF.rootTransformation(mMotionDOFcontainer.mot:row(i))
				local rotY=rootTF.rotation:rotationY()
				headvel(i):assign(rotate(matHeadVel:row(i-s):toVector3(0), rotY:inverse()))
				head(i):assign(rotate(headAcc:row(i-s):toVector3(0), rotY:inverse()))
			end
		end


		--mObjectList:registerObject("footL", "LineList", "solidred", footL:matView()*100,0)

		local function derivative(mat)
			local out=matrixn(mat:rows(), mat:cols())

			for i=0, mat:rows()-2 do
				out:row(i):assign(mat:row(i+1)-mat:row(i))
			end
			out:row(out:rows()-1):assign(out:row(out:rows()-2))
			return out
		end
		math.changeChartPrecision(50)
		local mrdplot
		if mPython then
			mrdplot=Physics.MRDplotwrap()
		end
		local function addPanel(a, source, tag)
			if source then
				assert(string.upper(string.sub(a,-4))=='.BMP')
				math.drawSignals(a, source)
				local label=string.sub(a, 1, -5)
				if mrdplot then mrdplot:add(label, source,tag) end
				if RE.motionPanel().scrollPanel then
					RE.motionPanel():scrollPanel():addPanel(a)
					RE.motionPanel():scrollPanel():setLabel(label..string.format(" Min:%f Max:%f", source:minimum(), source:maximum()))
				end
			end
		end

		addPanel("com.bmp", com)

		addPanel( "simulatedFootstate.bmp", con:column(), 'con')
		if mMotionDOFcontainer.signals then
			addPanel('desiredFootState.bmp', mMotionDOFcontainer.signals.state,'con') -- 
		end

		if mMotionDOFcontainer.signals and mMotionDOFcontainer.signals.cf then
			local cf=mMotionDOFcontainer.signals.cf 

			local function clamp(mat, thr)
				local out=mat:copy()
				for i=0,out:rows()-1 do
					for j=0,out:cols()-1 do
						out:set(i,j, math.clamp(out(i,j), thr*-1, thr))
					end
				end
				return out
			end
			addPanel('GRF_Lx.bmp', cf:sub(0,0,0,1), 'GRF_x')
			addPanel('GRF_Rx.bmp', cf:sub(0,0,3,4), 'GRF_x')
			addPanel('GRF_Ox.bmp', cf:sub(0,0,6,7), 'GRF_x')
			addPanel('GRF_x.bmp', cf:sub(0,0,0,1)+cf:sub(0,0,3,4),'GRF__all')
			addPanel('GRF_Ly.bmp', cf:sub(0,0,1,2), 'GRF_y')
			addPanel('GRF_Ry.bmp', cf:sub(0,0,4,5), 'GRF_y')
			addPanel('GRF_Oy.bmp', cf:sub(0,0,7,8), 'GRF_y')
			addPanel('GRF_y.bmp', cf:sub(0,0,1,2)+cf:sub(0,0,4,5),'GRF__all')
			addPanel('GRF_Lz.bmp', cf:sub(0,0,2,3), 'GRF_z')
			addPanel('GRF_Rz.bmp', cf:sub(0,0,5,6), 'GRF_z')
			addPanel('GRF_Oz.bmp', cf:sub(0,0,8,9), 'GRF_z')
			addPanel('GRF_z.bmp', cf:sub(0,0,2,3)+cf:sub(0,0,5,6),'GRF__all')
			addPanel('GRF_Lcy.bmp', clamp(cf:sub(0,0,1,2),30), 'clamped GRF_y')
			addPanel('GRF_Rcy.bmp', clamp(cf:sub(0,0,4,5),30), 'clamped GRF_y')
		end
		addPanel( "comspeed.bmp", speedAll:column(), "comspeed")
		addPanel( "comspeedx.bmp", speedX:column(), "comspeed")
		addPanel( "comspeedy.bmp", speedY:column(), "comspeed")
		addPanel( "comspeedz.bmp", speedZ:column(), "comspeed")
		addPanel( "roll.bmp", roll:column())
		addPanel( "pitch.bmp", pitch:column())

		if mMotionDOFcontainer.signals and mMotionDOFcontainer.signals.desiredAcc then
			local size=mMotionDOFcontainer.signals.desiredAcc:cols()/3
			addPanel('desiredAcc.bmp', mMotionDOFcontainer.signals.desiredAcc:sub(0,0,0,size),'desiredacc')
			addPanel('theta.bmp', mMotionDOFcontainer.signals.desiredAcc:sub(0,0,size,size*2),'theta' )
			addPanel('theta_d.bmp', mMotionDOFcontainer.signals.desiredAcc:sub(0,0,size*2,size*3),'theta')
		end

		if mMotionDOFcontainer.signals and mMotionDOFcontainer.signals.coord_zmp_coord_L then
			local zL=mMotionDOFcontainer.signals.coord_zmp_coord_L
			local zR=mMotionDOFcontainer.signals.coord_zmp_coord_R
			addPanel('pendBase_Lx.bmp', zL:sub(0,0,0,1), 'pendBase_x')
			addPanel('pendBase_Rx.bmp', zR:sub(0,0,0,1), 'pendBase_x')
			addPanel('pendBase_Lz.bmp', zL:sub(0,0,2,3), 'pendBase_z')
			addPanel('pendBase_Rz.bmp', zR:sub(0,0,2,3), 'pendBase_z')
		end

		if kneeIndex then
			addPanel( "knee.bmp", knee:column())
			addPanel( "hip.bmp", hip:column())
		end
		--addPanel( "foot.bmp", derivative(footL:matView()))
		addPanel( "foot.bmp", footL:matView():copy())
		addPanel( "deltaangle.bmp", deltaangle:column())
		addPanel( "rotspeed.bmp", rotspeed:column())
		addPanel( "headvel.bmp", headvel:matView())
		addPanel( "headacc.bmp", head:matView())
		math.changeChartPrecision(250)
		addPanel( "footLori.bmp", footLori:column())
		addPanel( "footRori.bmp", footRori:column())
		--addPanel( "hip.bmp", pose:range(0, pose:rows(), 0,3))
		if mrdplot then
			mrdplot:init()
			--[[
			mrdplot:initMRD(17, speedAll:size(), 1)
			mrdplot.names:set(0, "sqrt(||comvel||)")
			mrdplot.names:set(1, "comvel.x")
			mrdplot.names:set(2, "comvel.z")
			mrdplot.names:set(3, "roll")
			mrdplot.names:set(4, "pitch")
			mrdplot.names:set(5, "yaw")
			mrdplot.names:set(6, "comy")
			mrdplot.names:set(7, "lknee")
			mrdplot.names:set(8, "footL.x")
			mrdplot.names:set(9, "footL.y")
			mrdplot.names:set(10, "footL.z")
			mrdplot.names:set(11, "footR.x")
			mrdplot.names:set(12, "footR.y")
			mrdplot.names:set(13, "footR.z")
			mrdplot.names:set(14, "headacc.x")
			mrdplot.names:set(15, "headacc.y")
			mrdplot.names:set(16, "headacc.z")
			mrdplot.data:column(0):assign(speedAll)
			mrdplot.data:column(1):assign(speedX)
			mrdplot.data:column(2):assign(speedZ)
			mrdplot.data:column(3):assign(roll)
			mrdplot.data:column(4):assign(pitch)
			mrdplot.data:column(5):assign(yaw)
			mrdplot.data:column(6):assign(com_y)
			--	   mrdplot.data:column(6):assign(knee)
			mrdplot.data:column(7):assign(pose:column(6))
			mrdplot.data:column(8):assign(footL:x())
			mrdplot.data:column(9):assign(footL:y())
			mrdplot.data:column(10):assign(footL:z())

			mrdplot.data:column(11):assign(footR:x())
			mrdplot.data:column(12):assign(footR:y())
			mrdplot.data:column(13):assign(footR:z())
			mrdplot.data:column(14):assign(head:x())
			mrdplot.data:column(15):assign(head:y())
			mrdplot.data:column(16):assign(head:z())

			]]--
			mrdplot:save("debug_plot.mrd")
		end
		if true then 
			local mrdplot_pose=Physics.MRDplot()
			mrdplot_pose:initMRD(8, speedAll:size(), 1)
			mrdplot_pose.units:set(0, "rad")
			mrdplot_pose.units:set(1, "rad")
			mrdplot_pose.units:set(2, "rad")
			mrdplot_pose.units:set(3, "rad")
			mrdplot_pose.units:set(4, "rad")
			mrdplot_pose.units:set(5, "rad")
			mrdplot_pose.units:set(6, "rad")
			mrdplot_pose.units:set(7, "rad")
			mrdplot_pose.names:set(0, "lhip.z")
			mrdplot_pose.names:set(1, "lhip.x")
			mrdplot_pose.names:set(2, "lhip.y")
			mrdplot_pose.names:set(3, "rhip.z")
			mrdplot_pose.names:set(4, "rhip.x")
			mrdplot_pose.names:set(5, "rhip.y")
			mrdplot_pose.names:set(6, "lknee")
			mrdplot_pose.names:set(7, "rknee")
			assert(pose:rows()==speedAll:size() and pose:cols()==8)
			mrdplot_pose.data:assign(pose)
			mrdplot_pose:save("debug_plot_pose.mrd")
		end

		if not mPython and mOctave then
			octave.__octaveInit()
			math.mrdplotFile("debug_plot.mrd")
		end
	end
end
function motionEditing(option)
	local function transMot(height)
		local mot=mMotionDOFcontainer.mot
		for i=0, mot:numFrames()-1 do
			mot:row(i):set(1, mot:row(i):get(1)+height)
		end
		mSkin:applyMotionDOF(mMotionDOFcontainer.mot)
	end
	if option=="+initialheight" or option=="+1" then

		local tiltedGround
		local initialHeight=0.07
		local mot=mMotionDOFcontainer.mot

		if model then
			tiltedGround=model.tiltedGround
			initialHeight=model.initialHeight
		end
		if option=="+1" then
			tiltedGround=nil
			initialHeight=0.01
		end
		if tiltedGround then
			for i=0, mot:numFrames()-1 do
				local tf=MotionDOF.rootTransformation(mot:row(i))
				MotionDOF.setRootTransformation(mot:row(i), tiltedGround*tf)
			end
		end
		adjustHeight(initialHeight)
	elseif option=='1cm up' then
		transMot(0.01)
	elseif option=='1cm down' then
		transMot(-0.01)
	elseif option=='50cm up' then
		transMot(0.5)
	elseif option=='50cm down' then
		transMot(-0.5)
	elseif option=="center motion" then
		local mot=mMotionDOFcontainer.mot
		local tf=transf()
		local slope=0
		if useCase and useCase.slope then
			slope=useCase.slope
		end
		tf:identity()
		local prevCenter=vector3(mot:row(0)(0), 0, mot:row(0)(2))
		prevCenter.y=-math.tan(slope)*prevCenter.z
		tf:leftMultTranslation(-prevCenter)
		if slope==0 then
			tf:leftMultRotation(MotionDOF.rootTransformation(mot:row(0)).rotation:rotationY():inverse())
		end

		for i=0, mot:numFrames()-1 do
			MotionDOF.setRootTransformation(mot:row(i), tf*MotionDOF.rootTransformation(mot:row(i)))
		end
		mSkin:applyMotionDOF(mMotionDOFcontainer.mot)

		if false then
			-- insert COM joint
			local skel=mLoader
			local mot=mMotionDOFcontainer.mot
			local pos=CT.zeros(mot:numFrames(),3)
			local ori=CT.zeros(mot:numFrames(),4)
			ori:range(0,mot:numFrames(), 0,1):setAllValue(1)
			local nmot=MotionUtil.insertRootJoint(skel, pos,ori,'COM', mMotionDOFcontainer.mot)

			mMotionDOFcontainer.mot=nmot
			mMotionDOF=mMotionDOFcontainer.mot
			RE.motionPanel():motionWin():detachSkin(mSkin)
			mSkin=nil
			collectgarbage()
			mSkin=RE.createVRMLskin(mLoader, drawSkeleton)
			mSkin:setThickness(0.03)
			mSkin:scale(100,100,100)
			mSkin:applyMotionDOF(mMotionDOFcontainer.mot)
			RE.motionPanel():motionWin():addSkin(mSkin)
			mLoader:export('temp.wrl')
		end
	elseif option=="rotate motion" then
		rotateMotion(math.rad(90))
	elseif option=='measure height' then
		local minY=10000
		local slope=0
		if useCase and useCase.slope then
			slope=useCase.slope
		end
		for i=0,mMotionDOFcontainer.mot:rows()-1 do
			mLoader:setPoseDOF(mMotionDOFcontainer.mot:row(i))
			local lfootIndex=mLoader:getTreeIndexByName(model.bones.left_ball)
			local rfootIndex=mLoader:getTreeIndexByName(model.bones.right_ball)
			local lfootPos=mLoader:VRMLbone(lfootIndex):getTranslation()
			lfootPos.y=lfootPos.y+math.tan(slope)*lfootPos.z
			local rfootPos=mLoader:VRMLbone(rfootIndex):getTranslation()
			rfootPos.y=rfootPos.y+math.tan(slope)*rfootPos.z
			minY=math.min(lfootPos.y, rfootPos.y, minY)
		end
		print("MIN Y", minY)
		return minY
	elseif option=='auto Y translation' then
		local minY=motionEditing('measure height')
		local minY_goal=-0.2838258
	elseif option=='4x downsample' then
		local mot=mMotionDOFcontainer.mot
		local origN=mot:numFrames()
		local newN=math.floor(origN/4)
		local conL=mMotionDOFcontainer.conL
		local conR=mMotionDOFcontainer.conR
		local dist=mMotionDOFcontainer.discontinuity
		for i=0, newN-1 do
			mot:row(i):assign(mot:row(i*4):copy())
			conL:set(i, conL(i*4))
			conR:set(i, conR(i*4))
			dist:set(i, dist(i*4))
		end
		mMotionDOFcontainer:resize(newN)
		mSkin:applyMotionDOF(mMotionDOFcontainer.mot)
	elseif option=='append identity pose' then
		mLoader:updateInitialBone()

		mMotionDOFcontainer:resize(mMotionDOFcontainer:numFrames()+1)
		mMotionDOFcontainer:row(mMotionDOFcontainer:numFrames()-1):assign(mLoader:getPoseDOF())
		mSkin:applyMotionDOF(mMotionDOFcontainer.mot)
		RE.motionPanel():motionWin():detachSkin(mSkin)
		RE.motionPanel():motionWin():addSkin(mSkin)
		RE.motionPanel():motionWin():changeCurrFrame(mMotionDOFcontainer:numFrames()-1)
	elseif option=='append T-pose' then
		mLoader:updateInitialBone()
		local M=require("RigidBodyWin/retargetting/module/retarget_common")
		M.setVoca(mLoader)

		local lsh=mLoader:getBoneByVoca(MotionLoader.LEFTSHOULDER)
		local rsh=mLoader:getBoneByVoca(MotionLoader.RIGHTSHOULDER)
		M.gotoTpose(mLoader)
		local Tpose=mLoader:getPoseDOF()
		if Tpose:isnan() then
			mLoader:updateInitialBone()
			mLoader:rotateBoneGlobal(lsh, quater(math.rad(90), vector3(0,0,1)))
			mLoader:rotateBoneGlobal(rsh, quater(math.rad(-90), vector3(0,0,1)))
			Tpose=mLoader:getPoseDOF()
		end
		print(table.tostring2(Tpose))

		mMotionDOFcontainer:resize(mMotionDOFcontainer:numFrames()+1)
		mMotionDOFcontainer:row(mMotionDOFcontainer:numFrames()-1):assign(Tpose)
		mSkin:applyMotionDOF(mMotionDOFcontainer.mot)
		RE.motionPanel():motionWin():detachSkin(mSkin)
	end
end
function loadDOF(chosenFile)
	if scenarios then
		model=scenarios.toModel(useCase.scenario)
		_start(model.file_name)
	end
	_applyMotion(chosenFile)
end
function loadBVH(chosenFile)
	if not model then model={} end
	mMotionDOFcontainer=MotionDOFcontainer(mLoader.dofInfo)
	local dof=_importBVH(chosenFile, model.initialheight or 0)
	mMotionDOFcontainer:resize(dof:rows())
	mMotionDOFcontainer.mot:assign(dof)
	_G.chosenMotFile=chosenFile
	mSkin:applyMotionDOF(mMotionDOFcontainer.mot)
	RE.motionPanel():motionWin():detachSkin(mSkin)
	RE.motionPanel():motionWin():addSkin(mSkin)
	useNearestSamplingWhenExportingBVH=true
end

function handleRendererEvent()
	return 0
end
