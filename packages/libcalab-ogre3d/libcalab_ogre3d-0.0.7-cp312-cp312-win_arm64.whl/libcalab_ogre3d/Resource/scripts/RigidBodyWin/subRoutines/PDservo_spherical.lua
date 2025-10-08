PDservo_spherical=LUAclass()

-- returns motQ, motDQ which are compatible with loader_spherical
function PDservo_spherical.convertMotionState(loader_euler, loader_spherical, motionDOF_euler, frame_rate)

	local DMotionDOF_euler=motionDOF_euler:calcDerivative(frame_rate)

	-- important!!!
	-- convert loader, motionDOF, and its time-derivative to new formats.

	local nf=motionDOF_euler:numFrames()
	local motQ=matrixn(nf, loader_spherical.dofInfo:numDOF())
	local motDQ=matrixn(nf, loader_spherical.dofInfo:numActualDOF())

	local tree=MotionUtil.LoaderToTree(loader_euler, false,false)

	local euler_dofInfo=loader_euler.dofInfo
	local spherical_dofInfo=loader_spherical.dofInfo

	for i=0, nf-1 do
		tree:setPoseDOF(euler_dofInfo, motionDOF_euler:row(i))
		tree:setVelocity(euler_dofInfo, DMotionDOF_euler:row(i))

		tree:getSphericalState(spherical_dofInfo, motQ:row(i), motDQ:row(i))
	end
	return motQ, motDQ
end

function PDservo_spherical:__init(dofInfo)
	self.theta=vectorn()
	self.dtheta=vectorn()
	self.theta_d=vectorn() -- desired q
	self.dtheta_d=vectorn() -- desired dq
	self.controlforce=vectorn()
	self.dofInfo=dofInfo
end

function PDservo_spherical:initPDservo(startf, endf,motQ, motDQ, simulator, ichara)
	local csize=vector3()
	local dofInfo=simulator:skeleton(ichara).dofInfo
	csize.y=simulator:numSphericalJoints(ichara)
	csize.x=dofInfo:numDOF() -csize.y*4

	-- for the root joint and other 1-DOF joints
	self.kp=vectorn(csize.x)
	self.kd=vectorn(csize.x)
	self.kp:setAllValue(k_p)
	self.kd:setAllValue(k_d)
	
	-- for ball joints
	self.k_p=k_p
	self.k_d=k_d

	-- exclude root translation
	self.kp:range(0,3):setAllValue(0)
	self.kd:range(0,3):setAllValue(0)

	print ("kp=",self.kp)
	print ("kd=",self.kd)

	local clampTorque=800
	local clampForce=8000

	if model.clampTorque~=nil then
		clampTorque=model.clampTorque
	end

	if model.clampForce~=nil then
		clampForce=model.clampForce
	end
	self.clampMax=vectorn(csize.x+csize.y*3)
	self.clampMax:setAllValue(clampTorque)
	self.clampMin=self.clampMax*-1

	self.startFrame=startf
	self.endFrame=endf
	self.currFrame=startf
	self.deltaTime=0

	local q=vectorn()
	local dq=vectorn()
	simulator:initSimulation()
	simulator:getSphericalState(ichara, q, dq)

	self.nonQsize=csize.x
	self.motions={motQ, motDQ}
end

-- generate FBtorque
function PDservo_spherical:generateTorque(simulator)

	self.currFrame=(simulator:currentTime()+self.deltaTime)*model.frame_rate+self.startFrame
	--print(self.currFrame) -- extremely slow.
	if self.currFrame>self.endFrame-1 then
		return false
	end

	self:_generateTorque(simulator, self.currFrame)
	return true
end

function PDservo_spherical:stepSimul(simulator, drawDebugInformation)
	simulator:setTau(0, self.controlforce)
	if drawDebugInformation then
		simulator:drawDebugInformation()
	end
	simulator:stepSimulation()
end

function PDservo_spherical:_generateTorque(simulator, frame)

	simulator:getSphericalState(0, self.theta, self.dtheta)

	self.motions[1]:sampleRow(frame, self.theta_d)
	self.motions[2]:sampleRow(frame, self.dtheta_d)
	
	local startQ=self.nonQsize
	local numBallJoints=(self.theta_d:size()-startQ)/4

	local function normalizeQ(v, i)
		v:setQuater(i, v:toQuater(i):Normalize())
	end

	local function normalizeTheta(theta)
		for i=0, numBallJoints-1 do
			normalizeQ(theta, startQ+i*4)
		end
	end
	normalizeTheta(self.theta_d)

	--   self.dtheta_d:setAllValue(0)
	self.controlforce:setSize(self.dtheta_d:size())


	local delta=self.theta_d:range(0, startQ)-self.theta:range(0,startQ)
	MainLib.VRMLloader.projectAngles(delta) -- [-pi, pi]


	self.controlforce:range(0, startQ):assign(self.kp*delta +
	self.kd*(self.dtheta_d:range(0, startQ)-self.dtheta:range(0,startQ)))


	-- now consider ball joints
	for i=0, numBallJoints-1 do
		local currentQuat=self.theta:toQuater(startQ+i*4)
		local desiredQuat=self.theta_d:toQuater(startQ+i*4)
		local relRot=currentQuat:inverse()*desiredQuat
		local qError=relRot:rotationVector() -- rotation vector

		local qdoterr=self.dtheta_d:toVector3(startQ+i*3)-self.dtheta:toVector3(startQ+i*3)

		local force=self.k_p*qError+self.k_d*qdoterr

		if i==0 then force:zero() end
		self.controlforce:setVec3(startQ+i*3, force)
	end

	self.controlforce:clamp(self.clampMin, self.clampMax)
end

function PDservo_spherical:rewindTargetMotion(simulator)
	self.deltaTime=-1*simulator:currentTime()
end


PoseMaintainer_spherical=LUAclass()

function PoseMaintainer_spherical:__init(skeletonIndex)
	self.theta=vectorn()
	self.dtheta=vectorn()
	self.theta_d=vectorn() -- desired q
	self.dtheta_d=vectorn() -- desired dq
	self.controlforce=vectorn()

	self.skeletonIndex=skeletonIndex or 0


end

function PoseMaintainer_spherical:init(skel, simulator, k_p, k_d)
	local csize=vector3()
	local ichara=self.skeletonIndex
	local dofInfo=simulator:skeleton(ichara).dofInfo
	csize.y=simulator:numSphericalJoints(ichara)
	csize.x=dofInfo:numDOF() -csize.y*4

	-- for the root joint and other 1-DOF joints
	self.kp=vectorn(csize.x)
	self.kd=vectorn(csize.x)
	self.kp:setAllValue(k_p)
	self.kd:setAllValue(k_d)
	
	-- for ball joints
	self.k_p=k_p
	self.k_d=k_d

	if dofInfo:hasTranslation(1) then
		-- exclude root translation
		self.kp:range(0,3):setAllValue(0)
		self.kd:range(0,3):setAllValue(0)
		self.freeRoot=true
	end


	print ("kp=",self.kp)
	print ("kd=",self.kd)

	local clampTorque=800
	local clampForce=8000

	if model then
		if model.clampTorque~=nil then
			clampTorque=model.clampTorque
		end

		if model.clampForce~=nil then
			clampForce=model.clampForce
		end
	end
	self.clampMax=vectorn(csize.x+csize.y*3)
	self.clampMax:setAllValue(clampTorque)
	self.clampMin=self.clampMax*-1

	local q=vectorn()
	local dq=vectorn()
	simulator:initSimulation()
	simulator:getSphericalState(self.skeletonIndex, q, dq)

	self.nonQsize=q:size()-csize.y*4
	assert(q:toQuater(self.nonQsize):length()>0.99)
	self.theta_d=q
	self.dtheta_d=dq
	self.dtheta_d:zero()
end

function PoseMaintainer_spherical:stepSimul(simulator, drawDebugInformation)
	simulator:setTau(self.skeletonIndex, self.controlforce)
	if drawDebugInformation then
		simulator:drawDebugInformation()
	end
	simulator:stepSimulation()
end

function PoseMaintainer_spherical:generateTorque(simulator)

	simulator:getSphericalState(self.skeletonIndex, self.theta, self.dtheta)

	--[[ continuous sampling ]]--
	--   print("theta",self.theta)

	-- desired (target) pose
	

	local startQ=self.nonQsize
	local numBallJoints=(self.theta_d:size()-startQ)/4

	local function normalizeQ(v, i)
		v:setQuater(i, v:toQuater(i):Normalize())
	end

	local function normalizeTheta(theta)
		for i=0, numBallJoints-1 do
			normalizeQ(theta, startQ+i*4)
		end
	end
	normalizeTheta(self.theta_d)

	--   self.dtheta_d:setAllValue(0)
	self.controlforce:setSize(self.dtheta_d:size())


	local delta=self.theta_d:range(0, startQ)-self.theta:range(0,startQ)
	MainLib.VRMLloader.projectAngles(delta) -- [-pi, pi]


	self.controlforce:range(0, startQ):assign(self.kp*delta +
	self.kd*(self.dtheta_d:range(0, startQ)-self.dtheta:range(0,startQ)))

	--local errLen=vectorn(numBallJoints)
	--local errLen2=vectorn(numBallJoints)

	-- now consider ball joints
	for i=0, numBallJoints-1 do
		local currentQuat=self.theta:toQuater(startQ+i*4)
		local desiredQuat=self.theta_d:toQuater(startQ+i*4)
		local relRot=currentQuat:inverse()*desiredQuat
		relRot:align(quater(1,0,0,0))
		local qError=relRot:rotationVector() -- rotation vector
		--errLen:set(i, qError:length())
		local qdoterr= self.dtheta_d:toVector3(startQ+i*3)-self.dtheta:toVector3(startQ+i*3)
		--errLen2:set(i, qdoterr:length())

		local force=self.k_p*qError+self.k_d*qdoterr


		self.controlforce:setVec3(startQ+i*3, force)
	end
	if self.freeRoot then
		self.controlforce:range(0,3):zero() 
		self.controlforce:range(startQ,startQ+3):zero()
	end

	--RE.output2('errLen', errLen)
	--RE.output2('errLenDQ', errLen2)
	self.controlforce:clamp(self.clampMin, self.clampMax)
	return true
end

