require("config")
require("common")
require("module")
require("RigidBodyWin/motionFormatConversion/convertMOTtoWRL")
require("RigidBodyWin/motionFormatConversion/RetargetDOFtoVRML")

function ctor()
	this:create('Button', 'choose file', '1. choose file')
	this:create('Button', 'choose file (1/100x)', '1. choose file (1/100x)')
	this:create('Button', 'export WRL', '2. export WRL')
	this:create('Button', 'export DOF', '3. export DOF')
	this:create('Button', 'export DOF (short)', '3. export DOF (short)')
	this:create('Button', 'export DOF (fast)', '3. export DOF (fast)')
	this:updateLayout()
end

function release()
	RE.motionPanel():motionWin():detachAllSkin()
	skel=nil
	mSkin=nil
	collectgarbage()
end
function chooseFile(scale)
	release()
	mScale=scale
	local chosenFile=Fltk.chooseFile("Choose a vsk file to view", '.', "*.{bvh,asf,mot}", false)
	if chosenFile and string.sub(string.upper(chosenFile),-3)=='BVH' then
		motion={skel_file=chosenFile, mot_files={chosenFile}, scale= scale }
	elseif chosenFile and string.sub(string.upper(chosenFile),-3)=='MOT' then
		motion={skel_file=chosenFile, mot_files={chosenFile}, scale= scale }
	elseif chosenFile and string.sub(string.upper(chosenFile),-3)=='ASF' then
		local chosenFile2=Fltk.chooseFile("Choose a asf file to view", '.', "*.amc", false)
		motion={skel_file=chosenFile, mot_files={chosenFile2}, scale= scale }
	end
	part1()
	mSkin:applyAnim(skel.mMotion)
	RE.motionPanel():motionWin():detachSkin(mSkin)
	RE.motionPanel():motionWin():addSkin(mSkin)
end
function onCallback(w, userData)
	if w:id()=='choose file' then
		chooseFile(1)
	elseif w:id()=='choose file (1/100x)' then
		chooseFile(0.01)
	elseif w:id()=='export WRL' then
		local chosenFile=Fltk.chooseFile("Choose a wrl file to create", '.', "*.wrl", true)
		if chosenFile then
			local key,path=os.processFileName(chosenFile)

			if string.lower(string.sub(key,-3))~='wrl' then
				key=key..'.wrl'
				chosenFile=chosenFile..'.wrl'
			end
			motion.out_path=path or '.'
			motion.out_path=motion.out_path..'/'
			motion.out_file=key
			motion.createFolder=motion.out_path..string.sub(key,1,-5)..'_sd'
			motion.name=key
			g_export_info=motion

			part3_exportWRL()
		end

	elseif w:id()=='export DOF' or w:id()=='export DOF (short)' or w:id()=='export DOF (fast)' then

		local isFast=w:id()=='export DOF (fast)'
		local motion_backup=motion
		local chosenFile=Fltk.chooseFile("Choose a DOF file to create", g_export_info.out_path, "*.dof", true)
		if chosenFile then
			local key,path=os.processFileName(chosenFile)

			if string.lower(string.sub(key,-3))~='dof' then
				key=key..'.dof'
				chosenFile=chosenFile..'.dof'
			end
			motion2=deepCopyTable(Motions.default)
			motion2.src_skel_file=motion.skel_file
			motion2.out_file=chosenFile
			motion2.wrl_file=motion.out_path..motion.out_file
			motion2.scale=mScale
			if isFast then
				motion2.conversionMethod= conversionMethod_T.  useLocalOrientation -- Forward kinematics. (all local axes of model and motion should match.)
				motion2.scale=1
			end
			if w:id()=='export DOF (short)'then
				endFrame=100	
			end
			__convert(skel,{file_name=motion2.wrl_file}, motion2, skel.mMotion, true)
			if mSkin2 then
				mSkin2:applyMotionDOF(mot2.mot)
				RE.motionPanel():motionWin():detachSkin(mSkin2)
				RE.motionPanel():motionWin():addSkin(mSkin2)
			end
		end
		motion=motion_backup
	end
end
