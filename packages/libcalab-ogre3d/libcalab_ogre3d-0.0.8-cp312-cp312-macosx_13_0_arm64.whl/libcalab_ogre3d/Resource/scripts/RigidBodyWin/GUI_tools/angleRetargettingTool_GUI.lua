require("config")
require("common")
require("module")
require("RigidBodyWin/retargetting/module/poseEditingModule")
require("RigidBodyWin/retargetting/module/boneSelectionModule")
require("RigidBodyWin/subRoutines/Timeline")
MotionUtil.PoseTransfer2=require("RigidBodyWin/subRoutines/PoseTransfer2")

A=nil
B=nil


function ctor()

	this:create("Button", "start", "start");
	this:create("Button", "start using script", "start using script");
	this:create("Button", "start using retargetConfig", "start using retargetConfig");
	this:widget(0):buttonShortcut("FL_ALT+s");
	this:create("Button", "restart", "restart");
	this:setWidgetHeight(50)
	this:create("Box", "info", "retargetConfig file can be \ngenerated using \ncorrespondenceTool_GUI.lua")
	this:resetToDefault()
	this:create("Button", "check completeness", "check completeness")
	this:create("Button", "Save retargetConfig", "Save retargetConfig")
	this:setUniformGuidelines(10);
	this:create("Button", "A goes to T", "A goes to T", 0, 8)
	this:create("Button", "A goes to I", "I", 8)
	this:create("Button", "B goes to T", "B goes to T", 0, 8)
	this:create("Button", "B -> T except fingers", "B -> T except fingers", 0, 8)
	this:create("Button", "B goes to I", "I", 8)
	this:create("Button", "setCurrPose as BindPoseA", "setCurrPose as BindPoseA", 0, 9)
	this:create("Button", "setCurrPose as BindPoseB", "B", 9)
	this:create("Button", "fit skeleton A to B", "fit skeleton A to B" , 0)
	this:setWidgetHeight(50)
	this:create("Box", "info2", 
	"fitting assumes that A and B\n are in a similar pose.");
	this:resetToDefault()
	this:create("Button", "export fitted skeleton", "export fitted skeleton")
	this:create("Button", "save skinning info", "save skinning info")
	this:updateLayout()
end

function filePatternToString(A_skel)
	local out=A_skel
	if select(1, string.find(A_skel, '%*')) then
		out=string.gsub(A_skel, '%*', '__all__')
	end
	return out
end

function removeSkinA()
	if mSkinA then
		RE.motionPanel():motionWin():detachSkin(mSkinA)
	end
	mSkinA=nil
	collectgarbage()
	collectgarbage()
	collectgarbage()
end

function createSkinA()
	local M=require("RigidBodyWin/retargetting/module/retarget_common")
	M.createSkinA()
end
function addAutomatic(M)
	local corr=M.setCorrespondences(motA.loader, motB.loader)
	for k,v in ipairs(corr) do
		A.boneCorrespondences[v[1]]=v[2]
	end
	printTable(corr)
end
function skelAtoIdentity()
	local M=require("RigidBodyWin/retargetting/module/retarget_common")
	M.skelAtoIdentity()
end

function onCallback(w, userData)
	if w:id()=="start" then
		local M=require("RigidBodyWin/retargetting/module/retarget_common")
		local path='../Resource/motion'
		if M.setAB(path) then
			start()
			addAutomatic(M) -- set correspondence
		end
	
	elseif w:id()=="fit skeleton A to B" then
		local M=require("RigidBodyWin/retargetting/module/retarget_common")
		--skelAtoIdentity()
		mSkelA:setPoseDOF(mBindPoseA)
		M.fitSkeletonAtoB(mSkelA, motB.loader, A.boneCorrespondences, B.skinScale/A.skinScale)
		mSkelA:setPoseDOF(mBindPoseA)
		removeSkinA()
		createSkinA()

	elseif w:id()=="export fitted skeleton" then
		local a,b=os.processFileName(A.wrl)
		local chosenFile=Fltk.chooseFile("Create a new file", b, "*.wrl", true)
		if chosenFile~='' then
			mSkelA:export(chosenFile)
		end
	elseif w:id()=="check completeness" then
		local M=require("RigidBodyWin/retargetting/module/retarget_common")
		M.checkCompleteness(motA.loader, A.boneCorrespondences)
	elseif w:id()=="start using script" then
		local M=require("RigidBodyWin/retargetting/module/retarget_common")
		local path='../Resource/scripts/modifyModel/'
		if M.setAB(path) then
			start()
			addAutomatic(M) -- set correspondence
		end
	elseif w:id()=="Save retargetConfig" then
		local M=require("RigidBodyWin/retargetting/module/retarget_common")
		M.saveRetargetInfo(A,B, mBindPoseA, mBindPoseB, getSkinScaleA(), getSkinScaleB(), mPrefix, mBindPoseAquat, mBindPoseBquat)
	elseif w:id()=="start using retargetConfig" then
		local path='../Resource/motion/'
		local chosenFile=Fltk.chooseFile("Choose a retargetConfig file", path, "*.retargetConfig.lua", false)
		local M=require("RigidBodyWin/retargetting/module/retarget_common")
		if M.loadRetargetInfo(chosenFile) then
			start()
		end
	elseif w:id()=="restart" then
		dtor()
		local M=require("RigidBodyWin/retargetting/module/retarget_common")
		if M.loadRetargetInfo(g_chosenFile) then
			start()
		else
			print('???')
		end
	elseif w:id()=="setCurrPose as BindPoseA" then
		print(mEventReceiver.currFrame)
		mBindPoseA=motA.motionDOFcontainer.mot:row(mEventReceiver.currFrame):copy()
		mBindPoseA:set(0,0)
		mBindPoseA:set(2,0)
		mSkinA:_setPoseDOF(mBindPoseA, motA.loader.dofInfo)
		setBoneSelectionPoseA(mBindPoseA)
	elseif w:id()=="setCurrPose as BindPoseB" then
		print(mEventReceiver.currFrame)
		mBindPoseB=motB.motionDOFcontainer.mot:row(mEventReceiver.currFrame):copy()
		mBindPoseB:set(0,0)
		mBindPoseB:set(2,0)
		mSkinB:_setPoseDOF(mBindPoseB, motB.loader.dofInfo)
	elseif w:id()=="A goes to I" then
		skelAtoIdentity()
	elseif w:id()=="B goes to I" then
		local h=mBindPoseB(1) 
		motB.loader:updateInitialBone()
		motB.loader:getPoseDOF(mBindPoseB) -- lightgrey_transparent
		mBindPoseB:set(1, h)
		mSkinB:_setPoseDOF(mBindPoseB, motB.loader.dofInfo) -- red_transparent
		print("BindPoseB has been modified. Save retargetInfo to save the result.")

	elseif w:id()=="A goes to T" then
		local M=require("RigidBodyWin/retargetting/module/retarget_common")
		M.skelAtoT()
	elseif w:id()=="B goes to T" then
		local M=require("RigidBodyWin/retargetting/module/retarget_common")
		motB.loader:setPoseDOF(mBindPoseB)
		print('motA.loader:')
		M.setVoca(motA.loader)
		print('motB.loader:')
		M.setVoca(motB.loader)
		for k,v in pairs(A.boneCorrespondences) do 
			local boneA= motA.loader:getBoneByName(k)
			if boneA:voca()~=-1 then
				local boneB= motB.loader:getBoneByName(v)
				if boneB:voca()==-1 then
					motB.loader:_changeVoca(boneA:voca(), boneB)
				else
					assert(boneA:voca()==boneB:voca())
				end
			end
		end
		M.gotoTpose(motB.loader)
		mBindPoseBquat=Pose()
		motB.loader:getPose(mBindPoseBquat)
		motB.loader:getPoseDOF(mBindPoseB)
		if false then
			mSkinB:_setPoseDOF(mBindPoseB, motB.loader.dofInfo)
		else
			PLDPrimSkin.setPose(mSkinB,mBindPoseBquat, motB.loader)
		end
		mPoseEditingModule:setPose(mBindPoseB)
		print("BindPoseB has been modified. Save retargetInfo to save the result.")
	elseif w:id()=="B -> T except fingers" then
		local M=require("RigidBodyWin/retargetting/module/retarget_common")
		motB.loader:setPoseDOF(mBindPoseB)
		print('motA.loader:')
		M.setVoca(motA.loader)
		print('motB.loader:')
		M.setVoca(motB.loader)
		for k,v in pairs(A.boneCorrespondences) do 
			local boneA= motA.loader:getBoneByName(k)
			if boneA:voca()~=-1 then
				local boneB= motB.loader:getBoneByName(v)
				if boneB:voca()==-1 then
					motB.loader:_changeVoca(boneA:voca(), boneB)
				else
					assert(boneA:voca()==boneB:voca())
				end
			end
		end
		M.gotoTpose(motB.loader, true)
		mBindPoseBquat=Pose()
		motB.loader:getPose(mBindPoseBquat)
		motB.loader:getPoseDOF(mBindPoseB)
		if false then
			mSkinB:_setPoseDOF(mBindPoseB, motB.loader.dofInfo)
		else
			PLDPrimSkin.setPose(mSkinB,mBindPoseBquat, motB.loader)
		end
		mPoseEditingModule:setPose(mBindPoseB)
		print("BindPoseB has been modified. Save retargetInfo to save the result.")

	elseif w:id()=="attach camera" then
		camInfo.attachToBody=w:checkButtonValue();
	elseif w:id()=="retarget A to B" then
		local treeIndexAfromB={}

		local convFile={}
		local convInfoA=TStrings()
		local convInfoB=TStrings()
		for k,v in pairs(A.boneCorrespondences) do
			local i=motB.loader:getTreeIndexByName( v)
			if(i==-1) then
				print('motB ('..B.skel..'): '..v..'?')
			end
			local j=motA.loader:getTreeIndexByName(k)
			if(j==-1) then
				print('motA ('..A.wrl..'): '..k..'?')
			end
			treeIndexAfromB[i]=j

			if i~=-1 and j~=-1 then
				table.insert(convFile, v..'\t'..k)
				convInfoA:pushBack(k)
				convInfoB:pushBack(v)
			end
		end
		local posScaleFactor=getSkinScaleB()/getSkinScaleA()


		util.writeFile("__conversionTable.txt", table.concat(convFile, '\n'))

		-- 바인드 자세 설정
		motA.loader:setPoseDOF(mBindPoseA)
		motB.loader:setPoseDOF(mBindPoseB)

		if mBindPoseAquat then
			motA.loader:setPose(mBindPoseAquat)
		end
		if mBindPoseBquat then
			motB.loader:setPose(mBindPoseBquat)
		end

		local M=require("RigidBodyWin/retargetting/module/retarget_common")
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
			assert(treeIndicesShoulder:findFirstIndex(-1)==-1)
			assert(treeIndicesElbow:findFirstIndex(-1)==-1)
			--assert(treeIndicesWrist:findFirstIndex(-1)==-1)
			if treeIndicesWrist(0)==-1 or 
				motB.loader.dofInfo:numDOF(motB.loader:getTreeIndexByVoca(MotionLoader.LEFTELBOW))~=1
				then
					treeIndicesShoulder=treeIndicesShoulder:range(2,4):copy()
					treeIndicesElbow=treeIndicesElbow:range(2,4):copy()
					treeIndicesWrist=treeIndicesWrist:range(2,4):copy()
			end
			use1Dknees={treeIndicesShoulder, treeIndicesElbow, treeIndicesWrist}
		end

		local saveBindPoseForCPP=true
		if saveBindPoseForCPP then
			-- 이 부분의 코드는 불필요하지만, cpp포팅시 파일에서 바인드포즈 불러오려면 필요함.
			local poseA=Pose() -- cpp에서는 클래스 이름이 Posture임.
			local poseB=Pose()
			motA.loader:getPose(poseA) -- 위의 mBindPoseA의 euler angle 을 quaternion형태로 변환.
			motB.loader:getPose(poseB)

			-- bindPose의 루트 위치는 없애야 PoseTransfer가 정상동작함. PoseTransfer2는 상관없음.
			-- poseA.translations(0):assign(vector3(0,0,0))
			-- poseB.translations(0):assign(vector3(0,0,0))
			RE.savePose(poseA, "__conversionBindPoseA")
			RE.savePose(poseB, "__conversionBindPoseB")
		end

		local motionA=Motion(motA.motionDOFcontainer.mot) -- MotionDOF를 Motion으로 conversion
		local motionB=Motion(motB.motionDOFcontainer.mot)

		do 
			-- 이 블락 안의 코드만 포팅하면 됨. (3개의 파일과 posScaleFactor만 사용해서 리타게팅)
			if saveBindPoseForCPP then
				local poseA=Pose() -- cpp에서는 클래스 이름이 Posture임.
				local poseB=Pose()
				RE.loadPose(poseA, "__conversionBindPoseA")
				RE.loadPose(poseB, "__conversionBindPoseB")
				motA.loader:setPose(poseA)
				motB.loader:setPose(poseB)
			end
			--local pt=MotionUtil.PoseTransfer(motA.loader, motB.loader,  "__conversionTable.txt", true)
			local pt=MotionUtil.PoseTransfer2(motA.loader, motB.loader,  convInfoA, convInfoB, posScaleFactor)

			-- solve ik for a few frames
			local startFrame=0
			local endFrame=motionA:numFrames()-1
			if this:findWidget('test only 50 frames'):checkButtonValue() then
				startFrame=mEventReceiver.currFrame
				endFrame=startFrame+50
			end

			motionB:resize( endFrame+1)
			for i=startFrame, endFrame do
				print(i)
				pt:setTargetSkeleton(motionA:pose(i))
				motB.loader:getPose(motionB:pose(i))

				-- 아래줄은 PoseTransfer를 쓰는경우만 필요함. PoseTransfer2는 기능 내장.
				--motionB:pose(i).translations(0):scale(1/posScaleFactor)
			end
			g_motionB=motionB
			--motB.skin:applyAnim(g_motionB)
		end

		-- 아래는 만들어진 Motion을 MotionDOF로 convert back하는 코드 (kist과제랑은 관련 없음)
		local motdofB=motB.motionDOFcontainer.mot
		motdofB:resize(motionB:numFrames())
		if use1Dknees then
			motdofB:set(motionB, use1Dknees[1], use1Dknees[2], use1Dknees[3])
		else
			motdofB:set(motionB)
		end
		
		print('Exporting to '..mPrefix..'.dof')

		motB.motionDOFcontainer.discontinuity:assign(motA.motionDOFcontainer.discontinuity)
		motB.motionDOFcontainer.conL:assign(motA.motionDOFcontainer.conL)
		motB.motionDOFcontainer.conR:assign(motA.motionDOFcontainer.conR)
		motB.motionDOFcontainer:exportMot(mPrefix..'.dof')
		--local mot=Motion(motB.motionDOFcontainer.mot)
		--MotionUtil.exportBVH(mot, filePatternToString(A.skel)..'.dof.bvh', 0, mot:numFrames())
		motB.skin:applyMotionDOF(motB.motionDOFcontainer.mot)
		motB.skin:setTranslation(-100+transA.x,0,0+transA.z)
		motA.skin:setMaterial('red_transparent')

	elseif w:id()=="export bindPoses" then
		exportAB()


	elseif w:id()=="A is visible" then
		motA.skin:setVisible(w:checkButtonValue())
	elseif w:id()=="B is visible" then
		motB.skin:setVisible(w:checkButtonValue())
	elseif w:id()=="rotate y90A" then
		local tf=MotionDOF.rootTransformation(mBindPoseA)
		local tf2=transf(quater(math.rad(90), vector3(0,1,0)), vector3(0,0,0))
		tf:leftMult(tf2)

		MotionDOF.setRootTransformation(mBindPoseA, tf)
		mSkinA:_setPoseDOF(mBindPoseA, motA.loader.dofInfo)
	elseif w:id()=="rotate y90B" then
		local tf=MotionDOF.rootTransformation(mBindPoseB)
		local tf2=transf(quater(math.rad(90), vector3(0,1,0)), vector3(0,0,0))
		tf:leftMult(tf2)

		MotionDOF.setRootTransformation(mBindPoseB, tf)
		mSkinB:_setPoseDOF(mBindPoseB, motB.loader.dofInfo)
		mPoseEditingModule:updateCON()
	elseif w:id()=='rotate light' then
		local osm=RE.ogreSceneManager()
		if osm:hasSceneNode("LightNode") then
			local lightnode=osm:getSceneNode("LightNode")
			lightnode:rotate(quater(math.rad(30), vector3(0,1,0)))
		end
	elseif w:id()=='scaleA' then
		local s=A.skinScale*w:sliderValue()
		motA.skin:setScale(s,s,s)
		mSkinA:setScale(s,s,s)
	elseif w:id()=='scaleB' then
		local s=B.skinScale*w:sliderValue()
		motB.skin:setScale(s,s,s)
		mSkinB:setScale(s,s,s)
	else 
		mPoseEditingModule:onCallback(w, userData)
	end
end
function start()

	mEventReceiver=FrameEvent()
	mTimeline=Timeline("Timeline", 10000)
	
	--dbg.startTrace()

	this:create("Check_Button", "attach camera", "attach camera",1);
	this:widget(0):checkButtonValue(false);
	this:create("Button", "save current pose", "save current pose",1);
	this:create("Button", "rotate light", "rotate light",1);
	this:create("Button", "rotate y90A", "rotate y90A",1);
	this:create("Button", "rotate y90B", "rotate y90B",1);
	--this:create("Button", "export bindPoses", "export bindPoses",1); -- now, a retargetinfo contains the bind poses.
	this:create("Check_Button", "A is visible", "A is visible",1);
	this:widget(0):checkButtonValue(true);
	this:create("Check_Button", "B is visible", "B is visible",1);
	this:widget(0):checkButtonValue(true);

	this:create("Value_Slider", "scaleA", "scaleA",1);
	this:widget(0):sliderRange(0.8,1.2);
	this:widget(0):sliderValue(1);

	this:create("Value_Slider", "scaleB", "scaleB",1);
	this:widget(0):sliderRange(0.8,1.2);
	this:widget(0):sliderValue(1);

	this:create("Button", "retarget A to B", "retarget A to B",1);
	this:create('Check_Button', 'test only 50 frames','test only 50 frames')

	initialize()

	this:updateLayout()

	camInfo={}
end
function dtor()
	do 
		if motA then
			RE.motionPanel():motionWin():detachSkin(motA.skin)
			motA.skin=nil
			motA=nil
		end
		if motB then
			RE.motionPanel():motionWin():detachSkin(motB.skin)
			motB.skin=nil
			motB=nil
		end
		mSkinA=nil
		mSkinB=nil
		mPoseEditingModule=nil
		mBoneSelectionModule=nil
		collectgarbage()
		collectgarbage()
		collectgarbage()
		collectgarbage()
	end
end

function removeFixed(mLoader)
	for i=1, mLoader:numBone()-1 do
		if mLoader:VRMLbone(i):numChannels()==0 then
			mLoader:removeAllRedundantBones()
			--mLoader:removeBone(mLoader:VRMLbone(i))
			--mLoader:export(config[1]..'_removed_fixed.wrl')
			break
		end
	end
	mLoader:_initDOFinfo()

	mLoader:printHierarchy()
end
function initialize()
	-- load B
	motB=loadMotion(B.skel, B.motion, B.skinScale, true)
	removeFixed(motB.loader)

	if B.height then
		for i=0,motB.motionDOFcontainer.mot:rows()-1 do
			motB.motionDOFcontainer.mot:row(i):set(1,motB.motionDOFcontainer.mot:row(i)(1)+B.height)
		end
	end

	if not mBindPoseB then
		-- angle retargeting 은 cpp내부적으로 Motion 클래스를 써서 구현되어있지만, 
		-- 이 GUI는 다른 리타게팅 툴과의 호환성을 위해 현재 MotionDOF를 쓰고 있음. 
		-- MotionDOF와 Motion은 상호 변환가능.
		mBindPoseB=motB.motionDOFcontainer.mot:row(0):copy()
		mBindPoseB:set(0,0)
		mBindPoseB:set(2,0)
	end

	RE.motionPanel():motionWin():addSkin(motB.skin)


	--mBindPoseB:range(7, mBindPoseB:size()):setAllValue(0)
	
	mUniqueID=string.sub(os.filename(A.wrl or filePatternToString(A.skel)),1,-5).."_to_"..string.sub(os.filename(B.skel),1,-5)
	--mPrefix=string.sub(A.wrl,1,-5).."_to_"..string.sub(os.filename(B.skel),1,-5)
	mPrefix=string.sub(B.skel,1,-5).."_"..string.sub(os.filename(A.wrl or filePatternToString(A.skel)),1,-5)
	print(mUniqueID)

	--[[
	now bind-poses are stored in the same retargetConfig.lua file.
	mBindPoseFile=A.bindPoseFile or mPrefix.."._bindTarget.info"
	if os.isFileExist(mBindPoseFile) then
		local out=util.loadTable(mBindPoseFile)
		--if out.skinScaleA then
		--	A.skinScale=out.skinScaleA 
		--end
		mBindPoseA=out.bindPoseA
		mBindPoseB=out.bindPoseB
	end
	]]--

	-- load A
	--if not A.reusePreviousBinding or not os.isFileExist(A.wrl) then
	--	motA=loadMotion(filePatternToString(A.skel), A.motion, A.skinScale)
	--	local fn= os.filename(A.wrl)
	--	MotionUtil.exportVRMLforRobotSimulation( motA.loader, A.wrl, fn, 1/A.skinScale)
	--	mSkelA=MainLib.VRMLloader(A.wrl)
	--	mSkelA:exportCurrentPose(A.wrl)
	--else
	motA=loadMotion(A.wrl or A.skel, A.motion, A.skinScale)
	--end

	if not A.boneCorrespondences then
		A.boneCorrespondences={}

		for i=1,motA.loader:numBone()-1 do
			local k=motA.loader:bone(i):name()
			print(k)
			A.boneCorrespondences[k]=k
		end
	end

	RE.motionPanel():motionWin():addSkin(motA.skin)

	if not A.wrl then
		A.wrl="__temp.wrl"
		local fn= os.filename(filePatternToString(A.skel))
		if true then
			-- rotChannels are converted to ZXY here. 
			MotionUtil.exportVRMLforRobotSimulation( motA.loader, A.wrl, fn, 1/A.skinScale)
			mSkelA=MainLib.VRMLloader(A.wrl)
		else
			require('subRoutines/WRLloader')
			-- exact copy of the original skeleton (which, in some cases, cannot be used in a physical simulator.).
			local wrl= MotionUtil.generateWRLforRobotSimulation(motA.loader, fn, 1/A.skinScale)
			mSkelA=MainLib.WRLloader(wrl)
		end
	else
		mSkelA=MainLib.VRMLloader(A.wrl)
	end

	createSkinA()
	mSkinB= createSkin(B.skel, motB.loader, B.skinScale)
	mSkinB:_setPoseDOF(mBindPoseB, motB.loader.dofInfo)

	if true then
		--모션은 그대로 두고 스킨을 원점에 놓기.
		transA=MotionDOF.rootTransformation(motA.motionDOFcontainer.mot:row(0)).translation:copy()
		transA:scale(-1*A.skinScale)
	else
		--스킨은 그대로 두고, 모션의 첫프레임만 원점에 놓기.
		transA=vector3()
		transA:zero()
		motA.motionDOFcontainer.mot:row(0):set(0,0)
		motA.motionDOFcontainer.mot:row(0):set(2,0)
	end
	motA.skin:setTranslation(-100+transA.x, 0,0+transA.z)
	motB.skin:setTranslation(100,0,0)

	do
		local vpos=RE.viewpoint().vpos:copy()
		local vat=RE.viewpoint().vat:copy()
		local rootpos=motB.motionDOFcontainer.mot:row(0):toVector3(0)*B.skinScale +vector3(-100, 0,0)
		local vdir=vat-vpos

		RE.viewpoint().vpos:assign(rootpos-vdir)
		RE.viewpoint().vat:assign(rootpos)
		RE.viewpoint():update()
	end

	mPoseEditingModule=PoseEditingModule(motB.loader, motB.motionDOFcontainer, motB.skin, B.skinScale, B.EE)
	mPoseEditingModule:setSkin(mSkinB, 'lightgrey_transparent')

	mPoseEditingModule:setPose(mBindPoseB)
	mPoseEditingModule.poseEditingEventFunction=poseEEvent

	mBoneSelectionModule=BoneSelectionModule(motA.loader, motA.motionDOFcontainer, motA.skin, A.skinScale, 'lightgrey_transparent')
	setBoneSelectionPoseA(mBindPoseA)
end
function poseEEvent(mod, id, pose)
	if id=="updateCON" then
		print(mBindPoseB-pose)
		print(pose)
		motB.loader:setPoseDOF(mBindPoseB)
	end
end
function setBoneSelectionPoseA(mBindPoseA)
	local poseA=mBindPoseA:copy()
	poseA:set(0,-100/A.skinScale)
	mBoneSelectionModule:setPose(poseA)
end
function handleRendererEvent(ev, button, x, y)
	mBoneSelectionModule:handleRendererEvent(ev, button, x,y)
	local o= mPoseEditingModule:handleRendererEvent(ev, button, x,y)
	return o
end
if EventReceiver then
	FrameEvent=LUAclass(EventReceiver)
	function FrameEvent:__init()
		self.currFrame=0
		self.cameraInfo={}
	end
end

function FrameEvent:frameMove(fElapsedTime)
end
function FrameEvent:onFrameChanged(win, iframe)
	self.currFrame=iframe
	RE.output("iframe", iframe)

	if camInfo.attachToBody then
		local motionDOF=motB.motionDOFcontainer.mot
		local p1=vector3(0,0,0);

		local BskinScale=getSkinScaleB()
		p1:assign(motionDOF:row(iframe):toVector3(0)*BskinScale )

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



function getSkinScaleA()
	return (A.skinScale*this:findWidget('scaleA'):sliderValue())
end
function getSkinScaleB()
	return (B.skinScale*this:findWidget('scaleB'):sliderValue())
end

function exportAB()
	local out={}
	out.bindPoseA=mBindPoseA
	out.bindPoseB=mBindPoseB
	out.skinScaleA=getSkinScaleA()
	out.skinScaleB=getSkinScaleB()
	util.saveTable(out, mBindPoseFile)
	if mBindPoseFile~=mPrefix.."._bindTarget.info" then
		-- also save to the default file for consistency
		util.saveTable(out, mPrefix.."._bindTarget.info")
		Fltk.msgBox("Bindposes exported to "..mPrefix.."._bindTarget.info")
	end
end
