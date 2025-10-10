require("config")
package.projectPath='../Samples/classification/'
package.path=package.path..";../Samples/classification/lua/?.lua" --;"..package.path
require("common")
require("module")
require("moduleIK")
require("RigidBodyWin/subRoutines/Constraints")

config_muaythai1= {
	skel="../Resource/motion/muaythai1.wrl",
	motion='../Resource/motion/muaythai1.dof',
}
config_muaythai2= {
	skel="../Resource/motion/muaythai2.wrl",
	motion='../Resource/motion/muaythai2.dof',
}
config_hyunwoo= {
	skel="../Resource/motion/locomotion_hyunwoo/hyunwoo_full_mod.wrl",
	motion="../Resource/motion/locomotion_hyunwoo/hyunwoo_full.dof", skinScale=100,
}
config_gymnist={
	skel="../Resource/motion/gymnist/gymnist.wrl",
	motion="../Resource/motion/gymnist/gymnist.dof",
	skinScale=100,
}
config_dance_M={
	--skel="../Resource/jae/dance/dance1_M.wrl",
	--motion="../Resource/jae/dance/dance1_M.dof",
	skel="../Resource/motion/skeletonEditor/dance1_M_1dof.wrl",
	motion="../Resource/motion/skeletonEditor/dance1_M_1dof.wrl.dof",
	skinScale=100,
}
config_justin_jump={
	skel="../Resource/motion/justin_jump.wrl",
	motion="../Resource/motion/justin_jump.dof",
	skinScale=100,
}
config_justin_jump={
	skel="../Resource/motion/justin_runf3_cart.wrl",
	motion="../Resource/motion/justin_straight_run/justin_runf3_cart_gen.dof",
	skinScale=100,
}
config_justin_straight_run={
	skel= "../Resource/motion/justin_straight_run/justin_straight_run.wrl",
	motion= "../Resource/motion/justin_straight_run/justin_straight_run.dof",
	skinScale=100,
}
config_ETRI={
	-- the skel wrl file is generated using rigidRiggingTool.lua
	--skel="../Samples/scripts/RigidBodyWin/retargetting/data/ETRI_Template_Skeleton/fitting2.wrl",
	--motion="../Samples/scripts/RigidBodyWin/retargetting/data/ETRI_Template_Skeleton/fitting2.bvh",
	skel="../Resource/motion/skeletonEditor/fitting2_1dof_fixed.wrl",
	motion="../Resource/motion/skeletonEditor/fitting2_1dof_fixed.wrl.dof",
	skinScale=2.54,
	mirror=function(x)
		return vector3(x.x, x.y, -x.z)
	end
}

--config=config_muaythai1
--config=config_muaythai2
--config=config_hyunwoo
--config=config_gymnist
--config=config_dance_M
--config=config_justin_straight_run
config=config_ETRI
--config=config_justin_jump

function symmetricBoneName(cname)

	local symTable={
		left='right',
		right='left',
		Left='Right',
		Right='Left',
		LEFT='RIGHT',
		RIGHT='LEFT',
		LHip='RHip',
		RHip='LHip',
		LKnee='RKnee',
		RKnee='LKnee',
		LAnkle='RAnkle',
		RAnkle='LAnkle',
		LShoulder='RShoulder',
		RShoulder='LShoulder',
		LElbow='RElbow',
		RElbow='LElbow',
		LWrist='RWrist',
		RWrist='LWrist',
	}

	for k,v in pairs(symTable) do
		if select(1, string.find(cname, k)) then
			local a=string.gsub(cname, k, v)
			return a
		end
	end
	return nil
end

function symmetricBone(bone)
	local cname=bone:name()
	local ti=mLoader:getTreeIndexByName( symmetricBoneName(cname))
	if ti==-1 then
		print('error')
		dbg.console()
	end
	return mLoader:VRMLbone(ti)
end
function mirror(x)
	if config.mirror then
		return config.mirror(x)
	end
	return vector3(-x.x, x.y, x.z)
end
function updateSkin()
	local iframe=mEventReceiver.currFrame
	mLoader:setPose(m_pushLoc.po)
	local pose=vectorn()
	mLoader:getPoseDOF(pose)
	mSkin:setPoseDOF(pose)
	mMotionDOFcontainer.mot:row(iframe):assign(pose)
end
function getOriginalPos(skel, pose)
		skel:setPoseDOF(pose)
		
		local originalPos={}
		for i=1,skel:numBone()-1 do
			local opos=skel:bone(i):getFrame()*vector3(0,0,0)
			originalPos[i]=opos*config.skinScale
		end
		return originalPos
end

function createSkin()
	mSkin= RE.createVRMLskin(mLoader, true);	-- to create character
	mSkin:setThickness(3/config.skinScale)
	local s=config.skinScale 
	mSkin:scale(s,s,s);					-- motion data is in meter unit while visualization uses cm unit.
	mSkin:applyMotionDOF(mMotionDOFcontainer.mot)
	mSkin:setMaterial('lightgrey_transparent')
	RE.motionPanel():motionWin():addSkin(mSkin)
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
function ctor()
	mEventReceiver=EVR()
	this:create("Check_Button", "length-change only", "length-change only",0);
	this:widget(0):checkButtonValue(false);
	this:create("Check_Button", "symmetric editing", "symmetric editing",0);
	this:widget(0):checkButtonValue(false);

	this:create("Check_Button", "attach camera", "attach camera",1);
	this:widget(0):checkButtonValue(false);

	this:create("Button", "save current pose", "save current pose",1);
	this:create("Button", "remove redundant bones", "remove redundant bones",1);
	this:create("Button", "rotate light", "rotate light",1);
	this:create("Button", "export model", "export model",1);
	this:create("Button", "export model (overwrite)", "export model (overwrite)",1);

	if not config.skinScale then
		config.skinScale=1
	end
	local mot=loadMotion(config.skel, config.motion, nil)
	mLoader=mot.loader
	mMotionDOFcontainer=mot.motionDOFcontainer

	createSkin()


	do
		local vpos=RE.viewpoint().vpos:copy()
		local vat=RE.viewpoint().vat:copy()
		local rootpos=mMotionDOFcontainer.mot:row(0):toVector3(0)*config.skinScale
		local vdir=vat-vpos

		RE.viewpoint().vpos:assign(rootpos-vdir)
		RE.viewpoint().vat:assign(rootpos)
		RE.viewpoint():update()
	end

	do
		this:create('Choice', 'choose bone','choose bone',0)
		this:widget(0):menuSize(mLoader:numBone())
		this:widget(0):menuItem(0, 'choose bone')
		for i=1, mLoader:numBone()-1 do
			this:widget(0):menuItem(i, mLoader:bone(i):name())
		end
		this:widget(0):menuValue(0)
	end
	this:create('Choice', 'edit mode','edit mode',0)
	this:widget(0):menuSize(9)
	this:widget(0):menuItem(0, 'scale mesh','q')
	this:widget(0):menuItem(1, 'translate joint','e')
	this:widget(0):menuItem(2, 'choose X axis')
	this:widget(0):menuItem(3, 'choose Y axis')
	this:widget(0):menuItem(4, 'choose Z axis')
	this:widget(0):menuItem(5, 'choose YZX axis')
	this:widget(0):menuItem(6, 'choose ZX axis')
	this:widget(0):menuItem(7, 'choose fixed')
	this:widget(0):menuItem(8, 'show axes')
	this:widget(0):menuValue(1)

	this:create('Button', 'revert axes','revert axes')
	this:create('Button', 'finalize axes','finalize axes')
	this:create('Check_Button', 'test only 3 frames','test only 3 frames')
	this:widget(0):checkButtonValue(false)

	this:updateLayout()

	do
		local currFrame=0
		local originalPos=getOriginalPos(mLoader, mMotionDOFcontainer.mot:row(currFrame))
		mCON=Constraints(unpack(originalPos))
		mCON:connect(eventFunction)
	end

	camInfo={}
end

function eventFunction(ev, val)
	if ev=='selected' then
		local w=this:findWidget('choose bone')
		w:menuValue(val+1)
		mSelected=val+1
		w:redraw()
	end
end
function dtor()
	removeSkin()
end

function handleRendererEvent(ev, button, x, y)
	if mCON then
		mCON:handleRendererEvent(ev, button, x,y)
	end
	--print('button', button)
	if ev=="PUSH" then
		--print("PUSH")
		local editMode=this:findWidget('edit mode'):menuText()
		mLoader:setPoseDOF(mMotionDOFcontainer.mot:row(mEventReceiver.currFrame))
		local currentPose=Pose()
		mLoader:getPose(currentPose)
		if mSelected then
			local ri=mLoader:getRotJointIndexByTreeIndex(mSelected)
			if ri==-1 then return 1 end
			local b=mLoader:VRMLbone(mSelected)
			local parentBone=MainLib.VRMLloader.upcast(b:parent())
			m_pushLoc={
				x=x,y=y,ri=ri, 
				bone=b,
				parentBone=parentBone,
				qo=b:getFrame():copy(),
				qoffset=b:getOffsetTransform():copy(),
				lq=currentPose.rotations(ri):copy(),
				po=currentPose,
			}
			if this:findWidget("symmetric editing"):checkButtonValue() 
				and symmetricBoneName(m_pushLoc.bone:name()) then
				m_pushLoc.qoffset_symmetric=symmetricBone(m_pushLoc.bone):getOffsetTransform():copy()
			end
			return 1
		end
		return 0
	elseif ev=="DRAG" then
		if m_pushLoc then
			local editMode=this:findWidget('edit mode'):menuText()
			if mSelected then
				if editMode=='translate joint' then
					--local v=RE.viewpoint()
					--local x_axis, y_axis, z_axis=v:getAxes()
					--local dx=(x-m_pushLoc.x)*0.001*x_axis
					--local dy=(y-m_pushLoc.y)*-0.001*y_axis
					local delta=mCON:getPos(m_pushLoc.bone:treeIndex())/config.skinScale -m_pushLoc.qo.translation
					delta=rotate(delta ,m_pushLoc.parentBone:getFrame().rotation:inverse()) 

					if this:findWidget( "length-change only"):checkButtonValue() then
						-- project to bone axes
						local dir=m_pushLoc.qoffset.translation:copy()
						dir:normalize()
						local amt=dir:dotProduct(delta)
						delta=dir*amt
					end

					m_pushLoc.bone:setJointPosition(m_pushLoc.qoffset.translation+delta)
					if this:findWidget("symmetric editing"):checkButtonValue() 
						and symmetricBoneName(m_pushLoc.bone:name()) then
						symmetricBone(m_pushLoc.bone):setJointPosition(mirror(m_pushLoc.qoffset.translation+delta))
					end

					mLoader:updateInitialBone()
					local pose=mMotionDOFcontainer.mot:row(mEventReceiver.currFrame)
					mCON:setPos(getOriginalPos(mLoader, pose))
					mLoader:_updateMeshEntity()
					mSkin:setPoseDOF(pose)
				elseif editMode=='scale mesh' then
					local v=RE.viewpoint()
					local x_axis, y_axis, z_axis=v:getAxes()
					local dx=(x-m_pushLoc.x)
					local dy=(y-m_pushLoc.y)
					local distance=math.sqrt(dx*dx+dy*dy)*0.01

					m_pushLoc.bone:getFrame().rotation:assign(dq*m_pushLoc.qo.rotation)
					local pose=vectorn()
					mLoader:fkSolver():getPoseDOFfromGlobal(pose)
					mLoader:fkSolver():setPoseDOF(pose)
					mLoader:getPose(m_pushLoc.po)
				else
					-- does nothing
					local pose=mMotionDOFcontainer.mot:row(mEventReceiver.currFrame)
					mCON:setPos(getOriginalPos(mLoader, pose))
				end
				updateSkin()
			end
		end

		--print("DRAG")
		return 1
	elseif ev=="RELEASE" then
		local editMode=this:findWidget('edit mode'):menuText()
		if mSelected and m_pushLoc then
			if editMode=='translate joint' then
				local to=m_pushLoc.qoffset.translation	
				local tc=m_pushLoc.bone:getOffsetTransform().translation
				if to:length()>0.01 then

					local function scaleMesh(bone, to, tc)
						local q=quater()
						local q2=quater()
						q:axisToAxis(to, vector3(0,0,1))
						q2:axisToAxis(vector3(0,0,1), tc)
						local m=matrix4()
						m:identity()
						m:leftMultRotation(q)
						m:leftMultScaling(1,1, tc:length()/to:length())
						m:leftMultRotation(q2)
						print(q)
						local parentBone=MainLib.VRMLloader.upcast(bone:parent())
						parentBone:transformMeshLocal(m)
					end
					scaleMesh(m_pushLoc.bone,  to, tc)
					if this:findWidget("symmetric editing"):checkButtonValue() 
						and symmetricBoneName(m_pushLoc.bone:name()) then
						scaleMesh(symmetricBone(m_pushLoc.bone), m_pushLoc.qoffset_symmetric.translation, mirror(tc))
					end
					mLoader:_updateMeshEntity()
					removeSkin()
					createSkin()
					RE.motionPanel():motionWin():changeCurrFrame(mEventReceiver.currFrame)
					local pose=mMotionDOFcontainer.mot:row(mEventReceiver.currFrame)
					mSkin:setPoseDOF(pose)
					mCON:setPos(getOriginalPos(mLoader, pose))
				end
			elseif editMode=='show axes' then
				print(m_pushLoc.bone:name(), m_pushLoc.bone:HRPjointAxis(-1), axis)
				dbg.draw('Axes', m_pushLoc.bone:getFrame(), 'axes', config.skinScale)
			elseif string.sub(editMode,1,6)=='choose' then
				local axis=string.sub(editMode,8,8)
				if string.sub(editMode, 10)~='axis' then
					if editMode=='choose fixed' then
						axis=""
					elseif editMode=='choose ZX axis' then
						axis=string.sub(editMode, 8, 9)
					else
						axis=string.sub(editMode, 8, 10)
					end
				end
				
				if not mAxisInfo then 
					mAxisInfo=
					{
						mot=Motion(mMotionDOFcontainer.mot),
						axes={},
						currentAxes={},
					} 

					local markerBoneIndices=intvectorn()
					for i=2, mLoader:numBone()-1 do
						markerBoneIndices:pushBack(i)
					end
					local markerDistance=2/config.skinScale 
					mIKsolver=createIKsolverForRetargetting(mLoader, markerBoneIndices, markerDistance)
				end
				if not mAxisInfo.axes[m_pushLoc.bone:name()] then
					mAxisInfo.axes[m_pushLoc.bone:name()]=
						m_pushLoc.bone:HRPjointAxis(-1)
				end

				if axis=="" then
					-- fixed axis cannot be reverted
					mAxisInfo.axes[m_pushLoc.bone:name()]=""
					local ri=m_pushLoc.bone:rotJointIndex()

					local mot=mAxisInfo.mot
					for i=0, mot:numFrames()-1 do
						local rr=mot:pose(i).rotations
						for j=ri, rr:size()-2 do
							rr(j):set(rr(j+1))
						end
						rr:resize(rr:size()-1)
					end
				end
				print(m_pushLoc.bone:name(), m_pushLoc.bone:HRPjointAxis(-1), axis)
				dbg.draw('Axes', m_pushLoc.bone:getFrame(), 'axes', config.skinScale)
				mAxisInfo.currentAxes[m_pushLoc.bone:name()]=axis
				m_pushLoc.bone:setJointAxes(axis)
				mLoader:_initDOFinfo()

				-- convert quaternions to joint angles
				mMotionDOFcontainer.mot:set(mAxisInfo.mot)

				local pose=mMotionDOFcontainer.mot:row(mEventReceiver.currFrame)
				mSkin:setPoseDOF(pose)
			end
		end
		m_pushLoc=nil
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

function onCallback(w, userData)
	if w:id()=="attach camera" then
		camInfo.attachToBody=w:checkButtonValue();
	elseif w:id()=="remove redundant bones" then
		mLoader:removeAllRedundantBones()
	elseif w:id()=='revert axes' then
		if mAxisInfo then
			print('reverting axes')
			setAxes(mAxisInfo.axes)
			mAxisInfo.axes={}
			mAxisInfo.currentAxes={}
			-- convert quaternions to joint angles
			mMotionDOFcontainer.mot:set(mAxisInfo.mot)
			local pose=mMotionDOFcontainer.mot:row(mEventReceiver.currFrame)
			mSkin:setPoseDOF(pose)
		end
	elseif w:id()=='finalize axes' then
		if mAxisInfo then

			--mIKsolver.solver=MotionUtil.createFullbodyIkDOF_UTPoser(mLoader.dofInfo, mIKsolver.effectors)
			g_con=MotionUtil.Constraints() -- std::vector<MotionUtil::RelativeConstraint>
			g_con:resize(0)
			mIKsolver.solver=MotionUtil.createFullbodyIk_MotionDOF_MultiTarget_lbfgs(motB.loader.dofInfo, mIKsolver.effectors, g_con);
			-- solve ik for a few frames
			local startFrame=0
			local endFrame=mMotionDOFcontainer:numFrames()-1
			if this:findWidget('test only 3 frames'):checkButtonValue() then
				startFrame=mEventReceiver.currFrame
				endFrame=startFrame+3
			end

			for iframe=startFrame,endFrame do
				print('ik '..iframe..'/'..(mMotionDOFcontainer:numFrames()-1))
				setAxes(mAxisInfo.axes)
				mLoader:setPose(mAxisInfo.mot:pose(iframe))
				getEffectorPos()
				setAxes(mAxisInfo.currentAxes)
				mIKsolver.solver:IKsolve(mMotionDOFcontainer.mot:row(iframe), mIKsolver.effectorPos)
			end

			if mExportedModelFile then
				print('Exporting to '..mExportedModelFile..'.dof')
				mMotionDOFcontainer:exportMot(mExportedModelFile..'.dof')
			else
				util.msgBox("Please export model to save the resulting DOF file")
			end
			local pose=mMotionDOFcontainer.mot:row(mEventReceiver.currFrame)
			mSkin:setPoseDOF(pose)
		end

	elseif w:id()=='export model' then
		local fn=Fltk.chooseFile('choose a wrl file', '../Resource/motion/skeletonEditor/','*.wrl', true)

		if fn~='' then
			exportModel(fn, fn..'.dof')
		end
	elseif w:id()=='export model (overwrite)' then
		if Fltk.ask("Original files will be modified! Are you sure?") then
			exportModel(config.skel, config.motion)
		end
	elseif w:id()=='save current pose' then
		mLoader:setPoseDOF(mMotionDOFcontainer.mot:row(mEventReceiver.currFrame))
		local currentPose=Pose()
		mLoader:getPose(currentPose)
		RE.savePose(currentPose, 'temp.pose')
		print("current pose has written to temp.pose")
	elseif w:id()=='choose bone' then
		print(w:menuText())
		mSelected=w:menuValue()
		if mSelected==0 then
			mSelected=nil
		end
	elseif w:id()=='rotate light' then
		local osm=RE.ogreSceneManager()
		if osm:hasSceneNode("LightNode") then
			local lightnode=osm:getSceneNode("LightNode")
			lightnode:rotate(quater(math.rad(30), vector3(0,1,0)))
		end
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

	local pose=mMotionDOFcontainer.mot:row(mEventReceiver.currFrame)
	mCON:setPos(getOriginalPos(mLoader, pose))
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


function setAxes(tbl)
	for k,v in pairs(tbl) do
		local bone=MainLib.VRMLloader.upcast(mLoader:getBoneByName(k))
		bone:setJointAxes(v)
	end
end

function getEffectorPos()
	local c=mIKsolver.effectorPos:size()
	local effectors=mIKsolver.effectors
	local effectorPos=mIKsolver.effectorPos
	local src_bones=mIKsolver.src_bones
	for j=0, c-1 do
		effectorPos:at(j):assign(
		src_bones[j]:getFrame():toGlobalPos(
		effectors(j).localpos))
	end
	if false then -- for debugging
		for j=0, c-1 do
			dbg.draw('Sphere', effectorPos:at(j)*config.skinScale, 'marker'..j, 'red', 2)
		end
	end
end

function exportModel(fn, dofFile)

	mExportedModelFile=fn
	mLoader:updateInitialBone()
	local objFolder=string.sub(fn, 1, -5).."_sd"
	print('creating '..objFolder..'. (An error message would be shown if the folder already exists. You can ignore it.)')
	os.createDir(objFolder)
	local rotateX90=true
	if rotateX90 then
		local T=transf(quater(math.rad(90), vector3(1,0,0)),vector3(0,0,0))
		mLoader:bone(1):getLocalFrame():leftMult(T)
		mLoader:fkSolver():forwardKinematics()
	end

	mLoader:export(fn)

	if mAxisInfo then
		print('Exporting to '..dofFile..' because the # of DOFs has changed')
		mMotionDOFcontainer:exportMot(dofFile)
	end
end
