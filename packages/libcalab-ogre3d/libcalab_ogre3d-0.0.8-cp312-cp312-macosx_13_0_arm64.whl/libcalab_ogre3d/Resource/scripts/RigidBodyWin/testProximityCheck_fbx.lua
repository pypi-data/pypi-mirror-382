
require("config")
require("module")
require("common")
require("RigidBodyWin/subRoutines/Constraints")
require("RigidBodyWin/subRoutines/CollisionChecker")
CA=require("RigidBodyWin/subRoutines/CollisionIK")
local FBXloader=require("FBXloader")

config={skinScale=100}
VERBOSE=true
dbg.fontSize=3
function ctor()
	this:updateLayout();

	this:create('Box', 'message', 'Usage: shift-drag ')
	this:create('Box', 'message2', 'the box with a sphere')
	this:updateLayout();


	local dh=21 -- default height

	local obstaclePos= {vector3(30,0+dh,0), vector3(-30,0+dh,0), vector3(60,30+dh,0), vector3(0,-10, 0), vector3(0, 2, 0), vector3(0,0,0)}
	local obstacleZrot={           10 ,             -10,               5,                      7,                0}
	--local obstacleSize={vector3(20,20,20),vector3(20,60,20), vector3(20,80,20), vector3(1000,20,2000)}
	local obstacleSize={vector3(20,20,20),vector3(20,60,20), vector3(20,20,40), vector3(1000,20,2000), vector3(20, 20, 60)}
	--local obstacleType={"BOX","BOX","BOX","BOX","BOX"} -- works well
	--local obstacleType={"BOX","SPHERE","BOX","PLANE"} -- works well
	local obstacleType={"CAPSULE","SPHERE","BOX","BOX", "BOX", "CHARACTER"}
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
			elseif obstacleType[i]=="CHARACTER" then
				assert(i==#obstacleType)
				require("subRoutines/WRLloader")

				local skelFile='../Resource/motion/Mixamo/passive_nomarker_man_T.fbx.dat' skinScale=100
				-- 위 fbx에 맞는 동작 만드는 예제는 ~/sample_SAMP/lua/showLafanMotions_skinned.lua
				fbx=FBXloader(skelFile, {skinScale=skinScale, newRootBone=root, mirror=mirror, useTexture=true})

				local _loader, _motdofc,mot=RE.loadMotions(nil,
				{
					{"../../Mixamo/fbx/Macarena Dance.fbx", identity_pose='../../Mixamo/fbx/T-Pose.fbx'},
					scale=0.01
				})
				_loader:setPoseDOF(_motdofc:row(0))
				local poseMap=_loader:getPoseMap()
				poseMap.rotJoints:gsub("mixamorig:", "")
				poseMap.transJoints:gsub("mixamorig:", "")

				fbx.cacheCollisionMesh=skelFile..'.colcache'
				fbx.loader:setPoseMap(poseMap) 

				mObstacles[i]=fbx

				g_fingers=CA.checkAllChildren(fbx.loader,'LeftHand'):bitwiseOR( CA.checkAllChildren(fbx.loader,'RightHand'))
				break
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

	mChecker=CollisionChecker('sdf') --signed-distance field
	--mChecker=CA.HCollisionChecker()
	for i, v in ipairs(mObstacles) do
		if obstacleType[i]=='CHARACTER' then
			mChecker.collisionDetector:addModel(v)
		else
			mChecker.collisionDetector:addObstacle(v)
		end
	end
	for i=1,#obstaclePos do
		if obstacleType[i]=='CHARACTER' then
			mChecker:setPoseDOF(i-1, mObstacles[i]:getPoseDOF())
			break
		end
		local initialState=vectorn(7)
		initialState:setVec3(0, obstaclePos[i]/config.skinScale)
		initialState:setQuater(3,quater(1,0,0,0))
		mChecker:setPoseDOF(i-1, initialState)
	end

	mObstacleSkins={}
	for i=1, #obstaclePos do
		local v=mChecker.collisionDetector:getModel(i-1)
		if mObstacles[i].fbxInfo then
			mObstacleSkins[i]= RE.createFBXskin(mObstacles[i], false);
			if false then
				debugSkin= RE.createVRMLskin(v, false);
				debugSkin:setMaterial('lightgrey_transparent')
				local s=config.skinScale
				debugSkin:setScale(s,s,s)
				local state=mChecker.pose[i-1]
				debugSkin:setPoseDOF(state)
			end
		else
			mObstacleSkins[i]= RE.createVRMLskin(v, false);
		end
		mObstacleSkins[i]:setMaterial('lightgrey_transparent')
		local s=config.skinScale
		mObstacleSkins[i]:setScale(s,s,s)
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
		local det=mChecker.collisionDetector
		local loader=det:getModel(i-1)
		for j=1, loader:numBone()-1 do
			if loader:VRMLbone(j):hasShape() then
				if j>1 and g_fingers(j) then
					-- too many finger geom -> cluttered rendering
				else
					local dist
					local surfacePoint

					if false then
						local normal=vector3()
						-- use low-level api. (inaccurate)
						dist=det:calculateSignedDistance(i-1, j, conPos, normal)
						surfacePoint=conPos-normal*dist
					else
						dist, surfacePoint=det:calculateNearestSurfacePoint(i-1, j, conPos)
					end
					if dist<minDist then
						argMin=i
						minDist=dist
					end
					print(i, dist)
					lines:pushBack(conPos*100)
					lines:pushBack(surfacePoint*100)
					if VERBOSE then
						local name=loader:VRMLbone(j):name()
						if name:sub(1,10)=='mixamorig:' then
							name=name:sub(11)
						end
						dbg.namedDraw('Sphere', surfacePoint*100, name..'_'..i, 'red', 2)
					else
						dbg.draw('Sphere', surfacePoint*100, 'nearestpos'..i..'_'..j, 'red', 2)
					end
				end
			end
		end
	end

	for i=1, #mObstacleSkins do
		mObstacleSkins[i]:setMaterial('lightgrey_transparent')
	end
	mObstacleSkins[argMin]:setMaterial('lightgrey_verytransparent')

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
