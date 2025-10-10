require("config")
require("module")
require("common")
require("subRoutines/QPservo")

config_gymnist_hand={
	"../Resource/motion/gymnist/gymnist.wrl",
	'../Resource/motion/gymnist/gymnist.dof',
	{
		{ 'lhand', vector3(0,0,0), },
		{ 'rhand', vector3(0,0,0), },
	},
	skinScale=100,
}

config_run={
	"../Resource/motion/justin_straight_run/justin_straight_run.wrl",
	"../Resource/motion/justin_straight_run/justin_straight_run.dof", 
	{
		{ 'lfemur', vector3(0,0,0),},
		{ 'rfemur', vector3(0,0,0),},
		{ 'ltibia', vector3(0,0,0),},
		{ 'rtibia', vector3(0,0,0),},
		{ 'lfoot', vector3(0.000000,-0.053740,0.111624),},
		{ 'rfoot', vector3(0.000000,-0.054795,0.112272),},
	},
	skinScale=100,
}

config_gymnist_all={
	"../Resource/motion/gymnist/gymnist.wrl",
	'../Resource/motion/gymnist/gymnist.dof',
	{ 
		{'lfoot', vector3(0.000000,-0.053740,0.111624)},
		{'rfoot', vector3(0.000000,-0.054795,0.112272)},
		{ 'lhand', vector3(0.000000,-0.053740,0.111624), },
		{ 'rhand', vector3(0.000000,-0.054795,0.112272), },
	},
	skinScale=100,
	initialHeight=0.07,
}
config=config_gymnist_all
--config=config_run

function check_s(vel, vel2, thr)
	if not thr or thr==0 then thr=0.001 end
	if (vel2-vel):length()<thr then 
		print("tested ok.")
	else
		print("test error.")
		dbg.console()
	end
end
if false then
	-- no random test
	math.random=function () return 0.5 end 
end
TestJacobian=LUAclass()

function TestJacobian:__init(skel, effector_list)
	self.skel=skel
	self.effector_list=effector_list
	self.numDof=3 -- 3: position only, 6: fix orientation
	local numDof=self.numDof
	self.J=matrixn(#effector_list*numDof, self.skel.dofInfo:numActualDOF())
	local idx=0

	for i,e in ipairs(effector_list) do
		if e[1]:treeIndex()~=1 then
			e.J=matrixn() -- temp matrix
			e.DJ=matrixn()
			idx=idx+numDof
		end
	end

	--self.simulator=Physics.DynamicsSimulator_gmbs_penalty() useCalcJacobianInstead=true
	--self.simulator=Physics.DynamicsSimulator_TRL_QP('libccd') 
	self.simulator=Physics.DynamicsSimulator_Trbdl_QP('libccd') -- jacobian, dotjacobian, massmatrix identical to gmbs
	self.simulator:registerCharacter(self.skel)
	self.simulator:init(1/120, Physics.DynamicsSimulator.EULER)

	if useCalcJacobianInstead then
		Physics.DynamicsSimulator_gmbs_penalty.calcJacobianAt=function (self, ichar, ibody, J, localpos)
			assert(localpos.x==0)
			assert(localpos.y==0)
			assert(localpos.z==0)
			self:calcJacobian(ichar, ibody, J)
		end
	end

	self.debug=false
	if self.debug then
		self.skin=RE.createVRMLskin(self.skel, true)
		self.skin:setThickness(0.03)
		self.skin:scale(100,100,100)
		self.skin:setTranslation(100,0,0)
	end
	self.count_ok=0
	self.count_not_ok=0
end
function TestJacobian:testJacobian(dtheta, i)

	--self.simulator:calcJacobian(0, e[1]:treeIndex(), e.J) J=e.J:sub(3,6)
	self.simulator:setLinkData(0, Physics.DynamicsSimulator.JOINT_VALUE, mPose)
	self.simulator:setLinkData(0, Physics.DynamicsSimulator.JOINT_VELOCITY, dtheta)
	self.simulator:initSimulation() -- very important
	local function check(vel, vel2)
		if (vel2-vel):length()<0.001 then
			print("tested ok.")
			self.count_ok=self.count_ok+1
		else
			print("test error.")
			dbg.console()
			self.count_not_ok=self.count_not_ok+1
		end
	end
	do
		local e=self.effector_list[i]

		print('test joint jacobian '..e[1]:name())
		self.simulator:calcJacobianAt(0, e[1]:treeIndex(), e.J, vector3(0,0,0))

		if true then
			local M=matrixn()
			local b=vectorn()
			self.simulator:calcMassMatrix3(0, M, b)
			print('m:', M)
			print('b:', b)
		end

		local vel=self.simulator:getWorldVelocity(0, e[1], vector3(0,0,0))
		local angvel=self.simulator:getWorldAngVel(0, e[1])

		local rootori=mPose:toQuater(3)
		local dq=vectorn()
		if self.simulator.dposeToDQ then
			-- this simulator uses world dq for jacobian.
			local dq2=vectorn()
			self.simulator:dposeToDQ(rootori, dtheta, dq2)
			self.simulator:getDQ(0, dq)
			-- dq == dq2
		else
			-- this simulator uses body dq for jacobian.
			self.simulator:getBodyDQ(0, dq)
		end

		local vel2=(e.J*dq:column()):column(0):toVector3(3)
		local angvel2=(e.J*dq:column()):column(0):toVector3(0)
		print(vel, vel2 )
		check(vel, vel2)
		print('angvel',angvel, angvel2)
		check(angvel, angvel2)
	end
end

function TestJacobian:testMomentumJacobian(dtheta)
	--self.simulator:calcJacobian(0, e[1]:treeIndex(), e.J) J=e.J:sub(3,6)
	self.simulator:setLinkData(0, Physics.DynamicsSimulator.JOINT_VALUE, mPose)
	self.simulator:setLinkData(0, Physics.DynamicsSimulator.JOINT_VELOCITY, dtheta)
	self.simulator:initSimulation() -- very important
	do

		print('test momentum jacobian ')
		local J=matrixn()
		local DJ=matrixn()
		self.simulator:calcMomentumDotJacobian(0, J, DJ)
		print('mmJ', J)
		print('mmDJ', DJ)

		local vel=self.simulator:calcMomentumCOM(0)

		local rootori=mPose:toQuater(3)
		local dq=vectorn()
		if self.simulator.dposeToDQ then
			-- this simulator uses world dq for jacobian.
			local dq2=vectorn()
			self.simulator:dposeToDQ(rootori, dtheta, dq2)
			self.simulator:getDQ(0, dq)
			-- dq == dq2
		else
			-- this simulator uses body dq for jacobian.
			self.simulator:getBodyDQ(0, dq)
		end

		local vel2=(J*dq:column()):column(0):copy()

		local M=vel2:toVector3(0)
		local F=vel2:toVector3(3)
		print('momentum', vel:M(), vel:F())
		print('momentum', M,F)
		check_s(vel:M(), M, M:length()*0.001)
		check_s(vel:F(), F, F:length()*0.001)
	end
end

function TestJacobian:testDeriv(dmot)

	local posVel={}
	local err={}
	for i,e in ipairs(self.effector_list) do
		posVel[i]=mMotionDOF:calcJointPosVel(e[1]:treeIndex(), e[2], 120)
	end
	posVel[0]=mMotionDOF:calcJointPosVel(1,vector3(0,0,0), 120)

	for i=0, #self.effector_list do
		err[i]={}
		err[i].posErr=vectorn(mMotionDOF:numFrames())
		err[i].posErr:setAllValue(0)
		err[i].velErr=vectorn(mMotionDOF:numFrames())
		err[i].velErr:setAllValue(0)
	end

	for i=1, mMotionDOF:numFrames()-2 do
		local theta=mMotionDOF:row(i)
		local dtheta=dmot:row(i)
		self.simulator:setLinkData(0, Physics.DynamicsSimulator.JOINT_VALUE, theta)
		self.simulator:setLinkData(0, Physics.DynamicsSimulator.JOINT_VELOCITY, dtheta)
		self.simulator:initSimulation() -- very important


		for ii=0, #self.effector_list do
			local e
			if ii==0 then
				e={mLoader:VRMLbone(1), vector3(0,0,0)}
			else
				e=self.effector_list[ii]
			end
			local pos=self.simulator:getWorldPosition(0, e[1], e[2])
			local vel=self.simulator:getWorldVelocity(0, e[1], e[2])

			
			local posErr=10000
			local velErr=10000
			for j=-1,1 do -- 주변 3개 프레임과 비교하는 이유는 속도가 급속히 변하는 경우 한프레임 정도 오차 있을 수 있기 때문.
				local pv=posVel[ii]:row(i+j) 
				posErr=math.min(posErr, (pos-pv:toVector3(0)):length())
				velErr=math.min(velErr, (vel-pv:toVector3(3)):length())
			end

			if mMotionDOFcontainer.discontinuity(i) or mMotionDOFcontainer.discontinuity(i+1) then 
				--skip
			else
				if ii==0 and velErr>0.2 then
					T1=MotionDOF.rootTransformation(mMotionDOF:row(i))
					T2=MotionDOF.rootTransformation(mMotionDOF:row(i+1))
					R=T1.rotation
					AV=self.simulator:getWorldAngVel(0, e[1])
					W=dmot:row(i):toVector3(4)
					V=dmot:row(i):toVector3(0)

					print('Too large error')
					dbg.console()
				end
				err[ii].posErr:set(i, posErr)
				err[ii].velErr:set(i, velErr)
			end
		end
	end
	for i=0, #self.effector_list do
		print('posErr min:', err[i].posErr:minimum())
		print('posErr max:', err[i].posErr:maximum())
		print('posErr avg:', err[i].posErr:avg())
		print('velErr min:', err[i].velErr:minimum())
		print('velErr max:', err[i].velErr:maximum())
		print('velErr avg:', err[i].velErr:avg())
	end
end

function TestJacobian:printSummary()
	print('Summary:\n ok:', self.count_ok, 'not ok:', self.count_not_ok)
end

do 

	TestEulerJacobian=LUAclass()

	function TestEulerJacobian:__init(skel, effector_list)
		self.skel=skel
		self.effector_list=effector_list
		self.numDof=3 -- 3: position only, 6: fix orientation
		local numDof=self.numDof
		self.J=matrixn(#effector_list*numDof, self.skel.dofInfo:numActualDOF())
		local idx=0
		local tj=matrixn(6*#effector_list, self.skel.dofInfo:numActualDOF())

		for i,e in ipairs(effector_list) do
			if e[1]:treeIndex()~=1 then
				e.J=tj -- temp matrix
				idx=idx+numDof
			end
		end

		local useEulerRoot=true
		assert(mLoader:bone(1):getRotationalChannels()=='ZXY')
		-- 'ZYX' or 'YXZ' works.
		mLoader:bone(1):setChannels('XYZ', 'YXZ')
		self.tree=MotionUtil.LoaderToTree(mLoader, useEulerRoot, false)

		--self.simulator=Physics.DynamicsSimulator_gmbs_penalty()
		self.simulator=Physics.DynamicsSimulator_TRL_QP('libccd')
		--self.simulator=Physics.DynamicsSimulator_Trbdl_QP('libccd')
		self.simulator:registerCharacter(self.skel)
		self.simulator:init(1/120, Physics.DynamicsSimulator.EULER)

		self.debug=false
		if self.debug then
			self.skin=RE.createVRMLskin(self.skel, true)
			self.skin:setThickness(0.03)
			self.skin:scale(100,100,100)
			self.skin:setTranslation(100,0,0)
		end
		self.count_ok=0
		self.count_not_ok=0
	end
	function TestEulerJacobian:testJacobian(dtheta, i)
		--self.simulator:calcJacobian(0, e[1]:treeIndex(), e.J) J=e.J:sub(3,6)
		self.simulator:setLinkData(0, Physics.DynamicsSimulator.JOINT_VALUE, mPose)
		self.simulator:setLinkData(0, Physics.DynamicsSimulator.JOINT_VELOCITY, dtheta)
		self.simulator:initSimulation() -- very important
		local function check(vel, vel2)
			if (vel2-vel):length()<0.001 then 
				print("tested ok.")
				self.count_ok=self.count_ok+1
			else
				print("test error.")
				dbg.console()
				self.count_not_ok=self.count_not_ok+1
			end
		end
		local estate=vectorn()
		do
			local q=vectorn()
			local dq=vectorn()
			self.simulator:getQ(0, q)
			self.simulator:getDQ(0, dq)
			--self.simulator:stateToEulerZYX(q, dq, estate)
			self.simulator:stateToEulerYXZ(q, dq, estate)


			if false then
				local state=vectorn()
				self.simulator:eulerYXZtoState(estate, state)
				print(((q..dq)-state):maximum())
				print(((q..dq)-state):minimum())
				dbg.console()
			end
		end
		local NDOF=self.simulator:dof(0)
		assert(estate:size()==NDOF*2)

		local q=estate:range(0, NDOF):copy()
		local dq=estate:range(NDOF, NDOF*2):copy()


		local tree=self.tree
		tree:setQ(q)

		do
			local e=self.effector_list[i]

			print('test euler jacobian '..e[1]:name())
			tree:calcJacobianTransposeAt(e.J, e[1]:treeIndex(), vector3(0,0,0))

			local J2=matrixn()
			self.simulator:calcJacobianAt(0, e[1]:treeIndex(), J2, vector3(0,0,0))

			local vel=self.simulator:getWorldVelocity(0, e[1], vector3(0,0,0))
			local angvel=self.simulator:getWorldAngVel(0, e[1])

			if true then
				tree:setDQ(dq)
				local vel2=tree:getWorldVelocity(e[1]:treeIndex())
				local angvel2=tree:getWorldAngVel(e[1]:treeIndex())
				check_s(vel, vel2)
				check_s(angvel, angvel2)
			end
			local rootori=mPose:toQuater(3)

			-- dq == dq2

			local Jdq=matrixn()
			Jdq:multAtB(e.J, dq:column())
			local vel2=Jdq:column(0):toVector3(0)

			tree:calcRotJacobianTranspose(e.J, e[1]:treeIndex())
			Jdq:multAtB(e.J, dq:column())
			local angvel2=Jdq:column(0):toVector3(0)

			print(vel, vel2 )
			check(vel, vel2)
			print('angvel',angvel, angvel2)
			check(angvel, angvel2)


		end
	end
	function TestEulerJacobian:testMomentumJacobian(dtheta, i)
		--self.simulator:calcJacobian(0, e[1]:treeIndex(), e.J) J=e.J:sub(3,6)
		self.simulator:setLinkData(0, Physics.DynamicsSimulator.JOINT_VALUE, mPose)
		self.simulator:setLinkData(0, Physics.DynamicsSimulator.JOINT_VELOCITY, dtheta)
		self.simulator:initSimulation() -- very important
		local estate=vectorn()
		do
			local q=vectorn()
			local dq=vectorn()
			self.simulator:getQ(0, q)
			self.simulator:getDQ(0, dq)
			--self.simulator:stateToEulerZYX(q, dq, estate)
			self.simulator:stateToEulerYXZ(q, dq, estate)
		end
		local NDOF=self.simulator:dof(0)
		assert(estate:size()==NDOF*2)

		local q=estate:range(0, NDOF):copy()
		local dq=estate:range(NDOF, NDOF*2):copy()


		local tree=self.tree
		tree:setQ(q)
		tree:setDQ(dq)

		do
			print('test momentum jacobian ')
			local J=matrixn()
			tree:calcMomentumJacobianTranspose(mLoader,J)
			local Jcom=matrixn()
			tree:calcCOMjacobianTranspose(mLoader,Jcom)

			--dbg.console()
			local J2=matrixn()
			local DJ=matrixn()
			self.simulator:calcMomentumDotJacobian(0, J2, DJ)

			local vel=tree:calcMomentumCOM(mLoader)
			if false then
				local vel2=self.simulator:calcMomentumCOM(0)
				local dq2=vectorn()
				self.simulator:getDQ(0, dq2)

				-- dq == dq2
				local vel3=(J2*dq2:column()):column(0):copy()
			end

			local rootori=mPose:toQuater(3)

			local Jdq=matrixn()
			Jdq:multAtB(J, dq:column())
			local vel2=Jdq:column(0):copy()

			local M=vel2:toVector3(0)
			local F=vel2:toVector3(3)
			check_s(vel:M(), M)
			check_s(vel:F(), F)
			print('momentum', M,F)
			print('momentum', vel:M(), vel:F())
		end
	end

	function TestEulerJacobian:printSummary()
		print('Summary:\n ok:', self.count_ok, 'not ok:', self.count_not_ok)
	end
end


function ctor()
	this:create("Button", "rotate light", "rotate light",1)
	this:create("Button", "testDeriv", "testDeriv",1)
	this:create("Button", "testDeriv zero_root", "testDeriv zero_root",1)
	
	this:updateLayout();

	mLoader=MainLib.VRMLloader (config[1])
	mMotionDOFcontainer=MotionDOFcontainer(mLoader.dofInfo, config[2])
	mMotionDOF=mMotionDOFcontainer.mot

	-- in meter scale
	for i=0, mMotionDOF:rows()-1 do
		mMotionDOF:matView():set(i, 1, mMotionDOF:matView()(i,1)+(config.initialHeight or 0))
	end

	-- rendering is done in cm scale
	mSkin= RE.createVRMLskin(mLoader, false);
	local s=config.skinScale
	mSkin:scale(s,s,s); -- motion data often is in meter unit while visualization uses cm unit.
	mPose=vectorn()
	mPose:assign(mMotionDOF:row(0));
	mSkin:applyMotionDOF(mMotionDOF)
	RE.motionPanel():motionWin():addSkin(mSkin)

	local effectors={}
	numCon=#config[3]
	for i=0,  numCon -1 do
		local conInfo=config[3][i+1]
		local bone=mLoader:getBoneByName(conInfo[1])
		local lpos=conInfo[2]

		effectors[i+1]={bone, lpos}
	end

	-- quaternion/angvel state
	mTest=TestJacobian(mLoader, effectors)

	-- euler/eulerrate state
	mTest2=TestEulerJacobian(mLoader, effectors)
	for i=1,10 do
		local q=mPose:toQuater(3)
		q.x=math.random()
		q:normalize()
		mPose:setQuater(3, q)

		if true then
			-- test euler conversion
			function toZUP_ori(q)
				return quater(q.w, q.z, q.x, q.y)
			end
			function toXUP_ori(q)
				return quater(q.w, q.y,  q.z, q.x);
			end

			local zyx=vector3()
			local yxz=vector3()
			do 
				toZUP_ori(q):getRotation('ZYX', zyx)
				q:getRotation('YXZ', yxz)
				check_s(yxz, zyx)
			end
			do
				local xzy=vector3()
				toXUP_ori(q):getRotation('ZYX', zyx)
				q:getRotation('XZY', xzy)
				check_s(xzy, zyx)
			end
			if false then
				local zxy=vector3()
				q:getRotation('ZXY', zxy)

				local q2=quater()
				q2:setRotation('ZYX', zxy)

				local R=quater(math.rad(90), vector3(0,0,1))
				dbg.console()
			end
		end
		local dtheta=vectorn(mPose:size())
		-- local angular velocities
		for i=0,dtheta:size()-1 do
			dtheta:set(i, math.random())
		end
		print('dtheta:', dtheta)
		for j=1, #effectors do
			print('effector', j)
			mTest:testJacobian(dtheta ,j )
			mTest2:testJacobian(dtheta ,j )
		end
		mTest:testMomentumJacobian(dtheta)
		mTest2:testMomentumJacobian(dtheta)
	end
	print('testJacobian1 finished. type "cont" to continue')
	if false then
		-- excluding root
		for i=1,10 do
			local dtheta=vectorn(mPose:size())
			-- local angular velocities
			for i=0,dtheta:size()-1 do
				dtheta:set(i, math.random())
			end
			dtheta:range(0,7):setAllValue(0)
			for j=1, #effectors do
				print('effector', j)
				mTest:testJacobian(dtheta,j )
				mTest2:testJacobian(dtheta,j )
			end
		end
	end
	print('testJacobian2 finished. type "cont" to continue')
	mTest:printSummary()
	mTest2:printSummary()

	dmot=calcDerivative(mMotionDOF, mMotionDOFcontainer.discontinuity)

	if true then
		-- test integration
		mMotionDOF_integ=mMotionDOF:copy()
		mSkin2= RE.createVRMLskin(mLoader, false);
		local s=config.skinScale
		mSkin2:scale(s,s,s); -- motion data often is in meter unit while visualization uses cm unit.
		mSkin2:setTranslation(0,0,100)
		mSkin2:applyMotionDOF(mMotionDOF_integ)
		RE.motionPanel():motionWin():addSkin(mSkin2)

		local startFrame=200
		mTest.simulator:setLinkData(0, Physics.DynamicsSimulator.JOINT_VALUE, mMotionDOF_integ:row(startFrame))
		local zero=dmot:row(0):copy()
		zero:setAllValue(0)
		for i=0,300 do
			local ddq=zero
			mTest.simulator:setLinkData(0, Physics.DynamicsSimulator.JOINT_VELOCITY, dmot:row(i+startFrame))
			mTest.simulator:initSimulation()

			if mTest.simulator.stepKinematic2 then
				mTest.simulator:stepKinematic2(0, ddq)
			else
				mTest.simulator:stepKinematic(ddq, zero,true )
			end
			local pose=vectorn()
			mTest.simulator:getLinkData(0, Physics.DynamicsSimulator.JOINT_VALUE,pose)
			mMotionDOF_integ:row(i+startFrame):assign(pose)
		end
	end
end

function onCallback(w, userData)  
	if w:id()=='rotate light' then
		local osm=RE.ogreSceneManager()
		if osm:hasSceneNode("LightNode") then
			local lightnode=osm:getSceneNode("LightNode")
			lightnode:rotate(quater(math.rad(30), vector3(0,1,0)))
		end
	elseif w:id()=="testDeriv" then
		print('TestDeriv full:')
		local dmot=calcDerivative(mMotionDOF, mMotionDOFcontainer.discontinuity)
		--local dmot=calcForwardDerivative(mMotionDOF, mMotionDOFcontainer.discontinuity)
		mTest:testDeriv(dmot)
	elseif w:id()=="testDeriv zero_root" then
		print('TestDeriv zero_root:')
		for i=0, mMotionDOF:numFrames()-1 do
			local tf=transf()
			tf:identity()
			MotionDOF.setRootTransformation(mMotionDOF:row(i), tf)
		end

		local dmot=calcDerivative(mMotionDOF, mMotionDOFcontainer.discontinuity)
		mTest:testDeriv(dmot)
	end
end

function dtor()
end

function frameMove(fElapsedTime)
end

