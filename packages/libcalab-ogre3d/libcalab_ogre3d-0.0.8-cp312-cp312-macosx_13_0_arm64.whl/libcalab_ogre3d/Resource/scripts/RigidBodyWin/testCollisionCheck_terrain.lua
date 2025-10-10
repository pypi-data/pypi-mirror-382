
require("config")
require("module")
require("common")
require("RigidBodyWin/subRoutines/Constraints")
require("RigidBodyWin/subRoutines/CollisionChecker")

config={skinScale=100}
function ctor()
	this:updateLayout();

	local bgnode=RE.ogreSceneManager():getSceneNode("BackgroundNode")
	bgnode:setVisible(false)

	this:create('Box', 'message', 'Usage: shift-drag ')
	this:create('Box', 'message2', 'the box with a sphere')
	this:updateLayout();


	local dh=21

	local obstaclePos= {vector3(30,0+dh,0), vector3(-30,0+dh,0), vector3(60,30+dh,0), vector3(0,-100+dh, 0), vector3(0, 2, 0)}
	local obstacleZrot={           10 ,             -10,               5,                      7,                0}
	--local obstacleSize={vector3(20,20,20),vector3(20,60,20), vector3(20,80,20), vector3(1000,20,2000)}
	local obstacleSize={vector3(20,20,20),vector3(20,60,20), vector3(20,20,40), vector3(2000,150,2000), vector3(20, 20, 60)}
	--local obstacleType={"BOX","BOX","BOX","BOX","BOX"} -- works well
	--local obstacleType={"BOX","SPHERE","BOX","PLANE"} -- works well
	local obstacleType={"CAPSULE","SPHERE","BOX","TERRAIN", "BOX", "BOX"}
	--local obstacleType={"SPHERE","SPHERE","CAPSULE","BOX"} -- works well (sphere-capsule)
	--local obstacleType={"CYLINDER","SPHERE","BOX","BOX"} -- works well
	--local obstacleType={"SPHERE","SPHERE","CYLINDER","BOX"}-- works well
	--local obstacleType={"CAPSULE","CAPSULE","CAPSULE","CAPSULE"}-- ???

	--controlIndex=1 -- move capsule
	controlIndex=5 -- move box
	local pos={obstaclePos[controlIndex]+vector3(0,10,0)}
	mCON=Constraints(unpack(pos))
	mCON:connect(solveIK)
	mObjectList=Ogre.ObjectList()

	mObstacles={}
	for i=1,#obstaclePos do
		mObstacles[i]=Geometry()

		do 
			local mesh=mObstacles[i]

			if obstacleType[i]=="BOX" then
				mesh:initBox(obstacleSize[i])
			elseif obstacleType[i]=="TERRAIN" then
				local terrain_size=obstacleSize[i].x
				local terrain_height=obstacleSize[i].y

				if false then
					g_terrain=OBJloader.Terrain("../Resource/crowdEditingScripts/terrain/heightmap1_256_256_2bytes.raw", 256, 256, terrain_size, terrain_size, terrain_height,1,1,true) -- 8 meter by 8 meter, which can be repeated infinitely along z-axis manually.
					mesh:assignTerrain(g_terrain, vector3(-terrain_size*0.5,0,-terrain_size*0.5))
				else
					mesh=nil
					g_terrain=OBJloader.Terrain("../Resource/crowdEditingScripts/terrain/heightmap1_256_256_2bytes.raw", 256, 256, terrain_size*0.01, terrain_size*0.01, terrain_height*0.01,1,1,true) -- 8 meter by 8 meter, which can be repeated infinitely along z-axis manually.
					mObstacles[i]=MainLib.VRMLloader(g_terrain)
					mObstacles[i]:setPosition(vector3(-terrain_size*0.5,0,-terrain_size*0.5)*0.01)
				end
			elseif obstacleType[i]=="SPHERE" then
				mesh:initEllipsoid(obstacleSize[i])
			elseif obstacleType[i]=="CYLINDER" then
				mesh:initCylinder(obstacleSize[i].x, obstacleSize[i].y, 20)
			elseif obstacleType[i]=="CAPSULE" then
				mesh:initCapsule(obstacleSize[i].x, obstacleSize[i].y)
			else
				mesh:initPlane(obstacleSize[i].x, obstacleSize[i].z)
			end

			if mesh then
				local s=1/config.skinScale
				mesh:scale(vector3(s,s,s))

				if i~=#obstaclePos then
					local tf=transf()
					tf.rotation:setRotation(vector3(0,0,1), math.rad(math.random()*math.rad(obstacleZrot[i])))
					tf.translation:assign(vector3(0,0,0))
					mesh:rigidTransform(tf)
				end
			end
		end
	end
	--mObjectList:registerMesh(mObstacles[1], 'meshtest'):getLastCreatedEntity():setMaterialName('lightgrey_transparent')
	--mObjectList:findNode('meshtest'):scale(config.skinScale)

	mChecker=CollisionChecker(unpack(mObstacles))
	for i=1,#obstaclePos do
		local initialState=vectorn(7)
		initialState:setVec3(0, obstaclePos[i]/config.skinScale)
		initialState:setQuater(3,quater(1,0,0,0))
		mChecker:setPoseDOF(i-1, initialState)
	end
	for i=1, #obstaclePos do
		if i~=controlIndex then
			mChecker:registerPair(controlIndex-1, i-1) -- 0 means the first obstacle.
		end
	end

	mObstacleSkins={}
	for i=1, #obstaclePos do
		local v=mChecker.collisionDetector:getModel(i-1)
		mObstacleSkins[i]= RE.createVRMLskin(v, false);
		mObstacleSkins[i]:setMaterial('lightgrey_transparent')
		local s=config.skinScale
		mObstacleSkins[i]:scale(s,s,s)
		local state=mChecker.pose[i-1]
		mObstacleSkins[i]:setPoseDOF(state)
		if i==1 then
			mPose=state:copy()
		end
	end
	mDebugDraw=Ogre.ObjectList()
end

function solveIK()
	mPose:setVec3(0, (mCON.conPos(0)+vector3(0,-10,0))/config.skinScale)
	mObstacleSkins[controlIndex]:setPoseDOF(mPose)
	mChecker:setPoseDOF(controlIndex-1,mPose)

	mDebugDraw:clear()
	if mObstacleSkins then
		for i=1, #mObstacleSkins do
			mObstacleSkins[i]:setMaterial('lightgrey_transparent')
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

				if mObstacleSkins then
					mObstacleSkins[iloader2+1]:setMaterial('red_transparent')
				end
				-- when b is plane, a is sphere
				--print(b.normal) 0 -1 0
				--print(b.idepth) 0.04 
				

				local p1=(b.position+b.normal*b.idepth)*config.skinScale
				local p2=b.position*config.skinScale

				--print(b.idepth)
				--local p1=(b.position-b.normal*b.idepth*0.5)*config.skinScale
				--local p2=(b.position+b.normal*b.idepth*0.5)*config.skinScale

				mDebugDraw:drawSphere(p1, "b1pos"..tostring(b.ibody)..tostring(i)..tostring(j), "green",1)
				mDebugDraw:drawSphere(p2, "b2pos"..tostring(b.ibody)..tostring(i)..tostring(j), "red",1.5)
				--print(b.idepth)

				lines:pushBack(p1)
				lines:pushBack(p2)
			end
		end
		dbg.drawTraj(mDebugDraw, lines:matView(), 'normals','solidred')
	end
end

function onCallback(w, userData)
end

function dtor()
	local bgnode=RE.ogreSceneManager():getSceneNode("BackgroundNode")
	bgnode:setVisible(true)
end

function frameMove(fElapsedTime)
end
function handleRendererEvent(ev, button, x,y) 
	if mCON then
		return mCON:handleRendererEvent(ev, button, x,y)
	end
	return 0
end
