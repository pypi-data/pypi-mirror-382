require("config")
require("module")
require("common")
require("RigidBodyWin/subRoutines/Constraints")

-- moduleIk.lua contains the actual contructors of the IK solvers.
require("moduleIK")

config={
	"../Resource/motion/justin_straight_run/justin_straight_run.wrl",
	"../Resource/motion/justin_straight_run/justin_straight_run.dof", 
	{
		{'ltibia', 'lfoot', vector3(0.000000,-0.053740,0.111624),},
		{'rtibia', 'rfoot', vector3(0.000000,-0.054795,0.112272),},
	},
	initialHeight=0,
	skinScale=100,
}

function ctor()
	this:updateLayout();


	mMot=loadMotion(config[1], config[2])
	mLoader=mMot.loader

	mMotionDOFcontainer=mMot.motionDOFcontainer
	mMotionDOF=mMotionDOFcontainer.mot

	-- in meter scale
	for i=0, mMotionDOF:rows()-1 do
		mMotionDOF:matView():set(i, 1, mMotionDOF:matView()(i,1)+config.initialHeight)
	end

	-- rendering is done in cm scale
	mSkin= RE.createVRMLskin(mLoader, false);
	mSkin:scale(config.skinScale,config.skinScale,config.skinScale); -- motion data is in meter unit while visualization uses cm unit.
	mPose=vectorn()
	mPose:assign(mMotionDOF:row(0));
	mSkin:setPoseDOF(mPose);
	mSkin:setMaterial('lightgrey_transparent')

	mEffectors=MotionUtil.Effectors()
	local con=config[3]
	
	footPos=vector3N (#con);
	mEffectors:resize(#con);
	for i=1,#con do
		mEffectors(i-1):init(mLoader:getBoneByName(con[i][2]), con[i][3])
	end
	--
	--mIK=COM_IKsolver(mLoader, mEffectors, kneeIndices, axisSign)
	mIK=MotionUtil.createFullbodyIk_MotionDOF_MultiTarget_lbfgs(mLoader.dofInfo)

	mPose=vectorn()
	mPose:assign(mMotionDOF:row(0));
	mSkin:setPoseDOF(mPose);
	mLoader:setPoseDOF(mPose)
	local originalPos={}
	numCon=#config[3]
	for i=0,numCon-1 do
		local opos=mEffectors(i).bone:getFrame():toGlobalPos(mEffectors(i).localpos)
		originalPos[i+1]=opos*config.skinScale
	end
	originalPos[numCon+1]=mLoader:calcCOM()*config.skinScale
	
	mCON=Constraints(unpack(originalPos))
	--mCON:setOption(1*config.skinScale)
	mCON:connect(eventFunction)
end
function eventFunction()
	mPose:assign(mMotionDOF:row(0));
	mIK:_changeNumEffectors(numCon)
	for i=0,numCon-1 do
		--local originalPos=mEffectors(i).bone:getFrame():toGlobalPos(mEffectors(i).localpos)
		local originalPos=mCON.conPos(i)/config.skinScale
		footPos(i):assign(originalPos);
		--dbg.namedDraw("Sphere", originalPos*config.skinScale, "x"..i)
		mIK:_setEffector(i, mEffectors(i).bone, mEffectors(i).localpos)
	end
	mIK:_changeNumConstraints(1)
	local COM=mCON.conPos(numCon)/config.skinScale
	local wy=0
	mIK:_setCOMConstraint(0, COM, 1,wy,1)

	mIK:_effectorUpdated()
	mIK:IKsolve(mPose, footPos)
	mSkin:setPoseDOF(mPose);
end

function onCallback(w, userData)
   if w:id()=="button1" then
	   print("button1\n");
   elseif w:id()=="button2" then
	   print("button2\n");
   end
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
