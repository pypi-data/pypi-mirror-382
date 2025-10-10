
require("config")
require("module")
require("common")
require("RigidBodyWin/subRoutines/Constraints")
require("RigidBodyWin/subRoutines/CollisionChecker")

config={skinScale=100}
function ctor()
	this:updateLayout();

	this:create('Box', 'message', 'Usage: shift-drag ')
	this:create('Box', 'message2', 'the box with a sphere')
	this:updateLayout();


	local dh=21 -- default height

	local obstaclePos= {vector3(30,0+dh,0), vector3(-30,0+dh,0), vector3(60,30+dh,0), vector3(0,-10, 0), vector3(0, 2, 0)}
	local obstacleZrot={           10 ,             -10,               5,                      7,                0}
	--local obstacleSize={vector3(20,20,20),vector3(20,60,20), vector3(20,80,20), vector3(1000,20,2000)}
	local obstacleSize={vector3(20,20,20),vector3(20,60,20), vector3(20,20,40), vector3(1000,20,2000), vector3(20, 20, 60)}
	--local obstacleType={"BOX","BOX","BOX","BOX","BOX"} -- works well
	--local obstacleType={"BOX","SPHERE","BOX","PLANE"} -- works well
	local obstacleType={"CAPSULE","SPHERE","BOX","BOX", "BOX", "BOX"}
	--local obstacleType={"SPHERE","SPHERE","CAPSULE","BOX"} -- works well (sphere-capsule)
	--local obstacleType={"CYLINDER","SPHERE","BOX","BOX"} -- works well
	--local obstacleType={"SPHERE","SPHERE","CYLINDER","BOX"}-- works well
	--local obstacleType={"CAPSULE","CAPSULE","CAPSULE","CAPSULE"}-- ???

	local pos={vector3(0,22,0)}
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
			elseif obstacleType[i]=="SPHERE" then
				mesh:initEllipsoid(obstacleSize[i])
			elseif obstacleType[i]=="CYLINDER" then
				mesh:initCylinder(obstacleSize[i].x, obstacleSize[i].y, 20)
			elseif obstacleType[i]=="CAPSULE" then
				mesh:initCapsule(obstacleSize[i].x, obstacleSize[i].y)
			else
				mesh:initPlane(obstacleSize[i].x, obstacleSize[i].z)
			end
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
	--mObjectList:registerMesh(mObstacles[1], 'meshtest'):getLastCreatedEntity():setMaterialName('lightgrey_transparent')
	--mObjectList:findNode('meshtest'):scale(config.skinScale)

	--dbg.console()
	mChecker=CollisionChecker('gjk')
	for i, v in ipairs(mObstacles) do
		mChecker.collisionDetector:addObstacle(v)
	end
	for i=1,#obstaclePos do
		local initialState=vectorn(7)
		initialState:setVec3(0, obstaclePos[i]/config.skinScale)
		initialState:setQuater(3,quater(1,0,0,0))
		mChecker:setPoseDOF(i-1, initialState)
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
	solveIK()
end

function solveIK()

	mDebugDraw:clear()
	if mObstacleSkins then
		for i=1, #mObstacleSkins do
			mObstacleSkins[i]:setMaterial('lightgrey_transparent')
		end
	end
	local lines=vector3N()
	assert(mChecker.collisionDetector:isSignedDistanceSupported())

	local conPos=mCON.conPos(0)*0.01
	local argMin=0
	local minDist=1e5
	for i, v in ipairs(mObstacles) do
		local normal=vector3()
		local dist=mChecker.collisionDetector:calculateSignedDistance(i-1, 1, conPos, normal)
		if dist<minDist then
			argMin=i
			minDist=dist
		end

		print(i, normal, dist)
		lines:pushBack(conPos*100)
		lines:pushBack((conPos-normal*dist)*100)
		dbg.draw('Sphere', (conPos-normal*dist)*100, 'nearestpos'..i, 'red', 2)
	end

	for i=1, #mObstacleSkins do
		mObstacleSkins[i]:setMaterial('lightgrey_transparent')
	end
	mObstacleSkins[argMin]:setMaterial('red_transparent')

	if lines:size()>0 then
		dbg.drawTraj(mDebugDraw, lines:matView(), 'normals','solidred')
	end

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
