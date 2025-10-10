
require("config")
require("module")
require("common")
require("RigidBodyWin/subRoutines/Constraints")
require("RigidBodyWin/subRoutines/CollisionChecker")

function ctor()
	this:updateLayout();

	config_manip={
		"../Resource/mocap_manipulation/bvh_files/gf_0515/2/gf_skel2-1.wrl",
		'../Resource/mocap_manipulation/bvh_files/gf_0515/2/gf_skel2-1.dof',
		"LeftElbow", "LeftWrist", vector3(0,0.0,0),
		"RightElbow", "RightWrist", vector3(0,0.0,0),
		reversed=true,
		skinScale=1,
	}

	config_gymnist={
		"../Resource/motion/gymnist/gymnist.wrl",
		'../Resource/motion/gymnist/gymnist.dof',
		'lradius', 'lhand', vector3(0,0,0),
		'rradius', 'rhand', vector3(0,0,0),
		reversed=false,
		skinScale=100,
	}
	config_run={
		"../Resource/motion/justin_straight_run/justin_straight_run.wrl",
		"../Resource/motion/justin_straight_run/justin_straight_run.dof", 
		'ltibia', 'lfoot', vector3(0.000000,-0.053740,0.111624),
		'rtibia', 'rfoot', vector3(0.000000,-0.054795,0.112272),
		reversed=false,
		skinScale=100,
	}

	--config=config_manip
	config=config_run
    mLoader=MainLib.VRMLloader (config[1])
	

	mMotionDOFcontainer=MotionDOFcontainer(mLoader.dofInfo, config[2])
	mMotionDOF=mMotionDOFcontainer.mot
	mMotionDOF:row(0):set(1, mMotionDOF:row(0):get(1)+0.1) -- adjust height

	-- rendering is done in cm scale
	mSkin= RE.createVRMLskin(mLoader, false);
	local s=config.skinScale
	mSkin:scale(s,s,s); -- motion data often is in meter unit while visualization uses cm unit.
	mPose=vectorn()
	mPose:assign(mMotionDOF:row(0));
	mSkin:setPoseDOF(mPose);
	mSkin:setMaterial('lightgrey_transparent')

	mEffectors=MotionUtil.Effectors()
	mEffectors:resize(2);
	lknee=mLoader:getBoneByName(config[3])
	mEffectors(0):init(mLoader:getBoneByName(config[4]), config[5])
	rknee=mLoader:getBoneByName(config[6]);
	mEffectors(1):init(mLoader:getBoneByName(config[7]), config[8])

	--mIK= MotionUtil.createFullbodyIkDOF_limbIK(mLoader.dofInfo, mEffectors, lknee, rknee, config.reversed);
	--mIK= MotionUtil.createFullbodyIk_MotionDOF_MultiTarget(mLoader.dofInfo, mEffectors);
	--mIK=MotionUtil.createFullbodyIkDOF_limbIK_straight(mLoader.dofInfo,mEffectors,lknee,rknee);
	if false then
		mIK=LimbIKsolver(mLoader.dofInfo,mEffectors, CT.ivec(lknee:treeIndex(), rknee:treeIndex()), CT.vec(1,1))
	else
		mIK=LimbIKsolver2(mLoader.dofInfo,mEffectors, CT.ivec(lknee:treeIndex(), rknee:treeIndex()), CT.vec(1,1))
		mIK:setOption(1)
		mIK:setOption(2)
		mIK:setOption(3)
		mIK:setValue(1,0.5,0.3,100)
	end
	mPose:assign(mMotionDOF:row(0));
	mLoader:setPoseDOF(mPose);

	local pos={}
	for i=0, 1 do
		local originalPos=mEffectors(i).bone:getFrame():toGlobalPos(mEffectors(i).localpos)*100
		table.insert(pos, originalPos)
	end
	mCON=Constraints(unpack(pos))
	mCON:connect(solveIK)
	mObjectList=Ogre.ObjectList()

	local obstaclePos={vector3(30,0,0), vector3(-30,0,0), vector3(60,30,0), vector3(0,0,0)}
	local obstacleSize={vector3(20,20,40),vector3(20,20,40), vector3(20,20,40), vector3(1000,0,2000)}
	local obstacleType={"BOX","SPHERE","CAPSULE","PLANE"}
	--local obstacleType={"BOX","SPHERE","BOX","PLANE"}

	mObstacles={}
	for i=1,#obstaclePos do
		mObstacles[i]=Geometry()

		do 
			local mesh=mObstacles[i]
			if obstacleType[i]=="BOX" then
				mesh:initBox(vector3(20, 20, 40))
			elseif obstacleType[i]=="SPHERE" then
				mesh:initEllipsoid(obstacleSize[i])
			elseif obstacleType[i]=="CAPSULE" then
				mesh:initCapsule(obstacleSize[i].x, obstacleSize[i].z)
			else
				mesh:initPlane(obstacleSize[i].x, obstacleSize[i].z)
			end
			local mat=matrix4()
			mat:identity()
			mat:leftMultScale(1/config.skinScale)
			mesh:transform(mat)
		end
	end
	--mObjectList:registerMesh(mObstacles[1], 'meshtest'):getLastCreatedEntity():setMaterialName('lightgrey_transparent')
	--mObjectList:findNode('meshtest'):scale(config.skinScale)

	mChecker=CollisionChecker(unpack{mLoader, unpack(mObstacles)})
	for i=1,#obstaclePos do
		local initialState=vectorn(7)
		local obstacleOffset=vector3(0,10,0)
		initialState:setVec3(0, (obstaclePos[i]+obstacleOffset)/config.skinScale)
		initialState:setQuater(3,quater(1,0,0,0))
		mChecker:setPoseDOF(i, initialState)
	end
	mObstacleSkins={}
	for i=1, #obstaclePos do
		local v=mChecker.collisionDetector:getModel(i)
		mObstacleSkins[i]= RE.createVRMLskin(v, false);
		mObstacleSkins[i]:scale(s,s,s)
		mChecker:registerPair(0,i) -- 0 means mLoader, 1 means mObstacles[1]
		local state=mChecker.pose[i]
		mObstacleSkins[i]:setPoseDOF(state)
	end
end
function solveIK()
	mPose:assign(mMotionDOF:row(0));
	mLoader:setPoseDOF(mPose);
	-- local pos to global pos
	local footOri=quaterN(2)
	local footPos=vector3N(2)
	for i=0,1 do
		--local originalPos=mEffectors(i).bone:getFrame():toGlobalPos(mEffectors(i).localpos)
		footPos(i):assign(mCON.conPos(i)*0.01);
		footOri(i):assign(mEffectors(i).bone:getFrame().rotation)
	end
	--footPos(0):radd(vector3(xx, yy,zz)/config.skinScale)
	--dbg.draw("Sphere", footPos(0)*config.skinScale, "x0")
	--mIK:IKsolve(mPose, footPos);
	local importance=vectorn(2)
	importance:setAllValue(1)
	mIK:IKsolve3(mPose, MotionDOF.rootTransformation(mPose), footPos, footOri, importance)
	mSkin:setPoseDOF(mPose);
	mChecker:setPoseDOF(0,mPose)

	if mObstacleSkins then
		for i=1, #mObstacleSkins do
			mObstacleSkins[i]:setMaterial('lightgrey')
		end
	end

	local bases=mChecker:checkCollision()
	local collisionLinkPairs=bases:getCollisionLinkPairs()
	if collisionLinkPairs:size()>=1 then
		local lines=vector3N()
		for i=0, collisionLinkPairs:size()-1 do
			local ilinkpair=collisionLinkPairs(i)
			local iloader1=bases:getCharacterIndex1(ilinkpair)
			local iloader2=bases:getCharacterIndex2(ilinkpair)
			local collisionPoints=bases:getCollisionPoints(ilinkpair)
			for j=0, collisionPoints:size()-1 do
				local b=collisionPoints(j)
				--print(loader1:name(), loader1:VRMLbone(linkpair[2]).NameId, loader2:name(), loader2:VRMLbone(linkpair[4]).NameId)
				if mObstacleSkins then
					mObstacleSkins[iloader2]:setMaterial('red_transparent')
				end
				lines:pushBack(b.position*config.skinScale)
				lines:pushBack((b.position+b.normal)*config.skinScale)
			end
		end
		dbg.draw('Traj', lines:matView(), 'normals','solidred')
		return lines
	else
		dbg.erase('Traj', 'normals')
	end
	--local iloaders={}
	--for i=1, #mObstacles do iloaders[i]=i end
	--mChecker:checkRayIntersection(iloaders, mCON.conPos, vector3(0,-1,0))
end

function onCallback(w, userData)
end

function dtor()
end

function frameMove(fElapsedTime)
end
function handleRendererEvent(ev, button, x,y) 
	if mCON then
		return mCON:handleRendererEvent(ev, button, x,y)
	end
	return 0
end
