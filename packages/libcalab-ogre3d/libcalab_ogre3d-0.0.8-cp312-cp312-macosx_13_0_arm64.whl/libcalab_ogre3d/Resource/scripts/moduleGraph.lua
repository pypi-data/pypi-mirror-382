
require("common")
require('subRoutines/VelocityFields')
require('tl')


function calcSmoothProjectedRootTraj(mot, discontinuity, cutState)
	local traj=calcProjectedEulerRootTraj(mot, discontinuity)
	local midtraj=_calcMidTraj(traj, discontinuity, cutState)
	local out=matrixn(mot:rows(), 7)

	out:column(1):setAllValue(0)
	out:column(0):assign(midtraj:column(0))
	out:column(2):assign(midtraj:column(1))
	for i =0, out:rows()-1 do
		out:row(i):setQuater(3, quater(midtraj(i,2), vector3(0,1,0)))
	end

	return out
end

function calcProjectedEulerRootTraj(mot, discontinuity)
	local out=matrixn(mot:rows(), 3)
	out:column(0):assign(mot:column(0)) -- x
	out:column(1):assign(mot:column(2)) -- z

	for i=0, mot:rows()-1 do -- ry
		out:set(i, 2, mot:row(i):toQuater(3):rotationAngleAboutAxis(vector3(0,1,0)))
	end

	local seg=SegmentFinder(discontinuity)

	for i=0, seg:numSegment()-1 do
		local s=seg:startFrame(i)
		local e=seg:endFrame(i)
		out:column(2):range(s,e):alignEulerAngles()
	end
	return out
end


-- traj: matrixn. for example, eulerRootTraj
function _calcMidTraj(traj, discontinuity, cutState)

	local out=matrixn(traj:rows(), traj:cols())
	local seg=SegmentFinder(discontinuity)

	for i=0, seg:numSegment()-1 do
		local s=seg:startFrame(i)
		local e=seg:endFrame(i)
		local spline=_private_calcMidTraj(traj:sub(s,e,0,0), cutState:range(s,e))
		assert(spline[1]:rows()==e-s)
		out:sub(s,e):assign(spline[1]*0.5+spline[2]*0.5)
	end
	return out
end

function _private_calcMidTraj(traj, cutState)

	local keyPoints={ matrixn(), matrixn()}
	local keyTimes={ vectorn(), vectorn()}

	local max_points=math.ceil((cutState:count()-1)/2)+1

	matrixn.reserve=function (self, nrow, ncol)  self:setSize(nrow, ncol) self:setSize(0,0) end

	keyPoints[1]:reserve(max_points, traj:cols())
	keyPoints[2]:reserve(max_points, traj:cols())

	keyPoints[1]:pushBack(traj:row(0))
	keyPoints[2]:pushBack(traj:row(0))
	keyTimes[1]:pushBack(0)
	keyTimes[2]:pushBack(0)

	c=1
	assert(cutState(cutState:size()-1)==false)
	for i =1, cutState:size()-1 do
		if cutState(i) then
			keyPoints[c]:pushBack(traj:row(i))
			keyTimes[c]:pushBack(i)
			c=math.fmod(c,2)+1
		end
	end

	for c = 1,2 do
		keyPoints[c]:pushBack(traj:row(traj:rows()-1))
		keyTimes[c]:pushBack(traj:rows()-1)
	end

	local nf=traj:rows()
	local ncols=traj:cols()

	local splines={ matrixn(nf, ncols), matrixn(nf, ncols)}

	for icurve =1, 2 do
		local spline=math.NonuniformSpline(keyTimes[icurve], keyPoints[icurve])
		local samplePoints=tl.linspace(0, nf-1, nf)
		spline:getCurve(samplePoints, splines[icurve])
	end
	return splines
end


function filterSegments(mat, discontinuity, filterWindow, frameRate)
	local seg=SegmentFinder(discontinuity)

	for i=0, seg:numSegment()-1 do
		local s=seg:startFrame(i)
		local e=seg:endFrame(i)
		if e-s>filterWindow*frameRate then
			local kernelSize=math.calcKernelSize(filterWindow, 1/frameRate)
			math.filter(mat:sub(s,e,0,0), kernelSize)
		end
	end
end

function checkEulerContinuity(mLoader, motionDOF_all, discontinuity)
	local seg
	if not discontinuity then
		discontinuity=boolN(motionDOF_all:rows())
	end
	seg=SegmentFinder(discontinuity)
	local maxAngle=0 
	local maxDeltaAngle=0
	for iseg=0, seg:numSegment()-1 do
		local s=seg:startFrame(iseg)
		local e=seg:endFrame(iseg)
		local motionDOF=motionDOF_all:range(s,e)
		for i=0, motionDOF:rows()-1 do
			xf=motionDOF:row(i)
			local a=xf:slice(7,0):maximum()
			local b=xf:slice(7,0):minimum()
			maxAngle=math.max(maxAngle, a, -b)
			if(a>5.5) or b<-5.5 then
				local dofIndex=xf:slice(7,0):abs():argMax()+7;
				local bone=mLoader:bone(mLoader.dofInfo:DOFtoBone(dofIndex))


				mLoader:setPoseDOF(xf)

				print('Euler angle error! frame:', i+s, xf(dofIndex), 'dofIndex:', dofIndex, bone:name(), 
				mLoader.dofInfo:startT(bone:treeIndex())-dofIndex, 
				bone:getRotationalChannels(),
				bone:getLocalFrame().rotation
				)

				return false
			end
		end
		for i=1, motionDOF:rows()-1 do
			pxf=motionDOF:row(i-1)
			xf=motionDOF:row(i)

			delta=xf-pxf
			local a=delta:slice(7,0):maximum()
			local b=delta:slice(7,0):minimum()
			maxDeltaAngle=math.max(maxDeltaAngle, a, -b)
			-- 1.5: 86 degrees
			if(a>1.8) or b<-1.8 then
				local dofIndex=delta:slice(7,0):abs():argMax()+7;
				local bone=mLoader:bone(mLoader.dofInfo:DOFtoBone(dofIndex))


				mLoader:setPoseDOF(xf)

				print('Ignoring euler anglular veloicty error! frame:', i+s, delta(dofIndex), pxf(dofIndex), xf(dofIndex), 'dofIndex:', dofIndex, bone:name(), 
				mLoader.dofInfo:startT(bone:treeIndex())-dofIndex, 
				bone:getRotationalChannels(),
				bone:getLocalFrame().rotation
				)
				local startT=mLoader.dofInfo:startT(bone:treeIndex())
				local endR=mLoader.dofInfo:endR(bone:treeIndex())
				print(xf:range(startT, endR))
				print(pxf:range(startT, endR))
				local s=mLoader.dofInfo:startT(bone:treeIndex())
				local e=mLoader.dofInfo:endR(bone:treeIndex())
				print(dofIndex, s, e, pxf:range(s,e), xf:range(s,e))

				mLoader:setPoseDOF(pxf)
				local q1=bone:getLocalFrame().rotation:copy()
				mLoader:setPoseDOF(xf)
				local q2=bone:getLocalFrame().rotation:copy()
				local qd=quater()
				qd:difference(q1,q2)
				print('quaternion diff:', qd:rotationAngle(), q1, q2)
				return true
			end
		end
	end
	print('maxAngle, deltaAngle:', maxAngle, maxDeltaAngle)
	return true
end
function calculateEulerDistance(mLoader, motionDOF_all, discontinuity)
	local seg
	if not discontinuity then
		discontinuity=boolN(motionDOF_all:rows())
	end
	seg=SegmentFinder(discontinuity)
	local distance=0
	local MSE=0
	for iseg=0, seg:numSegment()-1 do
		local s=seg:startFrame(iseg)
		local e=seg:endFrame(iseg)
		local motionDOF=motionDOF_all:range(s,e)
		for i=1, motionDOF:rows()-1 do
			pxf=motionDOF:row(i-1)
			xf=motionDOF:row(i)

			delta=xf-pxf
			distance=distance+delta:slice(7,0):abs():sum()
			MSE=MSE+delta:slice(7,0):dotProduct(delta:slice(7,0))
		end
		print(iseg, distance)
	end
	print('mean per-joint euler distance:', distance/(motionDOF_all:numFrames()*(mLoader:numBone()-1)))
	print('mean per-joint squared euler distance:', MSE/(motionDOF_all:numFrames()*(mLoader:numBone()-1)))
	local qd,sqd=calculateQuaterDistance(mLoader, motionDOF_all, discontinuity)
	print('ratio: ', (distance/(motionDOF_all:numFrames()*(mLoader:numBone()-1)))/qd,
	(MSE/(motionDOF_all:numFrames()*(mLoader:numBone()-1)))/sqd)

end

function calculateQuaterDistance(mLoader, motionDOF_all, discontinuity)
	local seg
	if not discontinuity then
		discontinuity=boolN(motionDOF_all:rows())
	end
	seg=SegmentFinder(discontinuity)
	local distance=0
	local MSE=0
	local mot
	if motionDOF_all.dofInfo then
		mot=Motion(motionDOF_all)
	else
		mot=Motion(mLoader, motionDOF_all)
	end
	for iseg=0, seg:numSegment()-1 do
		local s=seg:startFrame(iseg)
		local e=seg:endFrame(iseg)
		local motionDOF=motionDOF_all:range(s,e)
		for i=1, motionDOF:rows()-1 do
			pxf=mot:pose(i-1)
			xf=mot:pose(i)
			for j=1, pxf:numRotJoint()-1 do
				local d=quater()
				d:difference(pxf.rotations(j), xf.rotations(j))
				local angle=d:rotationAngle()
				distance=distance+angle
				MSE=MSE+angle*angle
			end


		end
		--print(iseg, distance)
	end
	print('mean per-joint quater distance:', distance/(motionDOF_all:numFrames()*(mLoader:numBone()-1)))
	print('mean per-joint squared quater distance:', MSE/(motionDOF_all:numFrames()*(mLoader:numBone()-1)))
	return distance/(motionDOF_all:numFrames()*(mLoader:numBone()-1)), MSE/(motionDOF_all:numFrames()*(mLoader:numBone()-1))
end

function findEulerMidPoint(mLoader, motionDOF_all)
	local minEuler=vectorn()
	local maxEuler=vectorn()
	minEuler:minimum(motionDOF_all)
	maxEuler:maximum(motionDOF_all)
	local midpose=mLoader:getPoseDOF()
	midpose:slice(7,0):assign(minEuler:slice(7,0)*0.5+maxEuler:slice(7,0)*0.5)
	return midpose
end

-- this function modifies both mLoader and motionDOF_all
-- ALso, you shod set vocaburaties for shoulder joints, for example:
-- mLoader:_changeVoca(MotionLoader.LEFTSHOULDER,mLoader:findBone("LeftShoulder"))
-- mLoader:_changeVoca(MotionLoader.RIGHTSHOULDER,mLoader:findBone("RightShoulder"))

function fixEulerContinuity(mLoader, motionDOF_all, discontinuity)
	local motion_all
	if motionDOF_all then
		motion_all=Motion(motionDOF_all)
	end
	local voca_backup={}
	for i=1, mLoader:numBone()-1 do
		voca_backup[i]=mLoader:bone(i):voca()
	end

	for i=2, mLoader:numBone()-1 do
		bone=mLoader:bone(i)
		if bone:voca()~=MotionLoader.LEFTKNEE and 
			bone:voca()~=MotionLoader.RIGHTKNEE and 
			not select(1, string.find(bone:name():lower(), 'knee'))
			then
				-- 무릎은 안건드리는게 날 것 같아서.
				mLoader:VRMLbone(i):setJointAxes('YZX')
			end
	end
	local lsh=mLoader:getTreeIndexByVoca(MotionLoader.LEFTSHOULDER)
	local rsh=mLoader:getTreeIndexByVoca(MotionLoader.RIGHTSHOULDER)
	assert( lsh~=-1)
	assert( rsh~=-1)
	local lsh=mLoader:VRMLbone(lsh)
	local rsh=mLoader:VRMLbone(rsh)
	print(lsh:name(), rsh:name())
	lsh:setJointAxes('XYZ')
	rsh:setJointAxes('XYZ')
	lsh=lsh:childHead() 
	while lsh do
		lsh=MainLib.VRMLloader.upcast(lsh) -- bone to VRMLbone
		lsh:setJointAxes('XYZ')
		lsh=lsh:childHead()
	end
	rsh=rsh:childHead() 
	while rsh do
		rsh=MainLib.VRMLloader.upcast(rsh) -- bone to VRMLbone
		rsh:setJointAxes('XYZ')
		rsh=rsh:childHead()
	end
	mLoader:_initDOFinfo()
	for i=1, mLoader:numBone()-1 do
		if voca_backup[i]~=-1 then
			mLoader:_changeVoca(voca_backup[i], mLoader:bone(i))
		end
	end
	if motion_all then
		motionDOF_all:set(motion_all)
		if not checkEulerContinuity(mLoader, motionDOF_all, discontinuity) then
			print('still not fixed!!!')
			dbg.console()
		end
	end
	print('Euler angles fixed!!!')
end

function segmentMotionDOF(mLoader, mMotionDOF, discont, frameRate, filterWindow)
	assert(math.floor(frameRate)==frameRate)
	assert(frameRate>15 and frameRate<200)
	local comtraj=calcCOMtrajectory(mLoader, mMotionDOF, discont)

	local aLinearMomentum=comtraj:matView():derivative(frameRate, discont)


	local thr_scale=vectorn()
	thr_scale:lengths(aLinearMomentum)
	filterSegments(thr_scale:column(), discont, filterWindow, frameRate)
	thr_scale:rmult(1)
	thr_scale=(thr_scale+1)*(thr_scale+1)

	RE.motionPanel():scrollPanel():addPanel(thr_scale)

	local aAggAcceleration=aLinearMomentum:derivative(frameRate, discont)

	local gravityAcceleration=CT.vec(0, -9.8, 0)
	for i=0,aAggAcceleration:rows()-1 do
		aAggAcceleration:row(i):rsub(gravityAcceleration)
	end
	local forceAll=vectorn()
	forceAll:lengths(aAggAcceleration)

	filterSegments(forceAll:column(), discont, filterWindow, frameRate)

	local signal=forceAll

	mCutState=boolN()
	mCutState:setSize(mMotionDOF:numFrames())
	mCutState:findLocalOptimum(signal, boolN.ZC_MIN);
	return mCutState, thr_scale
end

function createMotionGraph(nodes, distMat,squaredMomentum,  thr, discontinuity, _debugDraw)
	local minDist=distMat:minimum()
	local mGraph=util.Graph(nodes:size())

	-- 2. create edges
	for i=0, nodes:size() -2 do
		if nodes(i+1)<discontinuity:size() and discontinuity:range(nodes(i), nodes(i+1)+1):count()==0 then
			-- discard boundary segments
			mGraph:addEdge(i, i+1)   
		end
	end

	local graph, imp
	if _debugDraw then
		graph=CImage()
		graph:create(squaredMomentum:size(), 100)
		imp=CImage.Pixels(graph)
	end

	for i=1, nodes:size()-1 do
		for j=0, nodes:size()-1 do
			local v=squaredMomentum(nodes(i))
			if distMat(i,j)<thr * v and mGraph:hasEdge(i-1, i) then
				assert(not discontinuity(nodes(i)))
				
				mGraph:addEdge(i-1,j) -- segment i-1이 끝나면 j play가능

				if _debugDraw then
					imp:DrawLine(nodes(i), 0, nodes(j), 99, CPixelRGB8(255,0,0))
				end
			end
		end
	end
	if _debugDraw then
		RE.motionPanel():scrollPanel():addPanel(graph)
	end
	if false then
		mGraph:DRAW('g4')
		-- graph plot (dot works only when graph is very sparse)
		os.execute("dot -Tps ../graph/g4.dot -o g4.ps")
		os.execute("xdg-open g4.ps")
	end
	
	-- strongly connected component
	components=vecIntvectorn ()
	mGraph:SCC(components)

	local csize=vectorn(components:size())
	for i=0, csize:size()-1 do
		csize:set(i, components(i):size())
	end

	local largestComponent=components(csize:argMax())
	print(largestComponent)
	assert(largestComponent:size()>5)

	local newGraph={}

	frameToNodeIndex={}
	for i=0, nodes:size()-1 do
		frameToNodeIndex[nodes(i)]=i
	end

	for i=0, largestComponent:size()-1 do
		local inode=largestComponent(i)
		newGraph[inode]={} 
	end

	for i=0, largestComponent:size()-1 do
		local inode=largestComponent(i)

		local edges=mGraph:outEdges(inode)
		for j=0, edges:size()-1 do
			local inode2=edges(j):target()

			if largestComponent:findFirstIndex(inode2)~=-1 then
				local edge={ src=inode, tgt=inode2}
				table.insert(newGraph[inode], edge)
				assert(newGraph[inode2])
			end
		end
	end
	return newGraph
end
