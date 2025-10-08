
require("config")
require("module")
require("RigidBodyWin/subRoutines/WRLloader")

motion_path="../Resource/motion/"


function scr(p) -- for commandline use, e.g. lua short.lua wrlv "ctor();scr()"
	p =p or 1
	if p==1 then
		onCallback(this:findWidget("load (automatic)"),0)
	elseif type(p)=='string' and os.isFileExist(p) then
		loadFiles({p})
	end
end

function ctor()

   mEventReceiver=EVR()
   
--   this:create("Button", "load a predefined model", "load a predefined model", 0,3,0)

	dbg.draw('Axes', transf(quater(1,0,0,0), vector3(0,0,0)), 'axes')

	this:addCheckButton('show axes', false)
   this:create("Button", "load a folder", "load a folder")
   this:create("Button", "load (automatic)", "load (automatic)")
   this:create("Button", "load .wrl file", "load .wrl file")
   this:create("Button", "load .V file", "load .V file")
   this:create("Button", "load .bvh file", "load .bvh/.mot file")
   this:create("Button", "load .fbx file", "load .fbx file")
   this:create("Button", "load .fbx mesh file", "load .fbx mesh file")
   this:create("Button", "load .amc file", "load .amc file")
   this:create("Button", "load .mesh file", "load .mesh file")
   this:create("Button", "export .bvh file", "export .bvh file")
   this:create("Button", "export .bvh w/o Sjoint", "export .bvh w/o Sjoint")
   this:create("Button", "export .wrl file", "export .wrl file")
   this:create("Button", "scale 0.1 bvh file", "scale 0.1 bvh file")
   this:create("Button", "test", "test")
   this:create("Button", "changeMotionPath", "changeMotionPath")
   this:widget(0):buttonShortcut("FL_ALT+t")


   this:create("Box", "Adjust skin:", "Adjust skin:")
   this:create("Button", "scale 0.1", "scale 0.1")
   this:create("Button", "scale 10", "scale 10")
   this:create("Button", "scale 100", "scale 100")
   this:create("Button", "thickness 3", "thickness 3")
   this:create("Button", "thickness 0.3", "thickness 0.3")
   this:create("Button", "thickness 0.03", "thickness 0.03")
   this:create("Button", "translate 100", "translate 100")
   this:create("Button", "Zup to Yup", "Zup to Yup")
   this:create("Button", "Xdown to Yup", "Xdown to Yup")
   this:create("Button", "freeze current orientation to skel/mot", "freeze current orientation to skel/mot")
   this:create("Button", "show identity pose", "show identity pose")
   this:create("Button", "debug console","debug console")
   this:updateLayout()
   this:redraw()

   mObjectList=Ogre.ObjectList()

   RE.viewpoint():setFOVy(44.999999)
   RE.viewpoint().vpos:set(94.777964, 126.724047, 352.393547)
   RE.viewpoint().vat:set(-34.317428, 67.508947, -4.622992)
   RE.viewpoint():update()

   RE.renderer():fixedTimeStep(false)   
end


function loadFiles(files, path)
	if #files==0 then
		return 
	end
	if not path then
		local _
		_, path= os.processFileName(files[1])
		for i, v in ipairs(files) do
			files[i]=files[i]:sub(path:len()+1)
		end
	end
	local asf_files={}
	local amc_files={}
	local wrl_files={}
	local dof_files={}
	local other_files={}
	for i, file in ipairs(files) do

		if file:sub(-4):lower()=='.asf' then
			table.insert(asf_files, file)
		elseif file:sub(-4):lower()=='.wrl' then
			table.insert(wrl_files, file)
		elseif file:sub(-8):lower()=='.wrl.dat' then
			table.insert(wrl_files, file)
		elseif file:sub(-8):lower()=='.wrl.lua' then
			table.insert(wrl_files, file)
		elseif file:sub(-4):lower()=='.dof' then
			table.insert(dof_files, file)
		elseif file:sub(-4):lower()=='.amc' then
			table.insert(amc_files, file)
		elseif file:sub(-4):lower()=='.bvh' or file:sub(-4):lower()=='.fbx' then
			table.insert(other_files, file)
		else
			print("ignoring ", file)
		end
	end
	mSkins={}

	if #asf_files>=1 then
		local skels={}
		for i, v in ipairs(asf_files) do
			print('loading ', v)
			skels[i]=RE.motionLoader(path..'/'..v)
		end

		for i, v in ipairs(amc_files) do

			for j, vv in ipairs(asf_files) do
				local skel=vv:sub(1,-5)
				if v:sub(1, #skel+1)==skel..'.' or v:sub(1, #skel+1)==skel..'_' then

					local motion=Motion()
					print('loading ', v)
					skels[j]:loadAnimation(motion, path..'/'..v)

					skels[j].mMotion:concat(motion)
					break
				end
			end
		end

		for i, v in ipairs(asf_files) do
			local loader=skels[i]
			local skin=RE.createSkin(loader)
			skin:applyAnim(loader.mMotion)
			RE.motionPanel():motionWin():detachSkin(skin)
			RE.motionPanel():motionWin():addSkin(skin)
			table.insert(mSkins, { skels[i], skin})	
		end
		print('loading finished')
	elseif #other_files>=1 then
		for i, v in ipairs(other_files) do
			local loader
			print('loading ', v)
			if v:sub(-4)=='.bvh' then
				loader=RE.motionLoader(path..'/'..v)
			elseif v:sub(-4)=='.fbx' then
				local FBXloader=require("FBXloader")
				loader=FBXloader.motionLoader(path..'/'..v)
			else
				assert(false)
			end

			local skin=RE.createSkin(loader)
			if loader.mMotion:numFrames()>0 then
				skin:applyAnim(loader.mMotion)
				RE.motionPanel():motionWin():detachSkin(skin)
				RE.motionPanel():motionWin():addSkin(skin)
			end
			table.insert(mSkins, { loader, skin})	
		end
		print('loading finished')
	elseif #wrl_files>=1 then
		local skels={}
		for i, v in ipairs(wrl_files) do
			print('loading ', v)
			skels[i]=MainLib.WRLloader(path..'/'..v)
		end

		for i, v in ipairs(dof_files) do

			for j, vv in ipairs(wrl_files) do
				local skel=vv:sub(1,-5)
				if v:sub(1, #skel+1)==skel..'.' or v:sub(1, #skel+1)==skel..'_' then

					local motion=Motion()
					print('loading ', v)
					skels[j]:loadAnimation(motion, path..'/'..v)

					skels[j].mMotion:concat(motion)
					break
				end
			end
		end

		for i, v in ipairs(wrl_files) do
			local loader=skels[i]
			local skin=RE.createVRMLskin(loader, true)
			skin:setScale(100,100,100)
			skin:setSamePose(loader:fkSolver())

			if loader.mMotion:numFrames()>0 then
				skin:applyAnim(loader.mMotion)
			end
			RE.motionPanel():motionWin():detachSkin(skin)
			RE.motionPanel():motionWin():addSkin(skin)
			table.insert(mSkins, { skels[i], skin})	
		end
		print('loading finished')
	end
end


function onCallback(w, userData)
	if w:id()=="load a folder" then 
		local chosenFolder=Fltk.ChooseFolder("Choose any file to view", motion_path)
		if chosenFolder then
			local path=chosenFolder

			local files=string.lines(os.capture('ls -1 "'..path..'"', true))
			files[#files]=nil

			loadFiles(files, path)
		end
	elseif w:id()=="load (automatic)" then 
		local chosenFile=Fltk.chooseFile("Choose any file to view", motion_path, "*", false)
		if chosenFile~="" then
			local files={
				chosenFile
			}
			--local file, path= os.processFileName(chosenFile)

			--local files=string.lines(os.capture('ls -1 "'..path..'"', true))
			--files[#files]=nil

			loadFiles(files, path)
		end
	elseif w:id()=="load .bvh file" then
		local chosenFile=Fltk.chooseFile("Choose a BVH/MOT file to view", motion_path, "*.{bvh,mot}", false)
		if chosenFile~="" then
			mLoader=RE.motionLoader(chosenFile)
			if this:findWidget('show axes'):checkButtonValue() then
				mSkin=RE.createSkin(mLoader,PLDPrimSkin.POINT )
			else
				mSkin=RE.createSkin(mLoader)
			end
			if mLoader then
				if not mSkins then mSkins={} end
				table.insert(mSkins, { mLoader, mSkin})	
			end
			if mLoader.mMotion:numFrames()>0 then
				mSkin:applyAnim(mLoader.mMotion)
				RE.motionPanel():motionWin():detachSkin(mSkin)
				RE.motionPanel():motionWin():addSkin(mSkin)
			end
		end
	elseif w:id()=="load .fbx file" then
		local chosenFile=Fltk.chooseFile("Choose a FBX file to view", motion_path, "*.{fbx,FBX}", false)
		if chosenFile~="" then
			local FBXloader=require("FBXloader")
			mLoader=FBXloader.motionLoader(chosenFile)
			mSkin=RE.createSkin(mLoader)
			if mLoader then
				if not mSkins then mSkins={} end
				table.insert(mSkins, { mLoader, mSkin})	
			end
			if mLoader.mMotion:numFrames()>0 then
				mSkin:applyAnim(mLoader.mMotion)
				RE.motionPanel():motionWin():detachSkin(mSkin)
				RE.motionPanel():motionWin():addSkin(mSkin)
			end
		end
	elseif w:id()=="load .fbx mesh file" then
		local chosenFile=Fltk.chooseFile("Choose a FBX file to view", motion_path, "*.{fbx,FBX}", false)
		if chosenFile~="" then
			local FBXloader=require("FBXloader")
			mLoader=FBXloader(chosenFile)
			mSkin=RE.createFBXskin(mLoader)
			if mLoader then
				if not mSkins then mSkins={} end
				table.insert(mSkins, { mLoader, mSkin})	
			end
		end
   elseif w:id()=='debug console' then
	   dbg.console()
   elseif w:id()=='show identity pose' then
	   local function showIdentityPose(skel, skin)
		   local pose=skel:pose()
		   pose:identity()
		   skin:setPose(pose, skel)
	   end
		for i,v in ipairs(mSkins) do
			showIdentityPose(v[1], v[2])
		end
		if mLoader then
			showIdentityPose(mLoader, mSkin)
		end
   elseif w:id()=='load .mesh file' then
	   local chosenFile=Fltk.chooseFile("Choose a mesh file to view", '../media/models', "*.mesh", false)
	   if chosenFile~="" then
		   local fn=os.processFileName(chosenFile)
		   if g_node then RE.removeEntity(g_node) end
		   g_node=RE.createEntity("metric",fn)
	   end
   elseif w:id()=="scale 0.1 bvh file" then
	   local chosenFile=Fltk.chooseFile("Choose a BVH/MOT file to view", motion_path, "*.{bvh,mot}", false)
	   if chosenFile~="" then
		   mLoader=RE.motionLoader(chosenFile)
		   mLoader.mMotion:scale(0.1)
		   local mot=mLoader.mMotion
		   MotionUtil.exportBVH(mot, string.sub(chosenFile, 1,-5).."_0.1.bvh", 0, mot:numFrames())
	   end
   elseif w:id()=="changeMotionPath" then
	   motion_path="../Resource/scripts/ui/RigidBodyWin"
   elseif w:id()=="load .wrl file" then
	   local chosenFile=Fltk.chooseFile("Choose a wrl file to view", motion_path, "*.wrl", false)
	   if chosenFile~="" then
		   local chosenFile2=Fltk.chooseFile("Choose a dof file to view", motion_path, "*.dof", false)
		   mLoader=MainLib.VRMLloader(chosenFile)
		   if chosenFile2 then
			   mMotionDOFcontainer=MotionDOFcontainer(mLoader.dofInfo,chosenFile2)
		   end
		   local drawSkeleton=true
		   mSkin=RE.createVRMLskin(mLoader, drawSkeleton)

		   if  drawSkeleton then
			   mSkin:scale(100,100,100)
			   mSkin:setThickness(0.03)
		   end
		   mSkin:applyMotionDOF(mMotionDOFcontainer.mot)
		   RE.motionPanel():motionWin():detachSkin(mSkin)
		   RE.motionPanel():motionWin():addSkin(mSkin)
	   end
   elseif w:id()=="load .amc file" then
	   local chosenFile=Fltk.chooseFile("Choose a ASF file to view", motion_path, "*.asf", false)
	   if chosenFile~="" then
		   mLoader=RE.motionLoader(chosenFile)
		   if mLoader.mMotion:numFrames()==0 then
			   local chosenFile=Fltk.chooseFile("Choose a AMC file to view", motion_path, "*.amc", false)
			   if chosenFile~="" then mLoader:loadAnimation(mLoader.mMotion, chosenFile) end
		   end
		   mLoader:removeAllRedundantBones()
		   mSkin=RE.createSkin(mLoader)
		   mSkin:applyAnim(mLoader.mMotion)

		   -- detect fixed joints
		   min_len=vectorn();
		   max_len=vectorn();
		   dist=vectorn();
		   do
			   -- calc len and dist
			   local pose=mLoader.mMotion:pose(0)
			   local t=pose.translations
			   min_len:setSize(t:size())
			   min_len:set(0,0)
			   max_len:setSize(t:size())
			   max_len:set(0,0)
			   dist:setSize(t:size())
			   dist:set(0,0)
			   for j=1, t:size()-1 do
				   min_len:set(j, t(j):length())
				   max_len:set(j, t(j):length())
				   dist:set(j, 0)
			   end
		   end
		   for i=1, mLoader.mMotion:numFrames()-1 do
			   local pose=mLoader.mMotion:pose(i)
			   local ppose=mLoader.mMotion:pose(i-1)
			   local t=pose.translations
			   for j=1, t:size()-1 do
				   local l=t(j):length()
				   local d=t(j):distance(ppose.translations(j))
				   min_len:set(j, math.min(min_len(j), l))
				   max_len:set(j, math.max(max_len(j), l))
				   dist:set(j, math.max(d, dist(j)))
			   end
		   end

		   local pose=mLoader.mMotion:pose(0)
		   local t=pose.translations
		   for j=1, t:size()-1 do
			   if max_len(j)-min_len(j)>0.0001 then
				   print(':'..mLoader:getBoneByTreeIndex(mLoader:getTreeIndexByTransJointIndex(j)):name())
			   end
			   if dist(j)>0.0001 then
				   print(';'..mLoader:getBoneByTreeIndex(mLoader:getTreeIndexByTransJointIndex(j)):name(), dist(j))
			   end
		   end
		   RE.motionPanel():motionWin():detachSkin(mSkin)
		   RE.motionPanel():motionWin():addSkin(mSkin)
	   end
   elseif w:id()=="export .wrl file" then
		local chosenFile=Fltk.chooseFile("Choose a WRL file to create", ".", "*.wrl", true)
		if chosenFile and chosenFile ~='' then
			if dbg.lunaType(mLoader)=='MainLib.VRMLloader' then
				-- probably already in meter scale
				mLoader:export(chosenFile)
				mMotionDOFcontainer:exportMot(chosenFile..'.dof')
			else
				mLoader:Scale(0.01) -- convert to meter scale
				MotionUtil.exportVRMLforRobotSimulation(mLoader.mMotion, chosenFile, 'unknown robot', 0.01)
				local tempSkel=MainLib.VRMLloader(chosenFile)
				local motiondofc=MotionDOFcontainer(tempSkel.dofInfo)
				motiondofc.mot:set(mLoader.mMotion)
				motiondofc:exportMot(chosenFile..'.dof')
				mLoader:Scale(100) -- revert back to cm scale
			end
		end

   elseif w:id()=="export .bvh file" then
	   local chosenFile=Fltk.chooseFile("Choose a BVH file to create", motion_path, "*.bvh", true)
	   	local mot=mLoader.mMotion
		if mot :numFrames()==0 then
			mot:init(Motion(mMotionDOFcontainer.mot), 0, mMotionDOFcontainer:numFrames())

		   --mSkin2=RE.createSkin(mLoader)
		   --mSkin2:applyAnim(mLoader.mMotion)
		   --mSkin2:scale(100,100,100)
		   --RE.motionPanel():motionWin():detachSkin(mSkin2)
		   --RE.motionPanel():motionWin():addSkin(mSkin2)
		end
		for i=1, mot:skeleton():numBone()-1 do
			local bone=mot:skeleton():bone(i)
			local trans=bone:getTranslationalChannels()
			local rot=bone:getRotationalChannels()
			if rot and string.len(rot)~=0 then
				rot="ZXY"
			end

			if trans and string.len(trans)~=0 then
				trans="XYZ"
			end

			if rot or trans then
				if trans==nil then trans='' end
				bone:setChannels(trans, rot)
			end
		end
	   MotionUtil.exportBVH(mLoader.mMotion, chosenFile, 0, mLoader.mMotion:numFrames())
	   -- TODO: revert channels back to the original values.
	elseif w:id()=="export .bvh w/o Sjoint" then
	   local chosenFile=Fltk.chooseFile("Choose a BVH file to create", motion_path, "*.bvh", true)
	   MotionUtil.exportBVHwithoutSlidingJoints(mLoader.mMotion, chosenFile, 0, mLoader.mMotion:numFrames())
   elseif w:id()=="load .V file" then
	   local chosenFile=Fltk.chooseFile("Choose a vsk file to view", motion_path, "*.vsk", false)
	   if chosenFile~="" then
		   mLoader=RE.motionLoader(chosenFile)
		   --if mLoader.mMotion:numFrames()==0 then
		   if true then
			   local fn, path=os.processFileName(chosenFile)
			   motion_path=path
			   local chosenFile=Fltk.chooseFile("Choose v file to view", path, "*.v", false)
			   if chosenFile~="" then mLoader:loadAnimation(mLoader.mMotion, chosenFile) end
		   end
		   mSkin=RE.createSkin(mLoader)
		   mSkin:applyAnim(mLoader.mMotion)
		   RE.motionPanel():motionWin():detachSkin(mSkin)
		   RE.motionPanel():motionWin():addSkin(mSkin)
	   end
   elseif w:id()=="test" then
	   mLoader=RE.motionLoader("../Resource/motion/Gymnist/Project 2/Capture day 1/Session 1/gymnist1.vsk")
	   --mLoader:loadAnimation(mLoader.mMotion, "../Resource/motion/Gymnist/Project 2/Capture day 1/Session 1/matless_ROM.V")
	   --mLoader:loadAnimation(mLoader.mMotion, "../Resource/motion/Gymnist/Project 2/Capture day 1/Session 1/matless_walk.V")
	   mLoader:loadAnimation(mLoader.mMotion, "../Resource/motion/Gymnist/Project 2/Capture day 1/Session 1/matless_roundoff 1.V")
	   --mLoader:loadAnimation(mLoader.mMotion, "../Resource/motion/test.v")
	   mLoader:printHierarchy()
	   mEventReceiver:loadMarkers(mLoader.markers,mLoader.frames, mLoader)
	   mSkin=RE.createSkin(mLoader)
	   mSkin:applyAnim(mLoader.mMotion)
	   RE.motionPanel():motionWin():detachSkin(mSkin)
	   RE.motionPanel():motionWin():addSkin(mSkin)
   elseif w:id()=='translate 100' then
	   if mSkin then
		   mSkin:setTranslation(100,0,0)
	   end
   elseif w:id()=="scale 100" then
	   if mSkins then
		   for i, skin in ipairs(mSkins) do
			   skin[2]:scale(100,100,100)
		   end
	   end
	   if g_node then g_node:setScaleAndPosition(vector3(100,100,100), vector3(0,0,0)) end

   elseif w:id()=="thickness 3" then
	   mSkin:setThickness(3)
   elseif w:id()=="thickness 0.3" then
	   mSkin:setThickness(0.3)
   elseif w:id()=="thickness 0.03" then
	   mSkin:setThickness(0.03)
   elseif w:id()=="scale 10" then
	   if mSkins then
		   for i, skin in ipairs(mSkins) do
			   skin[2]:scale(10,10,10)
			   skin[2]:setThickness(3)
		   end
	   end
	   if g_node then g_node:setScaleAndPosition(vector3(10,10,10), vector3(0,0,0)) end
   elseif w:id()=="scale 0.1" then
	   if mSkins then
		   for i, skin in ipairs(mSkins) do
			   skin[2]:scale(0.1,0.1,0.1)
			   skin[2]:setThickness(3)
		   end
	   end
	   if g_node then g_node:setScaleAndPosition( vector3(0.1,0.1,0.1), vector3(0,0,0)) end
   elseif w:id()=="Zup to Yup" then
	   local dofRot=quater()
	   dofRot:axisToAxis(vector3(0,0,1), vector3(0,1,0))
	   if mSkins then
		   for i, skin in ipairs(mSkins) do
			   skin[2]:setRotation(dofRot)
		   end
	   end
   elseif w:id()=="Xdown to Yup" then
	   local dofRot=quater()
	   dofRot:axisToAxis(vector3(-1,0,0), vector3(0,1,0))
	   if mSkins then
		   for i, skin in ipairs(mSkins) do
			   skin[2]:setRotation(dofRot)
		   end
	   end
   elseif w:id()=="freeze current orientation to skel/mot" then
	   local dofRot=mSkin:getRotation()
	   assert(mSkin)

	   RE.motionPanel():motionWin():detachSkin(mSkin)
	   mSkin=nil
	   mSkins={}
	   collectgarbage()
	   collectgarbage()
	   collectgarbage()
	   collectgarbage()
	   for i=1, mLoader:numBone()-1 do
		   local bone=mLoader:bone(i)
		   local t=bone:getOffsetTransform().translation
		   t:assign(dofRot*t)
		   print(bone:getOffsetTransform().translation)
	   end
	   mLoader:updateInitialBone()

	   local mot=mLoader.mMotion
	   for i=0, mot:numFrames()-1 do
		   local p=mot:pose(i)
		   for ti=0, p.translations:size()-1 do
			   local t=p.translations(ti)
			   t:assign(dofRot*t)
		   end
		   for ri=0, p.rotations:size()-1 do
			   local r=p.rotations(ri)
			   r:assign(dofRot*r*dofRot:inverse())
		   end
	   end

	   mSkin=RE.createSkin(mLoader)
	   mSkin:applyAnim(mLoader.mMotion)
	   RE.motionPanel():motionWin():addSkin(mSkin)
   end

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
if EventReceiver then
	EVR=LUAclass(EventReceiver)
	function EVR:__init(graph)
		--EventReceiver.__init(self)
		self.currFrame=0
	end
else
	class 'EVR'
	function EVR:__init(graph)
	end
end
function EVR:loadMarkers(markers, bones, skel)
	self.traceManager=array:new()
	for i=1, markers:rows() do
		local markerdraw=TStrings()
		markerdraw:resize((markers:cols()/3)*2+ (bones:cols()/6)*2)

		local c=0
		local f=i-1
		for j=0, markers:cols()-1,3 do
			local nameid='m'..tostring(j/3)
			markerdraw:set(c, 'namedDraw_'..nameid)
			markerdraw:set(c+1, table.tostring2({'Sphere', vector3(markers(f,j), markers(f,j+1), markers(f,j+2)), nameid, 'red', 5}) )
			c=c+2
		end
		for j=0, bones:cols()-1,6 do
			local nameid='b'..skel:bone(j/6+1):name()
			markerdraw:set(c, 'namedDraw_'..nameid)
			local tf=transf()
			tf.translation:assign(vector3(bones(f,j+3), bones(f,j+4), bones(f,j+5)))
--			tf.rotation:setRotation("XYZ", vector3(bones(f,j), bones(f,j+1), bones(f,j+2))) -- EulerXYZ
			tf.rotation:setRotation( vector3(bones(f,j), bones(f,j+1), bones(f,j+2))) -- Rotation vector
			markerdraw:set(c+1, table.tostring2({'Axes', tf, nameid}))
			c=c+2
		end
		self.traceManager:pushBack(markerdraw)
	end
end
function EVR:loadTraceManager()
	self.traceManager=array:new()

	local binaryFile=util.BinaryFile()
	binaryFile:openRead("debug_plot.cf")
	local contactForce=matrixn()
	binaryFile:unpack(contactForce)
	local n=binaryFile:unpackInt()
	for i=1, n do
		local message=TStrings()
		binaryFile:unpack(message)
		self.traceManager:pushBack(message)
	end
	binaryFile:close()
end
function EVR:onFrameChanged(win, iframe)
	self.currFrame=iframe
	if self.traceManager then
		local message=self.traceManager[iframe+1]
		if message then
			dbg.eraseAllDrawn()
			RE.outputEraseAll(2)
			for i=0, message:size()-1,2 do
				RE.output2(message(i), message(i+1))
				if string.sub(message(i),1,10)== 'namedDraw_' then
					local tbl=table.fromstring2(message(i+1))
					dbg.namedDraw(unpack(tbl))
				end
			end
		end
	end
	if self.trajectory then
		if self.currFrame<self.trajectory:rows() then
			local curPos=self.trajectory:row(self.currFrame):toVector3(0)*100
			RE.viewpoint().vpos:assign(self.cameraInfo.vpos+curPos)
			RE.viewpoint().vat:assign(self.cameraInfo.vat+curPos)
			RE.viewpoint():update()     
		end
	end
end

function EVR:attachCamera()

	if mLoader~=nill then

		local discont=mMotionDOFcontainer.discontinuity
		local mMotionDOF=mMotionDOFcontainer.mot

		self.trajectory=matrixn(mMotionDOFcontainer:numFrames(),3)

		local segFinder=SegmentFinder(discont)

		for i=0, segFinder:numSegment()-1 do
			local s=segFinder:startFrame(i)
			local e=segFinder:endFrame(i)

			for f=s,e-1 do
				self.trajectory:row(f):setVec3(0, MotionDOF.rootTransformation(mMotionDOF:row(f)).translation)
				self.trajectory:row(f):set(1,0)
			end
			print("filtering",s,e)
			math.filter(self.trajectory:range(s,e,0, 3), 63)
		end

		self.cameraInfo={}
		local curPos=self.trajectory:row(self.currFrame):toVector3(0)*100
		self.cameraInfo.vpos=RE.viewpoint().vpos-curPos
		self.cameraInfo.vat=RE.viewpoint().vat-curPos
	end
end

function frameMove(fElapsedTime)
end

function _applyMotion(chosenFile, nodetach)

	if mLoader~=nill then

		mMotionDOFcontainer=MotionDOFcontainer(mLoader.dofInfo,chosenFile)
		mSkin:applyMotionDOF(mMotionDOFcontainer.mot)
		-- if not nodetach then
		-- 	 RE.motionPanel():motionWin():detachAllSkin()
		-- end
		RE.motionPanel():motionWin():detachSkin(mSkin)

		RE.motionPanel():motionWin():addSkin(mSkin)
	end
end

function handleRendererEvent(ev, button, x, y)
	return 0
end
