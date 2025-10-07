
require("config")
require("common")

target='synthesis2'

-- how to create a VRML model for simulation?
-- 1. run convertMotToVRML.lua  (lua short.lua mottovrml) to make a wrl file that represents a virtual robot.
--     a. Set the table: Motions (skel_file, mot_file, out_file, out_motfile, (optional) createFolder, out_marker_file, scale and rotation, ...)
--     b. Run
--     c. (optional) check output files using WRLViewer.lua - load model - apply animation.
-- 2. modify the output wrl file manually. 
--     a. Set DOFs (etc. jointaxis="YZX")
--     b. rename, add, or remove joints
--     c. you can change meshes later at step (5)
-- 3. retarget the captured motion to the modified WRL (the captured motion is
-- converted from .V, .BVH, .ASF/AMC files when MotToVRML is run.) 
--	   a. set the table Model in common.lua
--         : file_name: the modified model file
--         , mot_name: the output motion file (.dof)
--         , totalmass
--     b. run RetargetDOFToVrml.lua

-- Now, we have a WRL file (skeleton) and a DOF file (motion).

-- 4. run modifyModel.lua or WRLtoSDFAST.lua to calculate mass, inertia properties from mesh.
--    if ~~~_sd path doesn't exist, you have to create it by yourself--;
--    then, click export model2  button. 
--    now, you can replace the surface mesh by manually replacing the obj files
--    in ~~~_sd path

-- 5. use modifyModel.lua for fine tuning the surface mesh.

-- 6. (optional) you can use blender (l blender_install, blender object -> script -> taesoo import /export)

-- 7. (optional) use zmpAnalysis2.lua to verify that mass, inertia properties are properly set.
--    : ZMP calculated from captured motion should be in the supporting region.

Motions={}
Motions.default={}
Motions.default.mot_files={}-- skel_file contains motions too.

Motions.synthesis1=deepCopyTable(Motions.default)
Motions.synthesis1.skel_file="../work/mSynthesis1.mot"
Motions.synthesis1.scale=0.01		-- change cm to METER unit system
Motions.synthesis1.out_file="../../work/mSynthesis1.wrl"
Motions.synthesis1.name="mSynthesis1"

Motions.synthesis2=deepCopyTable(Motions.default)
Motions.synthesis2.skel_file="../work/mSynthesis2.mot"
Motions.synthesis2.scale=0.01		-- change cm to METER unit system
Motions.synthesis2.out_file="../../work/mSynthesis2.wrl"
Motions.synthesis2.name="mSynthesis2"

Motions.heavy=deepCopyTable(Motions.default)
Motions.heavy.skel_file="../Samples/classification/lua/gf/motion/human/test_skel.bvh"
Motions.heavy.scale=0.01		-- change cm to METER unit system
Motions.heavy.out_file="../Samples/classification/lua/gf/motion/human/test_skel.wrl"
Motions.heavy.name="heavy"

Motions.muaythai1=deepCopyTable(Motions.default)
Motions.muaythai1.skel_file="../Resource/motion/kickboxer/muaythai/muaythai1.mot"
Motions.muaythai1.scale=0.01		-- change cm to METER unit system
Motions.muaythai1.out_file="muaythai1.wrl"
Motions.muaythai1.name="muaythai1"

Motions.muaythai2=deepCopyTable(Motions.default)
Motions.muaythai2.skel_file="../Resource/motion/kickboxer/muaythai/muaythai2.mot"
Motions.muaythai2.scale=0.01		-- change cm to METER unit system
Motions.muaythai2.out_file="muaythai2.wrl"
Motions.muaythai2.name="muaythai2"

Motions.taekwondo1=deepCopyTable(Motions.default)
Motions.taekwondo1.skel_file="../Resource/motion/kickboxer/man1all_nd.mot"
Motions.taekwondo1.scale=0.0254		-- change inch to METER unit system
Motions.taekwondo1.out_file="taekwondo1.wrl"
Motions.taekwondo1.name="taekwondo1"

Motions.taekwondo2=deepCopyTable(Motions.default)
Motions.taekwondo2.skel_file="../Resource/motion/kickboxer/man2all_nd.mot"
Motions.taekwondo2.scale=0.0254		-- change inch to METER unit system
Motions.taekwondo2.out_file="taekwondo2.wrl"
Motions.taekwondo2.name="taekwondo2"

Motions.locomotion=deepCopyTable(Motions.default)
Motions.locomotion.skel_file="../Resource/motion/locomotion_hyunwoo2/locomotion.mot"
Motions.locomotion.scale=0.01	-- change to METER unit system
Motions.locomotion.out_file="locomotion.wrl"
Motions.locomotion.name="hyunwoo"

Motions.jump=deepCopyTable(Motions.default)
Motions.jump.skel_file="../Resource/scripts/ui/rigidbodywin/02.asf"
Motions.jump.mot_files={"../Resource/scripts/ui/rigidbodywin/02_04.amc"}
Motions.jump.scale=0.045	-- change to METER unit system
Motions.jump.out_file="jump_raw.wrl"	-- used only in MotToVRML.lua
Motions.jump.name="jump"		-- used only in MotToVRML.lua

Motions.jump4=deepCopyTable(Motions.jump)
Motions.jump4.scale=0.045*173/146	-- change to METER unit system

Motions.jump5=deepCopyTable(Motions.default)
Motions.jump5.skel_file="../Resource/scripts/ui/rigidbodywin/jump_raw.mot"
Motions.jump5.out_file="jump_raw.wrl"	-- used only in MotToVRML.lua
Motions.jump5.name="jump"	-- used only in MotToVRML.lua

Motions.boxer=deepCopyTable(Motions.default)
Motions.boxer.skel_file="../Resource/motion/boxer/boxer.asf"
Motions.boxer.mot_files={"../Resource/motion/boxer/boxer.amc"}
Motions.boxer.scale=0.01	-- change to METER unit system
Motions.boxer.out_file="boxer.wrl"
Motions.boxer.name="boxer"

Motions.justin=deepCopyTable(Motions.default)
Motions.justin.path="../Resource/scripts/ui/rigidbodywin/justin_jump/AMCs/"
Motions.justin.skel_file=Motions.justin.path.."ROM.asf"
Motions.justin.mot_files={
   Motions.justin.path.."stand.amc",
   Motions.justin.path.."stand001.amc",
   Motions.justin.path.."stand002.amc",
   Motions.justin.path.."stand003.amc",
   Motions.justin.path.."stand004.amc",
   Motions.justin.path.."stand005.amc"}
Motions.justin.out_file="justin_raw.wrl"
Motions.justin.out_mot_file="justin_raw.mot"
Motions.justin.scale=0.01*2.54 -- change to METER unit system
Motions.justin.rotation=quater(math.rad(-90), vector3(0,1,0))
*quater(math.rad(-90), vector3(1,0,0))
Motions.justin.name="justin"

Motions.justin_runf3=deepCopyTable(Motions.default)
-- Motions.justin_runf3.path="../Resource/motion/justin_data/Disney_characters/Project 2/Capture day 1/Session 4/"
-- Motions.justin_runf3.skel_file="skipping.bvh"
-- Motions.justin_runf3.mot_files={
--    Motions.justin_runf3.path.."skipping.bvh"
-- }

Motions.justin_runf3.path="../Resource/scripts/ui/rigidbodywin/justin_run/"
Motions.justin_runf3.skel_file=Motions.justin_runf3.path.."ROM.asf"
Motions.justin_runf3.mot_files={
   Motions.justin_runf3.path.."skipping.amc",
   -- Motions.justin_runf3.path.."normal_run1.amc",
   -- Motions.justin_runf3.path.."normal_run2.amc",
   -- Motions.justin_runf3.path.."run_fast_001.amc",
   -- Motions.justin_runf3.path.."run_fast_002.amc",
   -- Motions.justin_runf3.path.."run_fast_003.amc",
   -- Motions.justin_runf3.path.."run_fast_004.amc",
   -- Motions.justin_runf3.path.."run_fast_005.amc",
   -- Motions.justin_runf3.path.."run_med_001.amc",
   -- Motions.justin_runf3.path.."run_med_002.amc",
   -- Motions.justin_runf3.path.."run_med_003.amc",
   -- Motions.justin_runf3.path.."normal_run3.amc",
   -- Motions.justin_runf3.path.."normal_run4.amc",
   -- Motions.justin_runf3.path.."run_med_004.amc",
   -- Motions.justin_runf3.path.."run_med_005.amc",
   -- Motions.justin_runf3.path.."run_left.amc",
   -- Motions.justin_runf3.path.."run_right.amc",
   -- Motions.justin_runf3.path.."walk.amc"
}
Motions.justin_runf3.reference_file="justin_runf3_cart.wrl"
Motions.justin_runf3.out_file="justin_runf3_raw.wrl"
Motions.justin_runf3.out_mot_file="justin_runf3_raw.mot"
Motions.justin_runf3.scale=0.01*2.54 -- change to METER unit system
Motions.justin_runf3.rotation=quater(math.rad(-90), vector3(0,1,0))
*quater(math.rad(-90), vector3(1,0,0))
Motions.justin_runf3.name="justin"


Motions.justin_runf3_compare=deepCopyTable(Motions.default)
Motions.justin_runf3_compare.path="../Resource/scripts/ui/rigidbodywin/justin_run/"
Motions.justin_runf3_compare.skel_file=Motions.justin_runf3.path.."ROM.asf"
Motions.justin_runf3_compare.mot_files={
--   Motions.justin_runf3.path.."run_left.amc",
    Motions.justin_runf3.path.."run_right.amc",
   -- Motions.justin_runf3.path.."skipping.amc",
   -- Motions.justin_runf3.path.."walk.amc"
}
Motions.justin_runf3_compare.out_mot_file="justin_right.mot"
Motions.justin_runf3_compare.out_file="justrin_right.wrl"
Motions.justin_runf3_compare.scale=2.54 -- change to centi-meter unit system
Motions.justin_runf3_compare.rotation=quater(math.rad(-90), vector3(0,1,0))
*quater(math.rad(-90), vector3(1,0,0))
Motions.justin_runf3_compare.name="justin"

Motions.justin_runf3_compare_rom=deepCopyTable(Motions.justin_runf3_compare)
Motions.justin_runf3_compare_rom.mot_files={
--   Motions.justin_runf3.path.."run_left.amc",
   Motions.justin_runf3.path.."walk.amc",}
Motions.justin_runf3_compare_rom.out_mot_file="justin_right_ROM.mot"



Motions.justin_run=deepCopyTable(Motions.default)
Motions.justin_run.path="../Resource/motion/run_justin/"
Motions.justin_run.skel_file=Motions.justin_run.path.."ROM_runner.asf"
Motions.justin_run.mot_files={
   Motions.justin_run.path.."run_slow.amc",
   Motions.justin_run.path.."run_slow001.amc",
   Motions.justin_run.path.."run_slow002.amc",
   Motions.justin_run.path.."run_slow_004.amc",
   Motions.justin_run.path.."run_slow_005.amc",
   Motions.justin_run.path.."run_slow_med_001.amc",
   Motions.justin_run.path.."run_slow_med_002.amc",
   Motions.justin_run.path.."run_slow_med_003.amc",
   Motions.justin_run.path.."run_slow_med_004.amc",
   Motions.justin_run.path.."run_slow_med_005.amc",
   Motions.justin_run.path.."run_slow_fast_001.amc",
   Motions.justin_run.path.."run_slow_fast_002.amc",
   Motions.justin_run.path.."run_slow_fast_003.amc",
   Motions.justin_run.path.."run_slow_fast_004.amc",
   Motions.justin_run.path.."run_slow_fast_005.amc",
   Motions.justin_run.path.."run_med_slow_001.amc",
   Motions.justin_run.path.."run_med_slow_002.amc",
   Motions.justin_run.path.."run_med_slow_003.amc",
   Motions.justin_run.path.."run_med_slow_004.amc",
   Motions.justin_run.path.."run_med_slow_005.amc",
   Motions.justin_run.path.."run_med_001.amc",
   Motions.justin_run.path.."run_med_002.amc",
   Motions.justin_run.path.."run_med_003.amc",
   Motions.justin_run.path.."run_med_004.amc",
   Motions.justin_run.path.."run_med_005.amc",
   Motions.justin_run.path.."run_med_fast_001.amc",
   Motions.justin_run.path.."run_med_fast_002.amc",
   Motions.justin_run.path.."run_med_fast_003.amc",
   Motions.justin_run.path.."run_med_fast_004.amc",
   Motions.justin_run.path.."run_med_fast_005.amc",
   Motions.justin_run.path.."run_fast_slow_001.amc",
   Motions.justin_run.path.."run_fast_slow_002.amc",
   Motions.justin_run.path.."run_fast_slow_003.amc",
   Motions.justin_run.path.."run_fast_slow_004.amc",
   Motions.justin_run.path.."run_fast_slow_005.amc",
   Motions.justin_run.path.."run_fast_med_001.amc",
   Motions.justin_run.path.."run_fast_med_002.amc",
   Motions.justin_run.path.."run_fast_med_003.amc",
   Motions.justin_run.path.."run_fast_med_004.amc",
   Motions.justin_run.path.."run_fast_med_005.amc",
   Motions.justin_run.path.."run_fast_001.amc",
   Motions.justin_run.path.."run_fast_002.amc",
   Motions.justin_run.path.."run_fast_003.amc",
   Motions.justin_run.path.."run_fast_004.amc",
   Motions.justin_run.path.."run_fast_005.amc",}
Motions.justin_run.out_file="justin_run_raw.wrl"
Motions.justin_run.out_mot_file="justin_run_raw.mot"

Motions.justin_run.scale=0.01*2.54 -- change to METER unit system
Motions.justin_run.rotation=quater(math.rad(-90), vector3(0,1,0))
*quater(math.rad(-90), vector3(1,0,0))
Motions.justin_run.name="justin_run"


Motions.justin_straight_run=deepCopyTable(Motions.default)
Motions.justin_straight_run.path="../Resource/motion/run_justin_straight/bvh/"
Motions.justin_straight_run.skel_file=Motions.justin_straight_run.path.."ROM.bvh" 
Motions.justin_straight_run.mot_files={
   Motions.justin_straight_run.path.."slowrun.bvh",
   Motions.justin_straight_run.path.."slowrun001.bvh",
   Motions.justin_straight_run.path.."slowrun002.bvh",
   Motions.justin_straight_run.path.."slowrun003.bvh",
   Motions.justin_straight_run.path.."slowrun004.bvh",
   Motions.justin_straight_run.path.."slowrun005.bvh",
   Motions.justin_straight_run.path.."slowrun006.bvh",
   Motions.justin_straight_run.path.."slowrun007.bvh",
   Motions.justin_straight_run.path.."slowrun008.bvh",
   Motions.justin_straight_run.path.."slowrun009.bvh",
   Motions.justin_straight_run.path.."slowrun010.bvh",}
Motions.justin_straight_run.out_file="justin_straight_run_raw.wrl"
Motions.justin_straight_run.reference_file="justin_straight_run_cart.wrl"
Motions.justin_straight_run.out_mot_file="justin_straight_run_raw.mot"
Motions.justin_straight_run.scale=0.01*2.54 -- change to METER unit system
Motions.justin_straight_run.rotation=quater(math.rad(-90), vector3(0,1,0))
*quater(math.rad(-90), vector3(1,0,0)) -- change to Y_up
Motions.justin_straight_run.name="justin_straight_run"

Motions.gymnist=deepCopyTable(Motions.default)
Motions.gymnist.skel_file="../Resource/motion/gymnist1.vsk"
Motions.gymnist.mot_files={
	"../Resource/motion/Gymnist/Project2/capture/matless_roundoff 1.V",
	"../Resource/motion/Gymnist/Project2/capture/matless_walk.V",
	"../Resource/motion/Gymnist/Project2/capture/matless_popa 1.V",
	"../Resource/motion/Gymnist/Project2/capture/matless_cartwheel_backhandspring 1.V",
	"../Resource/motion/Gymnist/Project2/capture/matless_backhandspring_stepout_backlayout 1.V",
	"../Resource/motion/matless_walk 1.V",
	"../Resource/motion/Gymnist/Project2/capture/matless_handstand 1.V",
	"../Resource/motion/Gymnist/Project2/capture/matless_switch_side_leap.V",
	--"../Resource/motion/Gymnist/Project 2/Capture day 1/Session 1/matless_cartwheel.V",
}
Motions.gymnist.scale=0.001 -- change from MILLIMETER to METER unit system
Motions.gymnist.createFolder="gymnist_sd"
Motions.gymnist.out_file="gymnist_sd/gymnist_raw.wrl" -- used only in MotToVRML.lua
Motions.gymnist.out_mot_file="gymnist_sd/gymnist_raw.mot" -- used only in MotToVRML.lua
Motions.gymnist.out_marker_file="gymnist_sd/gymnist.mrk" -- used only in MotToVRML.lua
Motions.gymnist.rotation=quater(math.rad(-90), vector3(0,1,0))
*quater(math.rad(-90), vector3(1,0,0)) -- change to Y_up
Motions.gymnist.name="gymnist" -- used only in MotToVRML.lua

Motions.gymnist_ROM=deepCopyTable(Motions.gymnist)
Motions.gymnist_ROM.mot_files={
	"../Resource/motion/Gymnist/Project 2/Capture day 1/Session 1/ROM.V",
}
Motions.gymnist_ROM.out_mot_file="gymnist_sd/gymnist_raw_ROM.mot" -- used only in MotToVRML.lua
Motions.gymnist_ROM.out_marker_file="gymnist_sd/gymnist_ROM.mrk" -- used only in MotToVRML.lua

--motion=Motions.locomotion
--motion=Motions.justin_straight_run
--motion=Motions.justin_runf3
--motion=Motions.gymnist
--motion=Motions.gymnist_ROM
--motion=Motions.justin_runf3_compare_rom
--motion=Motions.justin_run
--motion=Motions.boxer
motion=Motions[target]

function loadSkel(motion)
   printTable(motion.mot_files)
   local skel=MotionLoader.new(motion.skel_file, motion.mot_files)
   skel:removeAllRedundantBones()
   if motion.scale~=nill then 
      skel:scale(motion.scale)
   end
   return skel
end

function part1()
	skel=loadSkel(motion)
	if motion.rotation~=nil then
		skel=rotateSkeleton(skel,motion.rotation)
	end

	skel:insertSiteBones()

	mSkin=RE.createSkin(skel, PLDPrimSkin.POINT)
	mSkin:scale(100,100,100)
	mSkin:setThickness(2)
	RE.motionPanel():motionWin():addSkin(mSkin)
end

function part2_exportMOT()
	if motion.out_mot_file~=nil then
		local out_mot_file=out_path..motion.out_mot_file
		if util.isFileExist(out_mot_file) then
			if not Fltk.ask(out_mot_file.." exists. Do you want to overwrite it?") then
				util.msgBox("exporting canceled")
				return
			end
		end
		skel.mMotion:exportMot(out_mot_file)
		print('num bones: ',skel:numBone(), skel:numRotJoint(), skel:numTransJoint())
	end
end
function part3_exportWRL()
	if motion.createFolder then
		os.createDir(motion.createFolder)
	end
	local out_path=motion.out_path or "../Resource/motion/"
	local out_file=out_path..motion.out_file
	if util.isFileExist(out_file) and not Fltk.ask(out_file.." exists. Do you want to overwrite it?") then
		util.msgBox("exporting canceled")
	else
		MotionUtil.exportVRMLforRobotSimulation(skel.mMotion, out_file, motion.name)
	end

	mLoader=MainLib.VRMLloader(out_file)

	if motion.reference_file then
		-- copy meshes from reference skeleton (assuming that the identity poses are identical.)
		local refLoader=MainLib.VRMLloader("../Resource/scripts/ui/RigidBodyWin/"..motion.reference_file)

		mLoader:updateInitialBone()
		refLoader:updateInitialBone()

		local totalMass=0
		for i=1, mLoader:numBone()-1 do
			local bone=mLoader:VRMLbone(i)
			local refIndex=refLoader:getTreeIndexByName(bone:name())
			local refIndex_cart=refLoader:getTreeIndexByName(bone:name().."_cart")
			if refIndex==-1 then
				if i==1 then -- root name can be changed.
					refIndex=1
				end
			end

			if refIndex_cart~=-1 then
				refIndex=refIndex_cart
			end

			if refIndex~=-1 then
				local refBone=refLoader:VRMLbone(refIndex)

				bone:setChannels(bone:getTranslationalChannels(), "ZXY")
				bone:getMesh():assign(refBone:getMesh())
				totalMass=totalMass+refBone:mass()
			end

		end

		mLoader:setTotalMass(totalMass)

		local folder=string.sub(out_file, 1, -5).."_sd"
		os.createDir(folder)
		mLoader:export(out_file)
	end

	mSkin2=RE.createVRMLskin(mLoader, true)
	mSkin2:scale(100,100,100)	-- rendering is in centi-meter unit.
	mSkin2:setThickness(0.02)
end
function ctor()
	part1()
	part2_exportMOT()

	if motion.out_marker_file~=nil then
		if skel.markers then
			local markers=skel.markers:copy()
			if motion.scale then
				markers:rmult(motion.scale)
			end
			if motion.rotation then
				local np=markers:cols()/3
				local q=motion.rotation

				for i=0, markers:rows()-1 do
					for j=0, np-1 do
						local v=markers:row(i):toVector3(j*3)
						v:rotate(q)
						markers:row(i):setVec3(j*3, v)
					end
				end
			end

			require('RigidBodyWin/subRoutines/CompareChain')

			util.saveTable({globalMarkers=markers}, out_path..motion.out_marker_file)
		else
			print('Warning! exporting markers requested but cannot find them')
		end
	end


	part3_exportWRL() -- export wrl
end

function dtor()
   dbg.finalize()
   if mSkin~=nill then
      RE.remove(mSkin)
      mSkin=nil
   end
   
   if mSkin2~=nill then
      RE.remove(mSkin2)
      mSkin2=nil
   end
   collectgarbage()
end

function onCallback(w, userData)
end

function frameMove(fElapsedTime)
end

function rotateSkeleton(skel,rotation)
   skel:updateInitialBone()
   local pose=Pose()
   skel:getPose(pose)
   pose.rotations(0):leftMult(rotation)
   pose.translations(0):rotate(rotation)
   skel:setPose(pose)
   
   skel2=loadSkel(motion)
   
   for i=1, skel2:numBone()-1 do
      local offset=skel2:bone(i):getOffsetTransform()
      offset.translation:rotate(rotation)
      offset.rotation:assign(rotation*offset.rotation*rotation:inverse())
   end
   
   skel2:updateInitialBone()
   
   local poseTransfer=MotionUtil.PoseTransfer(skel, skel2, "", true)
   
   for i=0, skel.mMotion:numFrames()-1 do
      local srcpose=skel.mMotion:pose(i)
      local tgtpose=skel2.mMotion:pose(i)
      srcpose.rotations(0):leftMult(rotation)
      srcpose.translations(0):rotate(rotation)
      
      poseTransfer:setTargetSkeletonBothRotAndTrans(srcpose)
      skel2:getPose(tgtpose)
      
      if i==0 then
	 print(srcpose.rotations(0), tgtpose.rotations(0))
	 for kk=0,tgtpose:numTransJoint()-1 do
	    print(srcpose.translations(kk),tgtpose.translations(kk))
	 end
      end
   end      
   
   Skin1=RE.createSkin(skel)
   Skin1:setPose(pose,skel)
   Skin1:setTranslation(50,0,0)
   Skin1:scale(100,100,100)
   Skin1:setThickness(2)
   
   Skin2=RE.createSkin(skel2)
   Skin2:setTranslation(100,0,0)
   Skin2:scale(100,100,100)
   Skin2:setThickness(2)

   return skel2
end
