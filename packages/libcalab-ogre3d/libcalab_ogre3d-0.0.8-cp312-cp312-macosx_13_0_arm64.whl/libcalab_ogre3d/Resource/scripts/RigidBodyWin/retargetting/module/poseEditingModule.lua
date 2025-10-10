require("RigidBodyWin/subRoutines/Constraints")
require("moduleIK")

config_examples={
	gymnist={
		skel="../Resource/motion/gymnist/gymnist.wrl",
		motion="../Resource/motion/gymnist/gymnist.dof",
		EE={ 
			-- local pos here has to be vector3(0,0,0)
			{'ltibia', 'lfoot', vector3(0,0,0)},
			{'rtibia', 'rfoot', vector3(0,0,0)},
			{'lradius', 'lhand', vector3(0,0,0), reversed=true},
			{'rradius', 'rhand', vector3(0,0,0), reversed=true},
		},
		skinScale=100, -- meter to cm
	},
	justin={
		--skel="../Resource/motion/justin_straight_run/justin_straight_run.wrl",
		--motion="../Resource/motion/justin_straight_run/justin_straight_run.dof",
		skel="../Resource/motion/skeletonEditor/justin_straight_run_full.wrl",
		motion="../Resource/motion/skeletonEditor/justin_straight_run_full.wrl.dof",
		EE={ 
			-- local pos here has to be vector3(0,0,0)
			{'ltibia', 'lfoot', vector3(0,0,0)},
			{'rtibia', 'rfoot', vector3(0,0,0)},
			{'lradius', 'lhand', vector3(0,0,0), reversed=true},
			{'rradius', 'rhand', vector3(0,0,0), reversed=true},
		},
		skinScale=100,
	},
	ETRI={
		-- the skel wrl file is generated using rigidRiggingTool.lua
		--skel="../Samples/scripts/RigidBodyWin/retargetting/data/ETRI_Template_Skeleton/fitting2.wrl",
		--motion="../Samples/scripts/RigidBodyWin/retargetting/data/ETRI_Template_Skeleton/fitting2.bvh",
		--skel="../Resource/motion/skeletonEditor/fitting2_1dof.wrl",
		--motion="../Resource/motion/skeletonEditor/fitting2_1dof.wrl.dof",
		skel="../Resource/motion/skeletonEditor/fitting2_1dof_fixed.wrl",
		motion="../Resource/motion/skeletonEditor/fitting2_1dof_fixed.wrl.dof",
		EE={ 
			-- local pos here has to be vector3(0,0,0)
			{'LHip', 'LKnee', 'LAnkle', vector3(0,0,0)},
			{'RHip', 'RKnee', 'RAnkle', vector3(0,0,0)},
			{'LShoulder', 'LElbow', 'LWrist', vector3(0,0,0), reversed=true},
			{'RShoulder', 'RElbow', 'RWrist', vector3(0,0,0), reversed=true},
		},
		skinScale=2.54,
	},
	humanHanyang={
		-- the skel wrl file is generated using rigidRiggingTool.lua
		skel="../Resource/Jun/humanHanyang/humanHanyang.wrl",
		motion="../Resource/Jun/humanHanyang/humanHanyang.dof",
		EE={ 
			-- local pos here has to be vector3(0,0,0)
			{'LeftHip', 'LeftKnee', 'LeftAnkle', vector3(0,0,0)},
			{'RightHip', 'RightKnee', 'RightAnkle', vector3(0,0,0)},
			{'LeftShoulder', 'LeftElbow', 'LeftWrist', vector3(0,0,0), reversed=true},
			{'RightShoulder', 'RightElbow', 'RightWrist', vector3(0,0,0), reversed=true},
		},
		skinScale=100,
	},
	skipping={
		skel="../Resource/motion/justin_runf3.wrl",
		motion="../Resource/motion/justin_runf3.wrl.dof",
		EE={
			{'ltibia', 'lfoot', vector3(0,0,0)},
			{'rtibia', 'rfoot', vector3(0,0,0)},
			--{'lradius', 'lhand', vector3(0,0,0), reversed=true},
			--{'rradius', 'rhand', vector3(0,0,0), reversed=true},
		},
		skinScale=100,
	},
	dance1={
		-- the skel wrl file is generated using rigidRiggingTool.lua
		skel="../Resource/jae/dance/dance1_M.wrl",
		motion="../Resource/jae/dance/dance1_M.dof",
		EE={ 
			-- local pos here has to be vector3(0,0,0)
--			{'LeftHip', 'LeftKnee', 'LeftAnkle', vector3(0,0,0)},
--			{'RightHip', 'RightKnee', 'RightAnkle', vector3(0,0,0)},
			{'LeftShoulder', 'LeftElbow', 'LeftWrist', vector3(0,0,0), reversed=true},
			{'RightShoulder', 'RightElbow', 'RightWrist', vector3(0,0,0), reversed=true},
		},
		skinScale=100,
	},

}
PoseEditingModule=LUAclass()
function PoseEditingModule.prepareJointRotation(loader, b)
	local ri=loader:getRotJointIndexByTreeIndex(b:treeIndex())
	if ri==-1 then return nil end
	local currentPose=Pose()
	loader:getPose(currentPose)
	local editInfo={
		loader=loader,
		ri=ri,
		bone=b,
		qo=b:getFrame():copy(),
		lq=currentPose.rotations(ri):copy(),
		po=currentPose,
	}
	if b:childHead() then
		editInfo.child_origin=b:childHead():getFrame().translation:copy()
	else
		local dir=b:getFrame().translation -b:parent():getFrame().translation
		editInfo.child_origin=b:getFrame().translation+dir
	end
	return editInfo
end

function PoseEditingModule.rotateJoint(editInfo, editMode, dq)
	if editMode=='local edit' then
		editInfo.bone:getFrame().rotation:assign(dq*editInfo.qo.rotation)
		local pose=vectorn()
		editInfo.loader:fkSolver():getPoseDOFfromGlobal(pose)
		editInfo.loader:fkSolver():setPoseDOF(pose)
		editInfo.loader:getPose(editInfo.po)
	elseif editMode=='twist' then
		local from=editInfo.qo.translation
		local to=editInfo.child_origin
		local dir=(to-from):normalized()
		local normal
		if math.abs(dir:dotProduct(vector3(1,0,0)))<math.abs(dir:dotProduct(vector3(0,1,0))) then
			normal=dir:cross(vector3(1,0,0)):normalized()
		else
			normal=dir:cross(vector3(0,1,0)):normalized()
		end
		local after=dq*normal
		local dq_axis=quater()
		dq_axis:setAxisRotation(dir, normal, after)

		editInfo.bone:getFrame().rotation:assign(dq_axis*editInfo.qo.rotation)
		local pose=vectorn()
		editInfo.loader:fkSolver():getPoseDOFfromGlobal(pose)
		editInfo.loader:fkSolver():setPoseDOF(pose)
		editInfo.loader:getPose(editInfo.po)
	elseif editMode=='global edit' then
		-- current global
		-- q0*q1*lq= qo
		--> parent_qo==q0*q1==qo*lq:inverse()
		local parent_qo=editInfo.qo.rotation*editInfo.lq:inverse()
		-- desired global
		-- dq*gq2
		-- q0*q1*x=dq*qo
		-- thus,
		local x=parent_qo:inverse()*dq*editInfo.qo.rotation
		editInfo.po.rotations(editInfo.ri):assign(x)
		editInfo.po.rotations(editInfo.ri):normalize()
	end
end

function PoseEditingModule:updateSkin(editedPose)
	self.loader:setPose(editedPose)
	self.skin:setPose(editedPose)

	local pose=vectorn()
	self.loader:getPoseDOF(pose)
	self.pose:assign(pose)

	self.mode=nil

	if self.poseEditingEventFunction then
		self:poseEditingEventFunction("poseEdited", self.pose)
	end
end
function PoseEditingModule:updateSkinPoseDOF(pose)
	self.skin:setPoseDOF(pose)
	self.pose:assign(pose)
	self.mode=nil

	if self.poseEditingEventFunction then
		self:poseEditingEventFunction("poseEdited", self.pose)
	end
end


function PoseEditingModule:setSkin(skin, defaultMaterial)
	self.skin=skin
	self.defaultMaterial=defaultMaterial
end

-- motionDOFcontainer can be nil
function PoseEditingModule:__init(loader, motionDOFcontainer, skin, skinScale, EE, menuName)
	self.loader=loader
	self.motionDOFcontainer=motionDOFcontainer
	self.skin=skin
	self.skinScale=skinScale

	self.solver=MotionUtil.createFullbodyIk_MotionDOF_MultiTarget_lbfgs(loader.dofInfo);

	if not menuName then
		menuName='edit current pose'
	end
	self.menuName=menuName
	if EE then
		if EE=='auto' then
			EE={}
			local bone
			for i=1, self.loader:numBone()-1 do
				bone=self.loader:VRMLbone(i)
				if bone:childHead()==nil then
					--table.insert(EE, { bone, bone:localCOM()})
					table.insert(EE, { bone, vector3(0,0,0)})
				end
			end
			-- effectors, numCon, solver
			local effectors=MotionUtil.Effectors()
			effectors:resize(#EE)
			for i, v in ipairs(EE) do
				effectors(i-1):init(v[1], v[2])
				v[1]=v[1]:name()
			end
			self.mSolverInfo={
				effectors=effectors,
				numCon=#EE,
				solver=MotionUtil.createFullbodyIk_MotionDOF_MultiTarget_lbfgs(loader.dofInfo)
			}
		else
			self.mSolverInfo=createIKsolver(solvers.LimbIKsolver, self.loader, EE)
		end
	end
	self.EE=EE

	if this:widgetIndex(self.menuName)==1 then
		-- if there is no widget
		this:setUniformGuidelines(6)
		do
			this:create('Choice', self.menuName,self.menuName..'   bone',1 )
			this:widget(0):menuSize(self.loader:numBone())
			this:widget(0):menuItem(0, 'choose bone')
			for i=1, self.loader:numBone()-1 do
				this:widget(0):menuItem(i, self.loader:bone(i):name())
			end
			this:widget(0):menuValue(0)
		end
		this:create('Choice', self.menuName..' mode',self.menuName..'   mode',1)
		this:widget(0):menuSize(9)
		this:widget(0):menuItem(0, 'local edit')
		this:widget(0):menuItem(1, 'twist','q')
		this:widget(0):menuItem(2, 'global edit','w')
		this:widget(0):menuItem(3, 'translate','e')
		this:widget(0):menuItem(4, 'skeleton edit','t')
		this:widget(0):menuItem(5, 'IK','y')
		this:widget(0):menuItem(6, 'IK (COM)','u') -- works only when EE== 'auto' 
		this:widget(0):menuItem(7, 'IK (MM)','u') -- works only when EE== 'auto' 
		this:widget(0):menuItem(8, 'READ ONLY MODE')
		this:widget(0):menuValue(2)

		this:resetToDefault()	
		this:create('Button', 'undo last edit', 'undo last edit', 0,2)
		this:widget(0):buttonShortcut('FL_CTRL+z')
		-- the current pose becomes the new undo point.
		this:create('Button', 'commit', 'commit', 2)
		this:widget(0):buttonShortcut('FL_CTRL+t')

		if string.sub(self.menuName, 1,4)=='show' then
			this:widget(0):menuValue(4) -- READ ONLY MODE
			this:widget(0):clearVisible()
		else
			this:create('Check_Button', 'rotate in plane','rotate in plane', 0)
			this:widget(0):buttonShortcut('r')
			this:widget(0):checkButtonValue(false)
			this:create("Check_Button", "length-change only", "length-change only",0);
			this:widget(0):checkButtonValue(true);
			this:create("Check_Button", "symmetric editing", "symmetric editing",0);
			this:widget(0):checkButtonValue(false);
		end
	end

	do
		if self.motionDOFcontainer then
			local currFrame=0
			self.loader:setPoseDOF(self.motionDOFcontainer.mot:row(currFrame))
		end
		local originalPos={}
		for i=1,self.loader:numBone()-1 do
			local opos=self.loader:bone(i):getFrame()*vector3(0,0,0)
			originalPos[i]=opos*self.skinScale
		end
		for i=2,self.loader:numBone()-1 do
			if originalPos[i]:distance(originalPos[i-1])<1 then
				originalPos[i]:radd(vector3(0,5,0))
			end
		end
		--originalPos.prefix='boneToEdit'
		originalPos.prefix=self.menuName
		self.CON=Constraints(originalPos)
		self.CON:setOption('draggingDisabled', false)
		self.CON:setOption(2) -- sphere size
		self.CON.unselectRadius=50 -- sphere size for unselect
		self.CON:connect(self.eventFunction, self)
	end
end
function PoseEditingModule.eventFunction(ev, val, self)
	if ev=='selected' then
		local w=this:findWidget(self.menuName)
		w:menuValue(val+1)
		self:_selectBone(val+1)
		w:redraw()
	end
end

function PoseEditingModule:setPose(pose)

	if dbg.lunaType(pose)=='Pose' then
		self.mode='Pose'
	end
	-- reference!
	self.pose=pose
	self.origPose=pose:copy()
	self:updateCON()
end

function PoseEditingModule:_setPose()
	if self.mode=='Pose' then
		self.loader:setPose(self.pose)
		local pose=vectorn()
		self.loader:getPoseDOF(pose)
		return pose
	end
	self.loader:setPoseDOF(self.pose)
	return self.pose
end
function PoseEditingModule:handleRendererEvent(ev, button, x, y)
	if self.CON then
		self.CON:handleRendererEvent(ev, button, x,y)
		if self.CON.selectedVertex~=-1 then
			self:_selectBone(self.CON.selectedVertex+1)
		else
			self:_selectBone(nil)
		end
	end
	assert(self.pose)
	--print('button', button)
	if ev=="PUSH" then
		--print("PUSH")
		local editMode=this:findWidget(self.menuName..' mode'):menuText()
		if editMode=='READ ONLY MODE' then
			return 0
		end
		self:_setPose()
		local currentPose=Pose()
		self.loader:getPose(currentPose)
		if editMode=='translate' then
			if self.selected then
				local b=self.loader:bone(self.selected)
					if b:treeIndex()~=1 and b:parent():treeIndex()~=1 then
						local parent 
						do 
							-- find non-fixed parent
							parent=b
							while true do
								parent=parent:parent()
								if parent:treeIndex()==1 then 
									break
								end
								print(parent:name(), parent:getRotationalChannels())
								if parent:getRotationalChannels() then
									break
								end
							end
						end

						local parentBone=MainLib.VRMLloader.upcast(parent)
						local editInfo=self.prepareJointRotation(self.loader, parentBone)
						if not editInfo then
							return 1
						end
						self.pushLoc={
							x=x,y=y,ri=ri, 
							bone=b,
							parentBone=parentBone,
							qo=b:getFrame():copy(),
							pqo=parentBone:getFrame():copy(),
							editInfo=editInfo,
						}
						self.CON:setOption('draggingDisabled', false)
						return 1
					end
			end
			self.pushLoc={
				x=x,y=y,t=currentPose.translations(0):copy(),
				qo=self.loader:bone(1):getFrame():copy(),
				po=currentPose,
			}
			return 1
		elseif editMode:sub(1,2)=='IK'  then
			if self.selected then
				local b=self.loader:bone(self.selected)
				if self.EE and #self.EE>0 and ( b:name()==self.EE[1][#self.EE[1]-1] or
					b:name()==self.EE[2][#self.EE[2]-1] or
					b:name()==self.EE[3][#self.EE[3]-1] or
					b:name()==self.EE[4][#self.EE[4]-1]) then
					self.pushLoc={
						bone=b,
						mode='IK',
						pose=self.pose:copy()
					}
					self.CON:setOption('draggingDisabled', false)
					return 1
				end
				if b:treeIndex()==1 and editMode:sub(1,4)=='IK (' then
					self.pushLoc={
						mode='IK',
						pose=self.pose:copy()
					}
					self.CON:setOption('draggingDisabled', false)
					return 1
				end
			end
		elseif editMode=='skeleton edit' then
			if self.selected then
				self.CON:setOption('draggingDisabled', false)
				local ri=self.loader:getRotJointIndexByTreeIndex(self.selected)
				if ri==-1 then return 1 end
				local b=self.loader:VRMLbone(self.selected)
				local parentBone=MainLib.VRMLloader.upcast(b:parent())
				self.pushLoc={
					x=x,y=y,ri=ri, 
					bone=b,
					parentBone=parentBone,
					qo=b:getFrame():copy(),
					qoffset=b:getOffsetTransform():copy(),
					lq=currentPose.rotations(ri):copy(),
					po=currentPose,
				}
				if this:findWidget("symmetric editing"):checkButtonValue() 
					and symmetricBoneName(self.pushLoc.bone:name()) then
					self.pushLoc.qoffset_symmetric=symmetricBone(self.pushLoc.bone):getOffsetTransform():copy()
				end
				return 1
			end
		elseif self.selected then
			if editMode=='local edit' or editMode=='twist' or editMode=='global edit' then
				local b=self.loader:bone(self.selected)
				local editInfo=self.prepareJointRotation(self.loader, b)
				if not editInfo then return 1 end
				self.pushLoc={
					x,y,
					editInfo=editInfo
				}
			end
			return 1
		end
		return 0
	elseif ev=="DRAG" then
		if self.pushLoc then
			local editMode=this:findWidget(self.menuName..' mode'):menuText()
			if editMode:sub(1,2)=='IK' and self.selected then
				if self.pushLoc.mode=='IK' then
					-- IK

					local pose=self.pushLoc.pose:copy()
					local numCon=self.mSolverInfo.numCon
					local footPos=vector3N (numCon);
					local footOri=quaterN(numCon)
					local importance=vectorn(numCon)
					importance:setAllValue(1)
					local effectors=self.mSolverInfo.effectors
					for i=0,numCon-1 do
						local originalPos=self.CON.conPos(effectors(i).bone:treeIndex()-1)/self.skinScale
						footPos(i):assign(originalPos);
						footOri(i):assign(effectors(i).bone:getFrame().rotation)
						--dbg.namedDraw("Sphere", originalPos*self.skinScale, "x"..i)
					end
					if self.mSolverInfo.solver.IKsolve3 then
						self.mSolverInfo.solver:IKsolve3(pose, MotionDOF.rootTransformation(pose), footPos, footOri, importance)
					else

						local hasCOM=self.hasCOM or 0
						local hasMM=self.hasMM or 0

						local effMap=CT.colon(0,numCon,1)
						if hasCOM==1 then
							local footPosBackup=footPos:copy()
							footPos:resize(0)
							effMap:resize(0)
							for i=0, footPosBackup:size()-1 do
								if footPosBackup(i).y<0.1 then -- below 10cm
									footPos:pushBack(footPosBackup(i))
									effMap:pushBack(i)
								end
							end
							numCon=footPos:size()
						end
						local hasRot=1
						local mIK=self.mSolverInfo.solver
						local mEffectors=self.mSolverInfo.effectors
						mIK:_changeNumEffectors(footPos:size())
						mIK:_changeNumConstraints(hasCOM+hasRot+hasMM)
						for i=0, numCon-1 do
							local ii=effMap(i)
							mIK:_setEffector(i, mEffectors(ii).bone, mEffectors(ii).localpos)
						end
						if hasCOM==1 then
							print('hasCOM')
							local COM=self.CON.conPos(0)/self.skinScale
							mIK:_setCOMConstraint(0, COM)
						end
						if hasRot==1 then
							local bone=self.loader:bone(1)
							mIK:_setOrientationConstraint(hasCOM, bone, pose:toQuater(3));
						end
						if hasMM==1 then
							mIK:_setMomentumConstraint(hasCOM+hasRot, vector3(0,0,0), vector3(0,0,0));
						end
						mIK:_effectorUpdated()
						mIK:IKsolve(pose, footPos)
					end
					self.pose:assign(pose)
					self.skin:setPoseDOF(pose)
					if self.poseEditingEventFunction then
						self:poseEditingEventFunction("poseEdited", self.pose)
					end
				end
			elseif editMode=='translate' and self.selected then

				if self.pushLoc.bone then
						local pl=self.pushLoc
						local cPos=self.CON.conPos(self.pushLoc.bone:treeIndex()-1)/self.skinScale
						local oPos=pl.qo.translation
						local pPos=pl.pqo.translation

						local v1=oPos-pPos
						local v2=cPos-pPos
						local delta=quater()
						delta:axisToAxis(v1, v2)

						self.rotateJoint(self.pushLoc.editInfo, 'global edit', delta)
						self:updateSkin(self.pushLoc.editInfo.po)
				else
					local cPos=self.CON.conPos(0)/self.skinScale
					self.pushLoc.po.translations(0):assign(cPos)
					self:updateSkin(self.pushLoc.po)
				end
			elseif editMode=='skeleton edit' then
				if self.selected and self.pushLoc then
					--local v=RE.viewpoint()
					--local x_axis, y_axis, z_axis=v:getAxes()
					--local dx=(x-self.pushLoc.x)*0.001*x_axis
					--local dy=(y-self.pushLoc.y)*-0.001*y_axis
					local delta=self.CON:getPos(self.pushLoc.bone:treeIndex())/self.skinScale -self.pushLoc.qo.translation
					delta=rotate(delta ,self.pushLoc.parentBone:getFrame().rotation:inverse()) 

					if this:findWidget( "length-change only"):checkButtonValue() then
						-- project to bone axes
						local dir=self.pushLoc.qoffset.translation:copy()
						dir:normalize()
						local amt=dir:dotProduct(delta)
						delta=dir*amt
					end

					self.pushLoc.bone:setJointPosition(self.pushLoc.qoffset.translation+delta)
					if this:findWidget("symmetric editing"):checkButtonValue() 
						and symmetricBoneName(self.pushLoc.bone:name()) then
						symmetricBone(self.pushLoc.bone):setJointPosition(mirror(self.pushLoc.qoffset.translation+delta))
					end

					self.loader:updateInitialBone()
					self:updateCON()
					self.loader:_updateMeshEntity()
					self:updateSkin(self.pushLoc.po)
				end
			elseif self.selected then
				local v=RE.viewpoint()
				local x_axis, y_axis, z_axis=v:getAxes()
				local speed=0.002
				local dx=quater((x-self.pushLoc[1])*speed, y_axis)
				local dy=quater((y-self.pushLoc[2])*speed, x_axis)
				if button==2 or this:findWidget('rotate in plane'):checkButtonValue() then
					dy=quater((y-self.pushLoc[2])*speed, z_axis)
				end
				local dq=dx*dy

				self.rotateJoint(self.pushLoc.editInfo, editMode, dq)
				self:updateSkin(self.pushLoc.editInfo.po)
			end
		end

		--print("DRAG")
		return 1
	elseif ev=="RELEASE" then
		local editMode=this:findWidget(self.menuName..' mode'):menuText()

		if editMode=='skeleton edit' then
			local to=self.pushLoc.qoffset.translation	
			local tc=self.pushLoc.bone:getOffsetTransform().translation
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
					--print(q)
					local parentBone=MainLib.VRMLloader.upcast(bone:parent())
					parentBone:transformMeshLocal(m)
				end
				scaleMesh(self.pushLoc.bone,  to, tc)
				if this:findWidget("symmetric editing"):checkButtonValue() 
					and symmetricBoneName(self.pushLoc.bone:name()) then
					scaleMesh(symmetricBone(self.pushLoc.bone), self.pushLoc.qoffset_symmetric.translation, mirror(tc))
				end
				self.loader:_updateMeshEntity()
				self:removeSkin()
				self:createSkin()
				self.skin:setPoseDOF(self:_setPose())
				self:updateCON()
			end
			self.CON:setOption('draggingDisabled', true)
		end
		if self.selected and self.pushLoc then
			if editMode=='translate' then
				self.CON:setOption('draggingDisabled', true)
				self:updateCON()
			end
		end
		self:updateCON()
		self.pushLoc=nil
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

function PoseEditingModule:saveCurrentPose()
		self:_setPose()
		local currentPose=Pose()
		self.loader:getPose(currentPose)
		RE.savePose(currentPose, 'temp.pose')
		print("current pose has written to temp.pose")
end

function PoseEditingModule:loadCurrentPose()
		self:_setPose()
		local currentPose=Pose()
		RE.loadPose(currentPose, 'temp.pose')
		self.loader:setPose(currentPose)
		print("current pose is loaded")
end

function PoseEditingModule:onCallback(w, userData)
	if w:id()=='save current pose' then
		self:saveCurrentPose()
	elseif w:id()=='load current pose' then
		self:loadCurrentPose()
	elseif w:id()=='undo last edit' then
		self.pose:assign(self.origPose)
		self:setPose(self.pose)
		if self.poseEditingEventFunction then
			self:poseEditingEventFunction('undo last edit')
		end
	elseif w:id()=='commit' then
		print('current pose becomes the new undo point!')
		self.origPose:assign(self.pose)
	elseif w:id()==self.menuName then
		print(w:menuText())
		self:_selectBone(w:menuValue())
	elseif w:id()==self.menuName ..' mode' then
		local t=w:menuText()
		self.hasCOM=nil
		self.hasMM=nil
		if t:sub(1,2)=='IK' or t=='translate' then
			self.CON:setOption('draggingDisabled', false)
			if t=='IK (COM)' then
				self.hasCOM=1
			elseif t=='IK (MM)' then
				self.hasCOM=1
				self.hasMM=1
			end
			self:updateCON()
		else
			self.CON:setOption('draggingDisabled', true)
			self:updateCON()
		end
	end
end
function PoseEditingModule:_selectBone(i)
	if i==0 then i=nil end

	local defaultMat=self.defaultMaterial 
	if self.selected and self.selected~=i and defaultMat then
		if self.skin.setBoneMaterial then 
			self.skin:setBoneMaterial(self.selected, defaultMat)
		end
	end
	self.selected=i
	if defaultMat and i then
		if self.skin.setBoneMaterial then 
			self.skin:setBoneMaterial(i, 'green_transparent')
		end
	end
end
function PoseEditingModule:updateCON()
	self:_setPose()
	local originalPos={}
	for i=1,self.loader:numBone()-1 do
		local opos=self.loader:bone(i):getFrame()*vector3(0,0,0)
		originalPos[i]=opos*self.skinScale
	end

	if self.hasCOM==1 then
		self.loader:setPoseDOF(self.pose)
		local COM=self.loader:calcCOM()
		originalPos[1]=COM*self.skinScale
	end
		for i=2,self.loader:numBone()-1 do
			if originalPos[i]:distance(originalPos[i-1])<0.001 then
				originalPos[i]:radd(vector3(0,5,0))
			end
		end
	self.CON:setPos(originalPos)
	if self.poseEditingEventFunction then
		self:poseEditingEventFunction("updateCON", self.pose)
	end
end
function PoseEditingModule:createSkin()
	self.skin= RE.createVRMLskin(self.loader, false);	-- to create character
	local s=self.skinScale 
	self.skin:scale(s,s,s);					-- motion data is in meter unit while visualization uses cm unit.
	--self.skin:applyMotionDOF(mMotionDOFcontainer.mot)
	self.skin:setMaterial('lightgrey_transparent')
	--RE.motionPanel():motionWin():addSkin(self.skin)
end
function PoseEditingModule:removeSkin()
	self.skin:setVisible(false)
	RE.motionPanel():motionWin():detachSkin(self.skin)
	self.skin=nil
	collectgarbage()
	collectgarbage()
	collectgarbage()
end
