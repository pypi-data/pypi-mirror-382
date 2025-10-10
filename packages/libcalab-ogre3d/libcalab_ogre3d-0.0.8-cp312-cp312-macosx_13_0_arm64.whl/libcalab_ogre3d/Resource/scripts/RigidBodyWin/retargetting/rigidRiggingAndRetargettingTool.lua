require("config")
package.projectPath='../Samples/classification/'
package.path=package.path..";../Samples/classification/lua/?.lua" --;"..package.path
require("common")
require("module")
require("moduleIK")
require("RigidBodyWin/retargetting/module/poseEditingModule")
require("RigidBodyWin/retargetting/module/boneSelectionModule")

-- to generate a rigid skin for ETRI_Template_Skeleton/fitting2.bvh
A_fitting2={
	skel="../Samples/scripts/RigidBodyWin/retargetting/data/ETRI_Template_Skeleton/fitting2.bvh",
	motion=nil,
	-- skel will be converted to wrl
	wrl="../Samples/scripts/RigidBodyWin/retargetting/data/ETRI_Template_Skeleton/fitting2.wrl",
	skinScale=2.54, -- inch to cm
	reusePreviousBinding=false,
	target=config_examples.justin,
	-- A to B
	boneCorrespondences={
		Pelvis='root', Spine1='lowerback', Spine2='upperback', Spine3='LowerNeck', Head='Neck',
		LHip='lfemur', LKnee='ltibia', LAnkle='lfoot', LToe='ltoes',
		RHip='rfemur', RKnee='rtibia', RAnkle='rfoot', RToe='rtoes',
		LCollarBone='lclavicle', LShoulder='lhumerus', LElbow='lradius', LWrist='lhand',
		RCollarBone='rclavicle', RShoulder='rhumerus', RElbow='rradius', RWrist='rhand',
	}
}

--local etriDataFile="../Samples/scripts/RigidBodyWin/retargetting/data/Data/5_8.bvh"
local etriDataFile="../Samples/scripts/RigidBodyWin/retargetting/data/Data/2_1.bvh"
A_ETRI_data={
	skel=etriDataFile,
	motion=nil,
	-- skeleton will be converted to wrl. 
	wrl=etriDataFile..".wrl", 
	bindPoseFile= "../Samples/scripts/RigidBodyWin/retargetting/data/Data/common_bindTarget.info", -- 모든 bvh에 대해서 같은 바인드 포즈
	skinScale=1.05, -- cm
	reusePreviousBinding=false,
	target=config_examples.ETRI,
	-- A to B
	boneCorrespondences={
		Hips='Pelvis', Spine='Spine', Spine1='Spine1', Neck='Neck', Head='Head',
		LeftUpLeg='LHip', LeftLeg='LKnee', LeftFoot='LAnkle', LeftFootHeel='LToe',
		RightUpLeg='RHip', RightLeg='RKnee', RightFoot='RAnkle', RightFootHeel='RToe',
		LeftShoulder='LCollarBone', LeftArm='LShoulder', LeftForeArm='LElbow', LeftHand='LWrist',
		RightShoulder='RCollarBone', RightArm='RShoulder', RightForeArm='RElbow', RightHand='RWrist',
	},
	markerDistanceOverride={Spine1=10}, -- Spine1 is more important then others
	exportBVHtemplate={
		"../Samples/scripts/RigidBodyWin/retargetting/data/ETRI_Template_Skeleton/fitting.asf",
		"../Samples/scripts/RigidBodyWin/retargetting/data/ETRI_Template_Skeleton/fitting.amc",
	}

}

A_skipping_data={
	target=table.merge(
	config_examples.skipping, 
	{motion="../../taesoo_qp/results/skipping_simulated.dof", }
	),
	wrl="../Resource/motion/justin_runf3.wrl",
	motion="../../taesoo_qp/results/skipping_simulated.dof", 
	bindPoseFile= "../Resource/motion/justin_runf3_avoid_leg_intersection.info", 
	skinScale=100,
	reusePreviousBinding=true,
}

-- retarget A to B
--A=A_fitting2
A=A_ETRI_data
--A=A_skipping_data
B=A.target

function createUI()
	this:create("Button", "retarget to T", "retarget to T",1);
	this:addButton("reload bindposes")
	this:setWidgetHeight(100)
	this:create("Multi_Browser","correspondence","",0)
	this:resetToDefault()
	this:create("Button", "Add selected", "Add selected",0,2)
	this:create("Button", "Add automatic", "automatic",2,3)
	this:create("Button", "Load mapping table", "Load mapping table",0,2)
	this:create("Button", "Check completeness", "Check",2,3)
	this:create("Button", "Remove selected", "Remove selected",0)
	this:create("Button", "Save retargetConfig", "Save retargetConfig")
	this:addText('Bind-pose editing operations')
	this:addText('(selected bone (B) only)')
	this:create("Button", "align", "align",0,1)
	this:create("Button", "align2D", "align2D",1,2)
	this:create("Button", "reset", "reset",2,3)
	this:resetToDefault()
	this:create("Choice", "pose operations")
	this:widget(0):menuSize(10)
	this:widget(0):menuItem(0, "choose a pose operation")
	this:widget(0):menuItem(1, "setCurrPose as BindPoseA")
	this:widget(0):menuItem(2, "setCurrPose as BindPoseB")
	this:widget(0):menuItem(3, "load A's bind pose")
	this:widget(0):menuItem(4, "A goes to bind pose")
	this:widget(0):menuItem(5, "A goes to I")
	this:widget(0):menuItem(6, "A goes to T")
	this:widget(0):menuItem(7, "B goes to I")
	this:widget(0):menuItem(8, "B goes to T")
	this:widget(0):menuItem(9, "rotate A 180-y")
	this:create("Choice", "mesh operations")
	this:widget(0):menuSize(6)
	this:widget(0):menuItem(0, "choose a mesh operation")
	this:widget(0):menuItem(1, "copy selected meshes (A->B)")
	this:widget(0):menuItem(2, "copy selected meshes (B->A)")
	this:widget(0):menuItem(3, "export B")
	this:widget(0):menuItem(4, "getMesh (B->A)")
	this:widget(0):menuItem(5, "Undo getMeth")
	this:updateLayout()
end

function createUI_part2_and_initialize()

	
	--dbg.startTrace2()
	mEventReceiver=EVR()

	this:create("Check_Button", "attach camera", "attach camera",1);
	this:widget(0):checkButtonValue(false);
	this:create("Button", "save current pose", "save current pose",1);

	this:setUniformGuidelines(4)
	this:create("Button", "rotate light", "rotate light",0,2);
	this:create("Button", "rotate y90A", "rotate y90A",2);
	this:create("Button", "rotate y90B", "rotate y90B",0,2);
	this:create("Button", "export A", "export A",2);
	this:create("Check_Button", "A is visible", "show A",0,2);
	this:widget(0):checkButtonValue(true);
	this:create("Check_Button", "B is visible", "show B",2);
	this:widget(0):checkButtonValue(true);

	this:create("Value_Slider", "scaleA", "scaleA",1);
	this:widget(0):sliderRange(0.8,1.2);
	this:widget(0):sliderValue(1);

	this:create("Value_Slider", "scaleB", "scaleB",1);
	this:widget(0):sliderRange(0.8,1.2);
	this:widget(0):sliderValue(1);

	this:create("Button", "retarget A to B", "IK retarget A to B",1);
	this:create("Button", "angle retarget A to B", "angle retarget A to B",1);
	this:create('Check_Button', 'test only 100 frames','test only 100 frames')

	initialize()

	this:updateLayout()

	camInfo={}
end


function ctor()
	createUI_part2_and_initialize()
end
function dtor()
	do 
		if motA then
			RE.motionPanel():motionWin():detachSkin(motA.skin)
			motA.skin=nil
		end
		if motB then
			RE.motionPanel():motionWin():detachSkin(motB.skin)
			motB.skin=nil
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

function filePatternToString(A_skel)
	local out=A_skel
	if select(1, string.find(A_skel, '%*')) then
		out=string.gsub(A_skel, '%*', '__all__')
	end
	return out
end

function initialize()
	-- load B
	motB=loadMotion(B.skel, B.motion, B.skinScale, true)
	--RE.motionPanel():motionWin():addSkin(motB.skin)

	if B.height then
		for i=0,motB.motionDOFcontainer.mot:rows()-1 do
			motB.motionDOFcontainer.mot:row(i):set(1,motB.motionDOFcontainer.mot:row(i)(1)+B.height)
		end
	end

	RET=require("retargetting/module/retarget_common")
	RET.updateBindPose()
	if not mBindPoseB or mBindPoseB:size()~=motB.motionDOFcontainer.mot:cols() then
		mBindPoseB=motB.motionDOFcontainer.mot:row(0):copy()
		mBindPoseB:set(0,0)
		mBindPoseB:set(2,0)
	end
	mUniqueID=string.sub(os.filename(A.wrl or filePatternToString(A.skel)),1,-5).."_to_"..string.sub(os.filename(B.skel or B.motion),1,-5)
	--mPrefix=string.sub(A.wrl,1,-5).."_to_"..string.sub(os.filename(B.skel),1,-5)
	mPrefix=string.sub(B.skel or B.motion,1,-5).."_"..string.sub(os.filename(A.wrl or filePatternToString(A.skel)),1,-5)
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
	--	motA=loadMotion(A.skel, A.motion, A.skinScale)
	--	local fn= os.filename(A.wrl)
	--	MotionUtil.exportVRMLforRobotSimulation( motA.loader, A.wrl, fn, 1/A.skinScale)
	--	mSkelA=MainLib.VRMLloader(A.wrl)
	--	mSkelA:exportCurrentPose(A.wrl)
	--else
	if A.loadMotion then
		A.motion=A.loadMotion()
	end
	
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
			-- todo: fix this. buggy.
			require('subRoutines/WRLloader')
			-- exact copy of the original skeleton (which, in some cases, cannot be used in a physical simulator.).
			local wrl= MotionUtil.generateWRLforRobotSimulation(motA.loader, fn, 1/A.skinScale)
			mSkelA=MainLib.WRLloader(wrl)
		end

		if not A.motion then
			A.motion=A.skel
		end
	else
		mSkelA=MainLib.VRMLloader(A.wrl)
	end
	local M=require("RigidBodyWin/retargetting/module/retarget_common")
	M.createSkinA()

	mSkinB= createSkin(B.skel, motB.loader, B.skinScale)
	if false then
		a=Pose()
		mSkelA:setPoseDOF(motA.motionDOFcontainer.mot:row(0))
		mSkelA:getPose(a)
		dbg.console()
		-- for testing only
		--mSkinA:applyAnim(motA.loader.mMotion) -- works good.
		mSkinA:applyMotionDOF(motA.motionDOFcontainer.mot) -- works badly.
		RE.motionPanel():motionWin():addSkin(mSkinA)

		dbg.console()
	end
	mSkinB:_setPoseDOF(mBindPoseB, motB.loader.dofInfo)

	local transA=MotionDOF.rootTransformation(motA.motionDOFcontainer.mot:row(0)).translation:copy()
	transA:scale(-1*A.skinScale)
	motA.skin:setTranslation(-190+transA.x, 0,0+transA.z)
	motB.skin:setTranslation(190,0,0)

	do
		local vpos=RE.viewpoint().vpos:copy()
		local vat=RE.viewpoint().vat:copy()
		local rootpos=motB.motionDOFcontainer.mot:row(0):toVector3(0)*B.skinScale +vector3(-190, 0,0)
		local vdir=vat-vpos

		RE.viewpoint().vpos:assign(rootpos-vdir)
		RE.viewpoint().vat:assign(rootpos)
		RE.viewpoint():update()
	end

	mPoseEditingModule=PoseEditingModule(motB.loader, motB.motionDOFcontainer, motB.skin, B.skinScale, B.EE)
	mPoseEditingModule:setSkin(mSkinB, 'lightgrey_transparent')

	mPoseEditingModule:setPose(mBindPoseB)

	mBoneSelectionModule=BoneSelectionModule(motA.loader, motA.motionDOFcontainer, nil, A.skinScale, 'lightgrey_transparent')
	setBoneSelectionPoseA(mBindPoseA, mBindPoseAquat)
	updateScript()
end
function setBoneSelectionPoseA(mBindPoseA, mBindPoseAquat)
	local poseA=mBindPoseA:copy()
	poseA:set(0,-190/A.skinScale)

	if mBindPoseAquat then
		local poseAq=mBindPoseAquat:copy()
		poseAq.translations(0).x=-190/A.skinScale

		mBoneSelectionModule:setPose(poseA, poseAq)
	else
		mBoneSelectionModule:setPose(poseA)
	end
end
function handleRendererEvent(ev, button, x, y)
	mBoneSelectionModule:handleRendererEvent(ev, button, x,y)
	return mPoseEditingModule:handleRendererEvent(ev, button, x,y)
end

function gotoBindPoseA()
	local skelA=motA.loader
	if mBindPoseAquat then
		skelA:setPose(mBindPoseAquat)
	else
		skelA:setPoseDOF(mBindPoseA)
	end
end

function onCallback(w, userData)

	if w:id()=="Save retargetConfig" then
		local fn=saveRetargetInfo()
		util.msgBox("saved to"..fn)
		g_retargetConfigFile=fn
	elseif w:id()=="reload bindposes" then
		local A_backup=A
		local B_backup=B
		local bq_backup=bindposes_quat
		local bm_backup=bindposes_map

		if g_retargetConfigFile then
			local M=require("RigidBodyWin/retargetting/module/retarget_common")
			M.loadRetargetInfo(chosenFile)
			local bq=bindposes_quat
			A=A_backup
			B=B_backup
			bindposes_quat=bq_backup
			bindposes_map=bm_backup

			motB.loader:setPose(Pose.fromTable(bq[2]))
			motB.loader:getPoseDOF(mBindPoseB)
			bindPoseBupdated()
		else
			util.msgBox("Error! Save retargetConfig first.")
		end

	elseif w:id()=="reset" then
		local boneBname=this:findWidget(mPoseEditingModule.menuName):menuText()
		local tiB=motB.loader:getTreeIndexByName(boneBname)
		if tiB~=-1 then
			local boneB=motB.loader:bone(tiB):parent()
			motB.loader:setPoseDOF(mBindPoseB)
			boneB:getLocalFrame().rotation:identity()
			motB.loader:fkSolver():getPoseDOFfromLocal(mBindPoseB)
			bindPoseBupdated()
		else
			util.msgBox("select a bone first")
		end
	elseif w:id()=="align" then
		local boneBname=this:findWidget(mPoseEditingModule.menuName):menuText()
		local tiB=motB.loader:getTreeIndexByName(boneBname)
		if tiB~=-1 then
			local boneB=motB.loader:bone(tiB)
			motB.loader:setPoseDOF(mBindPoseB)
			local dir=boneB:parent():getFrame().translation-boneB:getFrame().translation

			local v1=findCorrespondingBoneAfromBoneB(boneB)
			if v1 then
				local boneA=motA.loader:getBoneByName(v1)
				local tdir=boneA:parent():getFrame().translation-boneA:getFrame().translation
				local q=quater()
				q:axisToAxis(dir, tdir)
				motB.loader:rotateBoneGlobal(boneB:parent(), q)
				motB.loader:getPoseDOF(mBindPoseB)
				bindPoseBupdated()
			else
				util.msgBox("Error! bone "..boneBname.. " doesn't have a corresponding bone of A!")
			end
		else
			util.msgBox("select a bone first")
		end

	elseif w:id()=="align2D" then
		local boneBname=this:findWidget(mPoseEditingModule.menuName):menuText()
		local tiB=motB.loader:getTreeIndexByName(boneBname)
		if tiB~=-1 then
			local boneB=motB.loader:bone(tiB)
			motB.loader:setPoseDOF(mBindPoseB)
			local dir=boneB:parent():getFrame().translation-boneB:getFrame().translation

			local v1=findCorrespondingBoneAfromBoneB(boneB)
			if v1 then
				local boneA=motA.loader:getBoneByName(v1)
				local tdir=boneA:parent():getFrame().translation-boneA:getFrame().translation
				local q=quater()
				q:setAxisRotation(vector3(0,1,0), dir, tdir)
				motB.loader:rotateBoneGlobal(boneB:parent(), q)
				motB.loader:getPoseDOF(mBindPoseB)
				bindPoseBupdated()
			else
				util.msgBox("Error! bone "..boneBname.. " doesn't have a corresponding bone of A!")
			end
		else
			util.msgBox("select a bone first")
		end

	elseif w:id()=="Check completeness" then
		local M=require("RigidBodyWin/retargetting/module/retarget_common")
		M.checkCompleteness(motA.loader, A.boneCorrespondences)
	elseif w:id()=="pose operations" then
		local mid=w:menuText()
		if mid=="setCurrPose as BindPoseA" then
			print(mEventReceiver.currFrame)
			mBindPoseA=motA.motionDOFcontainer.mot:row(mEventReceiver.currFrame):copy()
			mBindPoseA:set(0,0)
			mBindPoseA:set(2,0)
			if motA.motion then
				mBindPoseAquat=motA.motion:pose(mEventReceiver.currFrame):copy()
				mBindPoseAquat.translations(0).x=0
				mBindPoseAquat.translations(0).z=0
			end
			bindPoseAupdated()
		elseif mid=="setCurrPose as BindPoseB" then
			print(mEventReceiver.currFrame)
			mBindPoseB=motB.motionDOFcontainer.mot:row(mEventReceiver.currFrame):copy()
			mBindPoseB:set(0,0)
			mBindPoseB:set(2,0)
			mSkinB:_setPoseDOF(mBindPoseB, motB.loader.dofInfo)
		elseif mid=="load A's bind pose" then
			local path='../Resource/motion'
			local chosenFileA=Fltk.chooseFile("Choose A", path, "*.pose", false)
			if chosenFileA~="" then
				local pose=Pose()

				local solver=RRIKsolver(motA, nil, 0.005)

				RE.loadPose(pose, chosenFileA)
				motA.loader:setPose(pose)
				for i=0, solver.effectors:size()-1 do
					solver.effectorPos(i):assign( solver.effectors(i).bone:getFrame()*solver.effectors(i).localpos)

					--dbg.draw("Sphere", solver.effectorPos(i)*100+vector3(10,0,0), "x"..i, 'blue', 1)
				end

				motA.loader:getPoseDOF(mBindPoseA)

				solver:IKsolve(mBindPoseA)
				if false then
					-- debug draw
					motA.loader:setPoseDOF(mBindPoseA)
					for i=0, solver.effectors:size()-1 do
						solver.effectorPos(i):assign( solver.effectors(i).bone:getFrame()*solver.effectors(i).localpos)
						dbg.draw("Sphere", solver.effectorPos(i)*100+vector3(11,0,0), "ax"..i, 'red', 1)
					end
				end

				mBindPoseA:set(0,0)
				mBindPoseA:set(2,0)
				motA.loader:setPoseDOF(mBindPoseA)
				mSkinA:_setPoseDOF(mBindPoseA, motA.loader.dofInfo)
				setBoneSelectionPoseA(mBindPoseA)
			end
		elseif mid=="A goes to bind pose" then
			motA.loader:setPose(mBindPoseAquat)
			mSkinA:setPose(mBindPoseAquat)
			setBoneSelectionPoseA(mBindPoseA, mBindPoseAquat)

		elseif mid=="A goes to I" then
			local M=require("RigidBodyWin/retargetting/module/retarget_common")
			M.skelAtoIdentity()
		elseif mid=="A goes to T" then
			local M=require("RigidBodyWin/retargetting/module/retarget_common")
			M.skelAtoT()
		elseif mid=="B goes to I" then
			local M=require("RigidBodyWin/retargetting/module/retarget_common")
			M.skelBtoIdentity()
			updateSkinB()
		elseif mid=="rotate A 180-y" then
			local q180y=quater(math.rad(180), vector3(0,1,0))
			if mBindPoseA then
				mBindPoseA:setQuater(3, q180y*mBindPoseA:toQuater(3))
			end
			if mBindPoseAquat then
				mBindPoseAquat.rotations(0):assign(q180y*mBindPoseAquat.rotations(0))
			end
			bindPoseAupdated()
		elseif w:id()=="A goes to T" then
			local M=require("RigidBodyWin/retargetting/module/retarget_common")
			M.skelAtoT()
		end
	elseif w:id()=="mesh operations" then
		local mid=w:menuText()
		if mid== "copy selected meshes (A->B)" then

			local _input=this:findWidget("correspondence")
			for i=1, _input:browserSize() do
				if _input:browserSelected(i) then
					local k=g_map[i]
					local v=A.boneCorrespondences[k]

					print(k,v)
					local boneA=mSkelA:VRMLbone(mSkelA:getTreeIndexByName(k))
					local boneB=motB.loader:VRMLbone(motB.loader:getTreeIndexByName(v))
					if boneA:hasShape() and boneB:hasShape() then
						local mesh=Geometry()
						mesh:assign(boneA:getMesh())
						local t=matrix4()
						t:identity()
						local s=getSkinScaleA()/getSkinScaleB()
						mesh:scale(vector3(s,s,s))
						boneB:getMesh():assign(mesh)

						--motB.skin
						--mSkinB
						--mPoseEditingModule.skin
						--local f=RE.motionPanel():motionWin():getCurrFrame()
						--removeSkin()
						--createSkin()
						--RE.motionPanel():motionWin():changeCurrFrame(f)
					end
				end
			end
			--[[
			motB.loader:_updateMeshEntity()
			local function recreateSkin(loader, skin, skinScale)
				local pose=Pose()
				local trans=skin:getTranslation():copy()
				skin:getPose(pose)
				local newskin=RE.createVRMLskin(loader, false)
				newskin:setScale(skinScale,skinScale,skinScale)
				PLDPrimSkin.setPose(newskin, pose, loader)
				newskin:setTranslation(trans.x, trans.y, trans.z)
				return newskin
			end
			-- recreate the three skins related to B
			local s=getSkinScaleB()
			local skin
			skin=recreateSkin(motB.loader, motB.skin, s)
			motB.skin=skin
			skin=recreateSkin(motB.loader, mPoseEditingModule.skin, s)
			mPoseEditingModule.skin=skin
			skin=recreateSkin(motB.loader, mSkinB, s)
			mSkinB=skin
			collectgarbage()
			]]

			--motB.loader:export("temp.wrl")
		elseif mid== "copy selected meshes (B->A)" then

			print("not immplemented yet")
		elseif mid=="export B" then
			motB.loader:export(B.skel)
		elseif mid== "getMesh (B->A)" then
			VRMLLoader_makeBackup(A.wrl)

			local bc=A.boneCorrespondences
			for k,v in pairs(bc) do
				local bone=mSkelA:VRMLbone(mSkelA:getTreeIndexByName(k))
				if bone:hasShape() then
					--bone:getMesh():convertToOBJ() no longer necessary
				else
					util.msgBox(bone:name() .. " has no geometry. We copied "..bone:name()..".obj file. To use it, manually edit the wrl file.")
				end
			end

			exportA()
			getMeshFromB()
			if A.wrl=='__temp.wrl' then
				local tmpLoader=MainLib.VRMLloader(A.wrl)
				A.wrl=filePatternToString(A.skel)..'.wrl'
				tmpLoader:export(A.wrl)
				util.msgBox(A.wrl .. " has been generated.")
				--os.copyFile('__temp.wrl', A.wrl)
				--local obj_path=string.sub(A.wrl, 1, -5).."_sd/"
				--os.createDir(obj_path)
				--os.copyFile('__temp_sd/*', obj_path)
			end
			dtor()
			initialize()
		elseif mid=="Undo getMesh" then
			VRMLLoader_restoreBackup(A.wrl)
			dtor()
			initialize()
		end
	elseif w:id()=="Add automatic" then
		local M=require("RigidBodyWin/retargetting/module/retarget_common")
		local corr=M.setCorrespondences(motA.loader, motB.loader)
		for k,v in ipairs(corr) do
			A.boneCorrespondences[v[1]]=v[2]
		end
		updateScript()
	elseif w:id()=="Add selected" then
		local boneA=this:findWidget('select bone'):menuText()
		local boneB=this:findWidget(mPoseEditingModule.menuName):menuText()
		if boneA~='choose bone' and boneB~='choose bone' then
			addSelected(boneA, boneB)
		end
	elseif w:id()=="Load mapping table" then
		require('subRoutines/exportOgreEntityToVRML')
		local path='../Resource/motion'
		local chosenFileA=Fltk.chooseFile("Choose mappingFile", path, "*.txt", false)
		local tbl=parseMappingFile(chosenFileA)
		A.boneCorrespondences=tbl
		updateScript()
	elseif w:id()=="Remove selected" then
		local boneA=this:findWidget('select bone'):menuText()
		if boneA~='choose bone'  then
			A.boneCorrespondences[boneA]=nil
			updateScript()
		end
	elseif w:id()=="correspondence" then
		local bFirst=true
		for i=1, w:browserSize() do
			local k=g_map[i]
			local v=A.boneCorrespondences[k]

			if mBoneSelectionModule.skin.setBoneMaterial then
				mBoneSelectionModule.skin:setBoneMaterial(motA.loader:getTreeIndexByName(k), 
				mBoneSelectionModule.defaultMaterial)
			end
			mPoseEditingModule.skin:setBoneMaterial(motB.loader:getTreeIndexByName(v), 
			mPoseEditingModule.defaultMaterial)
		end
		for i=1, w:browserSize() do
			if w:browserSelected(i) then
				local k=g_map[i]
				local v=A.boneCorrespondences[k]
				if bFirst then
					-- A:
					mBoneSelectionModule:_selectBone(motA.loader:getTreeIndexByName(k))
					-- B:
					mPoseEditingModule:_selectBone(motB.loader:getTreeIndexByName(v))
					print(':',k,v)
					bFirst=false
				else
					if mBoneSelectionModule.skin.setBoneMaterial then
						mBoneSelectionModule.skin:setBoneMaterial(motA.loader:getTreeIndexByName(k), 'green_transparent')
					end
					mPoseEditingModule.skin:setBoneMaterial(motB.loader:getTreeIndexByName(k), 'green_transparent')
				end
			end
		end
	elseif w:id()=="start" then
		local path='../Resource/motion'
		if setAB(path) then
			createUI_part2_and_initialize()
		end
	elseif w:id()=="start using script" then
		local chosenFileA=Fltk.chooseFile("Choose A", path, "*.lua", false)

		if chosenFileA ~='' then
			local chosenFileB=Fltk.chooseFile("Choose B", path, "*.lua", false)
			if chosenFileB ~='' then
				function Start(skel, mot)
					g_res={wrl=skel, motion=mot}
				end
				dofile(chosenFileA)
				A=g_res
				A.reusePreviousBinding=true
				A.boneCorrespondences={}
				A.skinScale=skinScale or 100
				dofile(chosenFileB)
				B=g_res
				B.skel=B.wrl
				B.wrl=nil
				B.skinScale=skinScale or 100
				skinScale=nil
				B.EE={}

				g_res=nil
				local out=
				"A="..table.toIndentedString(A,0)
				.."B="..table.toIndentedString(B,0)
				util.writeFile("temp.retargetConfig.lua", out)
				print("Saved to temp.retargetConfig.lua")
			else
				return 
			end
		else
			return 
		end
		createUI_part2_and_initialize()
	elseif w:id()=="retarget to T" then
		local path='../Resource/scripts/modifyModel/'
		local chosenFileA=Fltk.chooseFile("Choose A", path, "*.lua", false)

		if chosenFileA ~='' then
			function Start(skel, mot)
				g_res={wrl=skel, motion=mot}
			end
			dofile(chosenFileA)
			A=g_res
			A.reusePreviousBinding=true
			--A.boneCorrespondences={}
			A.skinScale=skinScale or 100

			B={}
			local fn=string.sub(A.wrl, 1, -5).."_T"
			local fn1=fn..".wrl"
			local fn2=fn.."0.pose"
			local fn3=fn..".dof"
			B.motion=fn3
			B.skel=fn1
			B.wrl=nil
			B.skinScale=skinScale or 100
			skinScale=nil
			B.EE={}

			mBindPoseAquat=Pose()
			mBindPoseBquat=Pose()
			RE.loadPose(mBindPoseAquat, fn2)
			RE.loadPose(mBindPoseBquat, fn2)

			mBindPoseBquat.rotations:setAllValue(quater(1,0,0,0))

			g_res=nil
			local out=
			"A="..table.toIndentedString(A,0)
			.."B="..table.toIndentedString(B,0)
			util.writeFile("temp.retargetConfig.lua", out)
			print("Saved to temp.retargetConfig.lua")
		else
			return 
		end
		createUI_part2_and_initialize()
	elseif w:id()=="start using retargetConfig" then
		local path='../Resource/motion'
		local chosenFile=Fltk.chooseFile("Choose a retargetConfig file", path, "*.retargetConfig.lua", false)
		startUsingRetargetConfig(chosenFile)
	elseif w:id()=="attach camera" then
		camInfo.attachToBody=w:checkButtonValue();
	elseif w:id()=="retarget A to B" then
		local defaultMarkerDistance=A.defaultMarkerDistance or 4
		local markerDistance=defaultMarkerDistance/B.skinScale 
		local markerBoneIndices=intvectorn()
		local treeIndexAfromB={}
		local deltaBindPose=quaterN()

		gotoBindPoseA()
		motB.loader:setPoseDOF(mBindPoseB)

		for k,v in pairs(A.boneCorrespondences) do
			local i=motB.loader:getTreeIndexByName( v)
			if(i==-1) then
				print('motB ('..B.skel..'): '..v..'?')
				dbg.console()
			end
			markerBoneIndices:pushBack(i)

			local j=motA.loader:getTreeIndexByName(k)
			if(j==-1) then
				print('motA ('..A.wrl..'): '..k..'?')
				dbg.console()
			end
			treeIndexAfromB[i]=j

			local q=quater()
			q:toLocal(motA.loader:bone(j):getFrame().rotation, motB.loader:bone(i):getFrame().rotation)
			deltaBindPose:pushBack(q)


			--local boneA=motA.loader:bone(j)
			--local desiredOri=boneA:getFrame().rotation*deltaBindPose(deltaBindPose:size()-1)
			--dbg.namedDraw('Axes', transf(desiredOri, boneA:getFrame().translation*getSkinScaleA()/getSkinScaleB()), 'a'..i, 100)
		end


		local BskinScale=getSkinScaleB()
		local mdo
		if A.markerDistanceOverride then
			mdo={}
			for k,v in pairs(A.markerDistanceOverride) do
				mdo[k]=v/BskinScale
			end
		end
		mIKsolver=createIKsolverForRetargetting(motB.loader, markerBoneIndices, markerDistance, mdo)
		if false then
			mIKsolver.solver=MotionUtil.createFullbodyIkDOF_UTPoser(motB.loader.dofInfo, mIKsolver.effectors)
			MotionUtil.FullbodyIK_UTPoser_setParam(mIKsolver.solver, 500, 0.01)
		else
			g_con=MotionUtil.Constraints() -- std::vector<MotionUtil::RelativeConstraint>
			g_con:resize(0)
			mIKsolver.solver=MotionUtil.createFullbodyIk_MotionDOF_MultiTarget_lbfgs(motB.loader.dofInfo, mIKsolver.effectors, g_con);
		end
		
		-- solve ik for a few frames
		local startFrame=0
		local endFrame=motA.motionDOFcontainer:numFrames()-1
		if this:findWidget('test only 100 frames'):checkButtonValue() then
			startFrame=mEventReceiver.currFrame
			endFrame=math.min(startFrame+100, endFrame)
		end

		local bones_A={}
		local localPos_A={}
		do
			local c=mIKsolver.effectorPos:size()
			local bones_B=mIKsolver.src_bones
			local effectors=mIKsolver.effectors
			local skelA=motA.loader
			local skelB=motB.loader
			gotoBindPoseA()
			skelB:setPoseDOF(mBindPoseB)
			-- calc local pos
			for i=0, c-1 do
				local boneB=bones_B[i]
				local localposB=effectors(i).localpos
				local globalposB=boneB:getFrame():toGlobalPos(localposB)
				local boneA=skelA:getBoneByTreeIndex(treeIndexAfromB[boneB:treeIndex()])
				local globalposA=globalposB*BskinScale/getSkinScaleA()
				local localposA=boneA:getFrame():toLocalPos(globalposA)

				bones_A[i]=boneA
				localPos_A[i]=localposA
			end
		end
		local function getEffectorPos()
			local c=mIKsolver.effectorPos:size()
			local effectorPos=mIKsolver.effectorPos
			for j=0, c-1 do
				local globalposA=bones_A[j]:getFrame():toGlobalPos(localPos_A[j])
				local globalposB=globalposA*getSkinScaleA()/BskinScale
				effectorPos:at(j):assign(globalposB)
			end
			if true then -- for debugging
				for j=0, c-1 do
					dbg.draw('Sphere', effectorPos:at(j)*BskinScale, 'marker'..j, 'red', 2)
				end
				RE.renderOneFrame(false)
			end
		end
		local skelA=motA.loader
		local motdofA=motA.motionDOFcontainer.mot
		local motionA=motA.motion
		local motdofB=motB.motionDOFcontainer.mot
		motdofB:resize(endFrame+1)
		for iframe=startFrame,endFrame do
			print('ik '..iframe..'/'..(endFrame-1))
			if motionA then
				skelA:setPose(motionA:pose(iframe))
			else
				skelA:setPoseDOF(motdofA:row(iframe))
			end
			getEffectorPos()

			if iframe>startFrame then
				motdofB:row(iframe):assign( motdofB:row(iframe-1))
			end
			local roottf=MotionDOF.rootTransformation(motdofA:row(iframe))
			roottf.translation:scale(getSkinScaleA()/BskinScale)
			MotionDOF.setRootTransformation(motdofB:row(iframe), roottf)

			if true then
				local solver=mIKsolver.solver
				solver:_changeNumConstraints(markerBoneIndices:size())
				for i=0, markerBoneIndices:size() -1 do
					local ti=markerBoneIndices(i)

					local tiA=treeIndexAfromB[ti]
					local boneA=motA.loader:bone(tiA)
					local desiredOri=boneA:getFrame().rotation*deltaBindPose(i)
					solver:_setOrientationConstraint(i, motB.loader:bone(ti), desiredOri)
					dbg.namedDraw('Axes', transf(desiredOri, boneA:getFrame().translation*getSkinScaleA()/BskinScale), 'a'..i, 100)
				end
				solver:_effectorUpdated()
			end

			mIKsolver.solver:IKsolve(motdofB:row(iframe), mIKsolver.effectorPos)
		end

		local prefix=filePatternToString(A.skel or A.motion)
		print('Exporting to '..prefix..'.dof')
		motB.motionDOFcontainer:exportMot(prefix..'.dof')
		--local mot=Motion(motB.motionDOFcontainer.mot)
		--MotionUtil.exportBVH(mot, A.skel..'.dof.bvh', 0, mot:numFrames())
		motB.skin:applyMotionDOF(motB.motionDOFcontainer.mot)

		if A.exportBVHtemplate then
			SkeletonEditorModule.exportBVHusingASFskeleton(A.exportBVHtemplate[1], A.exportBVHtemplate[2], motB.loader, motB.motionDOFcontainer.mot, A.skel..'.dof.bvh') 
		end
		updateSkinB()
	elseif w:id()=="angle retarget A to B" then

		if not mBindPoseAquat then
			mBindPoseAquat=Pose()
			motA.loader:setPoseDOF(mBindPoseA)
			motA.loader:getPose(mBindPoseAquat)
		end
		--local bindPoseBquat=mBindPoseBquat 
		local bindPoseBquat
		if not bindPoseBquat then
			bindPoseBquat=Pose()
			motB.loader:setPoseDOF(mBindPoseB)
			motB.loader:getPose(bindPoseBquat)
			print('updated')
		end
		local retargetConfig={
			A=copyTable(A),
			B=copyTable(B),
			bindposes_quat={
				mBindPoseAquat,
				bindPoseBquat
			}
		}
		assert(#retargetConfig.bindposes_quat==2)
		retargetConfig.A.mot=motA
		retargetConfig.B.mot=motB
		RET=require("retargetting/module/retarget_common")
		local ret=RET.AngleRetarget(retargetConfig)
		motB.motionDOFcontainer=MotionDOFcontainer(motB.loader.dofInfo)
		motB.motionDOFcontainer:resize(motA.motionDOFcontainer:numFrames())

		local motionA=motA.motion

		if not motionA then
			motionA=Motion(motA.motionDOFcontainer.mot)
		end

		motB.motionDOFcontainer.mot=ret:convertMotion(motionA)
		local prefix=filePatternToString(A.skel or A.motion)
		print('Exporting to '..prefix..'.dof')
		motB.motionDOFcontainer:exportMot(prefix..'.dof')
		--local mot=Motion(motB.motionDOFcontainer.mot)
		--MotionUtil.exportBVH(mot, A.skel..'.dof.bvh', 0, mot:numFrames())
		motB.skin:applyMotionDOF(motB.motionDOFcontainer.mot)

		if A.exportBVHtemplate then
			SkeletonEditorModule.exportBVHusingASFskeleton(A.exportBVHtemplate[1], A.exportBVHtemplate[2], motB.loader, motB.motionDOFcontainer.mot, A.skel..'.dof.bvh') 
		end

		updateSkinB()
	elseif w:id()=="export A" then
		exportA()


		if A.getMeshFromB then
			getMeshFromB()
		end
	elseif w:id()=="A is visible" then
		motA.skin:setVisible(w:checkButtonValue())
	elseif w:id()=="B is visible" then
		motB.skin:setVisible(w:checkButtonValue())
	elseif w:id()=="rotate y90A" then
		if mBindPoseAquat then
			print('not implmented yet')
			dbg.console()
		else
			local tf=MotionDOF.rootTransformation(mBindPoseA)
			local tf2=transf(quater(math.rad(90), vector3(0,1,0)), vector3(0,0,0))
			tf:leftMult(tf2)

			MotionDOF.setRootTransformation(mBindPoseA, tf)
			mSkinA:_setPoseDOF(mBindPoseA, motA.loader.dofInfo)
		end
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

if EventReceiver then
	EVR=LUAclass(EventReceiver)
	function EVR:__init(graph)
		self.currFrame=0
		self.cameraInfo={}
	end
end

function EVR:onFrameChanged(win, iframe)
	self.currFrame=iframe

	RE.output("iframe", iframe)
	print(iframe)

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

	if motB.motionDOFcontainer.mot and mTargetSkin then
		if iframe<motB.motionDOFcontainer:numFrames() then
			mTargetSkin:setPoseDOF(motB.motionDOFcontainer.mot:row(iframe))
		end
	end


end

function frameMove(fElapsedTime)
	dbg.updateBillboards(fElapsedTime)
end



function getSkinScaleA()
	return (A.skinScale*this:findWidget('scaleA'):sliderValue())
end
function getSkinScaleB()
	return (B.skinScale*this:findWidget('scaleB'):sliderValue())
end

function getMeshFromB()
	local bc=A.boneCorrespondences
	local sd_path1=string.sub(A.wrl, 1, -5).."_sd/"
	local sd_path2=A.wrl.."._bindTarget_sd/"
	for k,v in pairs(bc) do
		local mesh=Geometry()
		do
			local boneA=mSkelA:VRMLbone(mSkelA:getTreeIndexByName(k))
			local boneB=motB.loader:VRMLbone(motB.loader:getTreeIndexByName(v))
			if boneA:hasShape() and boneB:hasShape() then
				mesh:assign(boneB:getMesh())
				mesh:rigidTransform(boneB:getFrame())
				local s=getSkinScaleB()/getSkinScaleA()
				mesh:scale(vector3(s,s,s))
				mesh:rigidTransform(boneA:getFrame():inverse())
				boneA:getMesh():assign(mesh)
			else
				mesh=nil
			end

			--motB.skin
			--mSkinB
			--mPoseEditingModule.skin
			--local f=RE.motionPanel():motionWin():getCurrFrame()
			--removeSkin()
			--createSkin()
			--RE.motionPanel():motionWin():changeCurrFrame(f)

		end
		if mesh then
			local fn=sd_path1..k..'.obj'
			print(fn)
			mesh:saveOBJ(fn, true, false)
		end
	end
	--mSkelA=MainLib.VRMLloader(A.wrl)
	mSkelA:updateInitialBone()
	mSkelA:exportCurrentPose(A.wrl)

end
function exportA()
	local out={}
	out.bindPoseA=mBindPoseA
	out.bindPoseB=mBindPoseB
	out.skinScaleA=getSkinScaleA()
	out.skinScaleB=getSkinScaleB()
	mSkelA:setPoseDOF(out.bindPoseA)
	mSkelA:exportCurrentPose(A.wrl)
	motB.loader:setPoseDOF(out.bindPoseB)
	motB.loader:exportCurrentPose(A.wrl.."._bindTarget.wrl")
	--[[ 
	bind poses will be saved when exporting retargetInfo
	util.saveTable(out, mBindPoseFile)
	if mBindPoseFile~=mPrefix.."._bindTarget.info" then
		-- also save to the default file for consistency
		util.saveTable(out, mPrefix.."._bindTarget.info")
	end
	]]--
end
function updateSkinB()
	if B.skel:sub(-4)=='.fbx' or B.skel:sub(-8)=='.fbx.dat' then
		local FBXloader=require('FBXloader')
		if not mTargetLoader then 
			mTargetLoader=FBXloader(B.skel)
			mTargetSkin=RE.createFBXskin(mTargetLoader, false)
		end
		mTargetSkin:setScale(B.skinScale)
		mTargetSkin:setTranslation(100,0,0)
	end
end
function bindPoseBupdated()
	mPoseEditingModule:setPose(mBindPoseB)
	mSkinB:_setPoseDOF(mBindPoseB, motB.loader.dofInfo)
	mPoseEditingModule:updateCON()
end
function saveRetargetInfo()
	local M=require("RigidBodyWin/retargetting/module/retarget_common")
	return M.saveRetargetInfo(A,B, mBindPoseA, mBindPoseB, getSkinScaleA(), getSkinScaleB(), mPrefix, mBindPoseAquat, mBindPoseBquat)
end

function updateScript()
	local _input=this:findWidget("correspondence")
	_input:browserClear()
	g_map={}
	for i=1, motA.loader:numBone()-1 do
		local k=motA.loader:bone(i):name()
		local v=A.boneCorrespondences[k]
		if v then
			table.insert(g_map, k)
			if k==v then
				_input:browserAdd(k)
			else
				_input:browserAdd(k..'=='..v)
			end
		end
	end
	_input:redraw()
end
function VRMLLoader_makeBackup(fn)
	local objFolder=string.sub(fn, 1, -5).."_sd"
	print('creating '..objFolder..'. (An error message would be shown if the folder already exists. You can ignore it.)')
	os.createDir(objFolder..".backup")
	os.copyRecursive(objFolder, objFolder..".backup", {'%.obj'})
	os.copyFile(fn, objFolder..".backup/backup.wrl")
end
function VRMLLoader_restoreBackup(fn)
	local objFolder=string.sub(fn, 1, -5).."_sd"
	if os.isFileExist(objFolder..".backup/backup.wrl") then
		os.copyRecursive(objFolder..".backup", objFolder, {'%.obj'})
		os.copyFile(objFolder..".backup/backup.wrl", fn)
	end
end


function addSelected(boneA, boneB)
	print(boneA, boneB)
	A.boneCorrespondences[boneA]=boneB
	updateScript()
end

function setAB(path)
	local M=require("RigidBodyWin/retargetting/module/retarget_common")
	return M.setAB(path)
end
function startUsingRetargetConfig(chosenFile)
	if chosenFile then
		g_retargetConfigFile=chosenFile
		local M=require("RigidBodyWin/retargetting/module/retarget_common")
		M.loadRetargetInfo(chosenFile)
	else
		return 
	end

	if not A or not B then
		print('incorrect config')
		return
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

	createUI_part2_and_initialize()
	updateScript()


	-- todo. it is slow to render motA.skin, mSkinA on mac when A has many joints.
	-- -> fixed. simply turned off shadow.
	--motA.skin:setVisible(false)
	--	mSkinA:setVisible(false)
end
function bindPoseAupdated()
	if motA.motion then
		mSkinA:_setPose(mBindPoseAquat, motA.loader)
		setBoneSelectionPoseA(mBindPoseA, mBindPoseAquat)
	else
		mSkinA:_setPoseDOF(mBindPoseA, motA.loader.dofInfo)
		setBoneSelectionPoseA(mBindPoseA)
	end
end
-- returns bone name
function findCorrespondingBoneAfromBoneB(boneB)

	local function findBone1(nameB)
		for k,v in pairs(A.boneCorrespondences) do
			if v==nameB then
				return k
			end
		end
	end
	local v1=findBone1(boneB:name())
	if not v1 and boneB:childHead() then
		v1=findBone1(boneB:childHead())
	end
	if not v1 then
		local v2=findBone1(boneB:parent():name())
		if v2 then
			local boneA=motA.loader:getBoneByName(v2)
			if boneA:childHead() and not boneA:childHead():sibling() then
				-- only child
				return boneA:childHead():name()
			end
		end
	end
	return v1
end
