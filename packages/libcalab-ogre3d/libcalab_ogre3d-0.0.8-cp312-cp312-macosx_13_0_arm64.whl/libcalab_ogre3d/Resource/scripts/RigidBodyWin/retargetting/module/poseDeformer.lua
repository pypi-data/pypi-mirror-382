require("retargetting/module/poseGraph")

local function  Xindex(x) 
	return (x)*3;
end

local function  Yindex(x) 
	return (x)*3+1;
end

local function  Zindex(x)
	return (x)*3+2;
end

local useSparseSolver=false -- faster but difficult to debug
local useSingleContactConstraint=false
if useSparseSolver and SparseQuadraticFunctionHardCon then
	SparseQuadraticFunctionHardCon.addWeighted= QuadraticFunctionHardCon.addWeighted
	SparseQuadraticFunctionHardCon.add= QuadraticFunctionHardCon.add
	SparseQuadraticFunctionHardCon.con= QuadraticFunctionHardCon.con
	QuadraticFunctionHardCon=SparseQuadraticFunctionHardCon
	SparseQuadraticFunctionHardCon._solve= SparseQuadraticFunctionHardCon.solve
	gTimer=util.PerfTimer2()
	function SparseQuadraticFunctionHardCon:solve()
		local A=gmm.wsmatrixn()
		local b=vectorn()
		local x=vectorn()
		if true then
			self:buildSystem(A,b)
			self:_solve(A,b, x)
		else
			gTimer:start()
			self:buildSystem(A,b)
			print('time0:',gTimer:stop())
			gTimer:start()
			local cache=self:factorize(A)
			print('time1:',gTimer:stop())
			gTimer:start()
			self:solveFactorized(cache,b,x)
			print('time2:',gTimer:stop())
			self:freeUMFsolver(cache)
		end
		return x;
	end
end


function PoseDeformer.solve(loader, graph, numIter, conIndex, conPos, constraints, targets, iframe)
	local original=graph.original_vertices
	local initial=original:copy()
	local deformed=initial:copy()
	local numIterOuter=5
	local numIter=numIter or 1
	for j=1, numIterOuter do
		for i=1, numIter do
			PoseDeformer.solveOneIter(loader, graph, conIndex, conPos, deformed, initial, constraints, targets, iframe)
		end
		PoseDeformer.fitting(loader, graph, conIndex, conPos, deformed, original, constraints, targets, iframe)
		initial:assign(deformed)
	end
	return deformed
end

function PoseDeformer.solveOneIter(loader, graph, conIndexAll, conPosAll, deformed, vertices, constraints, targets, iframe)
	local nvar=vertices:size()*3
	local numCon=conIndexAll:size()*3;
	numCon=numCon+PoseDeformer.countConstraints(constraints, graph, iframe)

	if useCOMcon then
		numCon=numCon+numFrames*2
	end
	local h=QuadraticFunctionHardCon(nvar, numCon);

	local weight=1
	PoseDeformer.addLaplacianTerms(graph.adj, weight, deformed, vertices, h)

	for i=0, conIndexAll:size()-1 do
		-- h:con(3,0,4,1,5,2,-1) 은 3x+4y+5z-1==0 이라는 constraint 추가.
		h:con(1, Xindex(conIndexAll(i)), -conPosAll(i).x)
		h:con(1, Yindex(conIndexAll(i)), -conPosAll(i).y)
		h:con(1, Zindex(conIndexAll(i)), -conPosAll(i).z) 
	end

	PoseDeformer.addConstraints(h, graph, loader, constraints, targets, iframe)
	if useCOMcon then
		addCOMcon(vertices, h)
	end
	local x=h:solve()
	deformed:setSize(vertices:size());
	for i=0,vertices:size()-1 do
		deformed(i).x=x(Xindex(i));
		deformed(i).y=x(Yindex(i));
		deformed(i).z=x(Zindex(i));
	end
end
function PoseDeformer.addLaplacianTerms(adj, weight, deformed, vertices, h)
	for i=1, #adj do 
		local vi=adj[i]
		local n=#vi

		local _0=i-1

		local function getPositions(vertices, i, adj)
			local vi=adj[i]
			local pos=vectorn((#vi+1)*3)
			pos:setVec3(0, vertices(i-1))

			for j=1, #vi do
				pos:setVec3(j*3, vertices(vi[j]))
			end
			return pos
		end
		local orig=getPositions(vertices, i, adj)
		local deformed=getPositions(deformed, i, adj)

		local err_thr=0.01
		if true and (orig-deformed):length()> err_thr then --optimal local match
			local ones=CT.ones(vertices:size())
			local metric=math.WeightedPointCloudMetric(ones)
			for i=0, #vi do
				deformed:set(i*3,deformed(i*3)+2)
			end
			metric:calcDistance(deformed, orig)
			orig:fromMatrix(metric.transformedB)
		end

		local l=vector3(0,0,0)
		do 
			-- calc laplacian from the original mesh
			local v0=orig:toVector3(0)
			for j=1, #vi do
				local v1=orig:toVector3(j*3)
				local v01=vector3()
				v01:difference(v0, v1) -- v1-v0
				l:radd(v01)
			end
		end

		local function makeParam(indexFcn, vi, l)
			local param={}
			for j=1, #vi do
				param[#param+1]=1
				param[#param+1]=indexFcn(vi[j])
			end
			param[#param+1]=-#vi
			param[#param+1]=indexFcn(_0)
			param[#param+1]=-l
			return param
		end
		local param
		param=makeParam(Xindex, vi, l.x)
		h:addWeighted(weight,unpack(param))
		param=makeParam(Yindex, vi, l.y)
		h:addWeighted(weight,unpack(param))
		param=makeParam(Zindex, vi, l.z)
		h:addWeighted(weight,unpack(param))
	end
end
--
-- deformed : input/output
-- vertices : input
function PoseDeformer.fitting(loader, graph, conIndexAll, conPosAll, deformed, vertices, constraints, targets, iframe)
	local nvar=vertices:size()*3
	local numCon=conIndexAll:size()*3;
	numCon=numCon+PoseDeformer.countConstraints(constraints, graph, iframe)
	local h=QuadraticFunctionHardCon(nvar, numCon);
	local function addPoissonTerms()
		local edge=graph.edge
		for i=1, #edge do
			local _0=edge[i][1]
			local _1=edge[i][2]
			local l0=vertices(_0):distance(vertices(_1))
			local v0=deformed(_0)
			local v1=deformed(_1)
			local v01=v1-v0
			v01:normalize()
			v01:rmult(l0)

			h:add(1.0, Xindex(_1), -1.0, Xindex(_0), -v01.x)
			h:add(1.0, Yindex(_1), -1.0, Yindex(_0), -v01.y)
			h:add(1.0, Zindex(_1), -1.0, Zindex(_0), -v01.z)
		end
	end

	--addLaplacianTerms(mAdj, 1)
	addPoissonTerms()
	
	for i=0, conIndexAll:size()-1 do
		-- h:con(3,0,4,1,5,2,-1) 은 3x+4y+5z-1==0 이라는 constraint 추가.
		h:con(1, Xindex(conIndexAll(i)), -conPosAll(i).x)
		h:con(1, Yindex(conIndexAll(i)), -conPosAll(i).y)
		h:con(1, Zindex(conIndexAll(i)), -conPosAll(i).z) 
	end
	PoseDeformer.addConstraints(h, graph, loader, constraints, targets, iframe)

	local x=h:solve()
	deformed:setSize(vertices:size());
	for i=0,vertices:size()-1 do
		deformed(i).x=x(Xindex(i));
		deformed(i).y=x(Yindex(i));
		deformed(i).z=x(Zindex(i));
	end
end
function PoseDeformer.addConstraints(h, graph, loader, constraints, targets, iframe)
	for k,v in pairs(constraints) do
		if v.conType==ConTypes.GROUND_CONTACT then
			if not v.conIndex then
				v.conIndex=graph.treeIndexToJointIndex[loader:getTreeIndexByName(v.heel)]
			end
			if useSingleContactConstraint then
				local ns=graph.numSides
				local index=intvectorn(ns)
				local coef=vectorn(ns+1)
				coef:setAllValue(1)
				local toePos=-ns*targets[k].jointPos:row(iframe)
				local s=graph.skinScale
				for axis=0, 2  do
					for j=0, ns-1 do
						index:set(j, Xindex(v.conIndex*ns+j)+axis)
					end
					coef:set(ns, toePos(axis)*s)
					h:addCon(index, coef)
				end
			else
				local ns=graph.numSides
				local index=intvectorn(1)
				local coef=vectorn(2)
				coef:setAllValue(1)
				local toePos=targets[k].jointPos:row(iframe)*config.skinScale
				local toePos2=CT.vec(PoseDeformer.getJointPosition(graph, v.conIndex))*config.skinScale
				local center=vector3(0,0,0)
				
				for s=0, ns-1 do
					center=center+graph.original_vertices(v.conIndex*ns+s)/ns
				end

				for s=0, ns-1 do
					local delta=CT.vec(graph.original_vertices(v.conIndex*ns+s)-center)

					for axis=0, 2  do
						index:set(0, Xindex(v.conIndex*ns+s)+axis)
						coef:set(1, -(toePos(axis)+delta(axis)))
						h:addCon(index, coef)
					end
				end
			end
		elseif v.conType==ConTypes.RELATIVE_POSITION then
			if not v.conIndices then
				v.conIndices=intvectorn(#v.bones)

				for i,vv in ipairs(v.bones) do
					v.conIndices:set(i-1, graph.treeIndexToJointIndex[loader:getTreeIndexByName(vv)])
				end
			end
			local conI=v.conIndices
			local ns=graph.numSides
			
			local nvar=graph.original_vertices:size()*3

			local s=graph.skinScale
			local n=ns*2
			local index=intvectorn(n)
			local coef=vectorn(n+1)
			local importance=v.importance(iframe)
			if importance>0.001 then
				for i=0, conI:size()-2 do
					local i1=conI(i)*ns
					local i2=conI(i+1)*ns
					local orig=targets[k].pos
					local originalDistance=
					PoseDeformer.getJointPosition(graph, conI(i+1))-
					PoseDeformer.getJointPosition(graph, conI(i))

					--originalDistance=originalDistance*0 -- debugging
					local d=orig[i+2]:row(iframe)-orig[i+1]:row(iframe)
					d=d:range(0,3)*importance+CT.vec(originalDistance*(1-importance))

					if false then
						--dbg.namedDraw('Sphere', s*PoseDeformer.getJointPosition(graph, conI(i+1)), "i+1")
						--dbg.namedDraw('Sphere', s*PoseDeformer.getJointPosition(graph, conI(i)), "i")
						dbg.namedDraw('Sphere', s*orig[i+2]:row(iframe):toVector3(0), "i+1")
						dbg.namedDraw('Sphere', s*orig[i+1]:row(iframe):toVector3(0), "i")
						print('??', originalDistance, d)
					end

					for axis=0, 2  do
						for j=0, ns-1 do
							assert(Xindex(i2+j)+axis< nvar);
							index:set(j, Xindex(i2+j)+axis)
							coef:set(j, 1/ns)
						end
						for j=0, ns-1 do
							assert(Xindex(i1+j)+axis< nvar);
							index:set(ns+j, Xindex(i1+j)+axis)
							coef:set(ns+j, -1/ns)
						end
						coef:set(n, -d(axis)*s)
						h:addCon(index, coef)
					end
				end
			end
		end
	end
end

function PoseDeformer.addCOMcon(vertices, h)
	local orig_com=vector3(0,0,0)

	for j=0, numVertex-1 do
		orig_com:radd(vertices(j+i*numVertex))
	end
	local function makeParam(indexFcn, i,l)
		local param={}
		for j=0, numVertex-1 do
			param[#param+1]=1
			param[#param+1]=indexFcn(j+i*numVertex)
		end
		param[#param+1]=-l
		return param
	end
	local param
	param=makeParam(Xindex, i, orig_com.x)
	h:con(unpack(param))
	param=makeParam(Zindex, i, orig_com.z)
	h:con(unpack(param))
end



