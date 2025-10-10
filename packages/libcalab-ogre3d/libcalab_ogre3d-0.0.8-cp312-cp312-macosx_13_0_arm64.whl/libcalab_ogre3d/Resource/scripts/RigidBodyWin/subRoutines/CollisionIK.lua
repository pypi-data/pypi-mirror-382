local CA={}
CA.CollisionIK=LUAclass()

CA.HCollisionChecker=LUAclass()
local function vec_abs(v)
	return vector3(math.abs(v.x), math.abs(v.y), math.abs(v.z))

end

function Physics.CollisionDetector:rayTestAll(ichar, from, to)

	local res=Physics.RayTestResult()
	local loader=self:getModel(ichar)
	local t=1.0

	for i=1, loader:numBone()-1 do
		self:rayTest(ichar, i, from, to, res)
		if res:hasHit() and res.m_closestHitFraction< t then 
			t=res.m_closestHitFraction
		end
	end

	return to*t + from *(1-t)
end
-- hybrid
function CA.HCollisionChecker:__init()
	local COLDET=LUAclass()
	function COLDET:__init(a)
		self.parent=a
	end
	function COLDET:addModel(v)
		self.parent.checker1.collisionDetector:addModel(v)
		self.parent.checker2.collisionDetector:addModel(v)
	end
	function COLDET:addObstacle(v)
		self.parent.checker1.collisionDetector:addObstacle(v)
		self.parent.checker2.collisionDetector:addObstacle(v)
	end
	function COLDET:getModel(i)
		return self.parent.checker2.collisionDetector:getModel(i)
	end
	function COLDET:isSignedDistanceSupported()
		return true 
	end
	function COLDET:setWorldTransformations(iloader, fkSolver)
		self.parent.checker1.collisionDetector:setWorldTransformations(iloader, fkSolver)
		self.parent.checker2.collisionDetector:setWorldTransformations(iloader, fkSolver)
	end

	
	function COLDET:calculateSignedDistance(iloader, ibody, in_global_pos, out_normal )
		--local dist=self.parent.checker1.collisionDetector:calculateSignedDistance(iloader, ibody, in_global_pos, out_normal) -> libccd does not support this
		local dist=self.parent.checker2.collisionDetector:calculateSignedDistance(iloader, ibody, in_global_pos, out_normal)
		return dist 
	end
	function COLDET:calculateNearestSurfacePoint(iloader, ibody, in_global_pos, radius)
		if not radius then radius=0.1 end
		local out_normal=vector3()
		local highresDetector=self.parent.checker2.collisionDetector
		local dist=highresDetector:calculateSignedDistance(iloader, ibody, in_global_pos, out_normal)
		if dist<radius then
			-- prev_surfacepoint=in_global_pos-out_normal*dist   (which can be inaccurate in this case so ...)
			local new_surfacepoint=vector3()
			-- lowres detector is more accurate for detecting surface normal.
			local depth=self.parent.checker1.collisionDetector:testSphereIntersection(iloader, ibody, in_global_pos, radius, new_surfacepoint, out_normal)
			if depth>0 then
				new_surfacepoint:radd(out_normal*0.005) -- heuristic to avoid discontinuity

				if true then
					-- further search for more precise surface point!
					local from=new_surfacepoint+out_normal
					local to=new_surfacepoint-out_normal
					local res=Physics.RayTestResult()
					local det=highresDetector:rayTest(iloader, ibody, from, to, res)
					if res:hasHit() and res.m_closestHitFraction<0.5 then
						local t=res.m_closestHitFraction
						new_surfacepoint=to*t+from*(1-t)
						new_surfacepoint:radd(out_normal*-0.0025) -- heuristic to avoid discontinuity
					end
				end

				return dist, new_surfacepoint
			end
		end
		return dist, in_global_pos-out_normal*dist
	end
	function COLDET:getLocalBoundingBoxSize(iloader, ibody, out_size)
		local size1=vector3()
		local size2=vector3()
		self.parent.checker1.collisionDetector:getLocalBoundingBoxSize(iloader, ibody, size1)
		self.parent.checker2.collisionDetector:getLocalBoundingBoxSize(iloader, ibody, size2)

		out_size:assign(size2)
	end
	function COLDET:addCollisionPair(loader,b, loader2, b2)
		self.parent.checker1.collisionDetector:addCollisionPair(loader, b, loader2, b2)
		self.parent.checker2.collisionDetector:addCollisionPair(loader, b, loader2, b2)
	end


	self.checker1=CollisionChecker('libccd_merged')
	self.checker2=CollisionChecker('gjk')
	self.collisionDetector=COLDET(self)
	self.pose=self.checker2.pose
end

function CA.HCollisionChecker:setPoseDOF(iloader, pose)
	self.checker1:setPoseDOF(iloader, pose)
	self.checker2:setPoseDOF(iloader, pose)
end
function CA.HCollisionChecker:registerPair(i,j)
	self.checker1:registerPair(i,j)
	self.checker2:registerPair(i,j)
end
function CA.HCollisionChecker:detectCollisionFrames(motdof, options, thr)
	thr=thr or 0
	local mChecker=self
	local col=boolN(motdof:numFrames())

	for i=0, motdof:rows()-1 do
		mChecker:setPoseDOF(0,motdof:row(i))
		local bases, maxDepth=mChecker:checkCollision(options)
		if maxDepth>thr then
			col:set(i, true)
		end
	end

	return col
end
function CA.HCollisionChecker:registerSelfPairs(i, collpairs)
	self.checker1:registerSelfPairs(i,collpairs)
	self.checker2:registerSelfPairs(i,collpairs)
	assert(i==0)
	self.collpairs=collpairs
end
function CA.HCollisionChecker:checkCollision(options)
	local bases1=self.checker1:checkCollision()
	local bases=self.checker2:checkCollision()
	local collisionLinkPairsRough=bases1:getCollisionLinkPairs()
	local collisionLinkPairs=bases:getCollisionLinkPairs()
	if not options then options={} end
	local dm=options.defaultMargin or 0
	local rdm=options.radiusDependentMargin or 0.05
	local coldet=self.checker1.collisionDetector -- libccd_merged
	local gmaxDepth=0
	if collisionLinkPairs:size()>=1 then
		for i=0, collisionLinkPairs:size()-1 do
			local ilinkpair=collisionLinkPairs(i)
			local collisionPoints=bases:getCollisionPoints(ilinkpair)

			if collisionPoints:size()>0 then
				local iloader1=bases:getCharacterIndex1(ilinkpair)
				local bone1=bases:getBone1(ilinkpair)
				local iloader2=bases:getCharacterIndex2(ilinkpair)
				local bone2=bases:getBone2(ilinkpair)

				local cp1=bases1:getCollisionPoints(ilinkpair)
				--if not (cp1:size()==1) then
				--	if cp1:size()>1 then
				--		print("????")
				--		dbg.console()
				--	end
				--else
				if cp1:size()>0 then
					if false then
						for icp=0, collisionPoints:size()-1 do
							collisionPoints(icp).normal:assign(cp1(0).normal)
						end
					else
						-- find maxDepth point
						local maxDepth=0
						local argMax=-1
						for icp=0, collisionPoints:size()-1 do
							local cp=collisionPoints(icp)
							if cp.idepth>maxDepth then
								argMax=icp
								maxDepth=cp.idepth
							end
						end
						assert(argMax~=-1)
						local cp=collisionPoints(argMax)
						collisionPoints(0).normal:assign(cp1(0).normal)
						collisionPoints(0).idepth=cp.idepth
						collisionPoints(0).position:assign(cp.position)
						collisionPoints:resize(1)

						-- now, let's handle margin.
						if iloader2==0 then
							-- only for self-collisions
							local margin=dm
							local size1=vector3()
							local size2=vector3()

							coldet:getLocalBoundingBoxSize(iloader1,bone1:treeIndex(), size1)
							coldet:getLocalBoundingBoxSize(iloader2,bone2:treeIndex(), size2)

							local b=collisionPoints(0)
							local minsize=math.min(
							vec_abs((bone1:getFrame().rotation:inverse()*b.normal)):dotProduct(size1),
							vec_abs((bone2:getFrame().rotation:inverse()*b.normal)):dotProduct(size2))
							margin=margin+math.max(0, minsize-0.02)*rdm

							if b.idepth>margin then
								b.idepth=b.idepth-margin
								gmaxDepth=math.max(b.idepth, gmaxDepth)
							else
								collisionPoints:erase(0)
							end
						else
							gmaxDepth=math.max(cp.idepth, gmaxDepth)
						end
					end
				end
			end
		end
	end
	return bases, gmaxDepth
end

CA.CollisionAvoid=LUAclass()

function CA.CollisionAvoid:createIKsolver(ikc )
	-- nlopt or lbfgs
	self.mIK=MotionUtil.createFullbodyIk_MotionDOF_MultiTarget_lbfgs(self.loader.dofInfo,self.mEffectors,self.g_con)
	--self.mIK=MotionUtil.createFullbodyIk_MotionDOF_MultiTarget_nlopt(mLoader.dofInfo,self.mEffectors,self.g_con)
	--mIK=MotionUtil.createFullbodyIk_MotionDOF_hybrid_lbfgs(mLoader.dofInfo,mEffectors,g_con, CT.ivec(lknee:treeIndex(), rknee:treeIndex()), CT.vec(1,1))
	self.mEffectors:resize(#ikc);
	for i, v in ipairs(ikc) do
		self.mEffectors(i-1):init(self.loader:getBoneByName(v[1]), v[2])
	end

	local mEffectors=self.mEffectors
	self.mIK:_changeNumEffectors(#ikc)
	for i, v in ipairs(ikc) do
		self.mIK:_setEffector(i-1, mEffectors(i-1).bone, mEffectors(i-1).localpos)
	end
end

function CA.CollisionAvoid:__init(mLoader, config)
	assert(config.skinScale)
	self.config=config
	self.loader=mLoader
	self.g_con=MotionUtil.Constraints() -- std::vector<MotionUtil::RelativeConstraint>
	self.g_con:resize(0)
	self.mEffectors=MotionUtil.Effectors()

	--local ikc=config.interactionBoneInfo
	local ikc={}
	for i, v in ipairs(config.con) do
		ikc[i]={v.bone, v.lpos}
	end

	self:createIKsolver(ikc)

	do
		local relm=config.con.relative
		if relm then
			self:prepareRelativeMarkers(relm, config.adaptMissingBone)
		end
	end
	if config.lockBones then
		local indices=vectorn()
		for i=1, config.lockBones:size()-1 do
			if config.lockBones(i) then
				indices:pushBack(i)
			end
		end
		self.mIK:setParam('jacobian_lock', indices)
	end
	if config.setIKparam then
		config:setIKparam(self.mIK)
	end
end
function CA.CollisionAvoid:prepareRelativeMarkers(relm, adaptMissingBone)
	self.mRelativeMarkers=MotionUtil.Effectors()

	self.mRelativeMarkers:resize(#relm);
	for i, v in ipairs(relm) do
		if adaptMissingBone then
			adaptMissingBone(self.loader, v)
		end
		local ti=self.loader:getTreeIndexByName(v.bone)
		if ti==-1 then 
			print(v.bone, adaptMissingBone)
			ti=0
			assert(false)
		end
		self.mRelativeMarkers(i-1):init(self.loader:bone(ti), v.lpos)
	end
end

function CA.CollisionAvoid:_setEffectors(mCON)
	local mIK=self.mIK
	local mEffectors=self.mEffectors
	if mCON then
		local con=mCON.con
		mIK:_changeNumEffectors(con:count())
		local c=0
		for i=0, con:size()-1 do
			if con(i) then
				mIK:_setEffector(c, mEffectors(i).bone, mEffectors(i).localpos)
				c=c+1
			end
		end
	else
		mIK:_changeNumEffectors(2)
		mIK:_setEffector(0, mEffectors(0).bone, mEffectors(0).localpos)
		mIK:_setEffector(1, mEffectors(1).bone, mEffectors(1).localpos)
	end
end

function CA.CollisionIK:getCollisionBones(bases)
	local mLoader=self.mLoader
	local hasCol=boolN(mLoader:numBone())
	local loaderIndex=0

	local collisionLinkPairs=bases:getCollisionLinkPairs()
	if collisionLinkPairs:size()>=1 then
		for i=0, collisionLinkPairs:size()-1 do
			local ilinkpair=collisionLinkPairs(i)
			local collisionPoints=bases:getCollisionPoints(ilinkpair)

			local iloader1=bases:getCharacterIndex1(ilinkpair)
			local iloader2=bases:getCharacterIndex2(ilinkpair)
			if iloader1==loaderIndex or iloader2==loaderIndex then
				local bone1=bases:getBone1(ilinkpair)
				if collisionPoints:size()>0 then
					if(iloader1==loaderIndex) then
						hasCol:set(bone1:treeIndex(), true)
					end
					if iloader2==loaderIndex then
						hasCol:set(bases:getBone2(ilinkpair):treeIndex(), true)
					end
				end
			end
		end
	end
	return hasCol
end
function CA.CollisionAvoid:_prepareEffectors(start_con, bases, collisionLinkPairs, loaderIndex, maxAvoid, mChecker, mCON, options, col_ik)
	local mIK=self.mIK
	local mEffectors=self.mEffectors
	loaderIndex=loaderIndex or 0

	local count=0

	local mLoader=self.loader
	local disableAvoid=boolN(mLoader:numBone())
	local function _disableAvoid(b)
		b=b:childHead()
		while b do
			disableAvoid:set(b:treeIndex(), true)
			b=b:sibling()
		end
	end

	if self.config.ignoreDeepCollisions then
		local hasDeepCol=boolN(mLoader:numBone())
		if collisionLinkPairs:size()>=1 then
			for i=0, collisionLinkPairs:size()-1 do
				local ilinkpair=collisionLinkPairs(i)
				local collisionPoints=bases:getCollisionPoints(ilinkpair)
				local iloader1=bases:getCharacterIndex1(ilinkpair)
				local iloader2=bases:getCharacterIndex2(ilinkpair)
				if iloader1==loaderIndex or iloader2==loaderIndex then
					for j=0, collisionPoints:size()-1 do
						local cp=collisionPoints(j)
						if iloader1==iloader2 then
							if cp.idepth>maxAvoid *2 then
								local bone1=bases:getBone1(ilinkpair)
								hasDeepCol:set(bone1:treeIndex(), true)
							end
						end
					end
				end
			end
		end
		for i=1, mLoader:numBone()-1 do
			if hasDeepCol(i) then
				_disableAvoid(mLoader:bone(i))
			end
		end
	end

	if not options.noCollisionAvoid then
	if collisionLinkPairs:size()>=1 then
		for i=0, collisionLinkPairs:size()-1 do
			local ilinkpair=collisionLinkPairs(i)
			local collisionPoints=bases:getCollisionPoints(ilinkpair)

			local iloader1=bases:getCharacterIndex1(ilinkpair)
			local iloader2=bases:getCharacterIndex2(ilinkpair)
			if iloader1==loaderIndex or iloader2==loaderIndex then
				local bone1=bases:getBone1(ilinkpair)
				--local bone2=bases:getBone2(ilinkpair)
				--print(bone1, bone2)
				if not disableAvoid(bone1:treeIndex()) then
					if iloader1==iloader2 then
						--count=count+collisionPoints:size()*2 --양쪽 밀기.
						count=count+collisionPoints:size() -- 한쪽 밀기(링크 페어중 첫번째 놈을 민다. 즉 누구를 밀지 지정 가능).
					else
						count=count+collisionPoints:size()
					end
				end
			end
		end
	end
	end

	if mCON and mCON.relative then
		if options.removeOvershooting then
			local iframe=options.iframe
			local hasCol=col_ik:getCollisionBones(bases)
			self._overshootingInfo, self._absOvershootingInfo=col_ik:_detectOvershooting(iframe, options, hasCol)

			local overshootingInfo=self._overshootingInfo
			for i_oi, oi in ipairs(overshootingInfo) do
				local i, eff, conTargetTI, in_global_pos, newdist, out_normal, delta=unpack(oi)
				if eff.bone:treeIndex()~=0 then
					count=count+1
				end
			end
			count=count+#self._absOvershootingInfo
		end
	end

	self:_setEffectors(mCON)


	mIK:_changeNumConstraints(start_con+count) 

	count=0
	local lines=vector3N()

	local maxDepth=0
	if not options.noCollisionAvoid then
	if collisionLinkPairs:size()>=1 then
		local margin=options.maxPenetrationDepth or 0.02 -- max penetration depth
		for i=0, collisionLinkPairs:size()-1 do
			local ilinkpair=collisionLinkPairs(i)
			local iloader1=bases:getCharacterIndex1(ilinkpair)
			local bone1=bases:getBone1(ilinkpair)
			local iloader2=bases:getCharacterIndex2(ilinkpair)
			local collisionPoints=bases:getCollisionPoints(ilinkpair)

			local config=self.config
			if iloader1==loaderIndex or iloader2==loaderIndex then
				for j=0, collisionPoints:size()-1 do
					local b=collisionPoints(j)
					--print(loader1:name(), loader1:VRMLbone(linkpair[2]).NameId, loader2:name(), loader2:VRMLbone(linkpair[4]).NameId)
					if mObstacleSkins and iloader2~=0 then
						mObstacleSkins[iloader2]:setMaterial('red_transparent')
					end
					do
						lines:pushBack(b.position*config.skinScale) -- inside bone1, on the bone2's surface
						--lines:pushBack((b.position+b.normal)*config.skinScale)
						lines:pushBack((b.position+b.normal*b.idepth)*config.skinScale) -- inside bone2, on the bone1's surface
						--lines:pushBack((b.position+b.normal*b.idepth)*config.skinScale)
						lines:pushBack((b.position+b.normal*b.idepth*2)*config.skinScale)
						lines:pushBack((b.position+b.normal)*config.skinScale)
					end
					maxDepth=math.max(maxDepth, b.idepth)

					if not disableAvoid(bone1:treeIndex()) then

						if maxAvoid then
							-- maximum-avoidance during a single-step
							if b.idepth>margin+maxAvoid then -- max penetration vel
								margin=b.idepth-maxAvoid
							end
						end

						local depth=b.idepth
						if iloader1==iloader2 then
							--depth=depth*0.5
						end

						if iloader1==loaderIndex then

							local collInfo=mChecker.collpairs[ilinkpair+1]
							if collInfo then
								assert(collInfo[1]==bone1:treeIndex())
							else
								collInfo={} -- probably obstacles
							end
							if not collInfo.relative then
								local bone=bone1
								local localpos=bone:getFrame():toLocalPos(b.position+b.normal*depth)
								--local localpos=bone:getFrame():toLocalPos(b.position+b.normal*depth*0.5)
								local plane=Plane(b.normal, b.position)
								mIK:_setHalfSpaceConstraint(start_con+count, bone, localpos, plane.normal, plane.d-margin)
							else
								--local gpos=b.position+b.normal*depth*0.5
								local bone2=bases:getBone2(ilinkpair)
								local localpos1=bone1:getFrame():toLocalPos(b.position+b.normal*depth)
								local localpos2 =bone2:getFrame():toLocalPos(b.position)


								---
								---               b1____
								---
								---                     |     -normal
								---           b2      ____
								---
								mIK:_setRelativeHalfSpaceConstraint(start_con+count, bone1, localpos1, bone2, localpos2, -b.normal, margin,1)
							end
						end
						if iloader1==iloader2 then
							--count=count+1 -- 양쪽 밀기시 uncomment.
						else
							if iloader2==loaderIndex then
								local bone=bases:getBone2(ilinkpair)
								local localpos=bone:getFrame():toLocalPos(b.position)
								--local localpos=bone:getFrame():toLocalPos(b.position+b.normal*depth*0.5)
								local plane=Plane(-b.normal, b.position+b.normal*depth)
								mIK:_setHalfSpaceConstraint(start_con+count, bone, localpos, plane.normal, plane.d-margin)
							end
						end
						count=count+1
					end
				end
			end
		end
		--dbg.draw('Traj', lines:matView(), 'normals'..loaderIndex,'solidred')
	else
		--dbg.erase('Traj', 'normals'..loaderIndex)
	end
	end

	if mCON and mCON.relative then
		if options.removeOvershooting then
			local iframe=options.iframe
			local rm=config.con.relative
			local effectors=self.mRelativeMarkers
			local overshootingInfo=self._overshootingInfo
			local absOvershootingInfo=self._absOvershootingInfo
			local mIK=self.mIK
			
			local maxAvoid=options.maxAvoid or 0.01
			local conWeight=options.overshootingConWeight or 1
			-- maximum-avoidance during a single-step
			for i_oi, oi in ipairs(overshootingInfo) do
				local i, eff, conTargetTI, in_global_pos, newdist, out_normal, delta=unpack(oi)
				local plane=Plane(out_normal, in_global_pos)
				maxDepth=math.max(maxDepth, delta)
				delta=math.min(delta, maxAvoid)
				--if conTargetTI=='unused' then dbg.console() end
				if eff.bone:treeIndex()~=0 then
					mIK:_setHalfSpaceConstraint(start_con+count, eff.bone, eff.localpos, plane.normal, plane.d+delta)
					--mIK:_setRelativeHalfSpaceConstraint(start_con+count, eff.bone, eff.localpos, bone2, localpos2, -plane.normal, maxDepth,1)
					mIK:_setConstraintWeight(start_con+count, conWeight)
					count=count+1
				end
			end
			for i_oi, oi in ipairs(absOvershootingInfo) do
				local i, eff, in_global_pos, newdist, tgt_pos, delta, importance=unpack(oi)
				--maxDepth=math.max(maxDepth, newdist)
				mIK:_setPositionConstraint(start_con+count, eff.bone, eff.localpos, tgt_pos, importance, importance, importance)
				--mIK:_setRelativeHalfSpaceConstraint(start_con+count, eff.bone, eff.localpos, bone2, localpos2, -plane.normal, maxDepth,1)
				mIK:_setConstraintWeight(start_con+count, conWeight)
				count=count+1
			end
		end
	end
	assert(count+start_con==mIK:_numConstraints())


	return maxDepth, lines
end

-- input : global obstaclePos, obstacleSize, obstacleType
function CA.CollisionIK:__init(mLoader, mMotionDOFcontainer, config)
	assert(mLoader)
	assert(mMotionDOFcontainer)
	self.mLoader=mLoader
	if config.prepareCollisionPairs then
		config:prepareCollisionPairs(mLoader)
	end
	self.mCollAvoid={}
	self.mCollAvoid[0]=CA.CollisionAvoid(mLoader, config)
	local mCollAvoid=self.mCollAvoid


	if config.obstacles then
		self.obstaclePos=config.obstacles.obstaclePos
		self.obstacleSize=config.obstacles.obstacleSize
		self.obstacleType=config.obstacles.obstacleType
	elseif obstaclePos then
		-- from global 
		self.obstaclePos=obstaclePos
		self.obstacleSize=obstacleSize
		self.obstacleType=obstacleType
	else
		self.obstaclePos={}--vector3(30,0,0), vector3(-30,0,0), vector3(60,30,0), vector3(0,0,0),vector3(110,100,0) }
		self.obstacleSize={}--vector3(20,20,40),vector3(20,20,40), vector3(20,20,40), vector3(1000,0,2000),vector3(0,0,0)}
		self.obstacleType={}--"BOX","SPHERE","CAPSULE","BOX", "CHAR"}
	end


	--mObjectList:registerMesh(mObstacles[1], 'meshtest'):getLastCreatedEntity():setMaterialName('lightgrey_transparent')
	--mObjectList:findNode('meshtest'):scale(config.skinScale)

	if config.createAdditionalCollisionChecker then
		self.mChecker=config:createAdditionalCollisionChecker()
		local mChecker=self.mChecker
		local coldet=self.mChecker.collisionDetector
		if config.obstacles then
			assert(coldet:numModels()==1+#config.obstacles.obstaclePos)
			self.mObstacles=mChecker.obstacleMeshes
		else
			assert(coldet:numModels()==1)
			self.mObstacles={}
		end
		local mObstacles=self.mObstacles
		assert(coldet:numModels()==1+#mObstacles)
	elseif config.collisionChecker then
		assert(config.mChecker==nil or config.mChecker==config.collisionChecker)
		self.mChecker=config.collisionChecker
		local mChecker=self.mChecker
		local coldet=self.mChecker.collisionDetector
		assert(coldet:numModels()==1)
		self.mObstacles=CollisionChecker._buildObstacleMeshes(self, 1/config.skinScale)
		local mObstacles=self.mObstacles
		for i,v in ipairs(mObstacles) do
			local ltype=getmetatable(v).luna_class
			if ltype=='MainLib.VRMLloader' then
				mChecker.collisionDetector:addModel(v)
			else
				mChecker.collisionDetector:addObstacle(v)
			end
		end
		assert(coldet:numModels()==1+#mObstacles)
	else
		-- replace collision checker
		--local mChecker=CollisionChecker('libccd_merged')
		--local mChecker=CollisionChecker('libccd')
		local mChecker=CA.HCollisionChecker()
		self.mChecker=mChecker
		local obj={mLoader, unpack(mObstacles)}
		self.mObstacles=CollisionChecker._buildObstacleMeshes(self, 1/config.skinScale)
		local mObstacles=self.mObstacles
		for i,v in ipairs(obj) do
			local ltype=getmetatable(v).luna_class
			if ltype=='MainLib.VRMLloader' then
				mChecker.collisionDetector:addModel(v)
			else
				mChecker.collisionDetector:addObstacle(v)
			end
		end
	end

	for i=1,#self.obstaclePos do
		if self.obstacleType[i]=="CHAR" then
			mObstacles[i]=MainLib.VRMLloader (config[1])
			mCollAvoid[i]=CA.CollisionAvoid(mObstacles[i], config)
		end
	end

	local mChecker=self.mChecker

	for i=1,#self.obstaclePos do

		local initialState=vectorn(7)
		local obstacleOffset=vector3(0,0,0)
		if self.obstacleType[i]=="CHAR" then
			initialState:resize(mObstacles[i].dofInfo:numDOF())
		end
		initialState:setVec3(0, (self.obstaclePos[i]+obstacleOffset)/config.skinScale)
		initialState:setQuater(3,quater(1,0,0,0))
		mChecker:setPoseDOF(i, initialState)
	end
	local mObstacleSkins={}
	local s=config.skinScale


	local collpairs=config.collpairs
	if collpairs then
		self.mChecker:registerSelfPairs(0,collpairs )-- 0 means mLoader, 1 means mObstacles[1]
	elseif config.defineCollisionPairs then
		local coll_pairs=config:defineCollisionPairs(mLoader,{true, true, true, true}) 
		self.mChecker:registerSelfPairs(0,coll_pairs )-- 0 means mLoader, 1 means mObstacles[1]
	end

	for i=1, #self.obstaclePos do
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
	self.config=config
end

function CA.CollisionIK:getEffectorPos()
	local mEffectors=self.mCollAvoid[0].mEffectors
	local pos = vector3N()
	pos:setSize(mEffectors:size())
	for i=0, pos:size()-1 do
		local originalPos=mEffectors(i).bone:getFrame():toGlobalPos(mEffectors(i).localpos)*100
		pos(i):assign(originalPos)
	end
	return pos
end


--  options의 default 값(미지정시 사용).
--	options={
--		terminationCondition =0.01, -- 최대 depth가 이 값 이하로 줄면 멈춤.
--		maxAvoid = 0.01, -- 각 iteration에서 최대로 꺼내는 양.
-- 		defaultMargin = 0,  -- cm
--		radiusDependentMargin = 0.05,  -- in [0,1]
--	}
--	optional mCON => { con=boolN..., conPos=vector3N..., relCon={ con=..., conPos=..., importance=...} }
CA._useSoftCon=true

local function getConTargetTI(mLoader, softCon)
	local conTargetTI=softCon.conTargetTI
	if not conTargetTI then
		conTargetTI=mLoader:getTreeIndexByName(softCon.other_body)
		softCon.conTargetTI=conTargetTI
	end
	return conTargetTI
end
local function getConTargetSourceTI(mSrcLoader, softCon)
	local conTargetTI=softCon.conTargetSrcTI
	if not conTargetTI then
		conTargetTI=mSrcLoader:getTreeIndexByName(softCon.other_body)
		softCon.conTargetSrcTI=conTargetTI
	end
	return conTargetTI
end
local function getImportance(iframe, softCon)
	local importance=softCon.importance
	local bcon= iframe>=importance:startI() and iframe<importance:endI() and importance(iframe)>0 
	if bcon then
		local i=importance(iframe)
		return i>0, i
	end
	return bcon, 0
end
CA.getImportance=getImportance
CA.getConTargetTI=getConTargetTI
-- overshooting : too much error detected in both relative and absolute constraints. 
--  other_body: case 1: relative-constraint -> name of the other bone : use half-space constraint
--  other_body: case 2: absolute-constraint -> (character index of the obs )
function CA.CollisionIK:_detectOvershooting(iframe, options, hasCol)
	local rm=config.con.relative
	local mLoader=config.mLoader
	local mChecker=self.mChecker
	local effectors=self.mCollAvoid[0].mRelativeMarkers
	local ignore_thr=options.overshooting_ignore_thr or 0-- 5cm 이내의 차이는 무시
	local overshootingInfo={}

	for i, marker in ipairs(rm) do
		local argMin=nil
		local minv=1e5
		-- 가장 error가 심한 other bone detect.
		for icon, softCon in ipairs(marker.softConstraints) do

			local bcon, importance_i=getImportance(iframe, softCon)
			if bcon and importance_i>=0.5 then
				local dist=softCon.dist
				local d=dist(iframe)
				if d<minv then
					minv=d
					argMin=icon
				end
			end
		end
		if argMin then 
			local softCon=marker.softConstraints[argMin]
			local dist=softCon.dist
			local d=dist(iframe)
			local bcon, importance_i=getImportance(iframe, softCon)
			if bcon and importance_i>=0.5 then
				--and not hasCol( effectors(i-1).bone:treeIndex()) then
				local conTargetTI=getConTargetTI(mLoader, softCon)
				local ef=effectors(i-1)

				local out_normal=vector3()
				local in_global_pos=effectors(i-1).bone:getFrame()*effectors(i-1).localpos
				local newdist
				if false then  
					-- direct search
					newdist= mChecker.collisionDetector:calculateSignedDistance(0, conTargetTI, in_global_pos, out_normal )
				else
					-- also search neighboring bones
					newdist= mChecker.collisionDetector:calculateSignedDistance(0, conTargetTI, in_global_pos, out_normal )
					local parentTI= mLoader:bone(conTargetTI):parent():treeIndex()
					if parentTI>=1 then
						local out_normal2=vector3()
						local newdist2= mChecker.collisionDetector:calculateSignedDistance(0, parentTI, in_global_pos, out_normal2 )
						if newdist2<newdist then
							newdist=newdist2
							conTargetTI=parentTI
							out_normal=out_normal2
						end
					end
				end

				-- ignore original collisions
				d=math.max(d, 0)

				if newdist>d+ignore_thr then
					-- 너무 멀리 떨어진 경우 
					local delta=newdist-d

					local conii=softCon.conInfo:row(iframe)
					local lnearestpos=conii:toVector3(0)
					local info={ i, effectors(i-1), conTargetTI, in_global_pos, newdist, out_normal,delta , importance_i, lnearestpos}
					table.insert(overshootingInfo, info)

					--dbg.draw('SphereM', in_global_pos, 'col'..c, 'red_transparent', marker.thr_distance*0.5)
					--dbg.draw('SphereM', in_global_pos+out_normal*(newdist-(d+ignore_thr)), 'ccol'..c, 'blue_transparent', marker.thr_distance*0.5)
					--dbg.draw('Line', in_global_pos*100, (in_global_pos+out_normal*(newdist-(d+ignore_thr)))*100, 'ccolline'..c, 'solidred')
					--print(iframe, mLoader:bone(conTargetTI):name())

					----if newdist-(d+ignore_thr)>0.1 then
					----	dbg.console() 
					----end
				elseif false and newdist<-0.05 then
					-- doesn't work at all.
					-- 너무 충돌한 경우. (collision으로 처리되지만, noCollisionAvoid==true일때도 최소한의 회피는 하기 위해 추가한 기능.)
					local conii=softCon.conInfo:row(iframe)
					if conii:size()>6 then
						local normal=conii:toVector3(6)


						local lnearestpos=conii:toVector3(0)
						local anchorPos=mLoader:bone(conTargetTI):getFrame()*lnearestpos

						local tgt_pos=anchorPos+softCon.conInfo:row(iframe):toVector3(3)
						local newdist2=(tgt_pos-in_global_pos):dotProduct(normal)
						--local info={ i, effectors(i-1), conTargetTI, in_global_pos, newdist, normal*-1,newdist2*-1, importance_i, lnearestpos}
						local info={ i, effectors(i-1), 'unused', tgt_pos, newdist, normal*-1,newdist2, importance_i, lnearestpos}
						--local info={ i, effectors(i-1), conTargetTI, in_global_pos, newdist, out_normal,(newdist+0.05)*-1, importance_i, lnearestpos}
						table.insert(overshootingInfo, info)
					end

				end
			end
		end
	end

	-- todo: detect overshooting of the absolute constraints too
	--dbg.console()
	local absOvershootingInfo={}
	do
		local am=config.con
		local abseffectors=self.mCollAvoid[0].mEffectors
		local ignore_thr=options.overshooting_ignore_thr or 0-- 5cm 이내의 차이는 무시
		local overshootingInfo={}

		for i, marker in ipairs(am) do
			if not marker.softConstraints then
				break
			end
			-- 가장 error가 심한 other obstacle detect.
			for icon, softCon in ipairs(marker.softConstraints) do

				local bcon, importance_i=getImportance(iframe, softCon)
				if bcon and importance_i>0 then
					local dist=softCon.dist
					local d=dist(iframe)
				--if d<thr then
					--if d<thr and not hasCol( effectors(i-1).bone:treeIndex()) then
					local conTargetTI=getConTargetTI(mLoader, softCon)
					local ef=abseffectors(i-1)

					local out_normal=vector3()
					local in_global_pos=abseffectors(i-1).bone:getFrame()*abseffectors(i-1).localpos
					local tgt_pos=softCon.anchorPos+softCon.conInfo:row(iframe):toVector3(3)
					local newdist=in_global_pos:distance(tgt_pos)

					if newdist>d+ignore_thr then

						local delta=newdist-d
						local info={ i, abseffectors(i-1), in_global_pos, d, tgt_pos, delta, importance_i}
						table.insert(absOvershootingInfo, info)

						--dbg.draw('SphereM', in_global_pos, 'col'..c, 'red_transparent', marker.thr_distance*0.5)
						--dbg.draw('SphereM', in_global_pos+out_normal*(newdist-(d+ignore_thr)), 'ccol'..c, 'blue_transparent', marker.thr_distance*0.5)
						--dbg.draw('Line', in_global_pos*100, (in_global_pos+out_normal*(newdist-(d+ignore_thr)))*100, 'ccolline'..c, 'solidred')
						--print(iframe, mLoader:bone(conTargetTI):name())

						----if newdist-(d+ignore_thr)>0.1 then
						----	dbg.console() 
						----end
					end
				end
			end
		end
	end

	return overshootingInfo, absOvershootingInfo
end
function CA.CollisionIK:solveIK(inputPose, mCON, options)
	local config = self.config

	if not options then options={} end
	local mLoader=self.mLoader
	local mCollAvoid=self.mCollAvoid
	local mChecker=self.mChecker
	local mObstacles=self.mObstacles
	local mObstacleSkins=self.mObstacleSkins 
	local speedLimit=self.config.speedLimit or 100

	local newpose=inputPose:copy()

	local mEffectors=mCollAvoid[0].mEffectors
	mLoader:setPoseDOF(newpose)
	local opos={}
	for i=0,mEffectors:size()-1 do
		local originalPos=mEffectors(i).bone:getFrame():toGlobalPos(mEffectors(i).localpos)
		opos[i]=originalPos
	end

	-- local pos to global pos
	local footPos=vector3N(mEffectors:size())
	local targetPos
	if mCON then
		footPos:setSize(mCON.con:count())

		if mCON.relCon then
			targetPos=vector3N(mCON.relCon.con:count())
		end
	end
	local c=0
	for i=0,mEffectors:size()-1 do
		local originalPos=opos[i]
		local delta=vector3(0,0,0)
		if mCON then
			if mCON.con(i) then
				footPos(c):assign(mCON.conPos(i))
				c=c+1
			end
		else
			footPos(i):assign(originalPos+delta);
		end
	end
	--[[
	mCollAvoid[0].mIK:_changeNumConstraints(0) 
	mCollAvoid[0].mIK:_effectorUpdated()
	mCollAvoid[0].mIK:IKsolve(newpose, footPos);
	]]

	--for i=0,1 do
--		local originalPos=mEffectors(i).bone:getFrame():toGlobalPos(mEffectors(i).localpos)
--		--footPos(i):assign(mCON.conPos(i)*0.01);
--		footPos(i):assign(originalPos)
--	end

	mChecker:setPoseDOF(0,newpose)

	for i=1,#mObstacles do
		mChecker:setPoseDOF(i, mChecker.pose[i])
	end

	if mObstacleSkins then
		for i=1, #mObstacleSkins do
			mObstacleSkins[i]:setMaterial('lightgrey')
		end
	end

	local maxAvoid=options.maxAvoid or 0.01
	local terminationCondition=options.terminationCondition or maxAvoid
	local bases=mChecker:checkCollision(options)
	local collisionLinkPairs=bases:getCollisionLinkPairs()

	local startConIndex=0
	if mCON and mCON.relative then
		local rel=mCON.relative 
		local c=0
		local rm=mCollAvoid[0].mRelativeMarkers
		if options.useRelConOri then 
			for i=0, rel.con:size()-1 do
				if rel.con(i) then
					local eff=rm(i)
					if (eff.bone:treeIndex()~=0) then
						c=c+1
					end
				end
			end
		end
		if options.useRelConPos then 
			local conPos, conTarget, conMarkerIndex=unpack(rel.conInfo)
			local markers=config.con.relative
			for i=0, conPos:size()-1 do
				local mi=conMarkerIndex(i)
				assert(markers[mi])
				local eff=rm(mi-1)
				if eff.bone:treeIndex()>=1 then
					c=c+1
				end
			end
		end
		if options.useAbsConPos then 
			local abs=mCON.absolute
			local conPos, conTarget, conMarkerIndex=unpack(abs.conInfo)
			local markers=config.con
			local am=mCollAvoid[0].mEffectors
			for i=0, conPos:size()-1 do
				local mi=conMarkerIndex(i)
				assert(markers[mi])
				local eff=am(mi-1)
				if eff.bone:treeIndex()>=1 then
					c=c+1
				end
			end
		end
		startConIndex=c
	end
	--mCollAvoid[0].mIK:setParam('damping_weight', 0.01, 0.01)  -- default
	--mCollAvoid[0].mIK:setParam('damping_weight', 0.1, 0.1)  --  a much higher value
	
	if options.initialPose then
		startConIndex=startConIndex+1
	end

	-- prepareEffectors: varying and accumulating constraints
	local maxDepth, lines=mCollAvoid[0]:_prepareEffectors(startConIndex, bases, collisionLinkPairs, 0, maxAvoid, mChecker, mCON, options, self)

	local c=0
	if mCON and mCON.relative then
		local rel=mCON.relative 
		local rm=mCollAvoid[0].mRelativeMarkers
		local markers=config.con.relative

		if options.useRelConOri then
			for i=0, rel.con:size()-1 do
				if rel.con(i) then
					local eff=rm(i)
					local importance=rel.importance(i)
					if (eff.bone:treeIndex()==0) then
						-- no geom
					else
						mCollAvoid[0].mIK:_setOrientationConstraint(c, eff.bone, rel.conOri(i), importance)
						c=c+1
					end
				end
			end
		end
		if options.useRelConPos then
			--local conPos, conTarget, conMarkerIndex, conLpos=unpack(rel.conInfo)
			local conPos, conTarget, conMarkerIndex, delta, importances=unpack(rel.conInfo)
			assert(conPos:size()==conMarkerIndex:size())
			for i=0, conPos:size()-1 do
				local mi=conMarkerIndex(i)
				local thr=config.con.relative[mi].thr_distance
				assert(thr)
				local markerInfo=markers[mi]
				assert(markerInfo)
				local eff=rm(mi-1)
				--mCollAvoid[0].mIK:_setDistanceConstraint(c, eff.bone, eff.localpos, rel.conPos(i), thr)
				local otherBone=mLoader:bone(conTarget(i))
				local importance=importances(i)
				if eff.bone:treeIndex()>=1 then
					assert(otherBone:treeIndex()>=1)
					--mCollAvoid[0].mIK:_setRelativeDistanceConstraint(c, eff.bone, eff.localpos, otherBone, conPos(i), thr,1*importance)
					mCollAvoid[0].mIK:_setRelativeDistanceConstraint(c, otherBone, conPos(i),eff.bone, eff.localpos, delta(i),  thr, 0.05*importance)
					c=c+1
				end
			end
		end
		if options.useAbsConPos then
			local abs=mCON.absolute
			local absmarkers=config.con
			local am=mCollAvoid[0].mEffectors
			local conPos, conTarget, conMarkerIndex, delta, importances=unpack(abs.conInfo)
			assert(conPos:size()==conMarkerIndex:size())
			for i=0, conPos:size()-1 do
				local mi=conMarkerIndex(i)
				local markerInfo=absmarkers[mi]
				assert(markerInfo)
				local eff=am(mi-1)
				--mCollAvoid[0].mIK:_setDistanceConstraint(c, eff.bone, eff.localpos, rel.conPos(i), thr)
				local importance=importances(i)*0.05
				if eff.bone:treeIndex()>=1 then
					mCollAvoid[0].mIK:_setPositionConstraint(c, eff.bone, eff.localpos, conPos(i), importance, importance, importance)
					--mCollAvoid[0].mIK:_setRelativeDistanceConstraint(c, eff.bone, eff.localpos, otherBone, conPos(i), thr,1*importance)
					c=c+1
				end
			end
		end
	end
	if options.initialPose then
		-- global inital pose  (which can be difference from per-stage-initial pose)
		mCollAvoid[0].mIK:setParam('damping_weight', 0.1, 0.1) 
		mCollAvoid[0].mIK:_setPoseConstraint(c, options.initialPose, 0.01)
		c=c+1
	end
	assert(c==startConIndex)

	mCollAvoid[0].mIK:_effectorUpdated()
	mCollAvoid[0].mIK:IKsolve(newpose, footPos);

	--do return newpose end
	local numIter=2*maxDepth/maxAvoid
	--local numIter=5
	numIter=math.floor(numIter)+1
	assert(numIter>=1)

	if options.numIterOverride then
		numIter=options.numIterOverride
	end
	

	--RE.output2("numCon", 0)
	for iter=1, numIter do
		if iter ~=1 then
			mChecker:setPoseDOF(0,newpose)
			bases=mChecker:checkCollision(options)
			collisionLinkPairs=bases:getCollisionLinkPairs()

			--mCollAvoid[0].mIK:_changeNumConstraints(0)  -- uncomment to turn off accumulation
			-- accumulate constraints
			local numCon=mCollAvoid[0].mIK:_numConstraints()
			local maxDepth, lines2=mCollAvoid[0]:_prepareEffectors(numCon, bases, collisionLinkPairs,0,maxAvoid, mChecker, mCON, options, self)
			--	for i=0, startConIndex-1 do
			--		mCollAvoid[0].mIK:_setConstraintWeight(i, lines2:rows())
			--	end

			local numCon2=mCollAvoid[0].mIK:_numConstraints()
			--for i=startConIndex, numCon2-1 do
			--	mCollAvoid[0].mIK:_setConstraintWeight(i, 1.0/(numCon2-startConIndex+1))
			--end

			if maxDepth<terminationCondition then
				break
			end

			--local newpose=mIntegrator.pose:copy() -- restart over
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

				local footPos=vector3N(mEffectors:size())
				loader:setPoseDOF(cpose)
				local mEffectors=mCollAvoid[i].mEffectors
				for ii=0,mEffectors:size()-1 do
					local originalPos=mEffectors(ii).bone:getFrame():toGlobalPos(mEffectors(ii).localpos)
					footPos(ii):assign(originalPos)
				end
				local numCon=mCollAvoid[i].mIK:_numConstraints() -- accumulate constraints
				mCollAvoid[i]:_prepareEffectors(numCon, bases, collisionLinkPairs, i, maxAvoid, mChecker, mCON, options, self)

				mCollAvoid[i].mIK:_effectorUpdated()
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

	for i=1,#mObstacles do
		if dbg.lunaType(mObstacles[i])~="Geometry" then
			local loader=mObstacles[i]
			local cpose=mChecker.pose[i]
			mObstacleSkins[i]:setPoseDOF(cpose)
		end
	end
	return newpose
end
-- assumes that mLoader:setPoseDOF has been already called
function CA.CollisionIK:annotateRelativeConOri(mLoader,  config, iframe)
	local rm=config.con.relative
	assert(rm)
	if not rm.conOri_all then
		rm.conOri_all={}
	end
	local conOri
	conOri=quaterN(#rm)

	local effectors=self.mCollAvoid[0].mRelativeMarkers
	for i, marker in ipairs(rm) do
		--for other_bone, con in pairs(marker.con) do
		--end
		conOri(i-1):assign(effectors(i-1).bone:getFrame().rotation)
	end
	rm.conOri_all[iframe+1]=conOri

end

local function _adaptRelativeAnchorAccordingToSurfaceGeometry(anchorPos, config, mProximityDetector, conTargetTI)
	local mLoader=config.mLoader
	if config.isHand and config.isHand(conTargetTI) then
		-- 손가락은 너무 작아 adapt필요 없음. 
		return anchorPos
	end
	local normal=nil
	local dist,nearestPoint, normal=mProximityDetector:calculateNearestSurfacePoint(0, conTargetTI, anchorPos )

	if config.isChest and config.isChest(conTargetTI) then
		-- also search adjacent bodies
		if conTargetTI~=1 then
			-- search parent
			local dist2, nearestPoint2, normal2=mProximityDetector:calculateNearestSurfacePoint(0, mLoader:bone(conTargetTI):parent():treeIndex(), anchorPos )
			if math.abs(dist2)<math.abs(dist) then
				dist=dist2
				nearestPoint=nearestPoint2
				normal=normal2
			end
		end

		if config.spine and config.spine(conTargetTI) then
			-- also search children
			local child=mLoader:bone(conTargetTI):childHead()

			while child do
				-- chest 밖은 search 하지 않는다(의미가 달라짐.)
				if not config.isChest(child:treeIndex())  then
					local dist2, nearestPoint2, normal2=mProximityDetector:calculateNearestSurfacePoint(0, child:treeIndex(), anchorPos )
					if math.abs(dist2)<math.abs(dist) then -- abs는 -값일때 penalty 로 작용. 
						dist=dist2
						nearestPoint=nearestPoint2
						normal=normal2
					end
				end
				child=child:sibling()
			end
		end
	end
	return nearestPoint, dist, normal
end
-- assumes that mLoader:setPoseDOF has been already called
-- 미리 계산한 relative, absolute(obstacle) constraint벡터에서 현재 프레임 값만 가져옴. 
function CA.CollisionIK:annotateRelativeConPos(mLoader, mProximityDetector, config, iframe)
	local rm=config.con.relative
	assert(rm)
	if not rm.conPos_all then
		rm.conPos_all={}
	end
	-- 모두 size는 # of active relative constraints
	local conPos=vector3N()
	local conTarget=intvectorn()
	local conMarkerIndex=intvectorn()
	local aDelta=vector3N()
	local importances=vectorn()


	mProximityDetector:setWorldTransformations(0, mLoader:fkSolver())

	local effectors=self.mCollAvoid[0].mRelativeMarkers
	local lines=vector3N()
	for i, marker in ipairs(rm) do
		for icon, softCon in ipairs(marker.softConstraints) do
			local conTargetTI=getConTargetTI(mLoader, softCon)
			local ef=effectors(i-1)
			local bcon, importance=getImportance(iframe, softCon)
			if bcon then

				--print(ef.bone, other_bone)
				local markerPos=ef.bone:getFrame()*ef.localpos
				dbg.draw('SphereM', markerPos, 'nearestpos'..i, 'red_transparent', marker.thr_distance)

				local dist
				local nearestPoint
				local lnearestpos, delta
				local conposInfo=softCon
				assert(conposInfo.dist(iframe)~=-1)
				local conii=conposInfo.conInfo:row(iframe)
				lnearestpos=conii:toVector3(0)
				delta=conii:toVector3(3)

				local otherBone=mLoader:bone(conTargetTI)
				local oframe=otherBone:getFrame()
				nearestPoint=oframe*lnearestpos
				-- wide-con adaptation is undesirable.
				--nearestPoint=_adaptRelativeAnchorAccordingToSurfaceGeometry(nearestPoint, config, mProximityDetector, conTargetTI)

				-- delta (should be similar to) markerPos -nearestPoint
				aDelta:pushBack(delta)
				importances:pushBack(importance)
				dist=0
				if true then
					-- markerInfo.conPos contains only active constraints.
					conPos:pushBack(otherBone:getFrame():inverse()*nearestPoint) -- local position
					conTarget:pushBack(conTargetTI)
					conMarkerIndex:pushBack(i)
					--conPos(i-1):assign(nearestPoint) -- global position
					dbg.draw('Sphere', nearestPoint*100, 'nearestpos'..i..'_'..conTargetTI, 'red', 1)
					lines:pushBack(markerPos*100)
					lines:pushBack(nearestPoint*100)
				end
			else
				dbg.erase('SphereM', 'nearestpos'..i)
				dbg.erase('Sphere', 'nearestpos'..i..'_'..conTargetTI)
			end
		end
	end
	if lines:size()>0 then
		dbg.draw('Traj', lines:matView(), 'relative','solidblue')
	end
	rm.conPos_all[iframe+1]={conPos, conTarget, conMarkerIndex, aDelta, importances}
end

function CA.CollisionIK:annotateAbsoluteConPos(mLoader, mProximityDetector, config, iframe)
	local am=config.con
	assert(am)
	if not am.conPos_all then
		am.conPos_all={}
	end
	local conPos=vector3N()
	local conMarkerIndex=intvectorn() 
	local conTarget=intvectorn()  
	local aDelta=vector3N()
	local importances=vectorn()

	mProximityDetector:setWorldTransformations(0, mLoader:fkSolver())

	-- see also visualizeRelativeConstraintsAdaptation.lua : visualizeConstraints function. 
	-- (visualizeConstraints를 먼저 구현한 후 이 함수를 구현해서 구조가 비슷함,)
	local effectors=self.mCollAvoid[0].mEffectors
	local lines=vector3N()
	for i, marker in ipairs(am) do
		-- marker.softContstraints are copied in "adaptConstraints" 
		for icon, softCon in ipairs(marker.softConstraints) do
			local dist=softCon.dist
			local softConInfo=softCon.conInfo
			local bcon, importance_o=getImportance(iframe, softCon)
			local ef=effectors(i-1)

			if bcon then

				--print(ef.bone, other_bone)
				local markerPos=ef.bone:getFrame()*ef.localpos
				dbg.draw('SphereM', markerPos, 'nearestpos'..i, 'red_transparent', marker.thr_distance)

				local nearestPoint
				local lnearestpos, delta
				local conii=softCon.conInfo:row(iframe)
				lnearestpos=conii:toVector3(0)
				delta=conii:toVector3(3)

				local other_loaderIndex=1
				local other_loader=mCollisionIK.mChecker.collisionDetector.detector:getModel(other_loaderIndex)
				assert(other_loader:name()==softCon.other_body)
				local oframe=other_loader:bone(1):getFrame() 
				nearestPoint=oframe*lnearestpos

				if true then
					-- adapt an absolute anchor to geoemtry.
					local _,nearestPoint2=mProximityDetector:calculateNearestSurfacePoint(other_loaderIndex, 1, nearestPoint )
					-- test passed
					--assert(nearestPoint:distance(nearestPoint2)<0.01)
					nearestPoint:assign(nearestPoint2)
				end

				-- delta (should be similar to) markerPos -nearestPoint

				aDelta:pushBack(delta)
				importances:pushBack(importance_o)
				if true then

					-- markerInfo.conPos contains only active constraints.
					--conPos:pushBack(oframe:inverse()*nearestPoint) -- local position
					conPos:pushBack(nearestPoint) -- global position
					conTarget:pushBack(other_loaderIndex)
					conMarkerIndex:pushBack(i)
					--conPos(i-1):assign(nearestPoint) -- global position
					dbg.draw('Sphere', nearestPoint*100, 'nearestpos'..i..'_'..icon, 'red', 1)
					lines:pushBack(markerPos*100)
					lines:pushBack(nearestPoint*100)
				end
			else
				dbg.erase('SphereM', 'abs_nearestpos'..i)
				dbg.erase('Sphere', 'abs_nearestpos'..i..'_'..icon)
			end
		end
	end
	if lines:size()>0 then
		dbg.draw('Traj', lines:matView(), 'absolute','solidblue')
	end
	am.conPos_all[iframe+1]={conPos, conTarget, conMarkerIndex, aDelta, importances}
end

function CA.CollisionIK:solveProximityIK(mProximityDetector, mLoader, posedof, config, options,iframe)

	local initialPose=posedof:copy()
	mLoader:setPoseDOF(initialPose)
	mProximityDetector:setWorldTransformations(0, mLoader:fkSolver())

	local con={}
	con.con=boolN(#config.con)
	con.conPos=vector3N(#config.con)

	if config.con.relative then
		local rm=config.con.relative
		con.relative={}
		-- # of relative markers
		con.relative.con=boolN(#rm)
		con.relative.importance=CT.ones(#rm)

		if options.useRelConPos then 
			assert(rm.conPos_all) -- annotateRelativeConPos prepares this.
			con.relative.conInfo=rm.conPos_all[iframe+1]
		end
		if options.useRelConOri then 
			assert(rm.conOri_all) -- annotateRelativeConOri prepares this.
			con.relative.conOri=rm.conOri_all[iframe+1]
		end
		if options.useAbsConPos then 
			local am=config.con
			con.absolute={}
			assert(am.conPos_all) -- annotateRelativeConPos prepares this.
			con.absolute.conInfo=am.conPos_all[iframe+1]
		end
	end

	local eff=self.mCollAvoid[0].mEffectors

	for i, v in ipairs(config.con) do
		con.con:set(i-1, v.con(iframe))
		local ef=eff(i-1)
		con.conPos(i-1):assign( ef.bone:getFrame()*ef.localpos)
	end

	if config.con.relative then
		-- for  orientation constraints
		local rm=config.con.relative
		local conr=con.relative
		local effectors=self.mCollAvoid[0].mRelativeMarkers
		local lines=vector3N()
		for i, marker in ipairs(rm) do
			conr.con:set(i-1, false)

			local marker_importance=0
			local ef=effectors(i-1)
			for icon, softCon in ipairs(marker.softConstraints) do
				local conTargetTI=getConTargetTI(mLoader, softCon)
				local bcon, importance=getImportance(iframe, softCon)

				if bcon then
					conr.con:set(i-1, true )
					marker_importance=math.max(importance, marker_importance)
				end
			end
			conr.importance:set(i-1, marker_importance)
		end
	end
	options.iframe=iframe
	options.initialPose=config.mMotionDOF:row(iframe)

	local pose=self:solveIK(initialPose, con, options )
	return pose
end

function CA.checkAllChildrenExcluding(loader, bonename)
	local out=CA.checkAllChildren(loader, bonename)
	local b=loader:getBoneByName(bonename)
	out:set(b:treeIndex(), false)
	return out
end

function CA.checkAllChildren(loader, bonename)
	local out=boolN()
	out:resize(loader:numBone())
	out:setAllValue(false)

	local b=loader:getBoneByName(bonename)

	local function dfs(out, b)
		out:set(b:treeIndex(), true)
		b=b:childHead()
		while b do
			dfs(out, b)
			b=b:sibling()
		end
	end
	if b then
		dfs(out, b)
	end
	return out
end
function CA.checkAllParentsIncluding(loader, bonename)
	local out=boolN()
	out:resize(loader:numBone())
	out:setAllValue(false)
	
	local b=bonename
	if type(bonename)=='string' then
		b=loader:getBoneByName(bonename)
	end
	CA._checkAllParentsIncluding(out, b)
	return out
end
function CA._checkAllParentsIncluding(out, b)
	while b do
		if b:treeIndex()==1 then
			break
		end
		out:set(b:treeIndex(), true)
		b=b:parent()
	end
end

function CA.checkHighPriorityConstrained(config, mLoader, constraints)
	local interactionBones=config.interactionBones
	assert(interactionBones)
	assert(#interactionBones==#constraints)

	local out=boolN()
	out:resize(mLoader:numBone())
	out:setAllValue(false)

	local interactionConfig=config.interactionBoneInfo
	assert(#interactionConfig==#constraints)
	for i, v in ipairs(interactionBones) do
		if constraints[i] and interactionConfig[i].high_priority then
			CA._checkAllParentsIncluding(out, mLoader:bone(config.interactionBones[i]))
		end
	end
	out:set(1, false)
	return out
end
function CA.printBones(mLoader, bones)
	for i=1, mLoader:numBone()-1 do
		if bones(i) then
			print(mLoader:bone(i))
		end
	end
end
function CA.checkBones(mLoader, bones)
	if type(bones)=='string' then
		bones={bones}
	end
	local out=boolN()
	out:resize(mLoader:numBone())
	out:setAllValue(false)
	for i,v in ipairs(bones) do
		out:set(mLoader:getTreeIndexByName(v), true)
	end
	return out
end
function CA.annotateImportance(config)
	print('deprecated, do not use.')
end
function CA.collectRelativeMarkerTraj(config)
	print('deprecated, do not use.')
	local mLoader=config.mLoader
	local mMotionDOF=config.mMotionDOF
	assert(mMotionDOF)
	local traj={}
	local rm=config.con.relative
	local frames={}
	for imarker, marker in ipairs(rm) do
		for other_bone, con in pairs(marker.con) do
			local softCon=marker.softCon[other_bone]
			local dist=softCon.dist
			local softConInfo=softCon.conInfo
			local conTargetTI=mLoader:getTreeIndexByName(other_bone)
			assert(conTargetTI~=-1)

			local conPhases=con:runLengthEncode()
			local frame_traj=matrixn(con:size(), 7)
			table.insert(frames, {frame_traj, conTargetTI})
		end
	end
	for i=0, mMotionDOF:numFrames()-1 do
		mLoader:setPoseDOF(mMotionDOF:row(i))
		for b,v in ipairs(frames) do
			local frame_traj=v[1]
			v[1]:row(i):setTransf(0, mLoader:bone(v[2]):getFrame())
		end
	end

	local con_true=boolN(mMotionDOF:rows())
	con_true:setAllValue(true)
	for imarker, marker in ipairs(rm) do
		for other_bone, con in pairs(marker.con) do
			local softCon=marker.softCon[other_bone]
			local dist=softCon.dist
			local softConInfo=softCon.conInfo
			--local importance=softCon.importance
			--local con=importance:greater(0.0)
			local con=con_true
			local conTargetTI=mLoader:getTreeIndexByName(other_bone)

			local conPhases=con:runLengthEncode()
			local markerTraj=vector3N(con:size())
			markerTraj:setAllValue(vector3(0,0,0))


			for i=0, conPhases:size()-1 do
				local s=conPhases:startI(i)
				local e=conPhases:endI(i)

				for f=s,e-1 do
					local conposInfo=marker.softCon[other_bone]
					assert(conposInfo.dist(f)~=-1)
					local conii=conposInfo.conInfo:row(f)
					local lnearestpos=conii:toVector3(0)
					--local oframe=mLoader:bone(conTargetTI):getFrame() -- setposedof necessary.
					local oframe=frames[#traj+1][1]:row(f):toTransf()
					nearestPoint=oframe*lnearestpos
					delta=conii:toVector3(3)
					-- delta == markerPos -nearestPoint
					local markerPos=nearestPoint+delta
					markerTraj(f):assign(markerPos)
				end
			end

			table.insert(traj, { con, markerTraj,markerIndex=imarker, other_bone=conTargetTI, frames=frames[#traj+1]})
		end
	end
	return traj
end
function CA.adaptAnchorsToCurrentSkeleton(config, loader, motiondof)
	return CA.adaptAnchors(config, loader, motiondof, mCollisionIK)
end
function CA.adaptAnchors(config, loader, motiondof, mCollisionIK, srcConfig)
	local rm=config.con.relative
	local mLoader=config.mLoader
	local effectors=mCollisionIK.mCollAvoid[0].mRelativeMarkers
	local mChecker=mCollisionIK.mChecker
	local mProximityDetector=mChecker.collisionDetector
	assert(mChecker)
	assert(mProximityDetector)

	for imarker, marker in ipairs(rm) do
		local ef=effectors(imarker-1)
		for icon, softCon in ipairs(marker.softConstraints) do
			local conTargetTI=getConTargetTI(mLoader, softCon)
			local conposInfo=softCon
			local dist=conposInfo.dist
			local softConInfo=conposInfo.conInfo
			softConInfo.v:resize(softConInfo.v:rows(), 9) -- add 3 columns to store normals.
			local importance=conposInfo.importance
			if conTargetTI==-1  and config.adaptMissingBone then
				local ts=softCon.ts
				local lnearest=softConInfo:row(ts):toVector3(0) -- on original skeleton
				local v={ bone=softCon.other_body, lpos=lnearest:copy()}
				config.adaptMissingBone(mLoader, v)
				conTargetTI=mLoader:getTreeIndexByName(v.bone)
				softConInfo:row(ts):setVec3(0, v.lpos)
				softCon.conTargetTI=conTargetTI
			end

			if conTargetTI~=-1 then
				local conTargetBone=mLoader:bone(conTargetTI)
				local s=importance:startI()
				local e=importance:endI()

				local ts=softCon.ts
				local te=softCon.te

				local lnearest=softConInfo:row(ts):toVector3(0) -- on original skeleton
				-- tested 0
				--for iframe=s, e-1 do
				--	print(softConInfo:row(iframe):toVector3(0):distance(lnearest))
				--end
				if srcConfig then
					assert(srcConfig.mChecker)
					local srcBboxSize=vector3()
					local conTargetSrcTI=getConTargetSourceTI(srcConfig.mLoader, softCon)
					local okay=srcConfig.mChecker.collisionDetector.detector:getLocalBoundingBoxSize(0, conTargetSrcTI, srcBboxSize)

					local tgtBboxSize=vector3()
					local okay2=mProximityDetector.detector:getLocalBoundingBoxSize(0, conTargetTI, tgtBboxSize)

					if okay and okay2 then
						lnearest.x=lnearest.x*tgtBboxSize.x/srcBboxSize.x
						lnearest.y=lnearest.y*tgtBboxSize.y/srcBboxSize.z
						lnearest.z=lnearest.z*tgtBboxSize.z/srcBboxSize.z
					end



				end


				for iframe=ts, te-1 do
					mLoader:setPoseDOF(motiondof:row(iframe))
					mChecker:setPoseDOF(0, motiondof:row(iframe))

					local oframe=mLoader:bone(conTargetTI):getFrame() -- setposedof necessary.
					-- the following two anchorPos methods both make sense with some trade-off
					-- method 1
					--local delta=softConInfo:row(iframe):toVector3(3)
					--local anchorPos=ef.bone:getFrame()*ef.localpos-delta

					--method 2
					local anchorPos=oframe*lnearest
					local nearestPoint, dist, normal=_adaptRelativeAnchorAccordingToSurfaceGeometry(anchorPos, config, mProximityDetector, conTargetTI)

					softConInfo:row(iframe):setVec3(0, oframe:inverse()*nearestPoint)
					
					if normal then
						softConInfo:row(iframe):setVec3(6, normal)
					end
				end
				local new_lnearestpos=softConInfo:range(ts, te, 0, 3):mean():toVector3(0)
				local new_normal=softConInfo:range(ts, te, 6, 9):mean():toVector3(0)
				if new_normal:length()>0.8 then
					new_normal:normalize()
				end
				for f=s,e-1 do
					assert(conposInfo.dist(f)~=-1)
					--local oframe=mLoader:bone(conTargetTI):getFrame() -- setposedof necessary.
					softConInfo:row(f):setVec3(0, new_lnearestpos)
					softConInfo:row(f):setVec3(6, new_normal)
				end
			end
		end
	end
	--print(rm[1].softConstraints[1].conInfo:row(0)) dbg.console()
	--
	if config.rootTranslationScaleFactor then
		local scalefactor=config.rootTranslationScaleFactor
		local am=config.con
		local abseffectors=mCollisionIK.mCollAvoid[0].mEffectors
		for i, marker in ipairs(am) do
			-- marker.softContstraints are copied in "adaptConstraints" 
			for icon, softCon in ipairs(marker.softConstraints or {}) do
				local dist=softCon.dist
				local softConInfo=softCon.conInfo
				local conii=softCon.conInfo.v
				local y=conii:column(1):copy()
				conii:slice(0,0,0,3):assign(conii:slice(0,0,0,3)*scalefactor) -- lnearestpos
				conii:column(1):assign(y) -- preserve y
				conii:slice(0,0,3,6):assign(conii:slice(0,0,3,6)*scalefactor) -- delta
				local yy=softCon.anchorPos.y
				softCon.anchorPos:scale(scalefactor)
				softCon.anchorPos.y=yy
			end
		end
	end
end

local function collectSoftConstraints(marker, MAX_SPREAD, ii, conPos , getTargetFrame, _other_body ,_useLocalConPos) 
	local softConstraints=marker.softConstraints
	local thr_distance=marker.thr_distance
	local markerTraj=marker.markerPos

	local function fill01basedOnDist(importance, prev_e, s, dist)
		prev_e=math.max(s-MAX_SPREAD, prev_e)
		for f=s-1, prev_e, -1 do
			if dist(f)>thr_distance then
				prev_e=f
				break
			end
		end
		for i=prev_e,s-1 do
			importance:set(i, sop.smoothMap(i, prev_e, s, 0, 1))
		end
	end

	local function fill10basedOnDist(importance, e, next_s, dist)
		next_s=math.min(e+MAX_SPREAD, next_s)
		for f=e, next_s-1 do
			if dist(f)>thr_distance then
				next_s=f
				break
			end
		end
		for i=e,next_s-1 do
			importance:set(i, sop.smoothMap(i, e, next_s, 1, 0))
		end
	end

	-- fill importance
	for i=0, ii:size()-1 do
		local anchorPos=conPos(i):copy()
		local s=ii:startI(i)
		local e=ii:endI(i)

		local prev_e, next_s
		if i==0 then
			prev_e=-MAX_SPREAD
		else
			prev_e=ii:endI(i-1)
		end
		if i==ii:size()-1 then
			next_s=e+MAX_SPREAD
		else
			next_s=ii:startI(i+1)
		end
		local importance=vector_offset(CT.zeros(e-s+MAX_SPREAD*2), MAX_SPREAD, s)
		local dist=vector_offset(CT.ones(e-s+MAX_SPREAD*2)*(1e5), MAX_SPREAD, s)
		local conInfo=mat_offset(CT.zeros(e-s+MAX_SPREAD*2, 6), MAX_SPREAD, s)
		if _useLocalConPos then
			for i=dist:startI(), dist:endI()-1 do
				if i>=markerTraj:rows() then
					break
				end
				local lnearest=anchorPos
				local nearest=getTargetFrame(marker, i)*lnearest

				--dist:set(i, nearest:distance(markerTraj:row(i):toVector3()))
				dist:set(i, marker.dist(i)) -- signed distance
				conInfo:row(i):setVec3(0, lnearest)
			end
		else
			for i=dist:startI(), dist:endI()-1 do
				if i>=markerTraj:rows() then
					break
				end
				dist:set(i, anchorPos:distance(markerTraj:row(i):toVector3()))

				local lnearest=getTargetFrame(marker, i):toLocalPos(anchorPos)
				conInfo:row(i):setVec3(0, lnearest) -- unused
			end
		end

		fill01basedOnDist(importance, prev_e,s, dist)
		importance:range(s,e):setAllValue(1)
		fill10basedOnDist(importance, e,next_s, dist)

		--if start_debugging then dbg.console() end

		local softCon={
			importance=importance, 
			dist=dist,
			other_body=_other_body,
			anchorPos=anchorPos,
			conInfo=conInfo,
			ts=s,
			te=e,
		}
		table.insert(softConstraints, softCon)
		-- fill delta
		local dist=softCon.dist
		local softConInfo=softCon.conInfo
		local importance=softCon.importance

		do
			local s=importance:startI()
			local e=math.min(importance:endI(), marker.markerPos:rows())

			local ts=softCon.ts
			local te=softCon.te
			--assert(conToe(ts) or conHeel(ts))
			--assert(conToe(te-1) or conHeel(te-1) )

			local lnearestpos=softConInfo:range(ts, te, 0, 3):mean():toVector3(0)
			for f=s,e-1 do

				assert(softCon.dist(f)~=-1)
				softConInfo:row(f):setVec3(0, lnearestpos)
				local nearestPoint=getTargetFrame(marker, f)*lnearestpos

				local markerPos=marker.markerPos:row(f):toVector3()
				local delta = markerPos -nearestPoint



				softConInfo:row(f):setVec3(3, delta)
			end
		end
	end
end

function CA.anchorRelativeMarkers(config)
	local mLoader=config.mLoader
	local mMotionDOF=config.mMotionDOF
	assert(mMotionDOF)
	local traj={}
	local rm=config.con.relative

	-- cache bone transformations
	for b=1, mLoader:numBone()-1 do
		traj[b]=matrixn(mMotionDOF:rows(), 7)
	end

	for i=0, mMotionDOF:numFrames()-1 do
		mLoader:setPoseDOF(mMotionDOF:row(i))
		for b=1, mLoader:numBone()-1 do
			traj[b]:row(i):setTransf(0, mLoader:bone(b):getFrame())
		end
	end
	fc=require('retargetting/module/footSkateCleanup')
	for imarker, marker in ipairs(rm) do
		marker.softConstraints={}
		local conSourceTI=mLoader:getTreeIndexByName(marker.bone)
		local markerTraj=matrixn(mMotionDOF:rows(), 3)
		for i=0, mMotionDOF:numFrames()-1 do
			markerTraj:row(i):setVec3(0, traj[conSourceTI]:row(i):toTransf()*marker.lpos)
		end
		for other_bone, con in pairs(marker.con) do
			local softCon=marker.softCon[other_bone]
			local conTargetTI=mLoader:getTreeIndexByName(other_bone)
			local conTargetBone=mLoader:bone(conTargetTI)
			local lnearestTraj=softCon.conInfo:sub(0,0,0,3)
			local conPos, ii=fc.getConstraintPositions(con, lnearestTraj)
			--dbg.quickDraw(conPos+vector3(1,0,0))

			local MAX_SPREAD=30

			local function getTargetFrame(markerConfig, i)
				return markerConfig.targetTraj:row(i):toTransf(0)
			end

			local markerConfig=
			{
				softConstraints=marker.softConstraints,
				thr_distance=marker.thr_distance  *3,
				markerPos=markerTraj,
				targetTraj=traj[conTargetTI],
				dist=softCon.dist,
			}
			--if other_bone=='mixamorig:Head' and marker[1]=='rightFinger2' then start_debugging=true end
			--if other_bone=='mixamorig:RightUpLeg' and marker[1]=='leftFinger2' then start_debugging=true dbg.console() end
			--if other_bone=='mixamorig:Spine2' and marker[1]=='leftPalm' then start_debugging=true dbg.console() end
			collectSoftConstraints(markerConfig, MAX_SPREAD, ii, conPos, getTargetFrame, other_bone, true)
			--if other_bone=='mixamorig:RightUpLeg' and marker[1]=='leftFinger2' then start_debugging=true dbg.console() end
		end
		--if marker[1]=='leftFinger2' then start_debugging=true dbg.console() end
		marker.softCon=nil
	end
end
function CA.anchorAbsoluteMarkers(config)
	local mLoader=config.mLoader
	local am=config.con

	assert(config.obstacles)
	for iobs, obs in ipairs(config.obstacles) do
		config.collisionChecker:registerPair(0, iobs)
	end
	assert(am[1][1]=='leftToe')
	assert(am[2][1]=='leftHeel')
	assert(am[3][1]=='rightToe')
	assert(am[4][1]=='rightHeel')

	if not config.collisionChecker then
		config.collisionChecker=config:createAdditionalCollisionChecker()
	end
	local mChecker=config.collisionChecker

	fc=require('retargetting/module/footSkateCleanup')
	local toe=am[1]
	local heel=am[2]
	local footLen=toe.markerPos:row(0):toVector3(0):distance(heel.markerPos:row(0):toVector3(0))
	local conPosL, conDirL, iiL=fc.getContactPositions_v2(footLen, toe.con, heel.con, toe.markerPos, heel.markerPos )
	toe=am[3]
	heel=am[4]
	local conPosR, conDirR, iiR=fc.getContactPositions_v2(footLen, toe.con, heel.con, toe.markerPos, heel.markerPos )
	for imarker, marker in ipairs(am) do
		local markerBone=mLoader:getBoneByName(marker.bone)
		marker.treeIndex=markerBone:treeIndex()
		local other_obs='floor'
		local other_loader=mChecker.collisionDetector.detector:getModel(1)
		assert(other_loader:name()==other_obs)
		local con=marker.con
		local markerTraj=marker.markerPos

		marker.softConstraints={}
		if not marker.thr_distance then
			marker.thr_distance=0.6  -- 60cm 넘어가면 importance -> 0. 
		end

		local ii, conPos, conDir, anchorPos
		if imarker<=2 then 
			ii=iiL
			conPos=conPosL
			conDir=conDirL
		else
			ii=iiR
			conPos=conPosR
			conDir=conDirR
		end
		if math.fmod(imarker, 2)==1 then
			anchorPos=conPos+conDir*(footLen*0.5)
		else
			anchorPos=conPos-conDir*(footLen*0.5)
		end
		

		local MAX_SPREAD=30
		local function getTargetFrame()
			return other_loader:bone(1):getFrame()
		end
		collectSoftConstraints(marker, MAX_SPREAD, ii, anchorPos, getTargetFrame, other_obs)

	end
end
return CA



