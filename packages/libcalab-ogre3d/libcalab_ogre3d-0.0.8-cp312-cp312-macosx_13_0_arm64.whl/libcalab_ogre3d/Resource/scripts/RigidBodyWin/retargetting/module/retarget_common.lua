require('moduleIK')
local M={}
M.thesaurus={
	-- sorted in a decreasing priority
	HIPS={'pelvis', 'hips', 'root'},
	LEFTHIP= {'leftupleg', 'left.*hip', 'lhip', 'lfemur', 'thigh_l', 'left_hip'}, -- like a thesaurus.
	RIGHTHIP= {'rightupleg','right.*hip', 'rhip', 'rfemur', 'thigh_r','right_hip'},
	LEFTKNEE={'left.*knee', 'lknee', 'ltibia', 'calf_l', 'left_knee'},
	RIGHTKNEE={'right.*knee', 'rknee', 'rtibia', 'calf_r', 'right_knee'},
	LEFTANKLE={'left.*ankle', 'lankle','lfoot', 'foot_l' ,'left_ankle'},
	RIGHTANKLE={'right.*ankle', 'rankle', 'rfoot', 'foot_r', 'right_ankle'},
	LEFTSHOULDER= {'leftarm', 'left.*shoulder', 'lshoulder','lhumerus', 'upperarm_l', 'left_shoulder'},
	RIGHTSHOULDER= {'rightarm', 'right.*shoulder', 'rshoulder','rhumerus', 'upperarm_r','right_shoulder'},
	LEFTELBOW= {'leftforearm', 'left.*elbow', 'lelbow', 'lradius', 'lowerarm_l', 'left_elbow'},
	RIGHTELBOW= {'rightforearm', 'right.*elbow', 'relbow', 'rradius', 'lowerarm_r','right_elbow'},
	LEFTWRIST= {'left.*wrist', 'left.*hand', 'lwrist', 'lhand', 'hand_l'},
	RIGHTWRIST= {'right.*wrist',  'right.*hand','rwrist', 'rhand', 'hand_r'},
	LEFTCOLLAR={'leftcollar', 'lcollar', 'lclavicle', 'clavicle_l'},
	RIGHTCOLLAR={'rightcollar', 'rcollar', 'rclavicle', 'clavicle_r'},
	NECK={'neck', 'neck_01'},
}
M.fingersThesaurus={
	ThWrist={'Thumb1', 'thumb_01', 'thumb1'}, 
	ThMetac={'Thumb2', 'thumb_02', 'thumb2'}, -- Metacarpophalangeal joint of the right thumb
	ThIntra1={'Thumb3', 'thumb_03','thumb3'},
	F1Metac= {'Index1','index_01', 'index1'}, -- Metacarpophalangeal joint of the right index finger
	F1Intra1={'Index2','index_02', 'index2'}, 
	F1Intra2={'Index3','index_03', 'index3'} ,
	F2Metac= {'Middle1', 'middle_01','middle1'}, -- Metacarpophalangeal joint of the right middle finger 
	F2Intra1={'Middle2', 'middle_02', 'middle2'}, 
	F2Intra2={'Middle3', 'middle_03', 'middle3'}, 
	F3Metac= {'Ring1','ring_01','ring1'}, -- Metacarpophalangeal joint of the right ring finger
	F3Intra1={'Ring2','ring_02','ring2'}, 
	F3Intra2={'Ring3','ring_03','ring3'}, 
	F4Metac= {'Little1', 'Pinky1','pinky_01','pinky1'}, -- Metacarpophalangeal joint of the right pinky finger
	F4Intra1={'Little2', 'Pinky2','pinky_02','pinky2'}, 
	F4Intra2={'Little3', 'Pinky3','pinky_03','pinky3'}, 
}
for k, v in pairs(M.fingersThesaurus) do
	table.insert(v,k)
end

-- set vocaburaries of the root bone and four limbs. (spine, neck, head bones cannot be automatically detected.)
function M.setVoca(loader)
	for k, v in pairs(M.thesaurus) do
		local bone, msg=M.findBone(loader, v)
		if bone then
			if (msg) then
				io.write(msg ..' warning: ' )
			end
			print(k, bone)
			loader:_changeVoca(MotionLoader[k], loader:getBoneByName(bone))
		end
	end
	for ii, wristNames in ipairs({M.thesaurus.LEFTWRIST, M.thesaurus.RIGHTWRIST}) do
		local wrist=M.findBone(loader, wristNames)
		if wrist then
			local fingerNames=M.findBoneNames(loader, loader:getTreeIndexByName(wrist))
			for k, v in pairs(M.fingersThesaurus) do
				local bone=M.findBoneFrom(fingerNames, v)
				if bone then
					print(k, bone)
					if ii==1 then
						loader:_changeVoca(MotionLoader["L"..k], loader:getBoneByName(bone))
					else
						loader:_changeVoca(MotionLoader["R"..k], loader:getBoneByName(bone))
					end
				end
			end
		end
	end
end
function M.skelAtoIdentity()
	local y=mBindPoseA(1)
	motA.loader:updateInitialBone()
	motA.loader:getPoseDOF(mBindPoseA) -- lightgrey_transparent
	mBindPoseA:set(0,0) -- x pos
	mBindPoseA:set(1,y) -- x pos
	mBindPoseA:set(2,0) -- z pos

	motA.loader:setPoseDOF(mBindPoseA) -- lightgrey_transparent
	mBindPoseAquat=Pose()
	motA.loader:getPose(mBindPoseAquat)

	mSkinA:setPoseDOF(mBindPoseA) -- red_transparent

	setBoneSelectionPoseA(mBindPoseA)
	print("BindPoseA has been modified. Save retargetInfo to save the result.")
end
function M.skelBtoIdentity()
	local y=mBindPoseB(1)
	motB.loader:updateInitialBone()
	motB.loader:getPoseDOF(mBindPoseB) -- lightgrey_transparent
	mBindPoseB:set(0,0) -- x pos
	mBindPoseB:set(1,y) -- x pos
	mBindPoseB:set(2,0) -- z pos

	motB.loader:setPoseDOF(mBindPoseB) -- lightgrey_transparent
	mBindPoseBquat=Pose()
	motB.loader:getPose(mBindPoseBquat)

	mSkinB:setPoseDOF(mBindPoseB) -- red_transparent

	print("BindPoseB has been modified. Save retargetInfo to save the result.")
end
function M.skelAtoT()
	local prev=mBindPoseA:copy()
	motA.loader:setPoseDOF(mBindPoseA)
	M.setVoca(motA.loader)
	M.gotoTpose(motA.loader)

	mBindPoseAquat=Pose()
	motA.loader:getPose(mBindPoseAquat)
	motA.loader:getPoseDOF(mBindPoseA) -- lightgrey_transparent
	print(prev-mBindPoseA)

	if false then
		motA.skin:_setPoseDOF(mBindPoseA, motA.loader.dofInfo)
		mSkinA:_setPoseDOF(mBindPoseA, motA.loader.dofInfo) -- red_transparent
	else
		PLDPrimSkin.setPose(motA.skin,mBindPoseAquat, motA.loader)
		PLDPrimSkin.setPose(mSkinA,mBindPoseAquat, motA.loader)
	end
	setBoneSelectionPoseA(mBindPoseA)
	--mSkinA:setVisible(false)
	print("BindPoseA has been modified. Save retargetInfo to save the result.")
end

function M.setCorrespondences(loaderA, loaderB)
	M.setVoca(loaderA)
	M.setVoca(loaderB)

	local boneCorrespondences={}
	local function addSelected(boneA, boneB)
		local found=false
		for i, v in ipairs(boneCorrespondences) do
			if v[1]==boneA and v[2]==boneB then
				found=true
				break
			end
		end
		if not found then
			print(boneA, boneB)
			table.insert(boneCorrespondences, {boneA, boneB})
		end
	end
	for i=1, loaderA:numBone() -1 do
		local voca=loaderA:getVocaByTreeIndex(i) 
		if voca~=-1 then
			local tb=loaderB:getTreeIndexByVoca(voca) 
			if tb~=-1 then
				addSelected(loaderA:bone(i):name(), loaderB:bone(tb):name())
			end
		end
	end

	-- now let's try to match spine bones
	local neckA=loaderA:getTreeIndexByVoca(MotionLoader.NECK)
	local neckB=loaderB:getTreeIndexByVoca(MotionLoader.NECK)
	local pelvisA=loaderA:getTreeIndexByVoca(MotionLoader.HIPS)
	local pelvisB=loaderB:getTreeIndexByVoca(MotionLoader.HIPS)
	if neckA~=-1 and neckB~=-1 and pelvisA~=-1 and pelvisB~=-1 then

		local cA=0
		local cbone
		cbone=loaderA:bone(neckA)
		pelvisA=loaderA:bone(pelvisA)
		while cbone and cbone~=pelvisA do cbone=cbone:parent() cA=cA+1 end
		local cB=0
		cbone=loaderB:bone(neckB)
		pelvisB=loaderB:bone(pelvisB)
		while cbone and cbone~=pelvisB do cbone=cbone:parent() cB=cB+1 end

		if cA==2 then
			-- only one chest bone (in the middle)
			--
			-- 0      midB       cB
			local midB=math.round(cB/2)
			if (midB~=0 and midB~=cB) then
				local cB=0
				cbone=loaderB:bone(neckB)
				neckA=loaderA:bone(neckA)
				while cbone and cbone~=pelvisB do 
					cbone=cbone:parent() 
					cB=cB+1 
					if cB==midB then
						addSelected(neckA:parent():name(), cbone:name())
					end
				end
			end
		elseif cA>2 and cB>=cA then
			local delta=cB-cA
			-- two chest bones
			local cB=0
			cbone=loaderB:bone(neckB)
			cboneA=loaderA:bone(neckA)
			while cbone and cbone~=pelvisB do 
				cbone=cbone:parent() 
				if delta==0 then
					cboneA=cboneA:parent()
					addSelected(cboneA:name(), cbone:name())
				else
					delta=delta-1
				end
				cB=cB+1 
			end
		end
	end

	for i=1, loaderA:numBone()-1 do
		local boneA=loaderA:bone(i):name()
		local boneB=M.findBone(loaderB, {boneA})
		if boneB then
			addSelected(boneA, boneB)
		end
	end
	for i=1, loaderA:numBone()-1 do
		local voca=loaderA:bone(i):voca()
		
	end
	return boneCorrespondences
end

function M.checkCompleteness(la, boneCorrespondences)
	local out=''
	local c=0
	for i=1, la:numBone()-1 do
		local name=la:bone(i):name()
		if not boneCorrespondences[name] then
			out=out ..'Correspondence for bone '..name..' misssing!\n'
			c=c+1
		end
	end
	if c>0 then
		util.msgBox(out)
	else
		util.msgBox("Perfect!!!")
	end
end
function M.findBoneNames(loader, ibone)
	local bonenames={}
	if not ibone or ibone==1 then
		for i=1, loader:numBone()-1 do
			local bone=loader:bone(i)
			local bname=bone:name()
			bonenames[i]=bname
		end
	else
		local function addList(bonenames, bone)
			table.insert(bonenames, bone:name())
			if bone:childHead() then
				addList(bonenames, bone:childHead())
			end
			if bone:sibling() then
				addList(bonenames, bone:sibling())
			end
		end
		addList(bonenames, loader:bone(ibone))
	end
	return bonenames
end

function M.findBone(loader, substrings)
	local bonenames=M.findBoneNames(loader)
	return M.findBoneFrom(bonenames, substrings)
end
function M.findBoneFrom(boneNames, substrings)
	local function _findBone(boneNames, substring)
		local output={}
		for i, bname in ipairs(boneNames) do 
			if select(1, string.find(string.lower(bname), string.lower(substring))) then
				table.insert(output, bname)
			end
		end
		return output
	end

	local function _findBoneAuto(boneNames, substrings, prefix, postfix)
		local oneCount=0
		local resOne=nil
		for i,substring in ipairs(substrings) do

			local res
			if prefix then
				res=_findBone(boneNames, prefix..substring..postfix)
			else
				res=_findBone(boneNames, substring)
			end
			-- 결과가 한개 또는 0개여야 하고, 한개짜리는 유일해야함.
			if #res==1 then
				oneCount=oneCount+1
				resOne=res
				break
			elseif #res>1 then
				--printTable(res)
				oneCount=2
				resOne=res
				break
			end
		end
		if oneCount==1 then
			assert(#resOne==1)
			return resOne[1], nil
		elseif oneCount==0 then
			return nil, nil
		end
		return resOne, 'ambiguous'
	end
	local a,b=_findBoneAuto(boneNames, substrings)
	if b then
		-- reduce ambiguity, and try again
		a,b=_findBoneAuto(boneNames, substrings, '', '$')
		if b then
			-- further reduce ambiguity, and try again
			a,b=_findBoneAuto(boneNames, substrings,'^', '$')
			if b then
				if #a==1 then
					return a[1]
				end
				
				dbg.console()
				return a, b
			end
		end
	end
	return a
end
function M.saveRetargetInfo(A,B, mBindPoseA, mBindPoseB, sA, sB, mPrefix, mBindPoseAquat, mBindPoseBquat)
	local AA=deepCopyTable(A)
	local BB=deepCopyTable(B)
	if type(AA.motion)=='table' then
		AA.motion=nil
	end
	if type(BB.motion)=='table' then
		BB.motion=nil
	end
	AA.target=nil

	AA.skinScale=sA
	if AA.motion==AA.skel then
		AA.motion=nil
	end
	if AA.wrl=="__temp.wrl" then
		AA.wrl=nil
	end
	if AA.skel==AA.motion then
		AA.motion=nil
	end
	BB.skinScale=sB
	local out=
	"A="..table.toIndentedString(AA,0)
	.."B="..table.toIndentedString(BB,0)

	if mBindPoseAquat then
		--if not mBindPoseBquat then
		if true then
			-- always update!
			mBindPoseBquat=Pose()
			motB.loader:setPoseDOF(mBindPoseB)
			motB.loader:getPose(mBindPoseBquat)
		end
		out=out.."\nbindposes_quat="..table.tostring2({mBindPoseAquat, mBindPoseBquat})

		local genMap=M.generateBindPoseMap
		local mapA=genMap(motA.loader)
		local mapB=genMap(motB.loader)
		out=out.."\nbindposes_map="..table.tostring2({mapA,mapB})
	else
		out=out.."bindposes="..table.tostring2({mBindPoseA, mBindPoseB})
	end
	util.writeFile(mPrefix..".retargetConfig.lua", out)
	print("Saved to "..mPrefix..".retargetConfig.lua")
	return mPrefix..".retargetConfig.lua"
end
function M.saveRetargetInfo2(retargetConfig)
	local B=retargetConfig.B
	local A=retargetConfig.A

	local b=B.skel
	if b:sub(-4)=='.dat' then
		b=b:sub(1,-5)
	end
	if b:sub(-4)=='.fbx' then
		b=b:sub(1,-5)
	end
	local fn=A.skel:sub(1,-5)
	fn=os.processFileName(fn)
	local filename=b..'_'..fn..'.retargetConfig.lua'
	util.saveTableToLua(retargetConfig, filename)
	print("Saved to "..filename)
	return filename
end
function M.loadRetargetInfo(chosenFile)
	if chosenFile then
		local fno,msg=loadfile(chosenFile)
		if not fno then print(msg) return end
		local out=fno()
		if out and type(out)=='table' and out.A then
			A=out.A
			B=out.B
			bindposes_map=out.bindposes_map
			bindposes_quat=out.bindposes_quat
		end
	else
		return 
	end

	if not A or not B then
		print('incorrect config')
		return false
	end

	if type(B)=='string' then
		local fno,msg=loadfile(B)
		if not fno then print(msg) return end
		B=fno()
	end

	-- rectify
	--
	for i=1,#B.EE do
		local limb=B.EE[i]
		local localpos=limb[3]
		if type(localpos)=='string' then
			localpos=limb[4]
		end
		-- local pos here has to be vector3(0,0,0)
		localpos.x=0
		localpos.y=0
		localpos.z=0
	end

	M.updateBindPose()

	return true
end
function M.updateBindPose()
	if bindposes then
		mBindPoseA=vectorn.fromTable(bindposes[1])
		mBindPoseB=vectorn.fromTable(bindposes[2])
	end
	if bindposes_quat then
		mBindPoseAquat=Pose.fromTable(bindposes_quat[1])
		if bindposes_quat[2] then
			mBindPoseBquat=Pose.fromTable(bindposes_quat[2])
		else
			mBindPoseBquat=nil
		end

		if bindposes_map then
			mBindPosesMap=bindposes_map
		end
	end
end

-- doesn't modify the root joint
function M.setCurrentPoseAsIdentityPose(mLoader, _motionDOF)
	local bindPose=mLoader:pose()
	local y=bindPose.translations(0).y
	local orig_q=bindPose.rotations(0):copy()
	if _motionDOF then
		local origLoader=mLoader:copy()
		bindPose.translations:setAllValue(vector3(0))
		bindPose.rotations(0):identity()
		origLoader:setPose(bindPose)
		mLoader:setPose(bindPose)

		mLoader:setCurPoseAsInitialPose();
		local pt=MotionUtil.PoseTransfer2(origLoader, mLoader)
		--local pt=MotionUtil.PoseTransfer(origLoader, mLoader)

		for i=0, _motionDOF:rows()-1 do
			pt:setTargetSkeleton(_motionDOF:row(i))
			_motionDOF:row(i):assign(mLoader:getPoseDOF())
		end
	else
		bindPose.rotations(0):identity()
		mLoader:setPose(bindPose)
		mLoader:setCurPoseAsInitialPose();
	end	
	bindPose:identity()
	bindPose.translations(0).y=y
	bindPose.rotations(0):assign(orig_q)
	return bindPose
end

function M.exportCurrentPoseAsIdentityPose(mLoader, orig_filename)
	local copyL=MainLib.VRMLloader(mLoader)
	local pose=Pose()
	mLoader:getPose(pose)
	local fn=string.sub(orig_filename, 1, -5).."_T"
	RE.savePose(pose, fn.."0.pose")
	copyL:setPose(pose)
	copyL:setCurPoseAsInitialPose()

	local objFolder=fn.."_sd"
	print('creating '..objFolder..'. (An error message would be shown if the folder already exists. You can ignore it.)')
	os.createDir(objFolder)
	copyL:export(fn..'.wrl')

	if true then
		g_testSkel=MainLib.VRMLloader(fn..".wrl")
		g_skin=RE.createVRMLskin(g_testSkel, true)
		g_skin:setScale(100,100,100)
		g_skin:setTranslation(100,0,0)
		g_skin:setThickness(0.02)
	end
	local motdofc=MotionDOFcontainer(copyL.dofInfo)
	motdofc:resize(1)
	local I=transf()
	I:identity()
	motdofc.mot:row(0):setAllValue(0)
	MotionDOF.setRootTransformation(motdofc.mot:row(0), I)
	motdofc.mot:row(0):setVec3(0, pose.translations(0))
	motdofc:exportMot(fn..".dof")
end
--
-- assumes M.setVoca(mLoader) had been called.
function M.gotoTpose(mLoader, bExcludingFingers)
	local function rotate(v1, v2, tdir)
		if mLoader:getTreeIndexByVoca(v1)==-1 or mLoader:getTreeIndexByVoca(v2)==-1 then
			return 
		end

		local shdr=mLoader:getBoneByVoca(v1)
		local elbow=mLoader:getBoneByVoca(v2)
		local dir=elbow:getFrame().translation-shdr:getFrame().translation
		local q=quater()
		q:axisToAxis(dir, tdir)
		mLoader:rotateBoneGlobal(shdr, q)
	end
	local chains=
	{
		{vector3(1,0,0), MotionLoader.LEFTSHOULDER, MotionLoader.LEFTELBOW, MotionLoader.LEFTWRIST},
		{vector3(-1,0,0), MotionLoader.RIGHTSHOULDER, MotionLoader.RIGHTELBOW, MotionLoader.RIGHTWRIST},
		{vector3(0,-1,0),MotionLoader.LEFTHIP, MotionLoader.LEFTKNEE, MotionLoader.LEFTANKLE},
		{vector3(0,-1,0),MotionLoader.RIGHTHIP, MotionLoader.RIGHTKNEE, MotionLoader.RIGHTANKLE},
	}
	local function getAxis(ii)
		local out={}
		if ii==1 then
			out[1]=vector3(1,0,0)
		else
			out[1]=vector3(-1,0,0)
		end
		return out
	end
	for ic, chain in ipairs(chains) do
		local axis=chain[1]
		local n=#chain-2
		for i=1, n do
			rotate(chain[i+1], chain[i+2], axis)
		end
	end
	if bExcludingFingers then return end
	chains={}
	local mfinger={"ThWrist", "Metac", "Intra1","Intra2"}
	for ii, vv in ipairs({"L","R"}) do
		local f=2
		local out=getAxis(ii)
		local wrist={"LEFTWRIST", "RIGHTWRIST"}
		table.insert(out, MotionLoader[wrist[ii]])
		for i, v in ipairs (mfinger) do
			table.insert(out, MotionLoader[vv.."F"..tostring(f)..v])
		end
		table.insert(chains, out)
	end
	if true then
		local thumb={ "ThWrist", "ThMetac", "ThIntra1", }
		--local thumb={ "ThMetac", "ThIntra1", } -- it is better not to modify the ThWrist joints?
		-- thumb axis
		for ii, vv in ipairs({"L","R"}) do
			local out=getAxis(ii)
			for i, v in ipairs (thumb) do
				table.insert(out, MotionLoader[vv..v])
			end
			table.insert(chains, out)
		end
	end
	local finger={"Metac", "Intra1", "Intra2"}
	for f=1,4 do
		-- LF1Metac, LF1Intra1, LF1Intra2 ..
		for ii, vv in ipairs({"L","R"}) do
			local out=getAxis(ii)
			for i, v in ipairs (finger) do
				table.insert(out, MotionLoader[vv.."F"..tostring(f)..v])
			end
			table.insert(chains, out)
		end
	end
	for ic, chain in ipairs(chains) do
		local axis=chain[1]
		local n=#chain-2
		for i=1, n do
			rotate(chain[i+1], chain[i+2], axis)
		end
	end
end
function M.mirrorDOF(loader, motionDOF, lrootindices, rrootindices)
	local mMirrorMotion=Motion()
	local mMotion=Motion(motionDOF)
	if lrootindices then
		mMirrorMotion:mirrorMotion( mMotion, lrootindices, rrootindices)
	else
		self.setVoca(loader)
		MotionUtil.transpose(mMirrorMotion, mMotion)
	end
	local mMirrorDOF=MotionDOF(mLoader.dofInfo)
	mMirrorDOF:set(mMirrorMotion)
	return mMirrorDOF
end

-- loaderA has to be a vrmlloader.  
function M.fitSkeletonAtoB(loaderA, loaderB, boneCorrespondences, Bscale_over_Ascale)
	if not Bscale_over_Ascale then Bscale_over_Ascale =1 end
	local pose=Pose()
	loaderA:getPose(pose)

	local nameB=boneCorrespondences[loaderA:bone(1):name()]
	assert(nameB)
	local boneB=loaderB:getBoneByName(nameB)
	local rootposB= loaderB:fkSolver():globalFrame(boneB).translation*(Bscale_over_Ascale)

	pose.translations(0):assign(rootposB)
	loaderA:setPose(pose)

	local function matchJointPosAtoB(boneA)
		local nameB=boneCorrespondences[boneA:name()]
		if nameB then

			-- M3= T0*R0 + T1*R1 + T2*R2 * T3*R3

			local boneB=loaderB:getBoneByName(nameB)
			local gposB=loaderB:fkSolver():globalFrame(boneB).translation*(Bscale_over_Ascale)

			--dbg.timedDraw(5, 'Sphere', gposB*100, 'red')

			local gposA=loaderA:fkSolver():globalFrame(boneA).translation
			local errorPos=gposB-gposA

			local piq=boneA:parent():getLocalFrame().rotation:inverse()
			boneA:getOffsetTransform().translation:radd(piq*errorPos)
			boneA:setJointPosition(boneA:getOffsetTransform().translation)

			loaderA:fkSolver():init() -- necessary if offsets are changed
			loaderA:setPose(pose)

			--[[
			local gposA=loaderA:fkSolver():globalFrame(boneA).translation
			print('err ', boneA:name(), gposA:distance(gposB))
			dbg.timedDraw(5, 'Sphere', gposA*100, 'blue')
			]]
		end
	end
	--		local tc=m_pushLoc.bone:getOffsetTransform().translation
	--				mLoader:_updateMeshEntity()
	--				removeSkin()
	--				createSkin()
	--	end
	for i=2, loaderA:numBone()-1 do
		matchJointPosAtoB(loaderA:VRMLbone(i))
	end
end
function createBackup(filename, cut, postfix)
	if os.isFileExist(filename) then
		os.rename(filename, string.sub(filename, 1,cut)..postfix)
	end
end

function M.setAB(path)
	local chosenFileA=Fltk.chooseFile("Choose A (source motion)", path, "*.{wrl,bvh,mot,lua,asf}", false)

	if chosenFileA~="" then
		local chosenFileAmot
		local Aext=string.sub(chosenFileA,-4)
		if Aext==".bvh" or  Aext==".mot" or Aext==".lua" then
			chosenFileAmot=Aext
		elseif Aext=='.asf' then
			chosenFileAmot=Fltk.chooseFile("Choose A", path, "*.amc", false)
		else
			chosenFileAmot=Fltk.chooseFile("Choose A", path, "*.dof", false)
		end
		if chosenFileAmot then
			local chosenFileB=Fltk.chooseFile("Choose B (target skeleton)", path, "*.{dat,fbx,wrl,bvh,mot,lua,mesh}", false)
			if chosenFileB then
				A={}
				A.wrl=chosenFileA
				if chosenFileAmot =='.bvh' then
					A.skel=A.wrl
					A.wrl=nil
				elseif chosenFileAmot=='.amc' then
					A.skel=A.wrl
					A.wrl=nil
				elseif chosenFileAmot =='.mot' then
					A.skel=A.wrl
					A.wrl=nil
				elseif chosenFileAmot =='.lua' then
					-- assuming modifyModel/*.lua
					function Start(skel, mot)
						g_res={wrl=skel, motion=mot}
					end
					dofile(chosenFileA)
					A.skinScale=skinScale or 100
					if not g_res then return end
					A.wrl=g_res.wrl
					A.motion=g_res.motion
					skinScale=nil
					g_res=nil
				else
					A.motion=chosenFileAmot
				end
				A.reusePreviousBinding=true
				A.boneCorrespondences={}
				if not A.skinScale then
					A.skinScale=100
				end

				if string.sub(chosenFileB, -4)==".lua" then
					-- assuming modifyModel/*.lua
					function Start(skel, mot)
						g_res={wrl=skel, motion=mot}
					end
					dofile(chosenFileB)
					B=g_res
					B.skel=B.wrl
					B.wrl=nil
					B.skinScale=skinScale or 100
					skinScale=nil
					B.EE={}

					g_res=nil
				elseif string.sub(chosenFileB, -4)==".bvh"  or string.sub(chosenFileB, -4)==".mot"  then
					local tmploader=RE.createMotionLoaderExt(chosenFileB)
					MotionUtil.exportVRMLforRobotSimulation(tmploader.mMotion, chosenFileB..'.wrl', chosenFileB, 0.02)
					B={}
					B.skel=chosenFileB..'.wrl'
					B.skinScale=100
					B.motion=chosenFileB
					B.EE={}
				elseif string.sub(chosenFileB, -5)=='.mesh' then
					print("Loading a bind pose. bind pose can be exported from configSkin.lua")
					local chosenFileBmot=Fltk.chooseFile("Choose bindpose for B", path, "*.pose", false)
					
					local meshFile=os.filename(chosenFileB)
					local tempEntity=RE.ogreSceneManager():createEntity('entity', meshFile)
					assert(tempEntity)
					local skinScale=100
					require('subRoutines/exportOgreEntityToVRML')
					local sf, offset=exportOgreEntityToVRML(tempEntity, meshFile..'.wrl', 'entity', 1/skinScale)
					local s=skinScale*sf
					B={}
					B.skel=meshFile..'.wrl'
					B.skinScale=s
					B.motion=chosenFileBmot
					B.EE={}
				else
					local chosenFileBmot=Fltk.chooseFile("Choose B motion (optional)", path, "*.dof", false)
					if chosenFileBmot then
						B={}
						B.skel=chosenFileB
						B.skinScale=100
						B.motion=chosenFileBmot
						B.EE={}
					else 
						B={}
						B.skel=chosenFileB
						B.skinScale=100
						B.EE={}
					end
				end
				local out=
				"A="..table.toIndentedString(A,0)
				.."B="..table.toIndentedString(B,0)
				util.writeFile("temp.retargetConfig.lua", out)
				print("Saved to temp.retargetConfig.lua")
			else
				return  false
			end
		else
			return  false
		end
	else
		return  false
	end
	return true
end

function M.createAngleRetarget(loaderA, loaderB, retargetConfig, _options)
	if not _options then
		_options={}
	end
	if retargetConfig.A then
		-- a retargetConfig generated from correspondenceTools_GUI.lua (which can also be used for models with fingers)

		local RET=require("retargetting/module/retarget_common")
		--RET.saveRetargetInfo2(retargetConfig) -- you can see the manual adjustment using correspondenceTools_GUI.lua

		retargetConfig.A.mot={
			loader=loaderA
		}
		retargetConfig.B.mot={
			loader=loaderB
		}

		local ret=RET.AngleRetarget(retargetConfig, _options)
		return ret
	else
		local boneCorrespondences=retargetConfig
		local config={
			A={
				mot={loader=loaderA},
				boneCorrespondences=boneCorrespondences,
				skinScale=100
			},
			B={
				mot={loader=loaderB},
				skinScale=100
			},
			bindposes_quat=
			{
				loaderA:pose(),
				loaderB:pose(),
			}
		}
		return M.AngleRetarget(config, _options)
	end
end

M.AngleRetarget=LUAclass()
M.AngleRetarget.loadRetargetInfo=M.loadRetargetInfo

-- from a .retargetConfigFile or  a config table
-- exampleConfig: 
-- {
-- 	A={
-- 		boneCorrespondences ={
-- 			Hips ="Hips",
-- 			LeftArm ="LeftShoulder",
-- 			LeftFoot ="LeftAnkle",
-- 			LeftForeArm ="LeftElbow",
-- 			LeftLeg ="LeftKnee",
-- 			LeftUpLeg ="LeftHip",
-- 			RightArm ="RightShoulder",
-- 			RightFoot ="RightAnkle",
-- 			RightForeArm ="RightElbow",
-- 			RightLeg ="RightKnee",
-- 			RightUpLeg ="RightHip",
-- 			Spine2 ="Chest",
-- 		},
-- 		reusePreviousBinding =true,
-- 		skel =getScriptPath().."dance2_subject5.bvh", 
-- 		skinScale =1.06,
-- 	},
-- 	B={
-- 		EE ={
-- 		},
-- 		motion ="",
-- 		skel ="../Resource/motion/locomotion_hyunwoo/hyunwoo_lowdof_T_boxfoot.wrl",
-- 		skinScale =100,
-- 	},
-- 	bindposes_quat={{"__userdata", "Pose", {"__userdata", "matrixn", {{0, 91.952423095703, 0, }, }, }, {"__userdata", "matrixn", {{0.49471335851256, 0.50849879746583, 0.5107022541274, 0.48566539254329, }, {-0.030921042674351, 0.04093840436468, 0.99675515661669, 0.062024945997903, }, {0.98998108908309, 0.02100641027623, 0.0050385331189368, -0.13953776252034, }, {0.78730601149623, -0.0039216476318909, -0.028760364971441, 0.61587880816639, }, {0.98252429143285, -5.027298625617e-06, 2.653696972655e-05, 0.18613440309328, }, {-0.019370904521322, -0.019734486782251, -0.9992130681072, 0.028435235417865, }, {0.98953989105114, 0.058604296360864, 0.02929970155415, -0.12852185788957, }, {0.77663131175655, 0.040508935605643, -0.0095967421389106, 0.62857834378518, }, {0.98252428523579, 4.9084334345615e-06, -2.6612779742249e-05, 0.18613443579729, }, {0.99885002925113, 0.0033569040264288, 0.0022670938826147, 0.04777248732998, }, {0.99993369893565, 0.006905781625972, 0.0041971503210924, 0.0082031604994332, }, {0.99995262433083, 0.0068906881210288, 0.0042202488003454, 0.00542743136044, }, {0.99820635153277, -0.021612318648645, 0.055000871941074, 0.0095860068847009, }, {0.98405233135652, 0.012846654950911, -0.12248558364735, 0.12834817648464, }, {0.017594494239767, -0.72186102291223, 0.04599504160083, -0.69028367612214, }, {0.98665608636692, -0.12759172252809, 0.038924106987672, -0.093354343619567, }, {0.99336747965295, -0.00034619021280752, -0.090945213220547, -0.070355516575169, }, {0.98113626216282, 0.15700923294504, 0.031159367873505, 0.10839201830809, }, {0.044001922735477, 0.71344019035453, -0.076261643727075, -0.69516263368979, }, {0.98760963531755, 0.13651948673487, -0.07417725737947, -0.022076513702037, }, {0.98236457326264, 0.0084927330352776, 0.13353177212055, -0.13060239093695, }, {0.98745569306081, -0.074180813279323, 0.08256719651283, 0.11229923972598, }, }, }, }, {"__userdata", "Pose", {"__userdata", "matrixn", {{0, 1, 0, }, }, }, {"__userdata", "matrixn", {{1, 0, 0, 0, }, {0.99689309691451, -0.06408175298272, 0.0072559846202422, 0.045222040489695, }, {0.98528361348621, 0.17092747291048, -1.3010426069826e-18, -6.505213034913e-18, }, {0.99344803700071, 0.092600233445518, -0.066689976428937, 0.0062162359336277, }, {0.9963536325769, -0.074718886530784, -0.019730554928026, -0.036155664129422, }, {0.98617489663248, 0.16570779478321, 4.336808689942e-19, 4.336808689942e-19, }, {0.99382460173343, 0.11096050254694, 0.00065007381492202, -7.2580732123696e-05, }, {1, 0, 0, 0, }, {0.99730957042138, -0.053757066469303, -0.041768188509835, 0.027188544998759, }, {0.99886447755088, 2.6020852139652e-18, -0.047641950915299, -4.336808689942e-19, }, {0.99976113895118, -0.016367338394975, -0.0037839542209537, -0.01398059252515, }, {0.99775346413329, 4.336808689942e-19, 0.066992722067579, 1.1045309632196e-18, }, {1, 0, 0, 0, }, }, }, }, },
-- 	bindposes_map={{['R']={['LeftFoot']=3, ['Hips']=0, ['LeftToe']=4, ['RightHand']=21, ['Spine']=9, ['Spine2']=11, ['Spine1']=10, ['RightShoulder']=18, ['RightFoot']=7, ['RightArm']=19, ['RightUpLeg']=5, ['Head']=13, ['LeftUpLeg']=1, ['RightForeArm']=20, ['LeftForeArm']=16, ['RightToe']=8, ['LeftHand']=17, ['LeftArm']=15, ['Neck']=12, ['LeftShoulder']=14, ['RightLeg']=6, ['LeftLeg']=2, }, ['T']={['Hips']=0, }, }, {['R']={['RightKnee']=5, ['Hips']=0, ['Neck']=12, ['RightElbow']=11, ['LeftHip']=1, ['Chest']=7, ['LeftKnee']=2, ['RightHip']=4, ['RightShoulder']=10, ['RightAnkle']=6, ['LeftElbow']=9, ['LeftShoulder']=8, ['LeftAnkle']=3, }, ['T']={['Hips']=0, }, }, },
-- }
-- (and optionally, to retarget from memory, set A.mot and B.mot as follows) 
-- retargetConfig.A.mot={ loader=loaderA, }
-- retargetConfig.B.mot={ loader=loaderB, }
function M.AngleRetarget:__init(chosenFile, options)
	self.options=options or {}
	if type(chosenFile)=='string' then
		local backupA=A
		local backupB=B
		-- backup
		local bindposes={
			mBindPoseA,
			mBindPoseB,
			mBindPoseAquat,
			mBindPoseBquat
		}
		self.loadRetargetInfo(chosenFile)
		self.bindposes={
			mBindPoseA,
			mBindPoseB,
			mBindPoseAquat,
			mBindPoseBquat
		}
		self.A=A
		self.B=B
		
		-- recover global variables
		A=backupA
		B=backupB
		mBindPoseA=bindposes[1]
		mBindPoseB=bindposes[2]
		mBindPoseAquat=bindposes[3]
		mBindPoseBquat=bindposes[4]
	else
		local config=chosenFile
		self.A=config.A
		self.B=config.B
		local bp=util.convertFromLuaNativeTable(config.bindposes_quat)
		self.bindposes={
			nil, nil,
			bp[1], bp[2]
		}
		self.bindposes_map=config.bindposes_map
	end
	local A=self.A
	local B=self.B
	local mBindPoseA=self.bindposes[1]
	local mBindPoseB=self.bindposes[2]
	
	--load B
	if B.mot and type(B.mot)=='table' then
		self.motB=B.mot
	else
		self.motB=loadMotion(B.skel, B.motion, B.skinScale)
	end
	local function removeFixed(mLoader)
		for i=1, mLoader:numBone()-1 do
			if mLoader:bone(i):numChannels()==0 then
				mLoader:removeAllRedundantBones()
				--mLoader:removeBone(mLoader:VRMLbone(i))
				--mLoader:export(config[1]..'_removed_fixed.wrl')
				break
			end
		end
		mLoader:_initDOFinfo()
	end
	removeFixed(self.motB.loader)
	if A.mot and type(A.mot)=='table' then
		self.motA=A.mot
	else
		self.motA=loadMotion(A.wrl or A.skel, A.motion)
	end

	do
		local decodeBindPose=M.decodeBindPose
		if self.bindposes_map then
			local bp=self.bindposes
			bp[3]=decodeBindPose(self.motA.loader, bp[3], self.bindposes_map[1])

			if bp[4] and self.bindposes_map[2] then
				bp[4]=decodeBindPose(self.motB.loader, bp[4], self.bindposes_map[2])
			end
		end
	end

	local mBindPoseAquat=self.bindposes[3]
	local mBindPoseBquat=self.bindposes[4]

	local motA=self.motA
	local motB=self.motB
	if A.boneCorrespondencesAtoB then
		A.boneCorrespondences=A.boneCorrespondencesAtoB
	end
	if A.boneCorrespondencesBtoA and not A.boneCorrespondences then
		A.boneCorrespondences={}
		for k, v in pairs(A.boneCorrespondencesBtoA) do
			A.boneCorrespondences[v]=k
		end
	end
	if not A.boneCorrespondences then

		A.boneCorrespondences={}

		for i=1,motA.loader:numBone()-1 do
			local k=motA.loader:bone(i):name()
			print(k)
			A.boneCorrespondences[k]=k
		end
	end
	if not A.wrl then
		A.wrl="__temp.wrl"
		--local fn= os.filename(A.skel)
		--MotionUtil.exportVRMLforRobotSimulation( motA.loader, A.wrl, fn, 1/A.skinScale)
	end

	local out=M.getConversionTable(motA.loader, motB.loader, A.boneCorrespondences)
	local convInfoA=out[1]
	local convInfoB=out[2]
	local posScaleFactor=B.skinScale/A.skinScale
	assert(convInfoA:size()>0)

	if mBindPoseA then
		motA.loader:setPoseDOF(mBindPoseA)
		motB.loader:setPoseDOF(mBindPoseB)
	else
		assert(mBindPoseAquat)
	end
	if mBindPoseAquat then
		-- 바인드 자세 설정
		motA.loader:setPose(mBindPoseAquat)
		motB.loader:setPose(mBindPoseBquat)
	end

	if false then
		debugSkinA= RE.createSkin(motA.loader, true)
		debugSkinA:setScale(100,100,100)
		debugSkinA:setTranslation(150,0,0)
		debugSkinA:setThickness(0.02)
		debugSkinA:_setPose(mBindPoseAquat, motA.loader)
		debugSkinA:setMaterial('lightgrey_transparent')
		debugSkinB= RE.createSkin(motB.loader, true)
		debugSkinB:setScale(100,100,100)
		debugSkinB:setTranslation(150,0,0)
		debugSkinB:setThickness(0.02)
		debugSkinB:_setPose(mBindPoseBquat, motB.loader)
		debugSkinB:setMaterial('lightgrey_transparent')
	end

	M.setVoca(motB.loader)
	local tiLknee=motB.loader:getTreeIndexByVoca(MotionLoader.LEFTKNEE)

	local use1Dknees=false
	if tiLknee~=-1 and motB.loader.dofInfo:numDOF(tiLknee)==1 and 
		motB.loader:getBoneByVoca(MotionLoader.LEFTKNEE) then
		use1Dknees={}
		local treeIndicesShoulder=intvectorn(4)
		treeIndicesShoulder:set(0, motB.loader:getTreeIndexByVoca(MotionLoader.LEFTSHOULDER))
		treeIndicesShoulder:set(1, motB.loader:getTreeIndexByVoca(MotionLoader.RIGHTSHOULDER))
		treeIndicesShoulder:set(2, motB.loader:getTreeIndexByVoca(MotionLoader.LEFTHIP))
		treeIndicesShoulder:set(3, motB.loader:getTreeIndexByVoca(MotionLoader.RIGHTHIP))
		local treeIndicesElbow=intvectorn(4)
		treeIndicesElbow:set(0, motB.loader:getTreeIndexByVoca(MotionLoader.LEFTELBOW))
		treeIndicesElbow:set(1, motB.loader:getTreeIndexByVoca(MotionLoader.RIGHTELBOW))
		treeIndicesElbow:set(2, motB.loader:getTreeIndexByVoca(MotionLoader.LEFTKNEE))
		treeIndicesElbow:set(3, motB.loader:getTreeIndexByVoca(MotionLoader.RIGHTKNEE))
		local treeIndicesWrist=intvectorn(4)
		treeIndicesWrist:set(0, motB.loader:getTreeIndexByVoca(MotionLoader.LEFTWRIST))
		treeIndicesWrist:set(1, motB.loader:getTreeIndexByVoca(MotionLoader.RIGHTWRIST))
		treeIndicesWrist:set(2, motB.loader:getTreeIndexByVoca(MotionLoader.LEFTANKLE))
		treeIndicesWrist:set(3, motB.loader:getTreeIndexByVoca(MotionLoader.RIGHTANKLE))
		local fi=treeIndicesWrist:findFirstIndex(-1)
		if fi==0 then
			-- has no wrist
			treeIndicesShoulder=treeIndicesShoulder:range(2,4):copy()
			treeIndicesElbow=treeIndicesElbow:range(2,4):copy()
			treeIndicesWrist=treeIndicesWrist:range(2,4):copy()
		end
		assert(treeIndicesShoulder:findFirstIndex(-1)==-1)
		assert(treeIndicesElbow:findFirstIndex(-1)==-1)
		assert(treeIndicesWrist:findFirstIndex(-1)==-1)
		use1Dknees={treeIndicesShoulder, treeIndicesElbow, treeIndicesWrist}
	end
	self.use1Dknees=use1Dknees


	self.convInfo={convInfoA, convInfoB}
	local pt=MotionUtil.PoseTransfer2(motA.loader, motB.loader,  convInfoA, convInfoB, posScaleFactor)
	self.pt=pt
	--[[
	local motionA=Motion(motA.motionDOFcontainer.mot) -- MotionDOF를 Motion으로 conversion
	local motionB=Motion(motB.motionDOFcontainer.mot)

	-- solve ik for a few frames
	local startFrame=0
	local endFrame=motionA:numFrames()-1

	motionB:resize( endFrame+1)
	for i=startFrame, endFrame do
		pt:setTargetSkeleton(motionA:pose(i))
		motB.loader:getPose(motionB:pose(i))

		-- 아래줄은 PoseTransfer를 쓰는경우만 필요함. PoseTransfer2는 기능 내장.
		--motionB:pose(i).translations(0):scale(1/posScaleFactor)
	end
	g_motionB=motionB
	--motB.skin:applyAnim(g_motionB)

	-- 아래는 만들어진 Motion을 MotionDOF로 convert back하는 코드 (kist과제랑은 관련 없음)
	local motdofB=motB.motionDOFcontainer.mot
	motdofB:resize(motionB:numFrames())
	if use1Dknees then
		motdofB:set(motionB, use1Dknees[1], use1Dknees[2], use1Dknees[3])
	else
		motdofB:set(motionB)
	end
	self.motionB=motionB
	]]--


	self.matched=matchedB
end

function M.getIndexMap(loaderA, loaderB, boneCorrespondences)
	local treeIndexAfromB={}
	local treeIndexBfromA={}

	local matchedA=boolN(loaderA:numBone())
	local matchedB=boolN(loaderB:numBone())
	for k,v in pairs(boneCorrespondences) do
		local i=loaderB:getTreeIndexByName( v)
		if(i==-1) then
			print('motB ('..B.skel..'): '..v..'?')
		end
		local j=loaderA:getTreeIndexByName(k)
		if(j==-1) then
			print('motA ('..A.wrl..'): '..k..'?')
		end
		treeIndexAfromB[i]=j
		treeIndexBfromA[j]=i
		matchedA:set(j, true)
		matchedB:set(i, true)
	end
	return { toA=treeIndexAfromB, toB=treeIndexBfromA, matched={matchedA, matchedB}}
end
function M.getConversionTable(loaderA, loaderB, boneCorrespondences)
	local treeIndexAfromB={}
	local treeIndexBfromA={}

	local convFile={}
	local convInfoA=TStrings()
	local convInfoB=TStrings()
	local matchedA=boolN(loaderA:numBone())
	local matchedB=boolN(loaderB:numBone())
	for k,v in pairs(boneCorrespondences) do
		local i=loaderB:getTreeIndexByName( v)
		if(i==-1) then
			print('motB : '..v..'?')
		end
		local j=loaderA:getTreeIndexByName(k)
		if(j==-1) then
			print('motA : '..k..'?')
		end

		if i~=-1 and j~=-1 then
			treeIndexAfromB[i]=j
			treeIndexBfromA[j]=i
			matchedA:set(j, true)
			matchedB:set(i, true)
			table.insert(convFile, v..'\t'..k)
			convInfoA:pushBack(k)
			convInfoB:pushBack(v)
		end
	end

	local function countUnmatchedParent(loader, i, matched)
		local count=0
		local bone=loader:bone(i):parent()
		while bone:treeIndex()>=1 do
			if not matched(bone:treeIndex()) then
				count=count+1
			else
				break
			end
			bone=bone:parent()
		end
		return count
	end
	for i=2, loaderA:numBone()-1 do
		local pi=loaderA:bone(i):parent():treeIndex() 
		if matchedA(i)  and not matchedA(pi) then
			local ca=countUnmatchedParent(loaderA, i, matchedA)
			local j=treeIndexBfromA[i]
			local cb=countUnmatchedParent(loaderB, j, matchedB)

			if ca==cb then
				local boneA=loaderA:bone(i):parent()
				local boneB=loaderB:bone(j):parent()
				for k=1, ca do
					matchedA:set(boneA:treeIndex(), true)
					matchedB:set(boneB:treeIndex(), true)
					print('autoAdd', boneA:name(), boneB:name())
					convInfoA:pushBack(boneA:name())
					convInfoB:pushBack(boneB:name())
					boneA=boneA:parent()
					boneB=boneB:parent()
				end
			end
		end
	end
	return { convInfoA, convInfoB, toA=treeIndexAfromB, toB=treeIndexBfromA, matched={matchedA, matchedB}}
end
function M.createPoseTransfer(loaderA, loaderB, boneCorrespondences, posScaleFactor)
	local tbl=M.getConversionTable(loaderA, loaderB, boneCorrespondences)
	local pt=MotionUtil.PoseTransfer2(loaderA, loaderB,  tbl[1], tbl[2], posScaleFactor)
	return pt, tbl
end

function M.autoFillCorrespondences(loaderA, loaderB, boneCorrespondences,indexMap)
	local function countUnmatchedParent(loader, i, matched)
		local count=0
		local bone=loader:bone(i):parent()
		while bone:treeIndex()>=1 do
			if not matched(bone:treeIndex()) then
				count=count+1
			else
				break
			end
			bone=bone:parent()
		end
		return count
	end

	local matchedA, matchedB=unpack(indexMap.matched)

	for i=2, loaderA:numBone()-1 do
		local pi=loaderA:bone(i):parent():treeIndex() 
		if matchedA(i)  and not matchedA(pi) then
			local ca=countUnmatchedParent(loaderA, i, matchedA)
			local j=indexMap.toB[i]
			local cb=countUnmatchedParent(loaderB, j, matchedB)

			if ca==cb then
				local boneA=loaderA:bone(i):parent()
				local boneB=loaderB:bone(j):parent()
				for k=1, ca do
					indexMap.toA[boneB:treeIndex()]=boneA:treeIndex()
					indexMap.toB[boneA:treeIndex()]=boneB:treeIndex()
					matchedA:set(boneA:treeIndex(), true)
					matchedB:set(boneB:treeIndex(), true)
					print('autoAdd', boneA:name(), boneB:name())
					boneCorrespondences[boneA:name()]=boneB:name()
					boneA=boneA:parent()
					boneB=boneB:parent()
				end
			end
		end
	end
end
function M.rotateBoneDir(mLoader, shdr, elbow, tdir)
	local dir=elbow:getFrame().translation-shdr:getFrame().translation
	local q=quater()
	q:axisToAxis(dir, tdir)
	mLoader:rotateBoneGlobal(shdr, q)
end

-- exampel rootBoneA : loader:getBoneByName('LeftArm')
function M.alignBoneDirections(loaderA, loaderB, rootBoneA, indexMap, ignoreSiteBones, maxDepth)
	local rotateDir=M.rotateBoneDir

	local bone=rootBoneA

	local function align(bone, maxDepth)
		local depth=1
		while bone do
			if maxDepth and depth>maxDepth then
				break
			end
			local nc=bone:numChildren()
			if nc==1 then
				local child1=bone:childHead()
				local tdir=child1:getFrame().translation-bone:getFrame().translation

				local indexB=indexMap.toB[child1:treeIndex()]
				if not indexB then
					if not ignoreSiteBones then
						--print(child1:name())
						assert(child1:numChannels()==0)
						local indexB=indexMap.toB[child1:parent():treeIndex()]
						local pchild2=loaderB:bone(indexB)

						local q=quater()
						local dir=pchild2:getFrame().translation-pchild2:parent():getFrame().translation
						q:axisToAxis(dir, tdir)
						loaderB:rotateBoneGlobal(pchild2,q)
					end
				else
					local child2=loaderB:bone(indexB)
					--print(child1:name(), child2:name())

					assert(indexMap.toA[child2:parent():treeIndex()]==bone:treeIndex())
					rotateDir(loaderB, child2:parent(), child2, tdir)
				end
				bone=bone:childHead()
			elseif nc>1 then
				local bone2=bone:childHead()
				while bone2 do
					align(bone2)
					bone2=bone2:sibling()
				end
				break
			else
				break
			end
			depth=depth+1
		end
	end
	align(bone, maxDepth)
end
function M.AngleRetarget:convertDOF(pose)

	local motB=self.motB
	self.pt:setTargetSkeleton(pose)
	local motionB=Motion(self.motB.loader)
	motionB:resize(1)
	motB.loader:getPose(motionB:pose(0))

	local use1Dknees=self.use1Dknees
	local motdofB=MotionDOF(self.motB.loader.dofInfo)
	motdofB:resize(1)
	if use1Dknees then
		motdofB:set(motionB, use1Dknees[1], use1Dknees[2], use1Dknees[3])
	else
		motdofB:set(motionB)
	end
	return motdofB:row(0):copy()
end
function M.AngleRetarget:__call(PoseA)
	return self:convertPose(PoseA)
end
function M.AngleRetarget:convertPose(poseA)
	local poseB=Pose(self.motB.loader)
	self:_convertPose(poseA, poseB)
	return poseB
end
function M.AngleRetarget:_convertPose(poseA, poseB)
	local motB=self.motB
	self.pt:setTargetSkeleton(poseA)
	motB.loader:getPose(poseB)
	local o=self.options
	if o.interpolateMissingBones then
		local l=motB.loader
		for i=2, l:numBone()-1 do 
			local pi=l:bone(i):parent():treeIndex()
			if not self.matched(i) and self.matched(pi) then
				assert(pi~=1)
				local ppi=l:bone(pi):parent():treeIndex()
				local qpp=l:bone(ppi):getFrame().rotation
				local q=l:bone(i):getFrame().rotation

				-- qpp * delta =q
				local delta=qpp:inverse()*q
				delta:scale(0.5)

				l:bone(pi):getLocalFrame().rotation:assign(delta)
				l:bone(i):getLocalFrame().rotation:assign(delta)
			end
		end

	end
	if o.heightAdjust then
		poseB.translations(0).y=poseB.translations(0).y+o.heightAdjust
	end
end

function M.AngleRetarget:_convertMotion(motion)
	local motB=self.motB

	local motionB=Motion(motB.loader)
	motionB:resize(motion:numFrames())
	for i=0, motion:numFrames()-1 do
		if math.fmod(i+1, 10000)==0 then
			print('angle converting', i)
		end
		local pose=motion:pose(i)
		self:_convertPose(pose, motionB:pose(i))
	end
	if motion.getConstraints then
		motionB:setConstraints( Motion.IS_DISCONTINUOUS, motion:getConstraints(Motion.IS_DISCONTINUOUS))
	end
	return motionB
end

function M.AngleRetarget:convertMotion(motion)

	local motB=self.motB
	local motionB=self:_convertMotion(motion)
	local use1Dknees=self.use1Dknees
	local motdofB=MotionDOF(self.motB.loader.dofInfo)
	motdofB:resize(motion:numFrames())
	if use1Dknees then
		motdofB:set(motionB, use1Dknees[1], use1Dknees[2], use1Dknees[3])
	else
		motdofB:set(motionB)
	end
	return motdofB
end

MotionUtil.PoseTransfer2=require("subRoutines/PoseTransfer2")
function M.generateBindPoseMap(loader)
	local mapA={R={}, T={}}
	for i=0, loader:numRotJoint()-1 do
		local k=loader:getBoneByRotJointIndex(i):name()
		mapA.R[k]=i
	end
	for i=0, loader:numTransJoint()-1 do
		local k=loader:getBoneByTransJointIndex(i):name()
		mapA.T[k]=i
	end
	return mapA
end
function M.printBindPoseMap(loader)
	print('-- pose')
	printLua(loader:pose())
	print('-- posemap')
	printLua(M.generateBindPoseMap(loader))
end
function M.decodeBindPose(loader, bindpose, mapA)
	local A=Pose()
	A:init(loader:numRotJoint(), loader:numTransJoint())
	A:identity()
	for k, v in pairs(mapA.R) do
		local i=loader:getTreeIndexByName(k)
		if i~=-1 then
			A.rotations(loader:getRotJointIndexByTreeIndex(i)):assign(bindpose.rotations(v))
		end
	end
	for k, v in pairs(mapA.T) do
		local i=loader:getTreeIndexByName(k)
		local j=loader:getTransJointIndexByTreeIndex(i)
		if i~=-1 and j~=-1 then
			A.translations(j):assign(bindpose.translations(v))
		end
	end
	local Adof=vectorn()
	loader:setPose(A)
	loader:getPoseDOF(Adof)
	return A, Adof
end
function M.createSkinA()
	local decodeBindPose=M.decodeBindPose
	assert(mSkelA.dofInfo:numDOF()==motA.loader.dofInfo:numDOF())
	if motA.fbx then
		mSkinA= RE.createFBXskin(motA.fbx, true)
	else
		mSkinA= RE.createSkin(mSkelA, false)
	end
	mSkinA:setScale(A.skinScale, A.skinScale, A.skinScale)
	mSkinA:setMaterial('red_transparent')

	if mBindPoseAquat and mBindPosesMap then
		mBindPoseAquat, mBindPoseA=decodeBindPose(motA.loader, mBindPoseAquat, mBindPosesMap[1])

		if mBindPoseBquat and mBindPosesMap[2] then
			mBindPoseBquat, mBindPoseB=decodeBindPose(motB.loader, mBindPoseBquat, mBindPosesMap[2])
		end
	end

	if not mBindPoseA or mBindPoseA:size()~=motA.motionDOFcontainer.mot:cols() then
		mBindPoseA=motA.motionDOFcontainer.mot:row(0):copy()
		mBindPoseA:set(0,0)
		mBindPoseA:set(2,0)

		if motA.motion then
			mBindPoseAquat=motA.motion:pose(0):copy()
		else
			mBindPoseAquat=Pose()
			motA.loader:setPoseDOF(mBindPoseA)
			motA.loader:getPose(mBindPoseAquat)
		end
	end

	if mBindPoseAquat then
		mSkinA:setPose( mBindPoseAquat)
	else
		mSkinA:setPoseDOF(mBindPoseA)
	end
end

return M
