
require("config")
require("module")
require("common")
require("RigidBodyWin/subRoutines/Constraints")
require("RigidBodyWin/subRoutines/CollisionChecker")
local FBXloader=require("FBXloader")

function ctor()
	this:updateLayout();

	mDebugDraw=Ogre.ObjectList()
	config_dance={
		'../Resource/motion/Mixamo/passive_nomarker_man_T.fbx.dat' ,
		'manually load',
		'LeftLeg', 'LeftFoot', vector3(0.000000,-0.053740,0.111624),
		'RightLeg', 'RightFoot', vector3(0.000000,-0.054795,0.112272),
		reversed=false,
		skinScale=100,
	}

	--config=config_manip
	config=config_dance



	local skelFile=config[1]

	mFbxLoader=FBXloader(skelFile, {skinScale=config.skinScale, useTexture=true})
	mFbxLoader.cacheCollisionMesh=skelFile..'.colcache'


	mChecker=CollisionChecker('sdf')
	mChecker.collisionDetector:addModel(mFbxLoader)

    mLoader=mChecker.collisionDetector.models[1].collisionLoader
	
	do
		-- manually load motions
		local _loader, _motdofc,mot=RE.loadMotions(nil,
		{
			{"../../Mixamo/fbx/Macarena Dance.fbx", identity_pose='../../Mixamo/fbx/T-Pose.fbx'},
			scale=0.01
		})
		_loader:setPoseDOF(_motdofc:row(0))
		local mm=mot:getMotionMap()

		-- 입력할 본의 이름 수정.
		mm.rotJoints:gsub("mixamorig:", "")
		mm.transJoints:gsub("mixamorig:", "")

		if false then
			debugSkin=RE.createSkinAuto(_loader)
			debugSkin:applyAnim(mot)
			debugSkin:setScale(100,100,100)
			RE.motionPanel():motionWin():addSkin(debugSkin)
		end

		--mMotion=mm:transferMotion(mLoader) -- mLoader and loader should initially be in the same pose
		mMotion=mm:copyMotion(mLoader) -- mLoader and loader should be angle-compatible.
		mMotion:translate(_loader:bone(2):getOffset()) -- loader's hip offset from the RootNode
		mMotionDOFcontainer= MotionDOFcontainer(mLoader.dofInfo, mMotion)
		mMotionDOFcontainer.files=_motdofc.files
		mMotionDOF=mMotionDOFcontainer.mot
	end

	-- rendering is done in cm scale
	--mSkin= RE.createVRMLskin(mLoader, false);
	mSkin= RE.createFBXskin(mFbxLoader, false);

	local s=config.skinScale
	mSkin:setScale(s,s,s); -- motion data often is in meter unit while visualization uses cm unit.
	mPose=vectorn()
	mPose:assign(mMotionDOF:row(0));
	mPose:set(0,0)
	mPose:set(2,0)
	mSkin:setPoseDOF(mPose);
	mSkin:setMaterial('lightgrey_transparent')

	mEffectors=MotionUtil.Effectors()
	mEffectors:resize(2);
	lknee=mLoader:getBoneByName(config[3])
	mEffectors(0):init(mLoader:getBoneByName(config[4]), config[5])
	rknee=mLoader:getBoneByName(config[6]);
	mEffectors(1):init(mLoader:getBoneByName(config[7]), config[8])

	--mIK= MotionUtil.createFullbodyIkDOF_limbIK(mLoader.dofInfo, mEffectors, lknee, rknee, config.reversed);
	--mIK=MotionUtil.createFullbodyIkDOF_limbIK_straight(mLoader.dofInfo,mEffectors,lknee,rknee);
	g_con=MotionUtil.Constraints() -- std::vector<MotionUtil::RelativeConstraint>
	mIK= MotionUtil.createFullbodyIk_MotionDOF_MultiTarget_lbfgs(mLoader.dofInfo,mEffectors, g_con); 
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

	for i,v in ipairs(mObstacles) do
		mChecker.collisionDetector:addObstacle(v)
	end

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
	mIK:IKsolve(mPose,  footPos)
	mSkin:setPoseDOF(mPose);
	mChecker:setPoseDOF(0,mPose)

	if mObstacleSkins then
		for i=1, #mObstacleSkins do
			mObstacleSkins[i]:setMaterial('lightgrey')
		end
	end

	mDebugDraw:clear()
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

				local p1=(b.position+b.normal*b.idepth)*config.skinScale
				local p2=b.position*config.skinScale

				mDebugDraw:drawSphere(p1, "b1pos"..tostring(b.ibody)..tostring(i)..tostring(j), "green",1)
				mDebugDraw:drawSphere(p2, "b2pos"..tostring(b.ibody)..tostring(i)..tostring(j), "red",1.5)
				--print(b.idepth)

				lines:pushBack(p1)
				lines:pushBack(p2)
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
	dbg.updateBillboards(fElapsedTime)
end
function handleRendererEvent(ev, button, x,y) 
	if mCON then
		return mCON:handleRendererEvent(ev, button, x,y)
	end
	return 0
end
