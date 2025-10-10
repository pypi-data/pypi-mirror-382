dofile("../Resource/scripts/ui/RigidBodyWin/common.lua")


max_numframe=300000
--max_numframe=30
target="justin_jump2"

conversionMethod_T={
   useJointPos=1, -- IK using only joint positions
   useAllLocalAxis=2, -- IK. use 3 markers for each joint.
   useJointAxis=3, -- IK. use 2 markers for each joint.
   useLocalOrientation=4 -- Forward kinematics. (all local axes of model and motion should match.)
}

-- to maintain a history of conversions
Motions={}
Motions.default={}
Motions.default.src_mot_files={}-- src_skel_file contains motions too.
Motions.default.conversionMethod=conversionMethod_T.useAllLocalAxis

Motions.locomotion=deepCopyTable(Motions.default)
Motions.locomotion.src_skel_file="../Resource/motion/locomotion_hyunwoo2/locomotion.mot"
Motions.locomotion.scale=0.01	-- change to METER unit system

Motions.woody=deepCopyTable(Motions.default)
Motions.woody.src_skel_file="../Resource/motion/woody/wd2_2foot_walk_turn2.bvh"
Motions.woody.scale=0.01	-- change to METER unit system

Motions.jump=deepCopyTable(Motions.default)
Motions.jump.src_skel_file="../Resource/scripts/ui/rigidbodywin/02.asf"
Motions.jump.src_mot_files={"../Resource/scripts/ui/rigidbodywin/02_04.amc"}
Motions.jump.scale=0.045	-- change to METER unit system

Motions.jump4=deepCopyTable(Motions.jump)
Motions.jump4.scale=0.045*173/146	-- change to METER unit system. taller than jump.

Motions.jump5=deepCopyTable(Motions.default)
Motions.jump5.src_skel_file="../Resource/scripts/ui/rigidbodywin/jump_raw.mot"

Motions.jump5_cart=deepCopyTable(Motions.jump5)
Motions.jump5_cart.src_skel_file="../Resource/scripts/ui/rigidbodywin/jump5.mot"
Motions.jump5_cart.conversionMethod=conversionMethod_T.useLocalOrientation

Motions.hyunwoo_real=deepCopyTable(Motions.default)
Motions.hyunwoo_real.src_skel_file="../Resource/motion/locomotion_hyunwoo2/locomotion.mot"
Motions.hyunwoo_real.scale=0.01	-- change to METER unit system
Motions.hyunwoo_real.conversionMethod=conversionMethod_T.useAllLocalAxis

-- the generation of *_cart.mot always depends on the ouput of *.mot
Motions.hyunwoo_real_cart=deepCopyTable(Motions.default)
Motions.hyunwoo_real_cart.src_skel_file="../Resource/scripts/ui/rigidbodywin/hyunwoo_real.mot"
Motions.hyunwoo_real_cart.conversionMethod=conversionMethod_T.useLocalOrientation

Motions.boxer=deepCopyTable(Motions.default)
Motions.boxer.src_skel_file="../Resource/motion/boxer/boxer.asf"
Motions.boxer.src_mot_files={"../Resource/motion/boxer/boxer.amc"}
Motions.boxer.scale=0.01	-- change to METER unit system

Motions.justin_jump=deepCopyTable(Motions.default)
Motions.justin_jump.src_skel_file="../Resource/scripts/ui/RigidBodyWin/justin_raw.mot"
Motions.justin_jump.conversionMethod=conversionMethod_T.useAllLocalAxis

Motions.justin_jump2=deepCopyTable(Motions.justin_jump)

Motions.justin_jump_cart=deepCopyTable(Motions.justin_jump)
Motions.justin_jump_cart.src_skel_file="../Resource/scripts/ui/rigidbodywin/justin_jump.mot"
Motions.justin_jump_cart.conversionMethod=conversionMethod_T.useLocalOrientation

model=model_files[target]-- defined in common.lua
motion=Motions[target]

-- output motion file name will be the same as the input model file!!!


function ctor()

   local skel1=MotionLoader.new(motion.src_skel_file, motion.src_mot_files)
   
   conversionMethod=	motion.conversionMethod
   if motion.scale~=nil then
      skel1:scale(motion.scale)
   end
   
   skel2=VRMLloader(model.file_name)
   skel2:updateInitialBone()
   
   local mot1=skel1.mMotion
   mot2=Motion(skel2)
   
   local numFrame2=math.min(max_numframe, mot1:numFrames())

   print(numFrame2)
   mot2:resize(numFrame2)
   
   local effectors=MotionUtil.Effectors()
   local effectorPos=vector3N()

   local jointName=vector()
   for i=0,skel1:numRotJoint()-1 do
      local nameId=skel1:getBoneByRotJointIndex(i).NameId;
      if skel2:getTreeIndexByName(nameId)~=-1 then
	 jointName:pushBack(nameId)
	 print(nameId)
      end
   end
   
   local countExistingJoint=jointName:size()
   if conversionMethod==conversionMethod_T.useJointPos then
      effectors:resize(countExistingJoint)
      effectorPos:resize(countExistingJoint)
      
      for i=0,countExistingJoint-1 do
	 effectors:at(i):init(skel2:getBoneByName(jointName(i)), vector3(0,0,0))
      end
      local iksolver=createIKsolver(skel2,effectors)
      
      for i=0,numFrame2-1 do
	 mot1:setSkeleton(i)
	 
	 for j=0,countExistingJoint-1 do
	    effectorPos:at(j):assign(skel1:getBoneByName(jointName(j)):getTranslation())
	 end
	 
	 print("ik"..i)
	 mot2:pose(i):identity()
	 mot2:pose(i).translations:at(0):assign(mot1:pose(i).translations:at(0))
	 mot2:pose(i).rotations:at(0):assign(mot1:pose(i).rotations:at(0))
	 
	 if i==0 then
	    iksolver:IKsolve(mot2:pose(i), effectorPos)
	 else	-- use previous frame as initial solution.
	    for j=1,mot2:pose(i):numRotJoint()-1 do
	       mot2:pose(i).rotations:at(j):assign(mot2:pose(i-1).rotations:at(j))
	    end
	    iksolver:IKsolve(mot2:pose(i), effectorPos)
	 end
      end
   elseif conversionMethod==conversionMethod_T.useAllLocalAxis  then
      local c=0
      for i=1, countExistingJoint-1 do
	 local bone=VRMLloader.upcast(skel2:getBoneByName(jointName(i)))
	 assert(bone~=nil)
	 if bone:childHead()==nil then
	    c=c+1
	 end
      end

      effectors:resize(countExistingJoint*3-3+3*c)	--excluding the root
      effectorPos:resize(countExistingJoint*3-3+3*c)
      local src_bones={}
      local c=0
      for i=1,countExistingJoint-1 do
	 local bone=VRMLloader.upcast(skel2:getBoneByName(jointName(i)))
	 assert(bone~=nil)
	 local srcbone=skel1:getBoneByName(jointName(i))

	 print("JOINT", bone, srcbone)
	 -- add joint marker
	 effectors:at(c):init(bone, vector3(0.02,0,0))
	 src_bones[c]=srcbone
	 c=c+1
	 effectors:at(c):init(bone, vector3(0,0.02,0))
	 src_bones[c]=srcbone
	 c=c+1
	 effectors:at(c):init(bone, vector3(0,0,0.02))
	 src_bones[c]=srcbone
	 c=c+1


	 if bone:childHead()==nil then
	    -- add SITE markers
	    local offset=bone:localCOM()
	    print("SITE", bone, srcbone, offset)

	    effectors:at(c):init(bone, vector3(0.02,0,0)+offset*2)
	    src_bones[c]=srcbone
	    c=c+1
	    effectors:at(c):init(bone, vector3(0,0.02,0)+offset*2)
	    src_bones[c]=srcbone
	    c=c+1
	    effectors:at(c):init(bone, vector3(0,0,0.02)+offset*2)
	    src_bones[c]=srcbone
	    c=c+1

	 end

      end
      
      local iksolver=createIKsolver(skel2,effectors)
      
      for i=0,numFrame2-1 do
	 mot1:setSkeleton(i)

	 for j=0, c-1 do
	    effectorPos:at(j):assign(
	       src_bones[j]:getFrame():toGlobalPos(
		  effectors(j).localpos))
	 end
	 
	 print("ik"..i)
	 mot2:pose(i):identity()
	 mot2:pose(i).translations:at(0):assign(mot1:pose(i).translations:at(0))
	 mot2:pose(i).rotations:at(0):assign(mot1:pose(i).rotations:at(0))
	 
	 if i==0 or mot1:isConstraint(i, FootstepDetection.IS_DISCONTINUOUS) then
	    iksolver:IKsolve(mot2:pose(i), effectorPos)
	    mot2:setConstraint(i, FootstepDetection.IS_DISCONTINUOUS, true)
	 else	-- use previous frame as initial solution.
	    for j=1,mot2:pose(i):numRotJoint()-1 do
	       mot2:pose(i).rotations:at(j):assign(mot2:pose(i-1).rotations:at(j))
	    end
	    iksolver:IKsolve(mot2:pose(i), effectorPos)
	 end
      end
   elseif conversionMethod==conversionMethod_T.useLocalOrientation then
      
      local existing_bones1={}
      local existing_bones2={}
      
      for i=0,countExistingJoint-1 do
	 existing_bones1[i]=skel1:getBoneByName(jointName(i))
	 existing_bones2[i]=skel2:getBoneByName(jointName(i))
      end
      
      for i=0, numFrame2-1 do
	 
	 skel1:setPose(mot1:pose(i))
	 
	 for j=0, countExistingJoint-1 do
	    existing_bones2[j]:getLocalFrame():assign(existing_bones1[j]:getLocalFrame())
	 end
	 
	 skel2:updateBone()				
	 skel2:getPose(mot2:pose(i))
      end
      
   else
      effectors:resize(countExistingJoint*2-2)
      effectorPos:resize(countExistingJoint*2-2)
      
      local c=0
      for i=1,countExistingJoint-1 do
	 local bone=skel2:getBoneByName(jointName(i))
	 effectors:at(c):init(bone, bone:axis(0)*0.02)	-- 2cm apart from joint center. for preserving yaw angles.
	 c=c+1
	 effectors:at(c):init(bone, bone:axis(0)*-0.02)
	 c=c+1
      end
      
      local iksolver=createIKsolver(skel2,effectors)
      
      for i=0,numFrame2-1 do
	 mot1:setSkeleton(i)
	 
	 local c=0
	 for j=1,countExistingJoint-1 do
	    local bone2=skel2:getBoneByName(jointName(j))
	    effectorPos:at(c):assign(skel1:getBoneByName(jointName(j)):getFrame():toGlobalPos(bone2:axis(0)*0.02))
	    c=c+1
	    effectorPos:at(c):assign(skel1:getBoneByName(jointName(j)):getFrame():toGlobalPos(bone2:axis(0)*-0.02))
	    c=c+1
	 end
	 
	 print("ik"..i)
	 mot2:pose(i):identity()
	 mot2:pose(i).translations:at(0):assign(mot1:pose(i).translations:at(0))
	 mot2:pose(i).rotations:at(0):assign(mot1:pose(i).rotations:at(0))
	 
	 if i==0 then
	    iksolver:IKsolve(mot2:pose(i), effectorPos)
	 else	-- use previous frame as initial solution.
	    for j=1,mot2:pose(i):numRotJoint()-1 do
	       mot2:pose(i).rotations:at(j):assign(mot2:pose(i-1).rotations:at(j))
	    end
	    iksolver:IKsolve(mot2:pose(i), effectorPos)
	 end
      end
      
   end
   
   local motFileName=str.left(model.file_name, -3).."mot"
   
   if util.isFileExist(motFileName) then
      if not Fltk.ask(motFileName.." exists. Do you want to overwrite it?") then
	 util.msgBox("exporting canceled")
      else
	 mot2:exportMot(motFileName)
      end
   else
      mot2:exportMot(motFileName)
   end
   
   mSkin1=RE.createSkin(mot1)
   mSkin1:scale(100,100,100)
   mSkin1:setThickness(1)

   RE.motionPanel():motionWin():addSkin(mSkin1)
   
   mSkin2=RE.createVRMLskin(skel2, true)
   mSkin2:scale(100,100,100)
   mSkin2:setThickness(0.02)
   mSkin2:applyAnim(mot2)
   mSkin2:startAnim()
   
   RE.motionPanel():motionWin():addSkin(mSkin2)

   createDebugSkin(mot1, vector3(50,0,0))
   createDebugSkin(mot2, vector3(100,0,0))

end

function createDebugSkin(mot, translation)
   local skin=RE.createSkin(mot, PLDPrimSkin.POINT)
   skin:scale(100,100,100)
   skin:setThickness(1)
   local skin2=RE.createSkin(mot, PLDPrimSkin.BOX)
   skin2:scale(100,100,100)
   skin2:setThickness(1)

   if translation~=nil then
      skin:setTranslation(translation.x, translation.y, translation.z)
      skin2:setTranslation(translation.x, translation.y, translation.z)
   end
   RE.connectSkin(skin)
   RE.connectSkin(skin2)
end

function dtor()
   dbg.finalize()
   RE.removeAllConnectedSkins()
   if RE.motionPanelValid() then RE.motionPanel():motionWin():detachAllSkin() end
   collectgarbage()
end

function onCallback(w, userData)
end

function frameMove(fElapsedTime)
end

function createIKsolver(skel, effectors)

-- return MotionUtil.createFullbodyIk_MultiTarget(skel, effectors)
   -- much faster with almost identical results
   return FullbodyIK_UTPoser(skel, effectors)
end

class 'FullbodyIK_UTPoser'
function FullbodyIK_UTPoser:__init(skel, effectors)
   self.skel=skel
   self.iksolver=MotionUtil.createFullbodyIkDOF_UTPoser(skel.dofInfo, effectors)
   self.tempPose=vectorn()
end

function FullbodyIK_UTPoser:IKsolve(pose_inout, effectorPos)
   self.skel.dofInfo:getDOF(pose_inout, self.tempPose)
   self.iksolver:IKsolve(self.tempPose, effectorPos)
   self.skel.dofInfo:setDOF(self.tempPose, pose_inout)
end
