
require("config")
require("module")
require("common")
require("RigidBodyWin/subRoutines/Constraints")
require("RigidBodyWin/subRoutines/CollisionChecker")

config={skinScale=100}
function ctor()

	this:create('Box', 'message', 'Usage: shift-drag on scene')

	this:updateLayout();



	local dh=0

	local obstaclePos= {vector3(30,0+dh,0), vector3(-30,0+dh,0), vector3(60,30+dh,0), vector3(0,-10+dh, 0), vector3(0, 2, 0)}
	local obstacleZrot={           10 ,             -10,               5,                      7,                0}
	--local obstacleSize={vector3(20,20,20),vector3(20,60,20), vector3(20,80,20), vector3(1000,20,2000)}
	local obstacleSize={vector3(20,20,20),vector3(20,60,20), vector3(20,20,40), vector3(1000,20,2000), vector3(20, 20, 60)}
	--local obstacleType={"BOX","BOX","BOX","BOX"} -- works well
	--local obstacleType={"BOX","SPHERE","BOX","PLANE"} -- works well
	local obstacleType={"CAPSULE","SPHERE","BOX","BOX", "BOX", "BOX"}
	--local obstacleType={"SPHERE","SPHERE","CAPSULE","BOX"} -- works well (sphere-capsule)
	--local obstacleType={"CYLINDER","SPHERE","BOX","BOX"} -- works well
	--local obstacleType={"SPHERE","SPHERE","CYLINDER","BOX"}-- works well
	--local obstacleType={"CAPSULE","CAPSULE","CAPSULE","CAPSULE"}-- ???

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

	mChecker=CollisionChecker(unpack(mObstacles))
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
end

function onCallback(w, userData)
end

function dtor()
end

function frameMove(fElapsedTime)
end
function handleRendererEvent(ev, button, x,y) 

	if ev=="PUSH" then
		return 1
	elseif ev=="DRAG" then
		return 1
	elseif ev=="RELEASE" then
		return 1
	elseif ev=="MOVE" then
		local ray=Ray()
		RE.FltkRenderer():screenToWorldRay(x, y,ray)

		local from=ray:origin()
		to=ray:origin()+ray:direction()*1000 -- 10 meter away.
		
		local res, pos, normal=mChecker:checkRayIntersection(from, to)

		if res then
			--dbg.draw("Sphere", o*config.skinScale, "x0")
			dbg.draw('Sphere', pos*config.skinScale, 'cursor_', 'red_transparent', 5)
			dbg.draw('Arrow', pos*config.skinScale, (pos+normal*0.2)*config.skinScale, 'arrowname',1)
		else
			dbg.erase('Sphere', 'cursor_')
			dbg.erase('Arrow', 'arrowname')
		end

		return 1
	end
	return 0
end
