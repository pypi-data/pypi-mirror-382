
require('moduleIK')
require("RigidBodyWin/subRoutines/MultiConstraints")

package.projectPath='../Samples/classification/'
package.path=package.path..";../Samples/classification/lua/?.lua" --;"..package.path
require("control/SDRE")



KinectTrackerFromFile=LUAclass()
KinectTrackerToFile=LUAclass()
if KinectTracker then
	function KinectTracker:trackSkeleton()
		local state=intvectorn()
		local data=vectorn()
		self:_trackSkeleton(state, data)
		return state, data
	end
end
function KinectTrackerFromFile:__init(stateFile, dataFile, numFrames)
	f=util.BinaryFile()
	f2=util.BinaryFile()
	f:openRead(stateFile)
	f2:openRead(dataFile)
	--local trackingState=intmatrixn();
	--local skeletonData=matrixn();
	local trackingState=intvectorn();
	local skeletonData=vectorn();
	f:unpack(trackingState)
	f2:unpack(skeletonData)
	--f:close()
	--f2:close()
	self.curr_frame=0
	numFrames=numFrames-20 -- i don't know why
	self.numFrames=numFrames 

	self.matTrackingState=intmatrixn()
	self.matTrackingState:resize(self.numFrames, NUI_SKELETON_POSITION_COUNT+1)
	self.matTrackingData=matrixn(self.numFrames, NUI_SKELETON_POSITION_COUNT*3)
	local function setData(i, trackingState, skeletonData)
		if trackingState:size()==1 then
			self.matTrackingState:row(i):set(0, trackingState(0))
		else
			self.matTrackingState:row(i):assign(trackingState)
			self.matTrackingData:row(i):assign(skeletonData)
		end
	end
	setData(0, trackingState, skeletonData)
	for i=1, numFrames-1 do
		local trackingState=intvectorn();
		local skeletonData=vectorn();
		f:unpack(trackingState)
		f2:unpack(skeletonData)

		print(i, numFrames)
		setData(i, trackingState, skeletonData)
	end
end

function KinectTrackerToFile:__init(filename )
	writeStateFile=util.BinaryFile()
	--writeStateFile:openWrite("kinect_state_gth.data")
	writeStateFile:openWrite(filename..'teststate.data')

	writeDataFile=util.BinaryFile()
	--writeDataFile:openWrite("kinect_data_gth.data")
	writeDataFile:openWrite(filename..'testdata.data')

	--self.trackingState=trackingState
	--self.skeletonData=skeletonData
	self.currFrame=0
end

function KinectTrackerToFile:close()
	writeStateFile:close()
	writeDataFile:close()
end
function KinectTrackerToFile:saveFeature(trackingState, skeletonData)
	writeStateFile:pack(trackingState)
	writeDataFile:pack(skeletonData)
end


function KinectTrackerFromFile:trackSkeleton(iframe)
	--	local i= self.currFrame
	--	if iframe then
	--		i=math.min(iframe, self.trackingState:rows()-1)
	--	end
	--	self.currFrame=math.min(i+1, self.trackingState:rows()-1)
	--	return self.trackingState:row(i), self.skeletonData:row(i)

	local trackingState=intvectorn();
	local skeletonData=vectorn();

	local curr_frame=self.curr_frame
	local num_frames=self.numFrames
	if (iframe>curr_frame and iframe < curr_frame+100 and curr_frame+1<num_frames and iframe<num_frames ) then -- this should be the same as that in KinectDevice.cpp
		curr_frame=curr_frame+1;
	else
		iframe=math.min(iframe, num_frames-1);
		curr_frame=iframe;
	end
	self.curr_frame=curr_frame
	trackingState:assign(self.matTrackingState:row(curr_frame))
	skeletonData:assign(self.matTrackingData:row(curr_frame))
	--f:unpack(trackingState)
	--f2:unpack(skeletonData)

	return  trackingState, skeletonData
end

function KinectTrackerFromFile:close()
end


KinectTrackerFromGUI=LUAclass()

function KinectTrackerFromGUI:__init(loader, initialPose, config)
	self.config=config
	require("RigidBodyWin/subRoutines/Constraints")
	self.loader=loader
	if initialPose then
		self.initialPose=initialPose:copy()
	end
end

function KinectTrackerFromGUI:finalizeSourceMotion(mMap, mMot)
	local loader=self.loader
	local config=self.config
	if not loader then
		self.loader=mMot.loader
		loader=self.loader
	end
	if not self.initialPose then
		self.initialPose=mMot.motionDOFcontainer.mot:row(0):copy()
	end
	self.loader:setPoseDOF(self.initialPose)

	local rootPos=loader:bone(1):getFrame().translation:copy()
	self.deltas=vector3N(4)
	self.deltas(0):assign( rootPos-mMap.NUI_SKELETON_POSITION_HIP_RIGHT:getFrame().translation) 
	self.deltas(1):assign( rootPos-mMap.NUI_SKELETON_POSITION_HIP_LEFT:getFrame().translation) 
	self.deltas(2):assign( rootPos-mMap.NUI_SKELETON_POSITION_SHOULDER_RIGHT:getFrame().translation)
	self.deltas(3):assign( rootPos-mMap.NUI_SKELETON_POSITION_SHOULDER_LEFT:getFrame().translation) 
	self.deltas=self.deltas*(config.skinScale/config.kinectScale)

	local pos={
		rootPos*config.skinScale,
		mMap.NUI_SKELETON_POSITION_ANKLE_RIGHT:getFrame().translation:copy()*config.skinScale, 
		mMap.NUI_SKELETON_POSITION_ANKLE_LEFT:getFrame().translation:copy()*config.skinScale, 
		mMap.NUI_SKELETON_POSITION_WRIST_RIGHT:getFrame().translation:copy()*config.skinScale, 
		mMap.NUI_SKELETON_POSITION_WRIST_LEFT:getFrame().translation:copy()*config.skinScale,
	}
	self.CON=Constraints(unpack(pos))
end
function KinectTrackerFromGUI:trackSkeleton()
	local state=intvectorn(NUI_SKELETON_POSITION_COUNT+1)
	local data=vectorn(NUI_SKELETON_POSITION_COUNT*3)
	local config=self.config
	state:setAllValue(STATE_TRACKED)
	data:setAllValue(0)

	-- A : meter unit
	-- B : kinect unit
	-- C : cm unit == A*skinScale
	-- C==B*kinectScale+kinectPosOffset
	-- (C-kinectPosOffset)*(1/kinectScale) == B
	
	local pos=(self.CON.conPos-config.kinectPosOffset)*(1/config.kinectScale)
	data:setVec3(3*NUI_SKELETON_POSITION_HIP_CENTER, pos(0))
	data:setVec3(3*NUI_SKELETON_POSITION_ANKLE_RIGHT, pos(1))
	data:setVec3(3*NUI_SKELETON_POSITION_ANKLE_LEFT, pos(2))
	data:setVec3(3*NUI_SKELETON_POSITION_WRIST_RIGHT, pos(3))
	data:setVec3(3*NUI_SKELETON_POSITION_WRIST_LEFT, pos(4))
	data:setVec3(3*NUI_SKELETON_POSITION_HIP_RIGHT, pos(0)-self.deltas(0))
	data:setVec3(3*NUI_SKELETON_POSITION_HIP_LEFT, pos(0)-self.deltas(1))
	data:setVec3(3*NUI_SKELETON_POSITION_SHOULDER_RIGHT, pos(0)-self.deltas(2))
	data:setVec3(3*NUI_SKELETON_POSITION_SHOULDER_LEFT, pos(0)-self.deltas(3))


	if false then
		local v=vectorn(5*3)
		v:setVec3(3*0, pos(0)*config.kinectScale+config.kinectPosOffset+vector3(10,0,0))
		v:setVec3(3*1, pos(1)*config.kinectScale+config.kinectPosOffset+vector3(10,0,0))
		v:setVec3(3*2, pos(2)*config.kinectScale+config.kinectPosOffset+vector3(10,0,0))
		v:setVec3(3*3, pos(3)*config.kinectScale+config.kinectPosOffset+vector3(10,0,0))
		v:setVec3(3*4, pos(4)*config.kinectScale+config.kinectPosOffset+vector3(10,0,0))
		dbg.namedDraw("PointClouds", "featureKK", v, "redCircle", "Z")
		v:setSize(4*3)
		v:setVec3(3*0, pos(0)-self.deltas(0)+vector3(10,0,0))
		v:setVec3(3*1, pos(0)-self.deltas(1)+vector3(10,0,0))
		v:setVec3(3*2, pos(0)-self.deltas(2)+vector3(10,0,0))
		v:setVec3(3*3, pos(0)-self.deltas(3)+vector3(10,0,0))
		dbg.namedDraw("PointClouds", "featureK2", v, "blueCircle", "Z")
	end
	return state, data
end

-- needs to optimize a=0.65, b=0.87, 
function getMatrix_to3Dcoord(kinectScale)
	local to3Dcoord=matrix4()
	to3Dcoord:setValue(0.65,0,0,0,
	0,0.86,0,0,
	0,0,1,0,
	0,0,0,1)
	local s= kinectScale*0.00100*1.0
	to3Dcoord:leftMultScaling(s,s,s)
	to3Dcoord:leftMultTranslation(config.kinectPosOffset)
	return to3Dcoord
end


local c=0
NUI_SKELETON_POSITION_HIP_CENTER = c c=c+1
NUI_SKELETON_POSITION_SPINE = c c=c+1
NUI_SKELETON_POSITION_SHOULDER_CENTER=c c=c+1
NUI_SKELETON_POSITION_HEAD=c c=c+1
NUI_SKELETON_POSITION_SHOULDER_LEFT=c c=c+1
NUI_SKELETON_POSITION_ELBOW_LEFT=c c=c+1
NUI_SKELETON_POSITION_WRIST_LEFT=c c=c+1
NUI_SKELETON_POSITION_HAND_LEFT=c c=c+1
NUI_SKELETON_POSITION_SHOULDER_RIGHT=c c=c+1
NUI_SKELETON_POSITION_ELBOW_RIGHT=c c=c+1
NUI_SKELETON_POSITION_WRIST_RIGHT=c c=c+1
NUI_SKELETON_POSITION_HAND_RIGHT=c c=c+1
NUI_SKELETON_POSITION_HIP_LEFT=c c=c+1
NUI_SKELETON_POSITION_KNEE_LEFT=c c=c+1
NUI_SKELETON_POSITION_ANKLE_LEFT=c c=c+1
NUI_SKELETON_POSITION_FOOT_LEFT=c c=c+1
NUI_SKELETON_POSITION_HIP_RIGHT=c c=c+1
NUI_SKELETON_POSITION_KNEE_RIGHT=c c=c+1
NUI_SKELETON_POSITION_ANKLE_RIGHT=c c=c+1
NUI_SKELETON_POSITION_FOOT_RIGHT=c c=c+1
NUI_SKELETON_POSITION_COUNT=c
names={
	"NUI_SKELETON_POSITION_SPINE",
	"NUI_SKELETON_POSITION_SHOULDER_CENTER",
	"NUI_SKELETON_POSITION_HEAD",
	"NUI_SKELETON_POSITION_SHOULDER_LEFT",
	"NUI_SKELETON_POSITION_ELBOW_LEFT",
	"NUI_SKELETON_POSITION_WRIST_LEFT",
	"NUI_SKELETON_POSITION_HAND_LEFT",
	"NUI_SKELETON_POSITION_SHOULDER_RIGHT",
	"NUI_SKELETON_POSITION_ELBOW_RIGHT",
	"NUI_SKELETON_POSITION_WRIST_RIGHT",
	"NUI_SKELETON_POSITION_HAND_RIGHT",
	"NUI_SKELETON_POSITION_HIP_LEFT",
	"NUI_SKELETON_POSITION_KNEE_LEFT",
	"NUI_SKELETON_POSITION_ANKLE_LEFT",
	"NUI_SKELETON_POSITION_FOOT_LEFT",
	"NUI_SKELETON_POSITION_HIP_RIGHT",
	"NUI_SKELETON_POSITION_KNEE_RIGHT",
	"NUI_SKELETON_POSITION_ANKLE_RIGHT",
	"NUI_SKELETON_POSITION_FOOT_RIGHT",
}
names[0]="NUI_SKELETON_POSITION_HIP_CENTER"
STATE_FAILED=0
STATE_POSITION_ONLY=1
STATE_TRACKED=2

config_ETRI={
	skel="../Resource/motion/skeletonEditor/fitting2_1dof_fixed.wrl",
	--skel="../Resource/motion/skeletonEditor/fitting2_1dof_fixed.wrl.bin",
	motion="../Samples/scripts/RigidBodyWin/retargetting/data/Data/2_1.bvh.dof.bvh",
	--conFile="../Samples/scripts/RigidBodyWin/retargetting/data/Data/2_1.bvh.dof.bvh.conEditor",
	skinScale=2.54*0.85,
	modelScale={
		leftLeg=1,
		rightLeg=1,
		spine=1,
		leftArm=1,
		rightArm=1,
	},
	kinectScale=100, 
	kinectPosOffset=vector3(0,105,-270),
	heightAdjustment={ 0, 0, 0},
	rightLeg={'RHip', 'RKnee', 'RAnkle', reversed=false},
	leftLeg= {'LHip', 'LKnee', 'LAnkle', reversed=false},
	rightArm={'RShoulder', 'RElbow', 'RWrist', reversed=false},
	leftArm= {'LShoulder', 'LElbow', 'LWrist', reversed=false},
	neck={'Neck', 'Head'},
	spine={'root', 'Neck'},
	toes={'LToe','RToe'},
	markerOffset=2,
	keyFrameDuration=10,
	debugMode=true,
	fixedJoints={ -- do not use these joints in the graph
		'LThWrist','LThMetac', 'LThIntra1', 
		'LF1Wrist', 'LF1Metac','LF1Intra1','LF1Intra2', 
		'LF2Wrist', 'LF2Metac','LF2Intra1','LF2Intra2', 
		'LF3Wrist', 'LF3Metac','LF3Intra1','LF3Intra2', 
		'LF4Wrist', 'LF4Metac','LF4Intra1','LF4Intra2', 
		'RThWrist', 'RThMetac','RThIntra1', 
		'RF1Wrist', 'RF1Metac','RF1Intra1','RF1Intra2', 
		'RF2Wrist', 'RF2Metac','RF2Intra1','RF2Intra2', 
		'RF3Wrist', 'RF3Metac','RF3Intra1','RF3Intra2', 
		'RF4Wrist', 'RF4Metac','RF4Intra1','RF4Intra2', 
		'Head1', 'LEyeJ', 'REyeJ',
		--'Spine','root',
		'LToe','RToe',
	},
	kneeDampingCoef_RO=math.rad(160),
	translateRefPoseAboveGround=true,	
	GROUND_HEIGHT=1, -- 1 cm. set this to nil to disable heightAdjustment
}
config_dance_M={
	skel="../../taesooLib/Resource/motion/skeletonEditor/dance1_M_1dof.wrl",
	motion="../../taesooLib/Resource/motion/skeletonEditor/dance1_M_1dof.wrl.dof",
	--conFile="../Samples/scripts/RigidBodyWin/retargetting/data/Data/2_1.bvh.dof.bvh.conEditor",
	skinScale=112.54*0.85,
	modelScale={
		leftLeg=1,
		rightLeg=1,
		spine=1,
		leftArm=1,
		rightArm=1,
	},
	kinectScale=100, 
	kinectPosOffset=vector3(0,105,-270),
	heightAdjustment={ 0, 0, 0},
	rightLeg={'RightHip', 'RightKnee', 'RightAnkle', reversed=true},
	leftLeg= {'LeftHip', 'LeftKnee', 'LeftAnkle', reversed=true},
	rightArm={'RightShoulder', 'RightElbow', 'RightWrist', reversed=false},
	leftArm= {'LeftShoulder', 'LeftElbow', 'LeftWrist', reversed=false},
	neck={'Neck', 'Head'},
	spine={'Hips', 'Neck'},
	toes={'LeftAnkle','RightAnkle'},
	markerOffset=2,
	keyFrameDuration=10,
	debugMode=true,
	--fixedJoints={ -- do not use these joints in the graph
	--	'LThWrist','LThMetac', 'LThIntra1', 
	--	'LF1Wrist', 'LF1Metac','LF1Intra1','LF1Intra2', 
	--	'LF2Wrist', 'LF2Metac','LF2Intra1','LF2Intra2', 
	--	'LF3Wrist', 'LF3Metac','LF3Intra1','LF3Intra2', 
	--	'LF4Wrist', 'LF4Metac','LF4Intra1','LF4Intra2', 
	--	'RThWrist', 'RThMetac','RThIntra1', 
	--	'RF1Wrist', 'RF1Metac','RF1Intra1','RF1Intra2', 
	--	'RF2Wrist', 'RF2Metac','RF2Intra1','RF2Intra2', 
	--	'RF3Wrist', 'RF3Metac','RF3Intra1','RF3Intra2', 
	--	'RF4Wrist', 'RF4Metac','RF4Intra1','RF4Intra2', 
	--	'Head1', 'LEyeJ', 'REyeJ',
	--	--'Spine','root',
	--	'LToe','RToe',
	--},
	kneeDampingCoef_RO=math.rad(160),
	translateRefPoseAboveGround=true,	
	GROUND_HEIGHT=0.01, -- 1 cm. set this to nil to disable heightAdjustment
}


kinectModule=LUAclass()

function _IKsolve(solver, pose, newRootTF, conpos, conori, importance)
	-- results go to solver.tempp
	local dim=6
	local max_iter=10
	local tol=0.001 -- used in frprmn termination condition
	local thr=1 -- used in NR_brek
	solver:init_cg(dim, 0.005, max_iter, tol, thr)
	local v=vectorn(dim)
	v:setAllValue(0)
	solver:optimize(v)
	local out=solver:getResult()
	_objectiveFunction (solver, out)
	solver.mSkeleton:getPoseDOF(pose)
end
function _objectiveFunction (solver, x)
	local eff=mEffectors
	--local hips=vector3N(eff:size())
	local pelvis=solver:getCenterBone(0)
	pelvis:getLocalFrame().translation:add(solver.mRootPos(0),x:toVector3(0))

	local theta=quater()
	theta:setRotation(x:toVector3(3))
	pelvis:getLocalFrame().rotation:mult(solver.mRootOri(0),theta)
	solver.mSkeleton:fkSolver():forwardKinematics()
	solver:_limbIK(solver.con, solver.conori, solver.impor)

	local d=0
	for c=0, solver.mEffectors:size()-1 do
		local eff=solver.mEffectors(c)
		local cpos=eff.bone:getFrame():toGlobalPos(eff.localpos)
		d=d+cpos:squaredDistance(solver.con(c))
	end
	-- skin scale 이 100인 경우에 적합하게 튜닝되어 있음.
	-- 
	local skinScale=config.skinScale
	local w=skinScale/100
	local l=x:length()
	d=d*w*w+0.1*l*l

	local self=mSolverInfo.kinectModule
	local featureD=self:extractFeature(solver.mSkeleton)
	-- excluding lHIP and rHip
	local n=featureD:size()
	local poseD=(mSolverInfo.featureK:range(6,n)-featureD:range(6,n)):length()
	--print(d, poseD*poseD/1000)
	return d+poseD*poseD/1000
end

--config=config_ETRI
config=config_dance_M
if KinectTracker then
	function KinectTracker:trackSkeleton()
		local state=intvectorn()
		local data=vectorn()
		self:_trackSkeleton(state, data)
		return state, data
	end
end
KinectTrackerFromFile=LUAclass()
function KinectTrackerFromFile:__init(filename, isTextFile)
	local trackingState=intmatrixn();
	local skeletonData=matrixn();
	if isTextFile then
		local f=util.readFile(filename) 
		f=string.tokenize(f, "%s+")
		local numState=NUI_SKELETON_POSITION_COUNT+1
		local numFrames=(#f-1)/NUI_SKELETON_POSITION_COUNT/3
		skeletonData:resize(numFrames, NUI_SKELETON_POSITION_COUNT*3)
		trackingState:resize(numFrames, numState)

		local TRACKED=2
		for i=0, numFrames-1 do
			trackingState:set(i,0, TRACKED)
			for j=0, NUI_SKELETON_POSITION_COUNT-1 do
				trackingState:set(i,j+1, 1)
				skeletonData:set(i,j*3, f[i*(NUI_SKELETON_POSITION_COUNT*3)+3*j+1])
				skeletonData:set(i,j*3+1, f[i*(NUI_SKELETON_POSITION_COUNT*3)+3*j+2])
				skeletonData:set(i,j*3+2, f[i*(NUI_SKELETON_POSITION_COUNT*3)+3*j+3])
			end
		end
	else
		local f=util.BinaryFile()
		f:openRead(filename)
		f:unpack(trackingState)
		f:unpack(skeletonData)
		f:close()
	end
	self.trackingState=trackingState
	self.skeletonData=skeletonData
	self.currFrame=0
end

function KinectTrackerFromFile:trackSkeleton(currFrameOverride)
	local i= self.currFrame
	if currFrameOverride then
		i=math.min(currFrameOverride, self.trackingState:rows()-1)
	end
	self.currFrame=math.min(i+1, self.trackingState:rows()-1)
	return self.trackingState:row(i), self.skeletonData:row(i)
end

function kinectModule:setLimbFeature(vec, pos1, pos2)
	vec:setVec3(0, pos1)
	vec:setVec3(3, pos2)
end
function kinectModule:setLimbFeature2(vec, pos1, pos2)
	vec:setVec3(0, self:kinectRawToCM(pos1))
	vec:setVec3(3, self:kinectRawToCM(pos2))
end
function kinectModule:offsetFeatureVector(feature, origin)

	local n=feature:size()/3
	for i=0, n-1 do
		feature:setVec3(i*3, feature:toVector3(i*3)-origin)
	end
end

function kinectModule:getFeatureSize()
	local limbFeatureSize=3*2
	return limbFeatureSize*4
end
-- loader's already set posed.
function kinectModule:extractFeature(loader)
	-- four limbs and two positons for each limb
	local limbFeatureSize=3*2
	local feature=vectorn()
	local config=self.config
	feature:setSize(limbFeatureSize*4+3)
	local  mMap=self.mMap

	self:setLimbFeature(feature:range(limbFeatureSize*0, limbFeatureSize*1), 
	mMap.NUI_SKELETON_POSITION_HIP_RIGHT:getFrame().translation, 
	mMap.NUI_SKELETON_POSITION_HIP_LEFT:getFrame().translation)
	self:setLimbFeature(feature:range(limbFeatureSize*1, limbFeatureSize*2), 
	mMap.NUI_SKELETON_POSITION_ANKLE_RIGHT:getFrame().translation, 
	mMap.NUI_SKELETON_POSITION_ANKLE_LEFT:getFrame().translation) 
	self:setLimbFeature(feature:range(limbFeatureSize*2, limbFeatureSize*3), 
	mMap.NUI_SKELETON_POSITION_SHOULDER_RIGHT:getFrame().translation, 
	mMap.NUI_SKELETON_POSITION_WRIST_RIGHT:getFrame().translation) 
	self:setLimbFeature(feature:range(limbFeatureSize*3, limbFeatureSize*4), 
	mMap.NUI_SKELETON_POSITION_SHOULDER_LEFT:getFrame().translation, 
	mMap.NUI_SKELETON_POSITION_WRIST_LEFT:getFrame().translation) 


	feature:setVec3(limbFeatureSize*4, loader:bone(1):getFrame().translation)
	--offsetFeatureVector(feature, loader:bone(1):getFrame().translation)

	feature=feature*config.skinScale
	return feature
end

function kinectModule:extractKinectFeature(data)
	-- four limbs and two positons for each limb
	local limbFeatureSize=3*2
	local feature=vectorn()
	feature:setSize(limbFeatureSize*4+3)

	self:setLimbFeature2(feature:range(limbFeatureSize*0, limbFeatureSize*1), 
	data:toVector3(3*NUI_SKELETON_POSITION_HIP_RIGHT),
	data:toVector3(3*NUI_SKELETON_POSITION_HIP_LEFT))
	self:setLimbFeature2(feature:range(limbFeatureSize*1, limbFeatureSize*2), 
	data:toVector3(3*NUI_SKELETON_POSITION_ANKLE_RIGHT),
	data:toVector3(3*NUI_SKELETON_POSITION_ANKLE_LEFT))
	self:setLimbFeature2(feature:range(limbFeatureSize*2, limbFeatureSize*3), 
	data:toVector3(3*NUI_SKELETON_POSITION_SHOULDER_RIGHT),
	data:toVector3(3*NUI_SKELETON_POSITION_WRIST_RIGHT))
	self:setLimbFeature2(feature:range(limbFeatureSize*3, limbFeatureSize*4), 
	data:toVector3(3*NUI_SKELETON_POSITION_SHOULDER_LEFT),
	data:toVector3(3*NUI_SKELETON_POSITION_WRIST_LEFT))

	--dbg.namedDraw("PointClouds", "featureK", feature, "redCircle", "Z")

	feature:setVec3(limbFeatureSize*4, self:kinectRawToCM(data:toVector3(3*NUI_SKELETON_POSITION_HIP_CENTER )))
	--offsetFeatureVector(feature, data:toVector3(3*NUI_SKELETON_POSITION_HIP_CENTER ))
	return feature
end

function kinectModule:__init(kinectTracker, mot_table, config)
	if config.filtering==nil then
		config.filtering=true
	end
	if config.kinectOriMod==nil then
		config.kinectOriMod=quater(1,0,0,0)
	end
	if not config.filteringMethod then
		config.filteringMethod='SDSFilter'
		--config.filteringMethod='OnlineFilter'
	end
	self.config=config
	self.mMap={
		NUI_SKELETON_POSITION_SHOULDER_LEFT=config.leftArm[1],
		NUI_SKELETON_POSITION_ELBOW_LEFT=config.leftArm[2],
		NUI_SKELETON_POSITION_WRIST_LEFT=config.leftArm[3],
		NUI_SKELETON_POSITION_SHOULDER_RIGHT=config.rightArm[1],
		NUI_SKELETON_POSITION_ELBOW_RIGHT=config.rightArm[2],
		NUI_SKELETON_POSITION_WRIST_RIGHT=config.rightArm[3],
		NUI_SKELETON_POSITION_HIP_LEFT=config.leftLeg[1],
		NUI_SKELETON_POSITION_KNEE_LEFT=config.leftLeg[2],
		NUI_SKELETON_POSITION_ANKLE_LEFT=config.leftLeg[3],
		NUI_SKELETON_POSITION_HIP_RIGHT=config.rightLeg[1],
		NUI_SKELETON_POSITION_KNEE_RIGHT=config.rightLeg[2],
		NUI_SKELETON_POSITION_ANKLE_RIGHT=config.rightLeg[3],
	}
	self.kinectTracker=kinectTracker
	--mKinectTracker=KinectTracker()
	local conPos=vector3N(NUI_SKELETON_POSITION_COUNT )
	conPos:setAllValue(vector3(0,0,0))
	self.mCON=MultiConstraints(conPos)
	if not mot_table then
		--local mMot=loadMotion(config.skel, config.motion, config.skinScale) 
		--self.mMot=mMot
		local mMot=loadMotion(config.skel, config.motion) 
		self.mMot=mMot
		local mLoader=mMot.loader

		--local max_iter=mLoader:numBone()
		for i=1, mLoader:numBone()-1 do
			if mLoader:VRMLbone(i):numChannels()==0 then
				mLoader:removeAllRedundantBones()
				--mLoader:removeBone(mLoader:VRMLbone(i))
				--mLoader:export(config[1]..'_removed_fixed.wrl')
				break
			end
		end
		mLoader:_initDOFinfo()
		mLoader:printHierarchy()

		mMot.skin=RE.createVRMLskin(mLoader, false)
		local s=config.skinScale
		mMot.skin:scale(s,s,s)
		mMot.skin:setThickness(3/s)
		mMot.skin:setMaterial('lightgrey_transparent')
		mMot.skin:setVisible(false)
		--mMot.skin:applyMotionDOF(mMot.motionDOFcontainer.mot)
	else
		self.mMot=mot_table
		assert(mot_table.loader)
		assert(mot_table.motionDOFcontainer)
	end
	local mMot=self.mMot

	if self.config.filteringMethod=='SDSFilter' then
		self.filter=SDSFilter(mMot.loader, 1, nil, config.skinScale)
	else
		self.filter=OnlineFilter(mMot.loader, nil, 5)
	end

	do
		local i=1
		config.toeIndices={}
		for k,v in pairs(config.toes) do
			config.toeIndices[i]=mMot.loader:getBoneByName(v):treeIndex()
		end
	end
	--mMot.loader:exportBinary(config.skel..".bin")
	--mMot._motion=mMot._loader.mMotion
	changeBoneLength(mMot.loader, config, config.modelScale)
	--mMot.skin:stopAnim()

	self:finalizeSourceMotion()
	if config.debugMode then
		g_skinDebugHuman=RE.createVRMLskin(mMot.loader, false)
		g_skinDebugHuman2=RE.createVRMLskin(mMot.loader, false)
		--g_skinDebugHuman:setVisible(false)
		
		--local temp=MotionLoader("../../testdata/etri_example.mot")
		--mMot._loader.mMotion:init(temp.mMotion, 0, temp.mMotion:numFrames())
		--_finalizeSourceMotionFromExternalInput()
	end
	if self.kinectTracker.finalizeSourceMotion then
		self.kinectTracker:finalizeSourceMotion(self.mMap, self.mMot)
		self.kinectTracker:finalizeSourceMotion(self.mMap)
	end



	self.simulator=Physics.DynamicsSimulator_TRL_QP('libccd')
	self.simulator:registerCharacter(mMot.loader)
	-- timestep: 1/120
	self.simulator:init(1/120, Physics.DynamicsSimulator.EULER)

end

function kinectModule:changeBoneLength_abs(indexBone, link_length)
	local mMot=self.mMot
	local loader=mMot.loader
	local b=loader:bone(indexBone)
	SkeletonEditorModule.changeLength_abs(loader, b, link_length)
end
function kinectModule:getJointIndices()
	local mMot=self.mMot
	local shoulders=intvectorn(4)
	local config=self.config
	shoulders:set(0, mMot.loader:getTreeIndexByName(config.rightLeg[1]))
	shoulders:set(1, mMot.loader:getTreeIndexByName(config.leftLeg[1]))
	shoulders:set(2, mMot.loader:getTreeIndexByName(config.rightArm[1]))
	shoulders:set(3, mMot.loader:getTreeIndexByName(config.leftArm[1]))
	local elbows=intvectorn(4)
	elbows:set(0, mMot.loader:getTreeIndexByName(config.rightLeg[2]))
	elbows:set(1, mMot.loader:getTreeIndexByName(config.leftLeg[2]))
	elbows:set(2, mMot.loader:getTreeIndexByName(config.rightArm[2]))
	elbows:set(3, mMot.loader:getTreeIndexByName(config.leftArm[2]))
	local wrists=intvectorn(4)
	wrists:set(0, mMot.loader:getTreeIndexByName(config.rightLeg[3]))
	wrists:set(1, mMot.loader:getTreeIndexByName(config.leftLeg[3]))
	wrists:set(2, mMot.loader:getTreeIndexByName(config.rightArm[3]))
	wrists:set(3, mMot.loader:getTreeIndexByName(config.leftArm[3]))
	return shoulders, elbows, wrists
end
function kinectModule:_finalizeSourceMotionFromExternalInput()
	local mMot=self.mMot
	local mMap=self.mMap
	local motion=mMot._loader.mMotion
	--local numRotJoint=motion:pose(0):numRotJoint()
	mMot.motionDOFcontainer:resize(motion:numFrames())

	local shoulders, elbows, wrists=self:getJointIndices()
	mMot.motionDOFcontainer.mot:set(motion, shoulders, elbows, wrists)
	--mMot.skin:applyMotionDOF(mMot.motionDOFcontainer.mot)
	--mMot.skin:stopAnim()
	self:finalizeSourceMotion()
end
function kinectModule:finalizeSourceMotion()

	local mMot=self.mMot
	local mMap=self.mMap
	for k,v in pairs(mMap) do
		if type(v)=='string' then
			mMap[k]=mMot.loader:getBoneByName(v)
		end
	end

	local features=matrixn()
	local mot=mMot.motionDOFcontainer.mot
	local shoulders, wrists=self:getJointIndices()
	local blendInfo={}
	blendInfo.shoulders=shoulders
	blendInfo.wrists=wrists
	blendInfo.q_shdr=matrixn(mot:numFrames(), 4*4) 
	blendInfo.q_wrst=matrixn(mot:numFrames(), 4*4) 

	for i=0, mot:numFrames()-1 do
		local loader=mMot.loader
		loader:setPoseDOF(mot:row(i))
		features:pushBack(self:extractFeature(loader))

		for j=0,3 do
			blendInfo.q_shdr:row(i):setQuater(j*4, loader:bone(blendInfo.shoulders(j)):getLocalFrame().rotation)
			blendInfo.q_wrst:row(i):setQuater(j*4, loader:bone(blendInfo.wrists(j)):getLocalFrame().rotation)
		end
	end
	mMetric=math.KovarMetric(true)
	mIDW=NonlinearFunctionIDW(mMetric, 30, 2.0)
	--mIDW=NonlinearFunctionIDW(mMetric, 30, 2.0)
	mIDW:learn(features, mot:matView())


	mBlendInfo=blendInfo
end

function kinectModule:dtor()
	dbg.finalize()
	detachSkins()
end


function kinectModule:calcLegLength(skel)
	local config=self.config
	local rightLeg=config.rightLeg
	local boneHip=skel:getBoneByName(rightLeg[1])
	local boneKnee=skel:getBoneByName(rightLeg[2])
	local boneAnkle=skel:getBoneByName(rightLeg[3])

	local l1=boneKnee:getOffsetTransform().translation:length()
	local l2=boneAnkle:getOffsetTransform().translation:length()

	return l1+l2
end

function kinectModule:getPendulum(vecn)
	self.filter:setCurrPose(vecn)
	vecn:assign(self.filter:getFiltered())
end
function kinectModule:calcKinectLegLen()
	local llen=self.mCON.conPos(NUI_SKELETON_POSITION_ANKLE_LEFT):distance(self.mCON.conPos(NUI_SKELETON_POSITION_KNEE_LEFT))+
	self.mCON.conPos(NUI_SKELETON_POSITION_KNEE_LEFT):distance(self.mCON.conPos(NUI_SKELETON_POSITION_HIP_LEFT))
	local rlen=self.mCON.conPos(NUI_SKELETON_POSITION_ANKLE_RIGHT):distance(self.mCON.conPos(NUI_SKELETON_POSITION_KNEE_RIGHT))+
	self.mCON.conPos(NUI_SKELETON_POSITION_KNEE_RIGHT):distance(self.mCON.conPos(NUI_SKELETON_POSITION_HIP_RIGHT))
	return llen, rlen
end

function kinectModule:oneStep(iframe)
	local mMot=self.mMot
	local state, data=self.kinectTracker:trackSkeleton(iframe)
	local config=self.config
	RE.output2("state", state)

	if state:count(STATE_TRACKED)>state:size()/2  then
	--if true then
		local conIndex=intvectorn()
		for i=0, NUI_SKELETON_POSITION_COUNT-1 do
--			--getPendulum(data:toVector3(i*3),i)
			if state(i+1)==1  or state(i+1) ==2 then
				self.mCON.conPos(i):assign(self:kinectRawToCM(data:toVector3(i*3)))
			else
				conIndex:pushBack(i)
			end
		end
		RE.output2('foot_left', self.mCON.conPos(NUI_SKELETON_POSITION_FOOT_LEFT))
		local llen, rlen=self:calcKinectLegLen()
		RE.output2('left_leglen', llen)
		RE.output2('right_leglen', rlen)
		RE.output2('legLen', self:calcLegLength(mMot.loader)*config.skinScale)
		self.mCON.conIndex=conIndex
		self.mCON:drawConstraints()

		local target=vectorn()
		local weight=vectorn() 
		local index=intvectorn()
		--mIDW:mapping(extractKinectFeature(data), target)
		--mIDW:mapping2(extractKinectFeature(data), target, weight)
		--g_argMax=weight:argMax()
		mIDW:mapping2(self:extractKinectFeature(data), target, index, weight)
		g_argMax=index(weight:argMax())

		local loader=mMot.loader

		target:setQuater(3, target:toQuater(3):Normalize())


		if true then
			local shdr=matrixn()
			local wrst=matrixn()
			local blendInfo=mBlendInfo
			shdr:extractRows(blendInfo.q_shdr, index)
			wrst:extractRows(blendInfo.q_wrst, index)

			loader:setPoseDOF(target)
			local q=quater()
			for j=0,3 do
				q:blend(weight, shdr:range(0, shdr:rows(), j*4, (j+1)*4))
				loader:bone(blendInfo.shoulders(j)):getLocalFrame().rotation:assign(q)
				q:blend(weight, wrst:range(0, shdr:rows(), j*4, (j+1)*4))
				loader:bone(blendInfo.wrists(j)):getLocalFrame().rotation:assign(q)
			end
			loader:fkSolver():forwardKinematics()
			loader:getPoseDOF(target)
		end

		local featureK=self:extractKinectFeature(data)
		local featureD=self:extractFeature(loader)
		mMetric:calcDistance(featureK, featureD)
		local tf=transf(mMetric.transfB)
		tf.translation:scale(1/config.skinScale)

		roottf=tf*MotionDOF.rootTransformation(target)
		MotionDOF.setRootTransformation(target, roottf)


		g_pose_beforeIK=target:copy()
		
--		quat_before_root:normalize()
		if true and config.GROUND_HEIGHT then
			loader:setPoseDOF(g_pose_beforeIK)
			local toeHeight=10000
			for i, v in ipairs(config.toeIndices) do
				toeHeight=math.min(toeHeight, loader:bone(v):getFrame().translation.y)
			end
			local s=config.skinScale
			if toeHeight*s<config.GROUND_HEIGHT then
				local delta=config.GROUND_HEIGHT/s-toeHeight
				g_pose_beforeIK:set(1, g_pose_beforeIK:get(1)+delta)
			end
		end



		if false then
			dbg.namedDraw("PointClouds", "featureK", featureK, "redCircle", "Z")
			dbg.namedDraw("PointClouds", "featureD", featureD, "blueCircle", "Z")
		end

		self:solveIK(target, state, data, featureK)
		self:clampVelocity(g_pose_beforeIK, target, config.velocityThrIK or 1)
		
		if self.config.filtering then
			local prevPose=self.filter:getCurrentDesired()
			self:clampVelocity(prevPose, target, config.velocityThr or 1)
		end

		g_pose_afterIK=target:copy()
		if config.debugMode then
			g_skinDebugHuman:setPoseDOF(g_pose_beforeIK)
			local s=config.skinScale
			g_skinDebugHuman:setScale(s,s,s)
			g_skinDebugHuman:setTranslation(100,0,0)
			g_skinDebugHuman:setMaterial('lightgrey_transparent')

			--g_skinDebugHuman2:setPoseDOF(mMot.motionDOFcontainer.mot:row(g_argMax))
			g_skinDebugHuman2:setPoseDOF(g_pose_afterIK)

			local s=config.skinScale
			g_skinDebugHuman2:setScale(s,s,s)
			g_skinDebugHuman2:setTranslation(200,0,0)
			g_skinDebugHuman2:setMaterial('lightgrey_verytransparent')
		end

		if self.config.filtering then
			-- with filtering
			self.filter:setCurrPose(g_pose_afterIK)
			g_pose_afterIK=self.filter:getFiltered()
		end

		-- further solve ik to position the feet above the ground.
		do 
			loader:setPoseDOF(g_pose_afterIK)
			local EE={
				NUI_SKELETON_POSITION_ANKLE_LEFT,
				NUI_SKELETON_POSITION_ANKLE_RIGHT,
			}
			
			local effectors=mSolverInfoFoot.effectors
			local footPos=vector3N(2)
			local footOri=quaterN(2)
			local importance=CT.ones(2)
			for limb=1,2 do
				local i=limb-1
				local treeIndex=effectors(i).bone:treeIndex()
				local originalJointPos=effectors(i).bone:getFrame().translation
				footPos(i):assign(originalJointPos);
				if footPos(i).y<config.GROUND_HEIGHT then
					footPos(i).y=config.GROUND_HEIGHT
				end
				footOri(i):assign(effectors(i).bone:getFrame().rotation)
			end
			mSolverInfoFoot.solver:IKsolve3(g_pose_afterIK, MotionDOF.rootTransformation(g_pose_afterIK), footPos, footOri, importance)
		end

		mMot.skin:setPoseDOF(g_pose_afterIK)
		--mMot.skin:setVisible(true)

	end
	return g_pose_afterIK
end

function kinectModule:solveIK(sourcePose, state, data, featureK)
	local mMot=self.mMot
	local config=self.config
	local EE={
		NUI_SKELETON_POSITION_ANKLE_LEFT,
		NUI_SKELETON_POSITION_ANKLE_RIGHT,
		NUI_SKELETON_POSITION_WRIST_LEFT, 
		NUI_SKELETON_POSITION_WRIST_RIGHT,
	}

	local elbows={
		NUI_SKELETON_POSITION_KNEE_LEFT,
		NUI_SKELETON_POSITION_KNEE_RIGHT,
		NUI_SKELETON_POSITION_ELBOW_LEFT,
		NUI_SKELETON_POSITION_ELBOW_RIGHT,
	}
	local shoulders={
		NUI_SKELETON_POSITION_HIP_LEFT,
		NUI_SKELETON_POSITION_HIP_RIGHT,
		NUI_SKELETON_POSITION_SHOULDER_LEFT,
		NUI_SKELETON_POSITION_SHOULDER_RIGHT,
	}
	local function genIKconfig(con)
		return {con[1], con[2], con[3], vector3(0,0,0), reversed=con.reversed}
	end
	local IKconfig=
	{
		genIKconfig(config.leftLeg),
		genIKconfig(config.rightLeg),
		genIKconfig(config.leftArm),
		genIKconfig(config.rightArm),
	}
	--local solver=solvers.MultiTarget_semihybrid_nlopt
	local solver=solvers.MultiTarget_lbfgs
	--local solver=solvers.LimbIKsolver
	--local solver=solvers.LUA -- does not work for etri.
	mSolverInfo=createIKsolver(solver, mMot.loader, IKconfig)
	mSolverInfoFoot=createIKsolver(solvers.LimbIKsolver, mMot.loader, { genIKconfig(config.leftLeg), genIKconfig(config.rightLeg)}) 

	local numCon=mSolverInfo.numCon
	local footPos=vector3N(numCon)
	local footOri=quaterN(numCon)
	if mMot.importance==nil then
		local importance=vectorn(numCon)
		importance:setAllValue(1)
		mMot.importance=importance
	end
	local importance=mMot.importance
	local mEffectors=mSolverInfo.effectors
	mMot.loader:setPoseDOF(sourcePose)
	for limb=1,4 do
		local i=limb-1
		local treeIndex=mEffectors(i).bone:treeIndex()
		local originalJointPos=mEffectors(i).bone:getFrame().translation
		footPos(i):assign(originalJointPos);
		footOri(i):assign(mEffectors(i).bone:getFrame().rotation)
		local ee=EE[limb]
		local delta=0.03

		footPos(i):assign(self.mCON.conPos(ee)/config.skinScale)
		if state(ee+1)~=STATE_FAILED then
			--addConstraints
			importance:set(limb-1, math.min(importance(limb-1)+delta, 1))
		else
			importance:set(limb-1, math.max(importance(limb-1)-delta, 0))
		end
	end
	--solveIKwhileMinizingTheErrorBetweenThePointCloudsAndTheBody
	mSolverInfo.conori=footOri
	mSolverInfo.featureK=featureK
	mSolverInfo.kinectModule=self
	local mMap=self.mMap
	
	if mSolverInfo.solver.IKsolve3 then
		mSolverInfo.solver:IKsolve3(sourcePose, MotionDOF.rootTransformation(sourcePose), footPos, footOri, importance)
	else
		mSolverInfo.solver:IKsolve(sourcePose, footPos)
	end
	--sourcePose:range(7,sourcePose:size()):setAllValue(0)


	local loader=mMot.loader
	loader:setPoseDOF(sourcePose)
	for i,v in ipairs(elbows) do
		local wrist_bone=mMap[names[ EE[i] ] ]
		local elb_bone=mMap[names[v] ]
		local sh_bone=mMap[names[ shoulders[i] ] ]
		local goal_elb=(self:kinectRawToCM(data:toVector3(v*3)))/config.skinScale

		local vv=vectorn(3*3)
		vv:setVec3(0,wrist_bone:getFrame().translation)
		--vv:setVec3(3,elb_bone:getFrame().translation)
		vv:setVec3(3,sh_bone:getFrame().translation)
		vv:setVec3(6,goal_elb)

		--dbg.namedDraw('PointClouds', "hihi"..v, vv*config.skinScale, "redCircle", "Z")
		self:IKsolveSwivelAngle(loader,sh_bone, elb_bone, wrist_bone, goal_elb)
	end

	loader:getPoseDOF(sourcePose)
end

function kinectModule:IKsolveSwivelAngle(loader, sh_bone, elb_bone, wrist_bone, goal_elb)
	local p0=sh_bone:getFrame().translation:copy()
	local p1=elb_bone:getFrame().translation:copy()
	local p2=wrist_bone:getFrame().translation:copy()
	
	local axis=p2-p0
	axis:normalize()
	local center=(p0+p2)/2
	local front=p1-center
	local target=goal_elb-center
	local q=quater()
	q:setAxisRotation(axis, front, target)
	local angle=q:rotationAngleAboutAxis(axis)
	if angle<-math.rad(30) then
		angle=-math.rad(30)
	elseif angle>math.rad(30) then
		angle=math.rad(30)
	end
	local femurLen=(p1-p0):length()
	local importance=sop.clampMap(target:length(), 0.2*femurLen,0.4*femurLen, 0, 1) 	
	angle=angle*importance
	q:setRotation(axis, angle)
	--q:setRotation(axis, math.rad(90))
	loader:rotateBoneGlobal(sh_bone,q)
end

function kinectModule:detachSkins()
	if RE.motionPanelValid() then
		if mSkin then
			RE.motionPanel():motionWin():detachSkin(mSkin)
			mSkin=nil
		end
	end
	-- remove objects that are owned by LUA
	collectgarbage()
end

function kinectModule:stepKinematic_row( pose, dpose)
	local sim=self.simulator
	sim:setLinkData(0, Physics.DynamicsSimulator.JOINT_VALUE, pose)
	local zero=vectorn()
	zero:setSize(dpose:size()-1)
	zero:setAllValue(0)
	local ddq=zero
	local tau=zero
	sim:setLinkData(0, Physics.DynamicsSimulator.JOINT_VELOCITY, dpose)
	sim:initSimulation()
	sim:stepKinematic(ddq, tau, true)
	sim:getLinkData(0, Physics.DynamicsSimulator.JOINT_VALUE, pose)
end
function calcDerivative_row_fd(i, dmotionDOF, motionDOF)
	local frameRate=120
   local q=quater()
   local v=vector3()
   local dmotionDOF_i=dmotionDOF:row(i);
   dmotionDOF_i:sub(motionDOF:row(i+1), motionDOF:row(i)) -- forward 
   MainLib.VRMLloader.projectAngles(dmotionDOF_i) -- align angles
   dmotionDOF_i:rmult(frameRate)

   local T=MotionDOF.rootTransformation(motionDOF, i)
   local twist=T:twist(MotionDOF.rootTransformation(motionDOF, i+1),1/frameRate)
   -- incorrect, but previous results were optimized using this.
   dmotionDOF_i:setVec3(0, twist.v)
   dmotionDOF_i:setVec3(4, twist.w)
end

function kinectModule:autoAdjust()
	-- adjust scale and height
	local loader=self.mMot.loader
	local skelLen=self:calcLegLength(loader)*config.skinScale
	local llen, rlen=self:calcKinectLegLen()
	local kinectSkelLen=llen*0.5+ rlen*0.5
	-- 90/170 =     110
	if kinectSkelLen>40 then --  leg should be longer than 40 cm. (all elemetry schoolers should meet this criteria.)
		local minY=math.min(self.mCON.conPos(NUI_SKELETON_POSITION_ANKLE_LEFT).y, self.mCON.conPos(NUI_SKELETON_POSITION_ANKLE_RIGHT).y) 

		local origKinectScale=config.kinectScale
		local origKinectPosOffsetY=config.kinectPosOffset.y
		local newKinectScale=skelLen/kinectSkelLen*origKinectScale
		local kinectY=(minY-origKinectPosOffsetY)/origKinectScale
		config.kinectScale=newKinectScale
		config.kinectPosOffset.y=-kinectY*newKinectScale+13 -- place the marker at 10 cm
	end
end
-- to centi-meter unit.
function kinectModule:kinectRawToCM(v)
	local config=self.config
	return config.kinectOriMod*(v*config.kinectScale+config.kinectPosOffset)
end

function kinectModule:clampVelocity(prevPose, newPose, thr)
	if not thr then 
		thr=1
	end
	-- clamp velocity
	local mot=matrixn(2, newPose:size())
	local dmot=matrixn(2, newPose:size())
	assert(newPose:size()==prevPose:size())
	mot:row(0):assign(prevPose)
	mot:row(1):assign(newPose)

	calcDerivative_row_fd(0, dmot, mot)

	-- threshhold
	local dpose=dmot:row(0)
	local rootvel=math.clampVec3(dpose:toVector3(0), 200*thr)
	dpose:setVec3(0, rootvel)
	local rootangvel=math.clampVec3(dpose:toVector3(4), 20*thr)
	dpose:setVec3(4, rootangvel)
	for i=7, newPose:size()-1 do
		dpose:set(i, math.clamp(dpose(i), -10*thr, 10*thr))
	end
	--print(dmot:row(0))
	newPose:assign(prevPose)
	self:stepKinematic_row(newPose, dmot:row(0))
end

SDSFilter=LUAclass()

function SDSFilter:__init(loader, mass, pose, skinScale)
	self.mPendulum={}
	-- the smaller, the smoother
	self.scaleFactor=vectorn(loader.dofInfo:numDOF()+1)
	self.scaleFactor:setAllValue(1)
   -- root position
   self.scaleFactor:range(0,3):setAllValue(skinScale/100) -- change to meter scale
   -- root orientation
   self.scaleFactor:range(3,7):setAllValue(1) -- offsetQ 
   self.scaleFactor:set(self.scaleFactor:size()-1,1) -- rotY

   local nDOF=loader.dofInfo:numDOF()
	for i=0,nDOF-1 do
		if i>=3 and i<7 then
			self.mPendulum[i+1]=SDS(mass,0.001, 1, 10000000, 0,1/120)
		else
			self.mPendulum[i+1]=SDS(mass,0.001, 1, 10000000, 0,1/120)
		end
	end
	-- rotY
	self.mPendulum[nDOF+1]=SDS(mass,0.001, 1, 10000000, 0,1/120)

	if pose then
		self:setCurrPose(pose)
	end
end
function SDSFilter:setCurrPose(pose) -- set the desired pose for tracking.
	local N = pose:size()
	local rotY=quater()
	local offsetQ=quater()
	pose:toQuater(3):decompose(rotY, offsetQ)

	if false then -- USE QUATERNION
		local i
		i=3 self.mPendulum[i+1].xd:set(0,0, self.scaleFactor(i)*offsetQ.w)
		i=4 self.mPendulum[i+1].xd:set(0,0, self.scaleFactor(i)*offsetQ.x)
		i=5 self.mPendulum[i+1].xd:set(0,0, self.scaleFactor(i)*offsetQ.y)
		i=6 self.mPendulum[i+1].xd:set(0,0, self.scaleFactor(i)*offsetQ.z)
	else
		local v=offsetQ:rotationVector()
		local i
		i=3 self.mPendulum[i+1].xd:set(0,0, 0)
		i=4 self.mPendulum[i+1].xd:set(0,0, self.scaleFactor(i)*v.x)
		i=5 self.mPendulum[i+1].xd:set(0,0, self.scaleFactor(i)*v.y)
		i=6 self.mPendulum[i+1].xd:set(0,0, self.scaleFactor(i)*v.z)
	end
	for i=0,N-1 do
		if i>=3 and i<7 then
		else
			self.mPendulum[i+1].xd:set(0,0, self.scaleFactor(i)*pose(i))
		end
	end
	local pRotY=self.mPendulum[N+1].x(0,0)
	local protY=quater(pRotY, vector3(0,1,0))
	local delta=quater()
	delta:difference(protY, rotY)
	delta:align(quater(1,0,0,0))

	--print(delta:rotationAngleAboutAxis(vector3(0,1,0)))
	self.mPendulum[N+1].xd:set(0,0, self.scaleFactor(N)*(pRotY+delta:rotationAngleAboutAxis(vector3(0,1,0))))
end
function SDSFilter:getCurrent()
	local N=#self.mPendulum-1
	local vecn=vectorn(N+1)
	for i=0,N do
		vecn:set(i,(1/self.scaleFactor(i))*self.mPendulum[i+1].x(0,0))
	end
	local offsetQ
	if false then -- USE QUATERNION
		offsetQ=vecn:toQuater(3)
		offsetQ:normalize()
	else
		offsetQ=quater()
		local v=vecn:toVector3(4)
		--print(v)
		--v:zero()
		offsetQ:setRotation(v)
	end
	local protY=quater(vecn(N), vector3(0,1,0))
	vecn:setQuater(3,protY*offsetQ)
	vecn:resize(vecn:size()-1)
	--vecn:setQuater(3, self.cpose:toQuater(3))
	return vecn
end
function SDSFilter:getCurrentDesired()
	local N=#self.mPendulum-1
	local vecn=vectorn(N+1)
	for i=0,N do
		vecn:set(i,(1/self.scaleFactor(i))*self.mPendulum[i+1].xd(0,0))
	end
	local offsetQ
	if false then -- USE QUATERNION
		offsetQ=vecn:toQuater(3)
		offsetQ:normalize()
	else
		offsetQ=quater()
		local v=vecn:toVector3(4)
		--print(v)
		--v:zero()
		offsetQ:setRotation(v)
	end
	local protY=quater(vecn(N), vector3(0,1,0))
	vecn:setQuater(3,protY*offsetQ)
	vecn:resize(vecn:size()-1)
	--vecn:setQuater(3, self.cpose:toQuater(3))
	return vecn
end

function SDSFilter:getFiltered()
	local N=#self.mPendulum-1
	for i=0,N do
		self.mPendulum[i+1]:singleStep()
	end

	return self:getCurrent()
end
