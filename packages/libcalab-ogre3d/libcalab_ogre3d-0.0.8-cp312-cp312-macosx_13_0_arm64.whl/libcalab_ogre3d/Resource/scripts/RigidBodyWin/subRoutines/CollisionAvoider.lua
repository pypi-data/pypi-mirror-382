local CA={}
CA.CollisionAvoider=LUAclass()


if false then
	-- use IKChain
	function CollisionAvoid:setIter(n)
		self.mIK.iter=n
	end
	function CollisionAvoid:createIKsolver(ikc, kneeIndex, axis)
		self.mEffectors:resize(2);
		self.mEffectors(0):init(mLoader:getBoneByName(ikc[1][2]), ikc[1][3])
		self.mEffectors(1):init(mLoader:getBoneByName(ikc[2][2]), ikc[2][3])

		self.mIK=IKChain(mLoader, ikc, kneeIndex, axis, self.mEffectors, self.g_con, {true, false,false})
	end
end
function CA.CollisionAvoider:__init(mLoader, mMotionDOFcontainer, initialPose, config)
	assert(mLoader)
	assert(mMotionDOFcontainer)
	self.mLoader=mLoader
	self.mIntegrator=VelocityFields(mLoader, mMotionDOFcontainer,initialPose )
	self.mIntegrator.pose:assign(initialPose)
	self.mFilter=OnlineFilter(mLoader, self.mIntegrator.pose, config.filterSize or 5)
	--self.mFilter=SDSFilter(mLoader, 1)
	self.mCollAvoid={}
	if false then
		mIK=LimbIKsolver(mLoader.dofInfo,mEffectors, CT.ivec(lknee:treeIndex(), rknee:treeIndex()), CT.vec(1,1))
	else
		self.mCollAvoid[0]=CollisionAvoid(mLoader, config)
	end
	local mCollAvoid=self.mCollAvoid
	self.mIntegrator.pose:assign(initialPose)

	local mObstacles={}
	self.mObstacles=mObstacles

	if not obstaclePos then
		obstaclePos={}--vector3(30,0,0), vector3(-30,0,0), vector3(60,30,0), vector3(0,0,0),vector3(110,100,0) }
		obstacleSize={}--vector3(20,20,40),vector3(20,20,40), vector3(20,20,40), vector3(1000,0,2000),vector3(0,0,0)}
		obstacleType={}--"BOX","SPHERE","CAPSULE","BOX", "CHAR"}
	end

	for i=1,#obstaclePos do
		mObstacles[i]=Geometry()

		do 
			local mesh=mObstacles[i]
			if obstacleType[i]=="BOX" then
				mesh:initBox(obstacleSize[i])
			elseif obstacleType[i]=="SPHERE" then
				mesh:initEllipsoid(obstacleSize[i])
			elseif obstacleType[i]=="CAPSULE" then
				mesh:initCapsule(obstacleSize[i].x, obstacleSize[i].z)
			elseif obstacleType[i]=="CHAR" then
				mObstacles[i]=MainLib.VRMLloader (config[1])
				mCollAvoid[i]=CollisionAvoid(mObstacles[i], config)
			else
				mesh:initPlane(obstacleSize[i].x, obstacleSize[i].z)
			end

			if obstacleType[i]~="CHAR" then
				local mat=matrix4()
				mat:identity()
				mat:leftMultScale(1/config.skinScale)
				mesh:transform(mat)
			end
		end
	end
	--mObjectList:registerMesh(mObstacles[1], 'meshtest'):getLastCreatedEntity():setMaterialName('lightgrey_transparent')
	--mObjectList:findNode('meshtest'):scale(config.skinScale)

	local mChecker=CollisionChecker()
	self.mChecker=mChecker
	local obj={mLoader, unpack(mObstacles)}
	for i,v in ipairs(obj) do
		local ltype=getmetatable(v).luna_class
		if ltype=='MainLib.VRMLloader' then
			mChecker.collisionDetector:addModel(v)
		else
			mChecker.collisionDetector:addObstacle(v)
		end
	end

	for i=1,#obstaclePos do

		local initialState=vectorn(7)
		local obstacleOffset=vector3(0,10,0)
		if obstacleType[i]=="CHAR" then
			initialState:resize(mObstacles[i].dofInfo:numDOF())
		end
		initialState:setVec3(0, (obstaclePos[i]+obstacleOffset)/config.skinScale)
		initialState:setQuater(3,quater(1,0,0,0))
		mChecker:setPoseDOF(i, initialState)
	end
	local mObstacleSkins={}
	local s=config.skinScale

	for i=1, #obstaclePos do
		local v=mChecker.collisionDetector:getModel(i)
		mObstacleSkins[i]= RE.createVRMLskin(v, false);
		mObstacleSkins[i]:scale(s,s,s)
		if config.ignoreCollPairs then
			if not config.ignoreCollPairs[i] then
				mChecker:registerPair(0,i) -- 0 means mLoader, 1 means mObstacles[1]
			end
		else
			mChecker:registerPair(0,i) -- 0 means mLoader, 1 means mObstacles[1]
		end
		local state=mChecker.pose[i]
		mObstacleSkins[i]:setPoseDOF(state)
	end
	self.mObstacleSkins=mObstacleSkins

	local collpairs=config.collpairs
	self.mChecker:registerSelfPairs(0,collpairs )-- 0 means mLoader, 1 means mObstacles[1]
	self.config=config
end

function CA.CollisionAvoider:getEffectorPos()
	pos = vector3N()
	pos:setSize(2)
	for i=0, 1 do
		local mEffectors=self.mCollAvoid[0].mEffectors
		local originalPos=mEffectors(i).bone:getFrame():toGlobalPos(mEffectors(i).localpos)*100
		pos(i):assign(originalPos)
	end
	return pos
end
function CA.CollisionAvoider:oneStep(currPose, currDPose, nextPose, blendWeight, mCON)
	local mLoader=self.mLoader
	local mIntegrator=self.mIntegrator
	local mCollAvoid=self.mCollAvoid
	local mChecker=self.mChecker
	local mObstacles=self.mObstacles
	local mFilter=self.mFilter
	local mObstacleSkins=self.mObstacleSkins 
	local speedLimit=self.config.speedLimit or 100
	mIntegrator.pose:assign(currPose)
	mIntegrator:stepKinematic(currDPose, nextPose, blendWeight, speedLiit)


	local mEffectors=mCollAvoid[0].mEffectors
	mLoader:setPoseDOF(mIntegrator.pose);
	local opos={}
	for i=0,1 do
		local originalPos=mEffectors(i).bone:getFrame():toGlobalPos(mEffectors(i).localpos)
		opos[i]=originalPos
	end
	mLoader:setPoseDOF(mIntegrator.pose);

	-- local pos to global pos
	local footPos=vector3N(2)
	for i=0,1 do
		--local originalPos=mEffectors(i).bone:getFrame():toGlobalPos(mEffectors(i).localpos)
		local originalPos=opos[i]

		local delta=vector3(0,0,0)
		if mCON then
		--print(i, mCON.conPos(i))
			delta=mCON.conPos(i)*0.01-originalPos
			--delta=math.clampVec3(delta, 0.15)
		end

		footPos(i):assign(originalPos+delta);
	end
	mCollAvoid[0].mIK:_changeNumConstraints(0) 
	mCollAvoid[0].mIK:_effectorUpdated()
	local newpose=mIntegrator.pose:copy()
	mCollAvoid[0]:setIter(1)
	mCollAvoid[0].mIK:IKsolve(newpose, footPos);
	local v=calcVelocity(mIntegrator.pose, newpose, 120)
	--v:clamp(10)
	mIntegrator:singleStep(v)

	mLoader:setPoseDOF(mIntegrator.pose);
	for i=0,1 do
		local originalPos=mEffectors(i).bone:getFrame():toGlobalPos(mEffectors(i).localpos)
		--footPos(i):assign(mCON.conPos(i)*0.01);
		footPos(i):assign(originalPos)
	end

	--footPos(0):radd(vector3(xx, yy,zz)/config.skinScale)
	--dbg.draw("Sphere", footPos(0)*config.skinScale, "x0")
	--mCollAvoid[0].mIK:IKsolve(mIntegrator.pose, footPos);
	--mSkin:setPoseDOF(mIntegrator.pose);
	mChecker:setPoseDOF(0,mIntegrator.pose)
	for i=1,#mObstacles do
		mChecker:setPoseDOF(i, mChecker.pose[i])
	end

	if mObstacleSkins then
		for i=1, #mObstacleSkins do
			mObstacleSkins[i]:setMaterial('lightgrey')
		end
	end

	local maxAvoid=0.01
	local bases=mChecker:checkCollision()
	local collisionLinkPairs=bases:getCollisionLinkPairs()
	local maxDepth, lines=mCollAvoid[0]:prepareEffectors(bases, collisionLinkPairs, 0, maxAvoid)
	local newpose=mIntegrator.pose:copy()
	mCollAvoid[0]:setIter(1)
	mCollAvoid[0].mIK:_effectorUpdated()
	mCollAvoid[0].mIK:IKsolve(newpose, footPos);

	local numIter=maxDepth/maxAvoid
	--local numIter=5
	numIter=math.floor(numIter)+1
	assert(numIter>=1)

	--RE.output2("numCon", 0)
	for iter=1, numIter do
		if iter ~=1 then
			mChecker:setPoseDOF(0,newpose)
			bases=mChecker:checkCollision()
			collisionLinkPairs=bases:getCollisionLinkPairs()

			if true then
				-- accumulate constraints
				local numCon=mCollAvoid[0].mIK:_numConstraints()
				--RE.output2("numCon", numCon)
				local maxDepth, lines2=mCollAvoid[0]:_prepareEffectors(numCon, bases, collisionLinkPairs,0,maxAvoid)
			else
				-- do not accumulate
				local maxDepth, lines2=mCollAvoid[0]:_prepareEffectors(0, bases, collisionLinkPairs,0,maxAvoid)
			end


			--local newpose=mIntegrator.pose:copy() -- restart over
			mCollAvoid[0]:setIter(iter+1)
			mCollAvoid[0].mIK:_effectorUpdated()
			mCollAvoid[0].mIK:IKsolve(newpose, footPos);
		end

		for i=1,#mObstacles do
			if dbg.lunaType(mObstacles[i])~="Geometry" then
				local loader=mObstacles[i]
				local cpose=mChecker.pose[i]
				if iter==1 then
					mCollAvoid[i].mIK:_changeNumConstraints(0) 
				end
				local numCon=mCollAvoid[i].mIK:_numConstraints() -- accumulate constraints

				local footPos=vector3N(2)
				loader:setPoseDOF(cpose)
				local mEffectors=mCollAvoid[i].mEffectors
				for ii=0,1 do
					local originalPos=mEffectors(ii).bone:getFrame():toGlobalPos(mEffectors(ii).localpos)
					footPos(ii):assign(originalPos)
				end
				local numCon=mCollAvoid[i].mIK:_numConstraints() -- accumulate constraints
				mCollAvoid[i]:_prepareEffectors(numCon, bases, collisionLinkPairs, i, maxAvoid)

				mCollAvoid[i].mIK:_effectorUpdated()
				mCollAvoid[i]:setIter(iter)
				mCollAvoid[i].mIK:IKsolve(cpose, footPos);
				mChecker:setPoseDOF(i, cpose)
			end
		end
	end

	local config=self.config
	if config.debugDraw then
		if lines:rows()>0 then
			dbg.draw('Traj', lines:matView(), 'allnormals0','solidgreen')
		else
			dbg.erase('Traj','allnormals0')
		end
	end
	local v=calcVelocity(mIntegrator.pose, newpose, 120)
	--print(speedLimit)
	v:clamp(speedLimit )
	mIntegrator:singleStep(v)


	mFilter:setCurrPose(mIntegrator.pose)
	for i=1,#mObstacles do
		if dbg.lunaType(mObstacles[i])~="Geometry" then
			local loader=mObstacles[i]
			local cpose=mChecker.pose[i]
			mObstacleSkins[i]:setPoseDOF(cpose)
		end
	end
	local config=self.config
	if config.noFiltering then
		return newpose
	else
		return mFilter:getFiltered()
	end
end
function CA.CollisionAvoider:getDMot()
	return self.mIntegrator.dmot
end
CA.OnlineLTIFilter=LUAclass()

function CA.OnlineLTIFilter:__init(pose, filterSize)
	self.filterSize=filterSize
	self.queue=Queue(filterSize)
end

function CA.OnlineLTIFilter:setCurrPose(pose)
	self.queue:pushBack(pose:copy())
end

function CA.OnlineLTIFilter:getFiltered()
	if #self.queue.data==self.queue.n then
		local sum=vectorn(self.queue:back():size())
		sum:setAllValue(0)

		for i,v in ipairs(self.queue.data) do
			sum:radd(self.queue.data[i])
		end
		sum:rmult(1/self.queue.n)
		return sum
	else
		return self.queue:back()
	end
end
return CA
