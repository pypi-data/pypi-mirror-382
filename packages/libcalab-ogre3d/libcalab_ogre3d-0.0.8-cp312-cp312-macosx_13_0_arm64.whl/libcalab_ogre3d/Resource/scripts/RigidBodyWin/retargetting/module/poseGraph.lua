PoseDeformer={
	numSides=3
}
function PoseDeformer.getJointPosition(graph, jointIndex, vertices)
	if not vertices then
		vertices=graph.original_vertices
	end
	local skinScale=graph.skinScale

	local sum=vector3(0,0,0)
	local numSides=PoseDeformer.numSides
	for j=0, numSides-1 do
		sum=sum+vertices((jointIndex)*numSides+j)
	end
	sum=sum*(1/skinScale)
	return sum/numSides
end
function PoseDeformer.getVertexPositions(loader, graph)
	local markerOffset=graph.markerOffset
	local skinScale=graph.skinScale
	local numSides=PoseDeformer.numSides
	markerOffset=markerOffset or 0.03*100

	--local numJoints=loader:numBone()-1
	local treeIndex=graph.jointIndexToTreeIndex
	local parentJointIndex=graph.treeIndexToParentJointIndex
	local numJoints=#treeIndex+1
	local numVertex=numJoints*numSides
	local original_vertices=vector3N(numVertex) -- 0 -indexing
	local axes=vector3N(numJoints)
	axes:setAllValue(vector3(0,0,0))
	
	-- axis(joint) is the sum of all connected link offsets
	local offsets =  {}
	local rotations = {}
	local local_rotations = {}
	for i=0, numJoints-1 do
		local bone=loader:bone(treeIndex[i])
		local R=bone:getFrame().rotation
		local r=bone:getLocalFrame().rotation
		rotations[i] = R
		local_rotations[i] = r
		axes(i):radd(r*bone:getOffsetTransform().translation)
		local offset = bone:getOffsetTransform().translation
		offsets[i] = offset
		local pindex=parentJointIndex[bone:treeIndex()]
		if pindex~=-1 then
			axes(pindex):radd(bone:getOffsetTransform().translation)
		end
	end
    -- dbg.console()
	-- build vertex array
	for i=0,numJoints-1 do
		local bone=loader:bone(treeIndex[i])
		local R=bone:getFrame().rotation

		local axis1=axes(1):Normalize()
		local axis2=vector3(0,0,1)
		if axis2:dotProduct(axis1)<0.1 then
			axis2=vector3(1,0,0)
		end
		local axis3=axis1:cross(axis2):Normalize()
		axis2=axis3:cross(axis1)
	
		for j=0,numSides-1 do
			local q=quater()
			q:setRotation(axis1, sop.map(j,0, numSides, 0, 2*math.pi))
			local axis=(R*q*axis2)*markerOffset
			original_vertices((i)*numSides+j):assign(bone:getFrame().translation+axis)
		end
		
		if false then
			print(PoseDeformer.getJointPosition(graph, i, original_vertices)*skinScale)
			print(bone:getFrame().translation)
			print("The above two positions should be identical")
			dbg.console()
		end
	end
	--dbg.console()
	return original_vertices*skinScale
end
function PoseDeformer.buildGraph(loader, markerOffset, customEdges, skinScale, fixedJoints) 

	local boneMap={}
	for i=1, loader:numBone()-1 do
		if loader:getRotJointIndexByTreeIndex(i)~=-1 then
			boneMap[i]=true
		else
			boneMap[i]=false
		end
	end
	if fixedJoints then
		for i,v in ipairs(fixedJoints) do
			boneMap[loader:getTreeIndexByName(v)]=false
		end
	end

	local treeIndexToJointIndex={} 
	local jointIndex=0
	for i=1, loader:numBone()-1 do
		if boneMap[i] then
			treeIndexToJointIndex[i]=jointIndex
			jointIndex=jointIndex+1
		else
			treeIndexToJointIndex[i]=-1
		end
	end
	return PoseDeformer._buildGraph(loader, treeIndexToJointIndex, markerOffset, customEdges, skinScale) 
end
function PoseDeformer._buildGraph(loader, treeIndexToJointIndex, markerOffset, customEdges, skinScale) 

	local graph={}
	graph.markerOffset=markerOffset
	graph.skinScale=skinScale
	local treeIndexToParentJointIndex={}
	local jointIndexToTreeIndex={}
	do
		for i=1, loader:numBone()-1 do
			local jointIndex=treeIndexToJointIndex[i]
			jointIndexToTreeIndex[jointIndex]=i
		end
		jointIndexToTreeIndex[-1]=nil
		-- dbg.console()
		-- calc parent joint index
		for i=1, loader:numBone()-1 do
			local p=loader:bone(i):parent()
			while(p:treeIndex()~=0 and treeIndexToJointIndex[p:treeIndex()]==-1 ) do
				p=p:parent()
			end

			if p:treeIndex()==0 then 
				treeIndexToParentJointIndex[i]=-1
			else
				treeIndexToParentJointIndex[i]=treeIndexToJointIndex[p:treeIndex()]
			end
		end
	end
	--dbg.console()
	graph.treeIndexToJointIndex=treeIndexToJointIndex
	graph.treeIndexToParentJointIndex=treeIndexToParentJointIndex
	graph.jointIndexToTreeIndex=jointIndexToTreeIndex
	local original_vertices=PoseDeformer.getVertexPositions(loader, graph)
	local numSides=PoseDeformer.numSides

	local function connectTwoBones(edge, i, pindex)
		for j=0, numSides-1 do -- edges to the parent vertex
			table.insert(edge, {(i)*numSides+j, (pindex)*numSides+j, weight})
		end
	end

	-- build edge array
	local edge={}
	local numJoints=#jointIndexToTreeIndex+1
	for i=0, numJoints-1 do
		local bone=loader:bone(jointIndexToTreeIndex[i])
		local weight=1
		local pindex=treeIndexToParentJointIndex[bone:treeIndex()]
		print(bone:name(), i, pindex)
		if pindex~=-1 then
			print(":"..loader:bone(jointIndexToTreeIndex[pindex]):name())
			connectTwoBones(edge, i, pindex)
		end
		for j=0, numSides -1 do 
			table.insert(edge, {(i)*numSides+j, (i)*numSides+math.mod(j+1, numSides)})
		end
	end
	if customEdges then
		for i, v in ipairs(customEdges) do
			connectTwoBones(edge, treeIndexToJointIndex[v[1]], treeIndexToJointIndex[v[2]])
		end
	end
--	dbg.console()
	local function buildAdj(numVertex, edge)
		-- build adj array from the edge array
		local adj={} -- uses 1-indexing
		for i=1, original_vertices:size() do
			adj[i]={}
		end
		--print('--------------------')
		for i=1, #edge do
			local v1=edge[i][1]
			local v2=edge[i][2]
			table.insert(adj[v1+1], v2) -- adj uses 1-indexing
			table.insert(adj[v2+1], v1)
			--print(v1, v2)
		end
		--print('--------------------')
		--		for i=1,#adj do
		--			for j=1,#adj[i] do
		--				local v1=i-1
		--				local v2=adj[i][j]
		--				if v1< v2 then
		--					print(v1, v2)
		--				end
		--			end
		--		end
		--		print('--------------------')
		--		dbg.console()

		return adj
	end

	local unused_vertices={}
	local c=0
	local adj=buildAdj(original_vertices:size(),  edge)
	for i=1, original_vertices:size() do
		if #adj[i]==0 then
			unused_vertices[i-1]=true
			c=c+1
			print('vertex '..(i-1)..' is missing an edge')
		end
	end
	assert(c==0)
--	dbg.console()
	graph.original_vertices=original_vertices 
	graph.edge=edge
	graph.adj=adj
	graph.numSides=numSides
	graph.unusedVertices=unused_vertices
	graph.unusedVertexCount=c

--	dbg.console()
	return graph
end
-- to erase edges, use "dbg.erase('Traj', nameid)"
function PoseDeformer.drawEdges(graph, vertices, nameid)
	local edge=graph.edge
	-- draw 
	local goal1=matrixn(#edge*2,3)    
	goal1:resize(0,3)
	goal1:setAllValue(0)
	local crow=0
	--	local f=1   --일단 1frame 에 대해 그리려고 1 해놨는데 수정 필요함
	for i=1, #edge do
		local small = 0
		local big = vertices:size()
		if edge[i][1]>=small and edge[i][1]<big and edge[i][2]>=small and edge[i][2]<big then
			goal1:resize(crow+2, 3)
			for j=1,2 do
				goal1:row(crow):setVec3(0,vertices:row(edge[i][j]))
				crow=crow+1
			end
		end
	end
	dbg.draw('Traj', goal1, nameid, 'solidred', 1, 'BillboardLineList') --Traj == LineList
	--2개씩 짝지어져서 선이 그려짐 
	--ex) 6개 vertex 가 있으면 0~1, 2~3, 4~5 로 선 3개가 표현됨
end
function _IKsolve(solver, pose, newRootTF, conpos, conori, importance)
	-- results go to solver.tempp
	solver:_limbIK(conpos, conori, importance)

	local dim=9
	local max_iter=10
	--solver:init_cg(0.01, dim, 0.01, 0.005)
	local tol=0.001 -- used in frprmn termination condition
	local thr=1 -- used in NR_brek
	solver:init_cg(dim, 0.005, max_iter, tol, thr)
	local v=vectorn(dim)
	v:setAllValue(0)
	print(v)
	if false then -- debug objective function
		local out=CT.vec(0.2,0,0)
		_objectiveFunction(solver, out)
		local temp=vectorn()
		solver.mSkeleton:getPoseDOF(temp)
		g_skinHuman:setPoseDOF(temp)
		RE.renderOneFrame(false)	
	end
	solver:optimize(v)
	local out=solver:getResult()
	_objectiveFunction(solver, out)
	solver.mSkeleton:getPoseDOF(pose)
	print(out)
end

function _objectiveFunction(solver, x)
	local pelvis=solver:getCenterBone(0)
	local trans=x:toVector3(0)/mSolverInfo.skinScale*100
	pelvis:getLocalFrame().translation:add(solver.mRootPos(0),trans)

	local theta=quater()
	theta:setRotation(x:toVector3(3)*10)
	pelvis:getLocalFrame().rotation:mult(solver.mRootOri(0),theta)

	local theta2=quater()
	theta2:setRotation(x:toVector3(6)*2)
	solver:getCenterBone(1):getLocalFrame().rotation:mult(solver.mRootOri(1),theta2)
	solver.mSkeleton:fkSolver():forwardKinematics()
	solver:_limbIK(solver.con, mSolverInfo.conori, solver.impor)

	local currPos=PoseDeformer.getVertexPositions(solver.mSkeleton, mSolverInfo.graph)
	if false then
		local con={}
		con.conPos=currPos
		con.size=1
		con.prefix='currPos'
		con.selectedVertex=-1
		Constraints.drawConstraints(con)
	end
	local d=currPos:MSE(deformed_vertices)
	local l=x:length()
	d=d+0.1*l*l
	--local a=x:toVector3(3)
	--d=d+a:dotProduct(a)
	return d
	--local hipoffset=solver.mHipOffset
end
function PoseDeformer.getConPos(conIndex, all_vertices)
	local conPos = vector3N(conIndex:size())
	for i=0, conIndex:size() -1 do
		conPos(i):assign(all_vertices(conIndex(i)))
	end
	return conPos
end
function PoseDeformer.countConstraints(constraints, graph, iframe)
	local numCon=0
	for i,v in pairs(constraints) do
		if v.conType==ConTypes.RELATIVE_POSITION then
			local importance=v.importance(iframe)
			if importance>0.001 then
				numCon=numCon+3*(#v.bones-1)
			end
		elseif v.conType==ConTypes.GROUND_CONTACT then
			if useSingleContactConstraint then
				numCon=numCon+3
			else
				numCon=numCon+3*graph.numSides
			end
		end
	end
	return numCon
end
